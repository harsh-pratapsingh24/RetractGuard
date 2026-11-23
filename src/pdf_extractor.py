"""
RetractGuard PDF Extraction Module
Uses PyMuPDF (fitz) to extract metadata, text, DOIs, authors, titles, and publication dates
from research paper PDFs, with robust handling for scanned documents and malformed files.
"""

import re
import os
import io
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
import fitz  # PyMuPDF

logger = logging.getLogger("RetractGuardPDFExtractor")

# Standard DOI regular expression matching common publisher syntax
DOI_REGEX_PATTERNS = [
    # Explicit DOI URL or prefix
    re.compile(r'(?:https?://(?:dx\.)?doi\.org/|doi:\s*|doi/)(10\.\d{4,9}/[^\s"\'<>]+)', re.IGNORECASE),
    # Raw DOI pattern starting with 10.xxxx/
    re.compile(r'\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)', re.IGNORECASE),
]

YEAR_REGEX = re.compile(r'\b(19\d{2}|20\d{2})\b')


def clean_extracted_doi(doi_candidate: str) -> Optional[str]:
    """
    Cleans trailing punctuation, parentheses, brackets, or HTML fragments from extracted DOI.
    """
    if not doi_candidate:
        return None

    cleaned = doi_candidate.strip()
    # Strip protocol prefix if present
    cleaned = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^doi:\s*', '', cleaned, flags=re.IGNORECASE)

    # Strip trailing punctuation marks commonly attached at the end of a sentence
    cleaned = re.sub(r'[\.,;:\)\'\"\]\>]+$', '', cleaned)
    # Strip trailing slash if not part of suffix
    cleaned = cleaned.rstrip('/')

    # Validate basic DOI structure: 10.xxxx/...
    if re.match(r'^10\.\d{4,9}/.+$', cleaned):
        return cleaned
    return None


