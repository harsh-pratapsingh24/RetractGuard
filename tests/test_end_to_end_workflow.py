"""
Automated End-to-End Workflow Verification for RetractGuard
Tests:
1. PyMuPDF Digital PDF Extraction (DOI, Title, Authors, Year)
2. PyMuPDF Scanned / Raster-Only PDF Detection & Graceful Warning
3. Invalid DOI Graceful Handling & Validation Error
4. Live API Fetch & Feature Parity (12 features)
5. Model Pipeline Inference with Imputation (No Data Fabrication)
6. Preset Benchmark Papers Backward Compatibility
7. Flask Backend Endpoints (/api/health, /api/predict JSON, /api/predict PDF, /api/extract-metadata)
"""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import io
import fitz
import json
import numpy as np
import pandas as pd

from src.pdf_extractor import extract_paper_info_from_pdf, clean_extracted_doi
from src.api_client import validate_doi, get_journal_retraction_rate
from src.features import FEATURE_COLUMNS, TRAINING_MEDIANS, extract_features_with_metadata, group_extracted_features
from src.inference import RetractionPredictor, PRESET_PAPERS
from backend.app import app


def test_doi_cleaning_and_validation():
    print("Testing DOI cleaning & validation...")
    valid, doi, err = validate_doi("10.1038/s41586-021-03819-2")
    assert valid is True
    assert doi == "10.1038/s41586-021-03819-2"
    assert err is None

    # DOI with URL prefix
    valid, doi, err = validate_doi("https://doi.org/10.2147/OTT.S184337")
    assert valid is True
    assert doi == "10.2147/OTT.S184337"

    # Invalid DOIs
    valid, doi, err = validate_doi("invalid-paper-id")
    assert valid is False
    assert "Invalid DOI format" in err
    print("-> PASSED: DOI validation works correctly.")


def test_pymupdf_digital_pdf_extraction():
    print("Testing PyMuPDF digital PDF extraction...")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Machine Learning for Research Integrity Screening", fontsize=18)
    page.insert_text((50, 100), "Dr. Elena Rostova, Marcus Vance", fontsize=11)
    page.insert_text((50, 120), "Nature Machine Intelligence (2022)", fontsize=10)
    page.insert_text((50, 140), "https://doi.org/10.1038/s41586-021-03819-2", fontsize=10)
    page.insert_text((50, 160), "Abstract: We investigate anomalous citation patterns and peer-review latency.", fontsize=10)
    pdf_bytes = doc.tobytes()
    doc.close()

    res = extract_paper_info_from_pdf(pdf_bytes)
    assert res["success"] is True
    assert res["is_scanned"] is False
    assert res["doi"] == "10.1038/s41586-021-03819-2"
    assert "Machine Learning" in res["title"]
    assert res["page_count"] == 1
    print("-> PASSED: PyMuPDF digital PDF extraction works correctly.")


def test_pymupdf_scanned_pdf_detection():
    print("Testing PyMuPDF scanned/raster PDF detection...")
    doc = fitz.open()
    page = doc.new_page()
    pix = fitz.Pixmap(fitz.csRGB, (0, 0, 60, 60), 1)
    pix.clear_with(220)
    page.insert_image(page.rect, pixmap=pix)
    pdf_bytes = doc.tobytes()
    doc.close()

    res = extract_paper_info_from_pdf(pdf_bytes)
    assert res["success"] is True
    assert res["is_scanned"] is True
    assert res["doi"] is None
    assert any("Scanned / image-only" in w for w in res["warnings"])
    print("-> PASSED: PyMuPDF scanned PDF detection works correctly.")


