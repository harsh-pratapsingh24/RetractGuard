"""
RetractGuard API Client Module
Fetches author, citation, journal, and publication data via OpenAlex and Crossref APIs
with polite pool headers, exponential backoff retries, local JSON caching, and graceful error handling.
"""

import os
import re
import json
import time
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import requests

logger = logging.getLogger("RetractGuardAPIClient")

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

PROCESSED_FEATURES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed_features.csv")

OPENALEX_WORKS_URL = "https://api.openalex.org/works"
OPENALEX_AUTHORS_URL = "https://api.openalex.org/authors"
CROSSREF_WORKS_URL = "https://api.crossref.org/works"

HEADERS = {
    "User-Agent": "RetractGuard/2.4 (mailto:retractguard@academic-integrity.org; Academic Research Script)"
}

# Cache for journal baseline rates
_JOURNAL_BASELINE_CACHE: Optional[Dict[str, float]] = None


def _get_cache_path(prefix: str, identifier: str) -> str:
    safe_id = hashlib.md5(identifier.strip().lower().encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{prefix}_{safe_id}.json")


def validate_doi(doi: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validates and cleans a DOI string.
    Returns: (is_valid, cleaned_doi, error_message)
    """
    if not doi or not isinstance(doi, str):
        return False, "", "DOI cannot be empty."

    cleaned = doi.strip()
    # Remove URL prefixes
    cleaned = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^doi:\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.rstrip('/')

    # Validate pattern: 10.xxxx/...
    if not re.match(r'^10\.\d{4,9}/[^\s]+$', cleaned):
        return False, cleaned, f"Invalid DOI format '{doi}'. Valid DOIs begin with '10.' followed by 4-9 digits, a slash, and a publisher suffix (e.g. 10.1038/s41586-021-03819-2)."

    return True, cleaned, None


def fetch_openalex_work(doi: str, title_fallback: Optional[str] = None, max_retries: int = 2) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Fetch paper work object from OpenAlex by DOI, with fallback to title search if 404.
    """
    warnings: List[str] = []
    is_valid, clean_doi, err = validate_doi(doi)
    if not is_valid:
        warnings.append(err or "Invalid DOI provided.")
        return None, warnings

    cache_path = _get_cache_path("openalex_work", clean_doi)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f), warnings
        except Exception:
            pass

    # Direct DOI query
    url = f"{OPENALEX_WORKS_URL}/https://doi.org/{clean_doi}"
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                try:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(data, f)
                except Exception:
                    pass
                return data, warnings
            elif resp.status_code == 404:
                warnings.append(f"DOI '{clean_doi}' was not indexed in OpenAlex works catalog.")
                break
            elif resp.status_code == 429:
                warnings.append("OpenAlex rate limit encountered (HTTP 429); applying backoff.")
                time.sleep(1.0 * (2 ** attempt))
            else:
                time.sleep(0.4 * (2 ** attempt))
        except Exception as e:
            if attempt == max_retries:
                warnings.append(f"Network error querying OpenAlex for DOI '{clean_doi}': {str(e)}")
            time.sleep(0.4 * (2 ** attempt))

    # Fallback to search by title if available
    if title_fallback and len(title_fallback.strip()) > 8:
        search_url = f"{OPENALEX_WORKS_URL}?search={requests.utils.quote(title_fallback.strip())}&per_page=1"
        try:
            resp = requests.get(search_url, headers=HEADERS, timeout=6)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    warnings.append(f"Resolved paper metadata using OpenAlex title search for '{title_fallback[:60]}...'.")
                    return results[0], warnings
        except Exception as e:
            warnings.append(f"Title fallback search in OpenAlex failed: {str(e)}")

    return None, warnings


def fetch_crossref_work(doi: str, max_retries: int = 2) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Fetch paper metadata from Crossref REST API for peer-review dates and publisher telemetry.
    """
    warnings: List[str] = []
    is_valid, clean_doi, err = validate_doi(doi)
    if not is_valid:
        warnings.append(err or "Invalid DOI provided for Crossref query.")
        return None, warnings

    cache_path = _get_cache_path("crossref_work", clean_doi)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f), warnings
        except Exception:
            pass

    url = f"{CROSSREF_WORKS_URL}/{clean_doi}"
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=6)
            if resp.status_code == 200:
                data = resp.json().get("message", {})
                try:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(data, f)
                except Exception:
                    pass
                return data, warnings
            elif resp.status_code == 404:
                warnings.append(f"DOI '{clean_doi}' was not found in Crossref metadata registry.")
                break
            elif resp.status_code == 429:
                warnings.append("Crossref rate limit encountered; backoff applied.")
                time.sleep(1.0 * (2 ** attempt))
            else:
                time.sleep(0.4 * (2 ** attempt))
        except Exception as e:
            if attempt == max_retries:
                warnings.append(f"Network error querying Crossref for DOI '{clean_doi}': {str(e)}")
            time.sleep(0.4 * (2 ** attempt))

    return None, warnings


def _parse_flexible_date(date_val: Any) -> Optional[datetime]:
    """
    Parses various date formats from Crossref assertions or date-parts into a datetime.
    """
    if not date_val:
        return None

    if isinstance(date_val, dict) and "date-parts" in date_val:
        parts = date_val.get("date-parts", [[]])[0]
        if parts and len(parts) >= 1:
            year = parts[0]
            month = parts[1] if len(parts) > 1 else 1
            day = parts[2] if len(parts) > 2 else 1
            try:
                return datetime(year, month, day)
            except Exception:
                return None

    if isinstance(date_val, str):
        date_str = date_val.strip()
        # Try ISO format
        for fmt in ["%Y-%m-%d", "%d %B %Y", "%B %d, %Y", "%Y/%m/%d", "%d %b %Y"]:
            try:
                return datetime.strptime(date_str, fmt)
            except Exception:
                pass
        # Try regex extract
        match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', date_str)
        if match:
            try:
                return datetime.strptime(f"{match.group(1)} {match.group(2)} {match.group(3)}", "%d %B %Y")
            except Exception:
                pass

    return None


def extract_peer_review_turnaround(crossref_data: Optional[Dict[str, Any]]) -> Tuple[Optional[float], List[str]]:
    """
    Extracts submission and acceptance dates to calculate peer-review turnaround in days.
    If dates are unavailable, returns None (without fabricating false numbers).
    """
    warnings: List[str] = []
    if not crossref_data:
        warnings.append("Crossref metadata unavailable; peer-review turnaround cannot be derived.")
        return None, warnings

    received_dt: Optional[datetime] = None
    accepted_dt: Optional[datetime] = None

    # Check assertions first (standard for Nature, Springer, Wiley, Elsevier)
    assertions = crossref_data.get("assertion", [])
    for a in assertions:
        name = (a.get("name") or "").lower()
        val = a.get("value")
        if name in ["received", "received-date", "manuscript-received"] and not received_dt:
            received_dt = _parse_flexible_date(val)
        elif name in ["accepted", "accepted-date", "manuscript-accepted"] and not accepted_dt:
            accepted_dt = _parse_flexible_date(val)

    # Check top-level date keys if assertions did not have both
    if not accepted_dt and "accepted" in crossref_data:
        accepted_dt = _parse_flexible_date(crossref_data.get("accepted"))

    if not received_dt and "created" in crossref_data and accepted_dt:
        # Crossref 'created' is sometimes the deposit or submission date
        # Only use if explicitly reasonable
        pass

    if received_dt and accepted_dt:
        delta = (accepted_dt - received_dt).days
        if 1 <= delta <= 1200:
            return float(delta), warnings
        else:
            warnings.append(f"Derived peer-review turnaround ({delta} days) is outside realistic range [1, 1200]; treated as missing.")
            return None, warnings

    warnings.append(
        "Peer-review turnaround dates ('received' and 'accepted') were not disclosed in Crossref metadata for this paper."
    )
    return None, warnings


def fetch_author_telemetry(
    authorships: List[Dict[str, Any]],
    publication_year: Optional[int] = None,
    max_authors_to_query: int = 5
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Queries OpenAlex author endpoints to fetch historical works count and prior retractions.
    Does not fabricate missing counts if APIs fail.
    """
    warnings: List[str] = []
    author_works_counts: List[int] = []
    prior_retractions_list: List[int] = []

    target_pub_year = publication_year or 2026

    # Take first N authors to avoid rate limit spikes on massive author lists
    subset = authorships[:max_authors_to_query]

    for auth_entry in subset:
        author_obj = auth_entry.get("author") or {}
        raw_id = author_obj.get("id") or ""
        author_id = raw_id.split("/")[-1] if "/" in raw_id else raw_id

        if not author_id:
            continue

        # Check local cache for author profile
        cache_path = _get_cache_path("openalex_author", author_id)
        author_data = None
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    author_data = json.load(f)
            except Exception:
                pass

        if not author_data:
            try:
                url = f"{OPENALEX_AUTHORS_URL}/{author_id}"
                resp = requests.get(url, headers=HEADERS, timeout=4)
                if resp.status_code == 200:
                    author_data = resp.json()
                    try:
                        with open(cache_path, "w", encoding="utf-8") as f:
                            json.dump(author_data, f)
                    except Exception:
                        pass
                time.sleep(0.15)
            except Exception:
                pass

        if author_data:
            works_cnt = author_data.get("works_count")
            if works_cnt is not None:
                author_works_counts.append(int(works_cnt))

        # Query prior retractions for this author strictly before publication year
        ret_cache_path = _get_cache_path(f"openalex_author_ret_{target_pub_year}", author_id)
        ret_count = None
        if os.path.exists(ret_cache_path):
            try:
                with open(ret_cache_path, "r", encoding="utf-8") as f:
                    ret_count = json.load(f).get("count")
            except Exception:
                pass

        if ret_count is None:
            try:
                ret_url = f"{OPENALEX_WORKS_URL}?filter=author.id:{author_id},is_retracted:true,publication_year:<{target_pub_year}"
                resp = requests.get(ret_url, headers=HEADERS, timeout=4)
                if resp.status_code == 200:
                    meta = resp.json().get("meta", {})
                    ret_count = int(meta.get("count", 0))
                    try:
                        with open(ret_cache_path, "w", encoding="utf-8") as f:
                            json.dump({"count": ret_count}, f)
                    except Exception:
                        pass
                time.sleep(0.15)
            except Exception:
                pass

        if ret_count is not None:
            prior_retractions_list.append(ret_count)

    max_works = float(max(author_works_counts)) if author_works_counts else None
    mean_works = float(sum(author_works_counts) / len(author_works_counts)) if author_works_counts else None
    prior_retractions = float(sum(prior_retractions_list)) if prior_retractions_list else (0.0 if author_works_counts else None)

    if max_works is None:
        warnings.append("Author publication volume statistics could not be retrieved from OpenAlex.")
    if prior_retractions is None:
        warnings.append("Author prior retraction records could not be verified from OpenAlex.")

    return {
        "max_author_works": max_works,
        "mean_author_works": mean_works,
        "prior_author_retractions": prior_retractions,
        "queried_author_count": len(subset)
    }, warnings


def get_journal_retraction_rate(journal_name: Optional[str]) -> Tuple[Optional[float], List[str]]:
    """
    Looks up historical baseline retraction frequency for the journal from the training dataset.
    Returns None if journal not found in database (no fabrication).
    """
    global _JOURNAL_BASELINE_CACHE
    warnings: List[str] = []

    if not journal_name:
        warnings.append("Publication venue / journal name is missing.")
        return None, warnings

    cleaned_name = journal_name.strip().lower()

    if _JOURNAL_BASELINE_CACHE is None:
        _JOURNAL_BASELINE_CACHE = {}
        if os.path.exists(PROCESSED_FEATURES_PATH):
            try:
                import pandas as pd
                df = pd.read_csv(PROCESSED_FEATURES_PATH, usecols=["Journal", "journal_retraction_rate"])
                grouped = df.groupby("Journal")["journal_retraction_rate"].mean().to_dict()
                _JOURNAL_BASELINE_CACHE = {str(k).strip().lower(): float(v) for k, v in grouped.items()}
            except Exception as e:
                logger.warning(f"Could not load journal baseline cache: {e}")

    # Exact match
    if cleaned_name in _JOURNAL_BASELINE_CACHE:
        return _JOURNAL_BASELINE_CACHE[cleaned_name], warnings

    # Substring / partial match
    for j_key, rate in _JOURNAL_BASELINE_CACHE.items():
        if len(j_key) > 4 and (j_key in cleaned_name or cleaned_name in j_key):
            return rate, warnings

    warnings.append(
        f"Venue '{journal_name}' is not recorded in historical retraction database; feature will be imputed by model pipeline."
    )
    return None, warnings
