"""
reference_auditor.py - Reference List Retraction Screening Module
Audits citations within an uploaded research paper / manuscript against Retraction Watch database.
"""

import os
import re
import csv
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

RETRACTIONS_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "retractions.csv")
RETRACTED_CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cache", "retracted_dois_index.json")

# In-memory dictionary: normalized_doi -> dict of retraction info
_RETRACTED_INDEX: Optional[Dict[str, Dict[str, Any]]] = None

# Regex patterns for DOIs
DOI_REGEX = re.compile(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+', re.IGNORECASE)

def _clean_doi(doi: str) -> str:
    """Strip trailing punctuation from extracted DOI."""
    if not doi:
        return ""
    d = doi.strip().rstrip(".,;)>]\"' ")
    return d.lower()

def load_retractions_index() -> Dict[str, Dict[str, Any]]:
    """
    Loads retracted paper DOIs into an in-memory lookup dict.
    Uses cached JSON index if available, else builds from retractions.csv and caches.
    """
    global _RETRACTED_INDEX
    if _RETRACTED_INDEX is not None:
        return _RETRACTED_INDEX

    os.makedirs(os.path.dirname(RETRACTED_CACHE_FILE), exist_ok=True)

    if os.path.exists(RETRACTED_CACHE_FILE):
        try:
            with open(RETRACTED_CACHE_FILE, "r", encoding="utf-8") as f:
                _RETRACTED_INDEX = json.load(f)
                logger.info(f"Loaded {len(_RETRACTED_INDEX)} retracted DOIs from cache.")
                return _RETRACTED_INDEX
        except Exception as e:
            logger.warning(f"Failed to load cached retracted DOIs index: {e}. Rebuilding from CSV.")

    index: Dict[str, Dict[str, Any]] = {}
    if not os.path.exists(RETRACTIONS_CSV):
        logger.error(f"retractions.csv not found at {RETRACTIONS_CSV}")
        _RETRACTED_INDEX = {}
        return _RETRACTED_INDEX

    try:
        # Use latin1 encoding as verified
        with open(RETRACTIONS_CSV, "r", encoding="latin1", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_doi = row.get("OriginalPaperDOI", "")
                if not raw_doi:
                    continue
                doi_clean = _clean_doi(raw_doi)
                if not doi_clean:
                    continue

                # Store essential retraction details
                if doi_clean not in index:
                    index[doi_clean] = {
                        "doi": doi_clean,
                        "title": row.get("Title", "").strip(),
                        "journal": row.get("Journal", "").strip(),
                        "retraction_date": row.get("RetractionDate", "").strip(),
                        "retraction_nature": row.get("RetractionNature", "").strip(),
                        "reason": row.get("Reason", "").strip()[:300], # truncate long reasons
                        "retraction_doi": row.get("RetractionDOI", "").strip()
                    }

        # Save to cache
        try:
            with open(RETRACTED_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(index, f)
            logger.info(f"Built and cached {len(index)} retracted DOIs index.")
        except Exception as e:
            logger.warning(f"Could not save cache to {RETRACTED_CACHE_FILE}: {e}")

        _RETRACTED_INDEX = index
        return _RETRACTED_INDEX
    except Exception as e:
        logger.error(f"Error building retractions index: {e}")
        _RETRACTED_INDEX = {}
        return _RETRACTED_INDEX


def extract_references_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Splits text into reference entries and extracts DOIs.
    Looks for References / Bibliography section or citation patterns.
    """
    if not text:
        return []

    # Find where References section starts
    ref_heading_match = re.search(r'\n\s*(?:references|bibliography|works cited|literature cited)\s*\n', text, re.IGNORECASE)
    
    if ref_heading_match:
        ref_text = text[ref_heading_match.end():]
    else:
        # If no explicit heading, check if there are bracketed citations at the end
        ref_text = text

    # Split into lines/blocks
    raw_lines = [l.strip() for l in ref_text.split('\n') if l.strip()]
    
    # Try chunking by numbered citation like [1], 1., (1)
    citations = []
    current_citation = []
    
    num_pattern = re.compile(r'^(\[\d+\]|\d+\.|\(\d+\))\s+')

    for line in raw_lines:
        if num_pattern.match(line):
            if current_citation:
                citations.append(" ".join(current_citation))
                current_citation = []
            current_citation.append(line)
        else:
            if current_citation:
                current_citation.append(line)
            else:
                # If no numbering started yet, check if line contains a DOI
                if DOI_REGEX.search(line):
                    citations.append(line)

    if current_citation:
        citations.append(" ".join(current_citation))

    # If numbered chunking yielded few results, extract all DOIs found anywhere in ref_text or full text
    refs_result = []
    seen_dois = set()

    for idx, c in enumerate(citations):
        doi_matches = DOI_REGEX.findall(c)
        clean_matches = [_clean_doi(m) for m in doi_matches if _clean_doi(m)]
        for d in clean_matches:
            seen_dois.add(d)
        refs_result.append({
            "index": idx + 1,
            "raw_text": c[:300] + ("..." if len(c) > 300 else ""),
            "dois": clean_matches
        })

    # Also search full text for any DOIs not captured in the references block
    all_dois_in_text = DOI_REGEX.findall(text)
    for raw_d in all_dois_in_text:
        d = _clean_doi(raw_d)
        if d and d not in seen_dois:
            seen_dois.add(d)
            refs_result.append({
                "index": len(refs_result) + 1,
                "raw_text": f"Extracted from manuscript body: {raw_d}",
                "dois": [d]
            })

    return refs_result


def audit_references(references: List[Dict[str, Any]], primary_doi: Optional[str] = None) -> Dict[str, Any]:
    """
    Matches extracted reference DOIs against the Retraction Watch index.
    Ignores the manuscript's own DOI if provided.
    """
    index = load_retractions_index()
    primary_clean = _clean_doi(primary_doi) if primary_doi else ""

    flagged_retractions = []
    checked_dois = set()

    for ref in references:
        for doi in ref.get("dois", []):
            if not doi or doi == primary_clean:
                continue
            if doi in checked_dois:
                continue
            checked_dois.add(doi)

            if doi in index:
                info = index[doi]
                flagged_retractions.append({
                    "doi": doi,
                    "title": info.get("title") or "Unknown Title",
                    "journal": info.get("journal") or "Unknown Journal",
                    "retraction_date": info.get("retraction_date") or "Unknown Date",
                    "retraction_nature": info.get("retraction_nature") or "Retraction",
                    "reason": info.get("reason") or "No reason specified in record",
                    "citation_context": ref.get("raw_text", "")
                })

    total_citations = len(references)
    retracted_count = len(flagged_retractions)

    status = "CLEAN" if retracted_count == 0 else "WARNING" if retracted_count < 3 else "CRITICAL"

    return {
        "status": status,
        "total_references_detected": total_citations,
        "dois_screened": len(checked_dois),
        "retracted_count": retracted_count,
        "retracted_references": flagged_retractions,
        "audit_summary": f"Detected {retracted_count} retracted work(s) out of {len(checked_dois)} screened reference DOIs." if retracted_count > 0 else f"No retracted works found among {len(checked_dois)} screened references."
    }