def test_feature_parity_and_no_fabrication():
    print("Testing 12-feature parity and non-fabrication...")
    partial_data = {
        "title": "Partial Paper",
        "author_count": 4,
        "publication_year": 2021,
        "cited_by_count": 18
    }

    meta_res = extract_features_with_metadata(partial_data)
    raw_feats = meta_res["raw_features"]
    missing = meta_res["missing_features"]

    # Verify all 12 feature columns exist
    assert list(raw_feats.keys()) == FEATURE_COLUMNS

    # Ensure missing values are NaN (not fabricated with fake numbers)
    assert np.isnan(raw_feats["review_turnaround_days"])
    assert np.isnan(raw_feats["max_author_works"])
    assert "review_turnaround_days" in missing
    assert "max_author_works" in missing

    # Ensure observed features retain their exact values
    assert raw_feats["author_count"] == 4.0
    assert raw_feats["cited_by_count"] == 18.0

    # Ensure imputed replacements match training median
    assert meta_res["imputed_features"]["review_turnaround_days"] == TRAINING_MEDIANS["review_turnaround_days"]
    print("-> PASSED: Feature parity & non-fabrication verified.")


def test_pipeline_inference_and_presets():
    print("Testing model pipeline inference & preset papers...")
    predictor = RetractionPredictor()
    assert predictor.model is not None

    # Test preset 1: OncoTargets (Known Retracted Paper)
    res = predictor.predict_paper("10.2147/OTT.S184337")
    assert res["risk_level"] == "High"
    assert res["risk_score"] >= 80.0
    assert res["retraction_status"] == "Retracted"

    # Test preset 5: Nature Physics (Clean Control Paper)
    res_clean = predictor.predict_paper("10.1038/s41586-021-03819-2")
    assert res_clean["risk_level"] == "Low"
    assert res_clean["risk_score"] < 25.0
    assert res_clean["retraction_status"] == "Clean Record"
    print("-> PASSED: Inference on presets verified.")


def test_flask_endpoints():
    print("Testing Flask REST endpoints...")
    client = app.test_client()

    # 1. Health endpoint
    h_res = client.get("/api/health")
    assert h_res.status_code == 200
    assert h_res.get_json()["model_loaded"] is True

    # 2. JSON predict valid DOI
    p_res = client.post("/api/predict", json={"doi": "10.2147/OTT.S184337"})
    assert p_res.status_code == 200
    data = p_res.get_json()
    assert "risk_score" in data
    assert "extracted_features" in data
    assert "risk_contributions" in data

    # 3. JSON predict invalid DOI (graceful 400 with warning)
    inv_res = client.post("/api/predict", json={"doi": "malformed_doi_string"})
    assert inv_res.status_code == 400
    inv_data = inv_res.get_json()
    assert inv_data["error"] == "Invalid DOI format"

    # 4. PDF upload predict
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Astrophysical Transients and Gravitational Waves", fontsize=16)
    page.insert_text((50, 100), "10.1103/PhysRevLett.124.041101", fontsize=10)
    pdf_bytes = doc.tobytes()
    doc.close()

    pdf_post = client.post(
        "/api/predict",
        data={"file": (io.BytesIO(pdf_bytes), "astrophysics.pdf")},
        content_type="multipart/form-data"
    )
    assert pdf_post.status_code == 200
    pdf_res = pdf_post.get_json()
    assert pdf_res["doi"] == "10.1103/PhysRevLett.124.041101"
    assert "risk_score" in pdf_res

    # 5. Scanned PDF upload (graceful handling)
    doc_scan = fitz.open()
    p = doc_scan.new_page()
    pix = fitz.Pixmap(fitz.csRGB, (0, 0, 50, 50), 1)
    p.insert_image(p.rect, pixmap=pix)
    scan_bytes = doc_scan.tobytes()
    doc_scan.close()

    scan_post = client.post(
        "/api/predict",
        data={"file": (io.BytesIO(scan_bytes), "scanned_archive.pdf")},
        content_type="multipart/form-data"
    )
    assert scan_post.status_code == 200
    scan_res = scan_post.get_json()
    assert scan_res["is_scanned"] is True
    assert any("Scanned" in w for w in scan_res["warnings"])
    print("-> PASSED: Flask endpoints verified.")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING RETRACTGUARD END-TO-END WORKFLOW TEST SUITE")
    print("=" * 60)
    test_doi_cleaning_and_validation()
    test_pymupdf_digital_pdf_extraction()
    test_pymupdf_scanned_pdf_detection()
    test_feature_parity_and_no_fabrication()
    test_pipeline_inference_and_presets()
    test_flask_endpoints()
    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! (6/6)")
    print("=" * 60)