def extract_paper_info_from_pdf(
    source: Union[str, bytes, io.BytesIO],
    max_pages_for_text: int = 5
) -> Dict[str, Any]:
    """
    Extracts paper metadata, text content, and publication identifiers from a PDF.

    Parameters:
    - source: File path (str), raw bytes (bytes), or file-like object.
    - max_pages_for_text: Max pages to inspect for DOI/title heuristics (default: 5).

    Returns:
    - Dict with extracted fields:
        success: bool
        is_scanned: bool
        doi: Optional[str]
        title: Optional[str]
        authors: List[str]
        authors_str: Optional[str]
        publication_year: Optional[int]
        page_count: int
        text_length: int
        extracted_text_preview: str
        warnings: List[str]
        metadata: Dict[str, Any]
    """
    warnings: List[str] = []
    doc = None

    try:
        if isinstance(source, str):
            if not os.path.exists(source):
                return {
                    "success": False,
                    "is_scanned": False,
                    "doi": None,
                    "title": None,
                    "authors": [],
                    "authors_str": None,
                    "publication_year": None,
                    "page_count": 0,
                    "text_length": 0,
                    "extracted_text_preview": "",
                    "warnings": [f"File not found: {source}"],
                    "metadata": {}
                }
            doc = fitz.open(source)
        elif isinstance(source, bytes):
            doc = fitz.open(stream=source, filetype="pdf")
        elif hasattr(source, "read"):
            data = source.read()
            doc = fitz.open(stream=data, filetype="pdf")
        else:
            return {
                "success": False,
                "is_scanned": False,
                "doi": None,
                "title": None,
                "authors": [],
                "authors_str": None,
                "publication_year": None,
                "page_count": 0,
                "text_length": 0,
                "extracted_text_preview": "",
                "warnings": ["Unsupported source type provided to PDF extractor."],
                "metadata": {}
            }

        page_count = len(doc)
        if page_count == 0:
            doc.close()
            return {
                "success": False,
                "is_scanned": False,
                "doi": None,
                "title": None,
                "authors": [],
                "authors_str": None,
                "publication_year": None,
                "page_count": 0,
                "text_length": 0,
                "extracted_text_preview": "",
                "warnings": ["The provided PDF has 0 pages (empty file)."],
                "metadata": {}
            }

        # 1. Inspect PDF metadata dictionary
        pdf_meta = doc.metadata or {}
        meta_title = (pdf_meta.get("title") or "").strip()
        meta_author = (pdf_meta.get("author") or "").strip()
        meta_subject = (pdf_meta.get("subject") or "").strip()
        meta_keywords = (pdf_meta.get("keywords") or "").strip()
        creation_date = (pdf_meta.get("creationDate") or "").strip()

        # Filter out generic default titles produced by word processors
        generic_titles = ["untitled", "microsoft word", "word document", "latex document", "manuscript", "document"]
        if meta_title.lower() in generic_titles or len(meta_title) < 5:
            meta_title = None

        # 2. Extract text and analyze page contents
        pages_to_read = min(page_count, max_pages_for_text)
        page_texts: List[str] = []
        total_chars = 0
        total_images = 0

        for p_idx in range(pages_to_read):
            page = doc[p_idx]
            text = page.get_text() or ""
            page_texts.append(text)
            total_chars += len(text.strip())
            total_images += len(page.get_images())

        full_extracted_text = "\n".join(page_texts)

        # 3. Detect Scanned / Image-Only PDFs
        # If very few characters extracted across the first few pages while images exist
        is_scanned = (total_chars < 80 and (total_images > 0 or page_count > 0))

        if is_scanned:
            warnings.append(
                "Scanned / image-only PDF detected (no embedded OCR text layer). "
                "Automatic text and DOI extraction is unavailable from bitmap pages. "
                "Please verify or enter the DOI manually."
            )

        # 4. Search for DOI
        detected_doi: Optional[str] = None
        doi_source: Optional[str] = None

        # Check metadata fields first
        combined_meta = f"{meta_subject} {meta_keywords} {meta_title or ''}"
        for pattern in DOI_REGEX_PATTERNS:
            match = pattern.search(combined_meta)
            if match:
                candidate = clean_extracted_doi(match.group(1) if match.lastindex else match.group(0))
                if candidate:
                    detected_doi = candidate
                    doi_source = "pdf_metadata"
                    break

        # Check extracted text if not found in metadata
        if not detected_doi and full_extracted_text:
            for pattern in DOI_REGEX_PATTERNS:
                matches = pattern.findall(full_extracted_text)
                for m in matches:
                    cand = m if isinstance(m, str) else m[0]
                    cleaned = clean_extracted_doi(cand)
                    if cleaned:
                        detected_doi = cleaned
                        doi_source = "pdf_text"
                        break
                if detected_doi:
                    break

        # 5. Extract Title Heuristic
        extracted_title: Optional[str] = meta_title
        if not extracted_title and not is_scanned and page_count > 0:
            first_page = doc[0]
            # Use block layout analysis to find the largest font in top half of page 1
            blocks = first_page.get_text("dict").get("blocks", [])
            candidate_blocks = []

            for b in blocks:
                if b.get("type") == 0:  # text block
                    # Only consider blocks in top 50% of the page
                    bbox = b.get("bbox", [0, 0, 0, 0])
                    if bbox[1] < first_page.rect.height * 0.55:
                        for line in b.get("lines", []):
                            for span in line.get("spans", []):
                                text_span = span.get("text", "").strip()
                                font_size = span.get("size", 0)
                                if len(text_span) > 8 and font_size >= 11:
                                    candidate_blocks.append((font_size, text_span))

            if candidate_blocks:
                # Pick span with largest font size
                candidate_blocks.sort(key=lambda x: x[0], reverse=True)
                largest_size = candidate_blocks[0][0]
                # Join consecutive spans sharing roughly the same largest font size
                title_parts = [t for s, t in candidate_blocks if abs(s - largest_size) < 1.0]
                extracted_title = " ".join(title_parts[:3]).strip()

        # 6. Extract Authors Heuristic
        extracted_authors: List[str] = []
        if meta_author and len(meta_author) > 2:
            # Split common delimiters: semicolon, comma, and
            split_authors = re.split(r'[,;]|\band\b', meta_author)
            extracted_authors = [a.strip() for a in split_authors if len(a.strip()) > 1]

        # If not in metadata, inspect lines beneath title on page 1
        if not extracted_authors and full_extracted_text and not is_scanned:
            lines = [l.strip() for l in page_texts[0].split("\n") if l.strip()]
            for line in lines[:10]:
                if any(x in line.lower() for x in ["university", "department", "doi:", "abstract", "http", "vol.", "issue"]):
                    continue
                if "," in line and len(line) < 120:
                    candidates = [a.strip() for a in line.split(",") if len(a.strip()) > 2]
                    if len(candidates) >= 2:
                        extracted_authors = candidates
                        break

        # 7. Extract Publication Year
        extracted_year: Optional[int] = None
        if creation_date.startswith("D:"):
            try:
                extracted_year = int(creation_date[2:6])
            except Exception:
                pass

        if not extracted_year and full_extracted_text:
            year_matches = YEAR_REGEX.findall(full_extracted_text[:1500])
            for y_str in year_matches:
                y = int(y_str)
                if 1990 <= y <= 2026:
                    extracted_year = y
                    break

        # 8. Check for Reference Section Count
        ref_count_heuristic = None
        if "reference" in full_extracted_text.lower() or "bibliography" in full_extracted_text.lower():
            # Count bracketed references like [1], [2], etc.
            ref_matches = re.findall(r'\[\d{1,3}\]', full_extracted_text)
            if ref_matches:
                ref_count_heuristic = len(set(ref_matches))

        # Close document
        doc.close()

        # Warning checks
        if not detected_doi:
            warnings.append(
                "DOI was not detected in document text or metadata. "
                "Will attempt title-based scholarly graph matching."
            )
        if not extracted_title:
            warnings.append("Document title could not be automatically determined from PDF text layers.")

        preview = full_extracted_text[:600].replace("\n", " ").strip() if full_extracted_text else ""

        return {
            "success": True,
            "is_scanned": is_scanned,
            "doi": detected_doi,
            "doi_source": doi_source,
            "title": extracted_title,
            "authors": extracted_authors,
            "authors_str": ", ".join(extracted_authors) if extracted_authors else None,
            "publication_year": extracted_year,
            "reference_count_heuristic": ref_count_heuristic,
            "page_count": page_count,
            "text_length": total_chars,
            "extracted_text_preview": preview,
            "warnings": warnings,
            "metadata": {
                "title": pdf_meta.get("title"),
                "author": pdf_meta.get("author"),
                "producer": pdf_meta.get("producer"),
                "creator": pdf_meta.get("creator"),
                "creation_date": creation_date
            }
        }

    except Exception as e:
        logger.error(f"Error processing PDF with PyMuPDF: {e}", exc_info=True)
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass
        return {
            "success": False,
            "is_scanned": False,
            "doi": None,
            "title": None,
            "authors": [],
            "authors_str": None,
            "publication_year": None,
            "page_count": 0,
            "text_length": 0,
            "extracted_text_preview": "",
            "warnings": [f"PyMuPDF failed to parse PDF document: {str(e)}"],
            "metadata": {}
        }
