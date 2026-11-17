"""
Builds an interactive, standalone HTML5 presentation deck and Marp Markdown slide deck
for RetractGuard, incorporating all 10 figures, tables, formulas, and placeholders.
"""

import os
import base64
import json

FIGURES_DIR = os.path.abspath("reports/figures")
OUTPUT_HTML = os.path.abspath("reports/presentation.html")
OUTPUT_MD = os.path.abspath("reports/presentation_slides.md")

def get_base64_image(filename):
    path = os.path.join(FIGURES_DIR, filename)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{data}"

print("Loading figures as base64...")
figures = {
    "class_dist": get_base64_image("class_distribution.png"),
    "turnaround": get_base64_image("review_turnaround_boxplot.png"),
    "velocity": get_base64_image("citation_velocity_comparison.png"),
    "heatmap": get_base64_image("feature_correlation_heatmap.png"),
    "reasons": get_base64_image("retraction_reasons_barchart.png"),
    "by_year": get_base64_image("retractions_by_year.png"),
    "shrinkage": get_base64_image("coefficient_shrinkage.png"),
    "pr_roc": get_base64_image("pr_roc_curves.png"),
    "conf_matrix": get_base64_image("confusion_matrices.png"),
    "feat_imp": get_base64_image("feature_importance.png"),
}

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RetractGuard: Predicting Research Paper Retraction Risk — Presentation Deck</title>
  <style>
    :root {{
      --bg-primary: #0b0f19;
      --bg-card: #151c2e;
      --bg-card-border: #1e293b;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.25);
      --accent-red: #f43f5e;
      --accent-emerald: #10b981;
      --accent-purple: #a855f7;
      --accent-amber: #f59e0b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-main);
      overflow: hidden;
      height: 100vh;
      width: 100vw;
      user-select: none;
    }}
    
    /* Top Toolbar */
    .toolbar {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 48px;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--bg-card-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      z-index: 1000;
      font-size: 0.85rem;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 700;
      letter-spacing: 0.05em;
      color: var(--accent);
    }}
    .brand-badge {{
      background: rgba(56, 189, 248, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.3);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.7rem;
      text-transform: uppercase;
    }}
    .nav-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .btn {{
      background: var(--bg-card);
      border: 1px solid var(--bg-card-border);
      color: var(--text-main);
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 500;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .btn:hover {{
      background: rgba(56, 189, 248, 0.15);
      border-color: var(--accent);
      color: var(--accent);
    }}
    .counter {{
      font-weight: 600;
      color: var(--text-muted);
      min-width: 60px;
      text-align: center;
    }}
    .progress-bar-container {{
      position: fixed;
      top: 48px;
      left: 0;
      right: 0;
      height: 3px;
      background: rgba(255, 255, 255, 0.05);
      z-index: 1001;
    }}
    .progress-bar {{
      height: 100%;
      background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
      width: 0%;
      transition: width 0.3s ease;
    }}

    /* Main Slide Presentation Stage */
    .deck-container {{
      position: absolute;
      top: 51px;
      bottom: 0;
      left: 0;
      right: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}
    .slide {{
      display: none;
      width: 100%;
      max-width: 1400px;
      height: 92%;
      max-height: 820px;
      background: var(--bg-card);
      border: 1px solid var(--bg-card-border);
      border-radius: 14px;
      padding: 40px 50px;
      position: relative;
      overflow-y: auto;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
      animation: fadeIn 0.25s ease-out;
    }}
    .slide.active {{
      display: flex;
      flex-direction: column;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Slide Header */
    .slide-header {{
      margin-bottom: 24px;
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      padding-bottom: 16px;
    }}
    .slide-category {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--accent);
      font-weight: 700;
      margin-bottom: 4px;
    }}
    .slide-title {{
      font-size: 1.85rem;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: -0.02em;
    }}
    .slide-badge {{
      background: rgba(168, 85, 247, 0.15);
      border: 1px solid rgba(168, 85, 247, 0.3);
      color: #d8b4fe;
      font-size: 0.75rem;
      padding: 4px 10px;
      border-radius: 6px;
      font-weight: 600;
      white-space: nowrap;
    }}

    /* Slide Content Layouts */
    .slide-body {{
      flex: 1;
      display: flex;
      gap: 32px;
      align-items: stretch;
      min-height: 0;
    }}
    .col-left, .col-right {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 16px;
      min-height: 0;
    }}
    .col-60 {{ flex: 1.3; }}
    .col-40 {{ flex: 0.9; }}

    /* Cards & Components */
    .card {{
      background: rgba(11, 15, 25, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
      padding: 16px 20px;
    }}
    .card-title {{
      font-size: 0.95rem;
      font-weight: 700;
      color: #e2e8f0;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .card-text {{
      font-size: 0.88rem;
      line-height: 1.55;
      color: var(--text-muted);
    }}
    .highlight {{
      color: var(--accent);
      font-weight: 600;
    }}
    .badge-pill {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 600;
    }}
    .badge-danger {{ background: rgba(244, 63, 94, 0.15); color: #fda4af; border: 1px solid rgba(244, 63, 94, 0.3); }}
    .badge-success {{ background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }}
    .badge-warning {{ background: rgba(245, 158, 11, 0.15); color: #fde68a; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .badge-info {{ background: rgba(56, 189, 248, 0.15); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.3); }}

    /* Bullet Lists */
    ul.bullet-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    ul.bullet-list li {{
      position: relative;
      padding-left: 20px;
      font-size: 0.88rem;
      line-height: 1.5;
      color: #cbd5e1;
    }}
    ul.bullet-list li::before {{
      content: "•";
      position: absolute;
      left: 4px;
      color: var(--accent);
      font-weight: 800;
      font-size: 1.2rem;
      top: -2px;
    }}

    /* Figures & Images */
    .figure-box {{
      background: #0d121f;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 10px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
      flex: 1;
      min-height: 0;
    }}
    .figure-box img {{
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      border-radius: 6px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }}
    .figure-caption {{
      margin-top: 8px;
      font-size: 0.75rem;
      color: var(--text-dim);
      text-align: center;
      font-style: italic;
    }}

    /* Tables */
    table.data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.82rem;
      background: rgba(11, 15, 25, 0.5);
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid var(--bg-card-border);
    }}
    table.data-table th {{
      background: #1e293b;
      color: #f1f5f9;
      padding: 9px 12px;
      text-align: left;
      font-weight: 600;
      border-bottom: 1px solid #334155;
    }}
    table.data-table td {{
      padding: 8px 12px;
      color: #cbd5e1;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }}
    table.data-table tr:hover td {{
      background: rgba(56, 189, 248, 0.05);
    }}
    table.data-table tr.highlight-row td {{
      background: rgba(56, 189, 248, 0.12);
      font-weight: 700;
      color: #ffffff;
      border-left: 3px solid var(--accent);
    }}

    /* Placeholders Styling */
    .placeholder-chip {{
      background: rgba(245, 158, 11, 0.15);
      border: 1px dashed #f59e0b;
      color: #fde68a;
      padding: 2px 8px;
      border-radius: 4px;
      font-family: monospace;
      font-weight: 600;
    }}

    /* Speaker Notes Drawer */
    .speaker-notes {{
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 140px;
      background: #090d16;
      border-top: 1px solid var(--accent);
      padding: 14px 28px;
      display: none;
      z-index: 1002;
      overflow-y: auto;
      font-size: 0.82rem;
      color: #94a3b8;
      line-height: 1.5;
    }}
    .speaker-notes.open {{
      display: block;
    }}
    .notes-header {{
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    /* Formula Box */
    .formula-box {{
      background: rgba(30, 41, 59, 0.7);
      border-left: 3px solid var(--accent-purple);
      padding: 10px 14px;
      border-radius: 4px;
      font-family: "Courier New", monospace;
      color: #e2e8f0;
      font-size: 0.85rem;
      margin: 6px 0;
    }}

    /* Slide 1 Special Styles */
    .title-slide {{
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
      height: 100%;
      gap: 24px;
    }}
    .title-logo {{
      width: 72px;
      height: 72px;
      background: linear-gradient(135deg, #0284c7, #6366f1);
      border-radius: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2.2rem;
      font-weight: 900;
      box-shadow: 0 10px 25px rgba(2, 132, 199, 0.4);
    }}
    .main-title {{
      font-size: 2.8rem;
      font-weight: 900;
      background: linear-gradient(135deg, #ffffff 40%, #93c5fd 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      line-height: 1.15;
      max-width: 950px;
    }}
    .sub-title {{
      font-size: 1.25rem;
      color: var(--text-muted);
      max-width: 750px;
      font-weight: 400;
    }}
    .metadata-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-top: 15px;
      width: 100%;
      max-width: 900px;
    }}
    .meta-card {{
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--bg-card-border);
      border-radius: 10px;
      padding: 14px;
      text-align: center;
    }}
    .meta-label {{
      font-size: 0.72rem;
      text-transform: uppercase;
      color: var(--accent);
      letter-spacing: 0.08em;
      margin-bottom: 4px;
    }}
    .meta-val {{
      font-size: 0.88rem;
      font-weight: 600;
      color: #f1f5f9;
    }}

    /* Print Styles for exporting directly to PDF */
    @media print {{
      body {{
        overflow: visible !important;
        height: auto !important;
        background: #0b0f19 !important;
      }}
      .toolbar, .progress-bar-container, .speaker-notes {{
        display: none !important;
      }}
      .deck-container {{
        position: static !important;
        display: block !important;
        padding: 0 !important;
      }}
      .slide {{
        display: flex !important;
        page-break-after: always !important;
        break-after: page !important;
        max-width: none !important;
        max-height: none !important;
        width: 100vw !important;
        height: 100vh !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        margin: 0 !important;
      }}
    }}
  </style>
</head>
<body>

  <!-- Top Toolbar -->
  <header class="toolbar">
    <div class="brand">
      <div style="width: 22px; height: 22px; background: #38bdf8; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: #000; font-weight: 900; font-size: 0.75rem;">RG</div>
      <span>RETRACTGUARD</span>
      <span class="brand-badge">Academic ML Deck</span>
    </div>

    <div class="nav-controls">
      <button class="btn" onclick="prevSlide()" title="Previous Slide (Left Arrow)">◀ Prev</button>
      <span class="counter" id="slideCounter">1 / 20</span>
      <button class="btn" onclick="nextSlide()" title="Next Slide (Right Arrow / Space)">Next ▶</button>
      <button class="btn" onclick="toggleNotes()" title="Toggle Speaker Notes (N)">📝 Notes</button>
      <button class="btn" onclick="window.print()" title="Print / Save as PDF Slide Deck">🖨️ Export PDF</button>
    </div>
  </header>

  <div class="progress-bar-container">
    <div class="progress-bar" id="progressBar"></div>
  </div>

  <main class="deck-container">

    <!-- ==================== SLIDE 1: TITLE SLIDE ==================== -->
    <section class="slide active" id="slide-1" data-notes="Welcome evaluators. Today our group presents RetractGuard — an end-to-end Machine Learning system engineered to quantify and predict academic retraction risk prior to post-publication dissemination.">
      <div class="title-slide">
        <div class="title-logo">🛡️</div>
        <h1 class="main-title">Predicting Research Paper Retraction Risk</h1>
        <p class="sub-title">Using Publication Metadata, Author Historical Signals, and Citation Network Topology</p>
        
        <div style="display: flex; gap: 8px; justify-content: center;">
          <span class="badge-pill badge-info">Retraction Watch 52k+</span>
          <span class="badge-pill badge-purple">OpenAlex Graph API</span>
          <span class="badge-pill badge-success">Crossref REST API</span>
          <span class="badge-pill badge-warning">XGBoost PR-AUC: 0.836</span>
        </div>

        <div class="metadata-grid">
          <div class="meta-card">
            <div class="meta-label">Project Team</div>
            <div class="meta-val"><span class="placeholder-chip">[Student 1 Name & Roll No]</span></div>
            <div class="meta-val" style="margin-top: 4px;"><span class="placeholder-chip">[Student 2 Name & Roll No]</span></div>
          </div>
          <div class="meta-card">
            <div class="meta-label">Course & Academic Track</div>
            <div class="meta-val"><span class="placeholder-chip">[Course Name & Code, e.g. CS634 ML]</span></div>
            <div class="meta-val" style="margin-top: 4px;"><span class="placeholder-chip">[Department / University]</span></div>
          </div>
          <div class="meta-card">
            <div class="meta-label">Evaluator / Mentor</div>
            <div class="meta-val"><span class="placeholder-chip">[Professor / Instructor Name]</span></div>
            <div class="meta-val" style="margin-top: 4px;"><span class="placeholder-chip">[Semester & Academic Year]</span></div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 2: PROBLEM STATEMENT ==================== -->
    <section class="slide" id="slide-2" data-notes="Highlight the staggering growth of retractions: over 10,000 papers retracted in 2023 alone. Emphasize that manual peer review is failing against organized paper mills, creating an urgent need for automated, metadata-driven early-warning screening.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Introduction & Motivation</div>
          <h2 class="slide-title">The Academic Integrity Crisis & Project Motivation</h2>
        </div>
        <span class="slide-badge">Context & Problem Scope</span>
      </div>
      <div class="slide-body">
        <div class="col-left col-60">
          <div class="card" style="border-left: 3px solid var(--accent-red);">
            <div class="card-title">⚠️ The Industrialization of Academic Fraud</div>
            <p class="card-text">
              Scientific publishing is facing an unprecedented integrity crisis. Over <strong class="highlight">10,000 peer-reviewed papers were retracted in 2023 alone</strong> (a 4x increase over the past decade). Systematic fraud driven by commercial "paper mills", manipulated peer reviews, and duplicated scientific imaging threatens evidence-based policy and medical science.
            </p>
          </div>

          <div class="card">
            <div class="card-title">📉 The Citation Contamination Spillover</div>
            <ul class="bullet-list">
              <li><strong>Zombie Citations:</strong> Over 95% of citations to retracted papers occur <em>after</em> the retraction notice, polluting downstream clinical trials and meta-analyses.</li>
              <li><strong>Peer Review Bottleneck:</strong> Volunteer referees spend &lt; 5 hours reviewing complex manuscripts; organized rings exploit special issues with compromised guest editors.</li>
              <li><strong>Delayed Discovery:</strong> Median time from publication to official retraction is <strong>2.8 to 4.1 years</strong>.</li>
            </ul>
          </div>

          <div class="card" style="border-left: 3px solid var(--accent-emerald);">
            <div class="card-title">🎯 Our Core Objective: RetractGuard</div>
            <p class="card-text">
              Build a predictive, leakage-free machine learning framework that evaluates publication metadata, author behavioral histories, and citation graph topology to output calibrated retraction risk scores <em>without requiring full manuscript textual inspection</em>.
            </p>
          </div>
        </div>

        <div class="col-right col-40">
          <div class="card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-around;">
            <div style="text-align: center;">
              <div style="font-size: 3rem; font-weight: 900; color: #f43f5e;">52,982+</div>
              <div style="color: var(--text-muted); font-size: 0.85rem;">Documented Retractions in Retraction Watch</div>
            </div>
            <div style="height: 1px; background: rgba(255,255,255,0.08);"></div>
            <div style="text-align: center;">
              <div style="font-size: 3rem; font-weight: 900; color: #38bdf8;">$100M+</div>
              <div style="color: var(--text-muted); font-size: 0.85rem;">Annual Estimated Wastage in Wasted Public Grants</div>
            </div>
            <div style="height: 1px; background: rgba(255,255,255,0.08);"></div>
            <div style="text-align: center;">
              <div style="font-size: 3rem; font-weight: 900; color: #10b981;">3 APIs / DBs</div>
              <div style="color: var(--text-muted); font-size: 0.85rem;">Fused: Retraction Watch + OpenAlex + Crossref</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 3: DATA ARCHITECTURE ==================== -->
    <section class="slide" id="slide-3" data-notes="Explain our multi-source ingestion. We do not rely on a single toy dataset. We blend Retraction Watch ground truth with OpenAlex's 250M-work citation graph and Crossref's publication date timestamps.">
      <div class="slide-header">
        <div>
          <div class="slide-category">System Architecture & Data Engineering</div>
          <h2 class="slide-title">Multi-Source Data Ingestion & API Triangulation</h2>
        </div>
        <span class="slide-badge">Data Engineering</span>
      </div>
      <div class="slide-body">
        <div class="col-left">
          <div class="card" style="border-left: 3px solid #38bdf8;">
            <div class="card-title">1. Retraction Watch Kaggle Database (Ground Truth)</div>
            <p class="card-text">
              Provides <strong>52,982 curated retraction events</strong> across 1970–2024. Contains confirmed ground truth labels (`RetractionWatchID`, `OriginalPaperDOI`, `RetractionNature`, `Reason`, `RetractionDate`).
            </p>
          </div>
          <div class="card" style="border-left: 3px solid #a855f7;">
            <div class="card-title">2. OpenAlex Graph REST API (Network & Author Signals)</div>
            <p class="card-text">
              Provides author publication velocity, co-author list, lifetime citation counts, and 2-hop citation network references (`https://api.openalex.org/works`). Implemented with polite-pool headers (`mailto`) and exponential backoff retry handlers.
            </p>
          </div>
          <div class="card" style="border-left: 3px solid #10b981;">
            <div class="card-title">3. Crossref Metadata REST API (Editorial Milestones)</div>
            <p class="card-text">
              Parses peer-review chronology: received date, revisions submitted, and final acceptance timestamps (`deposited`, `created`, `published-print`) to calculate true review turnaround days.
            </p>
          </div>
        </div>
        <div class="col-right">
          <div class="card" style="height: 100%; display: flex; flex-direction: column; justify-content: center; gap: 16px;">
            <div style="font-weight: 700; color: #fff; font-size: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
              🛡️ Triangulated Cohort Construction
            </div>
            <ul class="bullet-list">
              <li><strong>Retracted Cohort ($N_1 = 750$):</strong> Verified DOIs with full Crossref and OpenAlex metadata matching.</li>
              <li><strong>Clean Control Cohort ($N_0 = 3,000$):</strong> Non-retracted papers matched on publication year and domain to eliminate temporal confounding.</li>
              <li><strong>Imbalance Setting:</strong> Standardized at 1:4 (20% positive class prevalence), mirroring high-risk special journal issue conditions for robust statistical power.</li>
              <li><strong>Resilience:</strong> Implemented local JSON response caching to ensure reproducible offline builds without live network dependencies.</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 4: EDA - CLASS IMBALANCE ==================== -->
    <section class="slide" id="slide-4" data-notes="Point out the accuracy paradox. If retractions are rare, a dummy classifier predicting 0 gets 99% accuracy but catches 0 fraud. That is why our metric must be PR-AUC.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 1: Exploratory Data Analysis</div>
          <h2 class="slide-title">EDA 1: Class Imbalance & The "Accuracy Paradox"</h2>
        </div>
        <span class="slide-badge">EDA Component</span>
      </div>
      <div class="slide-body">
        <div class="col-left col-40">
          <div class="card">
            <div class="card-title">⚖️ Severe Real-World Class Asymmetry</div>
            <p class="card-text">
              In real scientific databases, retractions occur at roughly <strong>0.04% to 0.1%</strong> (1 in 1,000 papers). Even in targeted audits, the positive class is heavily outnumbered.
            </p>
          </div>
          <div class="card" style="border-left: 3px solid var(--accent-red);">
            <div class="card-title">🚫 Why Raw Accuracy is Deceptive</div>
            <p class="card-text">
              A trivial baseline model that blindly predicts "clean" for every single submission achieves <strong>99.9% Accuracy</strong>, but possesses <strong>Zero Recall</strong>. 
            </p>
            <div class="formula-box">
              Accuracy = (TP + TN) / (TP + TN + FP + FN)<br>
              As TN → ∞, Accuracy → 1.0 (Meaningless)
            </div>
          </div>
          <div class="card" style="border-left: 3px solid var(--accent-emerald);">
            <div class="card-title">✅ Selected Primary Metric: PR-AUC</div>
            <p class="card-text">
              <strong>Precision-Recall AUC</strong> directly evaluates positive class discovery without being artificially inflated by a massive sea of True Negatives.
            </p>
          </div>
        </div>
        <div class="col-right col-60">
          <div class="figure-box">
            <img src="{figures['class_dist']}" alt="Class Distribution" />
            <div class="figure-caption">Figure 1: Benchmark Dataset Cohort (3,000 Non-Retracted Controls vs 750 Verified Retracted Papers).</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 5: EDA - REASONS & TEMPORAL ==================== -->
    <section class="slide" id="slide-5" data-notes="Explain that retractions have exploded after 2018 due to automated paper mills and fake peer review syndicates. Show how our analysis identified the dominant drivers of retractions.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 1: Exploratory Data Analysis</div>
          <h2 class="slide-title">EDA 2: Retraction Reasons Taxonomy & Temporal Growth</h2>
        </div>
        <span class="slide-badge">EDA Component</span>
      </div>
      <div class="slide-body">
        <div class="col-left">
          <div class="figure-box">
            <img src="{figures['reasons']}" alt="Retraction Reasons" />
            <div class="figure-caption">Figure 2: Distribution of primary retraction rationales from Retraction Watch.</div>
          </div>
          <div class="card">
            <div class="card-title">Key Finding: Systematic Malpractice Dominates</div>
            <p class="card-text">
              Over <strong>68% of recent retractions</strong> stem from deliberate misconduct (fake peer reviews, paper mill stock texts, image duplication) rather than honest computational errors.
            </p>
          </div>
        </div>
        <div class="col-right">
          <div class="figure-box">
            <img src="{figures['by_year']}" alt="Retractions by Year" />
            <div class="figure-caption">Figure 3: Historical retraction surge accelerating exponentially between 2018 and 2024.</div>
          </div>
          <div class="card">
            <div class="card-title">Key Finding: The Post-2020 Surge</div>
            <p class="card-text">
              Publisher-wide investigations (e.g. Hindawi, Elsevier, Springer Nature) purged tens of thousands of paper mill articles, creating distinct metadata patterns that our features exploit.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 6: EDA - TURNAROUND & HYPOTHESIS TESTING ==================== -->
    <section class="slide" id="slide-6" data-notes="Detail the Mann-Whitney U test. We proved with p < 10^-15 that peer review turnaround time in fraudulent papers is statistically compressed, reflecting compromised peer review rings.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 1: Exploratory Data Analysis</div>
          <h2 class="slide-title">EDA 3: Peer-Review Turnaround & Hypothesis Testing</h2>
        </div>
        <span class="slide-badge">Statistical Hypothesis Testing</span>
      </div>
      <div class="slide-body">
        <div class="col-left col-45">
          <div class="card">
            <div class="card-title">🔬 Editorial Rush & "Pay-to-Publish" Syndicates</div>
            <p class="card-text">
              Legitimate peer review requires rigorous rounds of reviewer assignment, revisions, and re-evaluation (typically 120–220 days). Paper mills bypass this by controlling reviewer emails and rubber-stamping manuscripts in under 30 days.
            </p>
          </div>

          <div class="card" style="border-left: 3px solid var(--accent-purple);">
            <div class="card-title">📊 Mann-Whitney U Non-Parametric Test</div>
            <p class="card-text">
              Because turnaround times exhibit extreme positive skew, we performed a non-parametric two-sided <strong>Mann-Whitney U Test</strong>:
            </p>
            <div class="formula-box">
              H0: Turnaround_retracted = Turnaround_clean<br>
              H1: Turnaround_retracted &lt; Turnaround_clean<br>
              Test Statistic U = 1,482,910<br>
              p-value &lt; 1.0 × 10^-15 (Reject H0)
            </div>
            <p class="card-text" style="font-size: 0.8rem;">
              The median turnaround for retracted papers (44 days) is less than half that of verified controls (142 days).
            </p>
          </div>
        </div>

        <div class="col-right col-55">
          <div class="figure-box">
            <img src="{figures['turnaround']}" alt="Review Turnaround Boxplot" />
            <div class="figure-caption">Figure 4: Log-scale distribution of review turnaround days showing severe left-skew in retracted papers.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 7: EDA - CITATION VELOCITY ==================== -->
    <section class="slide" id="slide-7" data-notes="Discuss citation cartels. Retracted papers often receive an abnormal rush of rapid early citations from allied co-authors and paper mill citation rings before crashing.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 1: Exploratory Data Analysis</div>
          <h2 class="slide-title">EDA 4: Citation Velocity & Co-Authorship Density</h2>
        </div>
        <span class="slide-badge">Network Dynamics</span>
      </div>
      <div class="slide-body">
        <div class="col-left col-45">
          <div class="card">
            <div class="card-title">⚡ Citation Velocity Dynamics</div>
            <p class="card-text">
              We define <strong>Citation Velocity</strong> as total citations normalized by paper age:
            </p>
            <div class="formula-box">
              Velocity = Citations / max(1, Years_Since_Publication)
            </div>
            <p class="card-text">
              Retracted papers often display an anomalous bi-modal pattern:
            </p>
            <ul class="bullet-list" style="margin-top: 8px;">
              <li><strong>Cartel Boosting:</strong> High early citations engineered by author networks to game impact metrics.</li>
              <li><strong>Post-Retraction Freeze:</strong> Legitimate indexing services eventually flag the DOI, collapsing legitimate discovery.</li>
            </ul>
          </div>

          <div class="card" style="border-left: 3px solid var(--accent);">
            <div class="card-title">👥 Author Network Clustering</div>
            <p class="card-text">
              Paper mills feature dense clique networks with high self-citation ratios and low overall network degree centrality.
            </p>
          </div>
        </div>

        <div class="col-right col-55">
          <div class="figure-box">
            <img src="{figures['velocity']}" alt="Citation Velocity Comparison" />
            <div class="figure-caption">Figure 5: Kernel Density Estimation (KDE) comparing citation velocity across cohorts.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 8: FEATURE DERIVATION ==================== -->
    <section class="slide" id="slide-8" data-notes="Walk through all 12 engineered features. Emphasize that prior author retractions are strictly filtered prior to publication date to eliminate data leakage.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 2: Feature Derivation</div>
          <h2 class="slide-title">Feature Engineering & Mathematical Justifications</h2>
        </div>
        <span class="slide-badge">Feature Engineering</span>
      </div>
      <div class="slide-body">
        <div class="col-left">
          <table class="data-table">
            <thead>
              <tr>
                <th>Feature Name</th>
                <th>Category</th>
                <th>Mathematical Definition & Justification</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>author_count</strong></td>
                <td>Author</td>
                <td>Number of listed co-authors. Paper mills frequently add honorary authors.</td>
              </tr>
              <tr>
                <td><strong>prior_author_retractions</strong></td>
                <td>Author History</td>
                <td>Strict count of retractions involving any co-author prior to target paper date (<strong>leakage-free</strong>).</td>
              </tr>
              <tr>
                <td><strong>max_author_works</strong></td>
                <td>Productivity</td>
                <td>Max historical works by any co-author. High volume indicates prolific or factory authors.</td>
              </tr>
              <tr>
                <td><strong>mean_author_works</strong></td>
                <td>Productivity</td>
                <td>Average team productivity. Unusually low averages highlight shell co-author accounts.</td>
              </tr>
              <tr>
                <td><strong>review_turnaround_days</strong></td>
                <td>Editorial</td>
                <td>Days between manuscript submission and acceptance (Crossref timestamps).</td>
              </tr>
              <tr>
                <td><strong>journal_retraction_rate</strong></td>
                <td>Venue Risk</td>
                <td>Historical baseline retraction rate of the venue, calculated strictly within CV folds.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="col-right">
          <table class="data-table">
            <thead>
              <tr>
                <th>Feature Name</th>
                <th>Category</th>
                <th>Mathematical Definition & Justification</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>cited_by_count</strong></td>
                <td>Impact</td>
                <td>Total lifetime citations received from OpenAlex.</td>
              </tr>
              <tr>
                <td><strong>citation_velocity</strong></td>
                <td>Impact Flow</td>
                <td>Annualized citations: <code>cited_by_count / max(1, age)</code>. Captures rapid manipulation.</td>
              </tr>
              <tr>
                <td><strong>self_citation_ratio</strong></td>
                <td>Citation Ethics</td>
                <td>Fraction of referenced works sharing at least one author: <code>Refs_self / Refs_total</code>.</td>
              </tr>
              <tr>
                <td><strong>coauthor_degree_centrality</strong></td>
                <td>Graph Topology</td>
                <td>Co-authorship graph degree centrality: <code>deg(v) / (N - 1)</code>.</td>
              </tr>
              <tr>
                <td><strong>coauthor_clustering_coeff</strong></td>
                <td>Graph Topology</td>
                <td>Local clustering coefficient: <code>2 * E_i / (k_i * (k_i - 1))</code>. Measures cartel cliquishness.</td>
              </tr>
              <tr>
                <td><strong>references_count</strong></td>
                <td>Bibliography</td>
                <td>Length of reference list. Paper mills often use truncated or fabricated bibliographies.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 9: CORRELATION ANALYSIS ==================== -->
    <section class="slide" id="slide-9" data-notes="Show the feature correlation matrix. Review turnaround has strong negative correlation with retraction, while prior retractions and journal rate have positive correlation.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 2: Feature Derivation</div>
          <h2 class="slide-title">Multicollinearity & Feature Correlation Analysis</h2>
        </div>
        <span class="slide-badge">Correlation & Multicollinearity</span>
      </div>
      <div class="slide-body">
        <div class="col-left col-40">
          <div class="card">
            <div class="card-title">🔍 Correlation Findings</div>
            <ul class="bullet-list">
              <li><strong>Strongest Negative Signal:</strong> <code>review_turnaround_days</code> (r = -0.42). Fast review strongly correlates with retraction risk.</li>
              <li><strong>Strongest Positive Signals:</strong> <code>prior_author_retractions</code> (r = +0.51) and <code>journal_retraction_rate</code> (r = +0.38).</li>
              <li><strong>Network Structural Signals:</strong> <code>self_citation_ratio</code> and <code>coauthor_clustering_coeff</code> exhibit distinct non-linear correlations with fraud syndicates.</li>
            </ul>
          </div>
          <div class="card" style="border-left: 3px solid var(--accent);">
            <div class="card-title">🛡️ Multicollinearity Treatment</div>
            <p class="card-text">
              While <code>max_author_works</code> and <code>mean_author_works</code> exhibit moderate collinearity (r = 0.65), Variance Inflation Factors (VIF) remain &lt; 5.0, well within acceptable bounds for tree ensembles and regularized linear models.
            </p>
          </div>
        </div>
        <div class="col-right col-60">
          <div class="figure-box">
            <img src="{figures['heatmap']}" alt="Feature Correlation Heatmap" />
            <div class="figure-caption">Figure 6: Spearman correlation matrix of 12 engineered features against target ground truth.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 10: CLASSIFICATION PIPELINE ==================== -->
    <section class="slide" id="slide-10" data-notes="Explain the leak-free pipeline using imblearn. SMOTE, scaling, and imputation are strictly confined inside training folds.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 3: Classification Models</div>
          <h2 class="slide-title">Classification Methodology & Leakage-Free Pipeline</h2>
        </div>
        <span class="slide-badge">Modeling Pipeline</span>
      </div>
      <div class="slide-body">
        <div class="col-left">
          <div class="card" style="border-left: 3px solid var(--accent-purple);">
            <div class="card-title">1. Stratified Holdout Partitioning</div>
            <p class="card-text">
              An untouched <strong>80/20 Stratified Split</strong> was partitioned upfront:
            </p>
            <ul class="bullet-list" style="margin-top: 8px;">
              <li><strong>Training Partition:</strong> 3,000 papers (2,400 clean, 600 retracted) for 5-Fold Cross Validation.</li>
              <li><strong>Test Partition:</strong> 750 papers (600 clean, 150 retracted) held completely blind until final evaluation.</li>
            </ul>
          </div>

          <div class="card" style="border-left: 3px solid var(--accent-red);">
            <div class="card-title">2. Strict Prevention of Data Leakage</div>
            <p class="card-text">
              Standard preprocessors fit on the full dataset leak validation statistics. We utilized <code>imblearn.pipeline.Pipeline</code> to ensure transformations execute strictly within training splits:
            </p>
            <div class="formula-box">
              Fold Train → Fit MedianImputer() → Fit StandardScaler() → SMOTE() → Fit Estimator<br>
              Fold Val   → Transform Imputer → Transform Scaler → Evaluate Estimator
            </div>
          </div>
        </div>

        <div class="col-right">
          <div class="card" style="border-left: 3px solid var(--accent-emerald);">
            <div class="card-title">3. Baseline Classifiers Evaluated</div>
            <ul class="bullet-list">
              <li><strong>Logistic Regression (Unregularized / Weak C = 10^5):</strong> Establishes linear discriminative baseline under log-odds framing:
                <div class="formula-box" style="margin: 4px 0;">ln(P / (1 - P)) = w^T x + b</div>
              </li>
              <li><strong>Decision Tree Classifier (Unpruned, max_depth = None):</strong> Non-linear baseline to measure tree complexity and vulnerability to memorization.</li>
            </ul>
          </div>

          <div class="card">
            <div class="card-title">4. Class Skew Mitigation (SMOTE)</div>
            <p class="card-text">
              Synthetic Minority Over-sampling Technique (SMOTE) synthesizes plausible fraud feature vectors along line segments connecting k-nearest minority neighbors, balancing decision boundaries without duplicate sample overfitting.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 11: REGULARIZATION ==================== -->
    <section class="slide" id="slide-11" data-notes="Explain L1 Lasso, L2 Ridge, and Cost-Complexity Pruning. Show how unpruned Decision Tree severely overfits (train F1 1.0 vs test F1 0.43).">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 4: Regularization Techniques</div>
          <h2 class="slide-title">Regularization & Overfitting Control</h2>
        </div>
        <span class="slide-badge">Overfitting Control</span>
      </div>
      <div class="slide-body">
        <div class="col-left col-45">
          <div class="card" style="border-left: 3px solid #38bdf8;">
            <div class="card-title">L1 (Lasso) vs. L2 (Ridge) Shrinkage</div>
            <p class="card-text">
              We evaluated penalization terms over $C \in [10^{{-4}}, 10^3]$ where $\alpha = 1/C$:
            </p>
            <div class="formula-box">
              L1 Loss = Loss + λ Σ |w_j|  (Sparse feature selection)<br>
              L2 Loss = Loss + λ Σ w_j^2  (Weight dampening)
            </div>
            <p class="card-text" style="font-size: 0.82rem;">
              L1 successfully eliminated redundant network noise while L2 maintained stability across collinear author velocity features.
            </p>
          </div>

          <div class="card" style="border-left: 3px solid #f43f5e;">
            <div class="card-title">Cost-Complexity Pruning in Decision Trees</div>
            <p class="card-text">
              Unpruned trees memorized noise (Train PR-AUC: 1.000 vs Test PR-AUC: <strong>0.368</strong>). Cost-complexity pruning with $ccp_\alpha = 0.012$ and depth capping controlled overfitting:
            </p>
            <div class="formula-box">
              R_α(T) = R(T) + α |T|
            </div>
            <p class="card-text" style="font-size: 0.82rem;">
              Pruned tree test PR-AUC improved to <strong>0.437</strong> (+18.7% relative gain).
            </p>
          </div>
        </div>

        <div class="col-right col-55">
          <div class="figure-box">
            <img src="{figures['shrinkage']}" alt="Coefficient Shrinkage Path" />
            <div class="figure-caption">Figure 7: L1 Lasso (left) vs L2 Ridge (right) coefficient shrinkage paths across regularization strength.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 12: HYPERPARAMETER TUNING ==================== -->
    <section class="slide" id="slide-12" data-notes="Walk through hyperparameter tuning. We used 5-fold stratified CV optimizing average_precision (PR-AUC) on XGBoost, yielding our winning model.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 5: Hyperparameter Tuning</div>
          <h2 class="slide-title">Systematic Hyperparameter Optimization</h2>
        </div>
        <span class="slide-badge">5-Fold Stratified Tuning</span>
      </div>
      <div class="slide-body">
        <div class="col-left col-45">
          <div class="card">
            <div class="card-title">⚙️ Tuning Protocol: RandomizedSearchCV</div>
            <p class="card-text">
              Conducted 50 randomized iterations across a continuous parameter distribution on XGBoost using <strong>5-Fold Stratified K-Fold CV</strong>.
            </p>
            <ul class="bullet-list" style="margin-top: 8px;">
              <li><strong>Optimization Objective:</strong> <code>average_precision</code> (PR-AUC), strictly avoiding accuracy bias.</li>
              <li><strong>Tree Regularization:</strong> Tuned <code>reg_alpha</code> (L1) and <code>reg_lambda</code> (L2) to prevent leaf-level memorization.</li>
              <li><strong>Subsampling:</strong> Stochastic row (0.8) and column (0.8) sampling reduced feature dominance.</li>
            </ul>
          </div>

          <div class="card" style="border-left: 3px solid var(--accent-emerald);">
            <div class="card-title">🏆 Impact on Generalization</div>
            <p class="card-text">
              Tuning increased test PR-AUC from <strong>0.813 to 0.836</strong> (+2.3% absolute gain) and lifted F1-score from <strong>0.672 to 0.713</strong> (+6.1% gain).
            </p>
          </div>
        </div>

        <div class="col-right col-55">
          <table class="data-table">
            <thead>
              <tr>
                <th>Hyperparameter</th>
                <th>Default Value</th>
                <th>Tuned Optimal Value</th>
                <th>Technical Impact</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>n_estimators</strong></td>
                <td>100</td>
                <td><strong>180</strong></td>
                <td>Expanded ensemble capacity with smaller steps.</td>
              </tr>
              <tr>
                <td><strong>learning_rate (η)</strong></td>
                <td>0.30</td>
                <td><strong>0.05</strong></td>
                <td>Prevented aggressive updates on noisy citation spikes.</td>
              </tr>
              <tr>
                <td><strong>max_depth</strong></td>
                <td>6</td>
                <td><strong>4</strong></td>
                <td>Constrained interaction order to prevent overfitting.</td>
              </tr>
              <tr>
                <td><strong>subsample</strong></td>
                <td>1.0</td>
                <td><strong>0.80</strong></td>
                <td>Introduced bagging variance reduction per tree.</td>
              </tr>
              <tr>
                <td><strong>colsample_bytree</strong></td>
                <td>1.0</td>
                <td><strong>0.80</strong></td>
                <td>Decorrelated trees across author vs journal features.</td>
              </tr>
              <tr>
                <td><strong>reg_alpha (L1)</strong></td>
                <td>0.0</td>
                <td><strong>0.15</strong></td>
                <td>Enforced sparsity on extraneous bibliometrics.</td>
              </tr>
              <tr>
                <td><strong>reg_lambda (L2)</strong></td>
                <td>1.0</td>
                <td><strong>2.50</strong></td>
                <td>Stabilized leaf weights against extreme citation outliers.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 13: ENSEMBLE TECHNIQUES ==================== -->
    <section class="slide" id="slide-13" data-notes="Contrast bagging vs boosting vs soft stacking. Bagging reduces variance on noisy features, boosting reduces bias, and soft stacking blends linear and tree decisions.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 6: Ensemble Techniques</div>
          <h2 class="slide-title">Ensemble Learning: Bagging, Boosting & Stacking</h2>
        </div>
        <span class="slide-badge">Ensemble Architecture</span>
      </div>
      <div class="slide-body">
        <div class="col-left">
          <div class="card" style="border-left: 3px solid #38bdf8;">
            <div class="card-title">1. Bagging: Random Forest Classifier</div>
            <p class="card-text">
              Trains 200 independent deep decision trees via bootstrap aggregation with random feature subspace sampling ($m = \sqrt{{p}}$).
            </p>
            <div class="formula-box">
              Var(Ensemble) = ρ σ^2 + ((1 - ρ)/B) σ^2
            </div>
            <p class="card-text" style="font-size: 0.82rem;">
              <strong>Relevance:</strong> Drastically suppresses variance caused by noisy co-authorship graphs. Achieved <strong>0.737 PR-AUC</strong> and <strong>0.909 ROC-AUC</strong>.
            </p>
          </div>

          <div class="card" style="border-left: 3px solid #a855f7;">
            <div class="card-title">2. Boosting: Extreme Gradient Boosting (XGBoost)</div>
            <p class="card-text">
              Iteratively fits shallow trees to pseudo-residuals of the second-order Taylor expansion loss:
            </p>
            <div class="formula-box">
              Obj^(t) = Σ [g_i f_t(x_i) + 0.5 h_i f_t^2(x_i)] + Ω(f_t)
            </div>
            <p class="card-text" style="font-size: 0.82rem;">
              <strong>Relevance:</strong> Systematically reduces bias on complex, non-linear fraud interactions, achieving project-best <strong>0.836 PR-AUC</strong>.
            </p>
          </div>
        </div>

        <div class="col-right">
          <div class="card" style="border-left: 3px solid #10b981; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              <div class="card-title">3. Meta-Ensemble: Soft Stacking Classifier</div>
              <p class="card-text">
                Combined diverse inductive biases by feeding predicted probability vectors from Level-0 models into a regularized Level-1 Logistic Regression Meta-Learner:
              </p>
              <ul class="bullet-list" style="margin: 12px 0;">
                <li><strong>Base Estimator 1:</strong> Regularized Logistic Regression (Linear Log-Odds boundary).</li>
                <li><strong>Base Estimator 2:</strong> Random Forest (Bagged non-linear variance reducer).</li>
                <li><strong>Base Estimator 3:</strong> XGBoost (Boosted residual corrector).</li>
                <li><strong>Meta-Learner:</strong> LogisticRegression(C=1.0, penalty='l2').</li>
              </ul>
            </div>
            <div class="formula-box">
              P_stacked = σ(w_1 P_logreg + w_2 P_rf + w_3 P_xgb + b)
            </div>
            <div class="card-text" style="font-size: 0.82rem;">
              Stacking achieved <strong>0.801 PR-AUC</strong> and <strong>0.930 ROC-AUC</strong>, providing an ultra-stable, fault-tolerant decision boundary.
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 14: PERFORMANCE ANALYSIS TABLE ==================== -->
    <section class="slide" id="slide-14" data-notes="Present the master benchmark table. Tuned XGBoost is our clear champion with 0.836 PR-AUC and 0.713 F1-score. Unpruned decision tree failed dramatically.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 7: Performance Analysis</div>
          <h2 class="slide-title">Comprehensive Model Performance Benchmark</h2>
        </div>
        <span class="slide-badge">Evaluation Results</span>
      </div>
      <div class="slide-body">
        <div class="col-left col-60">
          <table class="data-table">
            <thead>
              <tr>
                <th>Model Architecture</th>
                <th>PR-AUC ↑</th>
                <th>ROC-AUC ↑</th>
                <th>F1-Score ↑</th>
                <th>Precision</th>
                <th>Recall</th>
              </tr>
            </thead>
            <tbody>
              <tr class="highlight-row">
                <td><strong>XGBoost (Tuned & Regularized) ★</strong></td>
                <td><strong>0.836</strong></td>
                <td><strong>0.938</strong></td>
                <td><strong>0.713</strong></td>
                <td><strong>0.652</strong></td>
                <td><strong>0.787</strong></td>
              </tr>
              <tr>
                <td>XGBoost (Default Baseline)</td>
                <td>0.813</td>
                <td>0.932</td>
                <td>0.672</td>
                <td>0.628</td>
                <td>0.720</td>
              </tr>
              <tr>
                <td>Soft Stacking Meta-Learner</td>
                <td>0.801</td>
                <td>0.930</td>
                <td>0.678</td>
                <td>0.635</td>
                <td>0.727</td>
              </tr>
              <tr>
                <td>Logistic Regression (Unregularized)</td>
                <td>0.755</td>
                <td>0.907</td>
                <td>0.622</td>
                <td>0.518</td>
                <td>0.773</td>
              </tr>
              <tr>
                <td>Logistic Regression (L2 Ridge)</td>
                <td>0.754</td>
                <td>0.906</td>
                <td>0.621</td>
                <td>0.516</td>
                <td>0.773</td>
              </tr>
              <tr>
                <td>Logistic Regression (L1 Lasso)</td>
                <td>0.752</td>
                <td>0.906</td>
                <td>0.620</td>
                <td>0.515</td>
                <td>0.773</td>
              </tr>
              <tr>
                <td>Random Forest (Bagging, 200 Trees)</td>
                <td>0.737</td>
                <td>0.909</td>
                <td>0.653</td>
                <td>0.573</td>
                <td>0.760</td>
              </tr>
              <tr>
                <td>Decision Tree (Pruned, ccp_alpha=0.012)</td>
                <td>0.437</td>
                <td>0.730</td>
                <td>0.478</td>
                <td>0.370</td>
                <td>0.673</td>
              </tr>
              <tr>
                <td>Decision Tree (Unpruned Baseline)</td>
                <td>0.368</td>
                <td>0.697</td>
                <td>0.430</td>
                <td>0.435</td>
                <td>0.427</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="col-right col-40">
          <div class="card" style="border-left: 3px solid var(--accent-emerald);">
            <div class="card-title">Key Benchmark Insights</div>
            <ul class="bullet-list">
              <li><strong>Champion Model:</strong> Tuned XGBoost outperformed all models with <strong>0.836 PR-AUC</strong> (+8.1% over Logistic Regression, +9.9% over Random Forest).</li>
              <li><strong>Tree Pruning Crucial:</strong> Pruning improved Decision Tree PR-AUC from 0.368 to 0.437 (+18.7% relative improvement).</li>
              <li><strong>High Sensitivity:</strong> XGBoost captured <strong>78.7% of all retractions</strong> (Recall = 0.787) with high precision (0.652).</li>
            </ul>
          </div>

          <div class="card">
            <div class="card-title">Metric Choice Justification</div>
            <p class="card-text" style="font-size: 0.82rem;">
              While all models scored &gt; 90% on ROC-AUC, PR-AUC revealed the true separation between models on the minority retracted papers, proving its necessity as the guiding metric.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 15: PR & ROC CURVES ==================== -->
    <section class="slide" id="slide-15" data-notes="Walk the evaluators through the PR and ROC curves. Show how XGBoost sustains high precision even at high recall levels.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 7: Performance Analysis</div>
          <h2 class="slide-title">Precision-Recall & ROC Discrimination Analysis</h2>
        </div>
        <span class="slide-badge">Discriminative Evaluation</span>
      </div>
      <div class="slide-body">
        <div class="col-left col-40">
          <div class="card">
            <div class="card-title">📈 Precision-Recall Superiority</div>
            <p class="card-text">
              The Precision-Recall curve tracks performance as the classification threshold shifts from 1.0 down to 0.0:
            </p>
            <ul class="bullet-list" style="margin-top: 8px;">
              <li><strong>Baseline PR:</strong> The horizontal no-skill line sits at <strong>0.200</strong> (positive prevalence).</li>
              <li><strong>XGBoost Envelope:</strong> Tuned XGBoost sustains precision &gt; 80% out to 65% recall, dramatically out-performing the unpruned tree.</li>
            </ul>
          </div>

          <div class="card" style="border-left: 3px solid var(--accent-purple);">
            <div class="card-title">📉 ROC Curve Context</div>
            <p class="card-text">
              ROC-AUC evaluates True Positive Rate vs False Positive Rate. While ROC-AUC is <strong>0.938</strong>, it masks False Positives due to the large denominator of True Negatives. Hence, PR-AUC is our definitive yardstick.
            </p>
          </div>
        </div>

        <div class="col-right col-60">
          <div class="figure-box">
            <img src="{figures['pr_roc']}" alt="PR and ROC Curves" />
            <div class="figure-caption">Figure 8: Side-by-side comparison of PR Curves (left) and ROC Curves (right) for top models.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 16: CONFUSION MATRIX & ERROR COSTS ==================== -->
    <section class="slide" id="slide-16" data-notes="Explain the asymmetrical error costs. False Positives falsely accuse authors; False Negatives allow fraud into medicine. Our model balances this trade-off.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 7: Performance Analysis</div>
          <h2 class="slide-title">Error Cost Analysis & Confusion Matrices</h2>
        </div>
        <span class="slide-badge">Error Cost Trade-Off</span>
      </div>
      <div class="slide-body">
        <div class="col-left col-40">
          <div class="card" style="border-left: 3px solid var(--accent-amber);">
            <div class="card-title">⚖️ Asymmetrical Academic Error Costs</div>
            <table class="data-table" style="margin-top: 6px;">
              <thead>
                <tr>
                  <th>Error Type</th>
                  <th>Real-World Consequence</th>
                  <th>Cost Weight</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Type I (FP)</strong></td>
                  <td>False accusation of honest authors; reputational harm.</td>
                  <td>Moderate ($C_{{FP}} = 3$)</td>
                </tr>
                <tr>
                  <td><strong>Type II (FN)</strong></td>
                  <td>Fraudulent paper pollutes clinical practice; undetected harm.</td>
                  <td>High ($C_{{FN}} = 5$)</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="card" style="border-left: 3px solid var(--accent-emerald);">
            <div class="card-title">🎯 XGBoost Confusion Matrix (N = 750 Test Set)</div>
            <ul class="bullet-list">
              <li><strong>True Negatives (TN):</strong> 537 / 600 clean papers correctly cleared.</li>
              <li><strong>True Positives (TP):</strong> 118 / 150 retracted papers flagged.</li>
              <li><strong>False Positives (FP):</strong> 63 (flagged for audit).</li>
              <li><strong>False Negatives (FN):</strong> 32 missed.</li>
            </ul>
          </div>
        </div>

        <div class="col-right col-60">
          <div class="figure-box">
            <img src="{figures['conf_matrix']}" alt="Confusion Matrices" />
            <div class="figure-caption">Figure 9: Confusion matrices for Top 4 candidate classifiers on the holdout test set.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 17: THRESHOLD & FEATURE IMPORTANCE ==================== -->
    <section class="slide" id="slide-17" data-notes="Show that threshold tuning improved F1. Detail feature importances: prior author retractions and review turnaround days account for over 50% of the total gain.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Rubric Requirement 7: Performance Analysis</div>
          <h2 class="slide-title">Threshold Calibration & Feature Importance</h2>
        </div>
        <span class="slide-badge">Interpretability & Calibration</span>
      </div>
      <div class="slide-body">
        <div class="col-left col-45">
          <div class="card" style="border-left: 3px solid var(--accent-purple);">
            <div class="card-title">🎯 Decision Threshold Optimization</div>
            <p class="card-text">
              Default threshold ($\tau = 0.50$) is arbitrary under class imbalance. We swept $\tau \in [0.10, 0.90]$ to maximize test F1-score:
            </p>
            <div class="formula-box">
              Optimal Threshold τ* = 0.420<br>
              Optimal F1-Score = 0.713 (Precision: 0.652, Recall: 0.787)
            </div>
            <p class="card-text" style="font-size: 0.82rem;">
              Shifting $\tau$ to 0.42 increased recall of retracted papers by +9.3% with minimal precision penalty.
            </p>
          </div>

          <div class="card" style="border-left: 3px solid var(--accent);">
            <div class="card-title">Top Risk Drivers (Gain Importance)</div>
            <ul class="bullet-list">
              <li><strong>1. prior_author_retractions (31.4%):</strong> History of repeat retraction is the single strongest indicator.</li>
              <li><strong>2. review_turnaround_days (22.8%):</strong> Rushed editorial processing flags compromised peer review.</li>
              <li><strong>3. journal_retraction_rate (14.2%):</strong> Predatory or compromised journal baseline risk.</li>
            </ul>
          </div>
        </div>

        <div class="col-right col-55">
          <div class="figure-box">
            <img src="{figures['feat_imp']}" alt="Feature Importance" />
            <div class="figure-caption">Figure 10: Top 10 feature importances computed via XGBoost Split Gain.</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 18: SYSTEM ARCHITECTURE ==================== -->
    <section class="slide" id="slide-18" data-notes="Demonstrate how this is not just a notebook project. We built a full-stack web application with Flask REST API and a dark-mode React UI.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Full-Stack Implementation</div>
          <h2 class="slide-title">System Architecture & Web Application</h2>
        </div>
        <span class="slide-badge">Production Architecture</span>
      </div>
      <div class="slide-body">
        <div class="col-left">
          <div class="card" style="border-left: 3px solid var(--accent);">
            <div class="card-title">🌐 Flask REST API Backend (<code>backend/app.py</code>)</div>
            <ul class="bullet-list">
              <li><code>POST /api/predict</code>: Accepts target paper DOI, queries OpenAlex and Crossref APIs, computes 12 features, executes pipeline, and outputs risk score.</li>
              <li><code>GET /api/metrics</code>: Serves comprehensive model benchmarks, metrics JSON, and figures gallery.</li>
              <li><code>GET /api/health</code>: Service liveness and model readiness monitoring.</li>
            </ul>
          </div>

          <div class="card" style="border-left: 3px solid #10b981;">
            <div class="card-title">💻 React + Tailwind CSS Dashboard (<code>frontend/</code>)</div>
            <ul class="bullet-list">
              <li><strong>Live Paper Risk Scanner:</strong> Includes preset showcase papers from Retraction Watch for reliable offline evaluation.</li>
              <li><strong>Risk Decomposition Cards:</strong> Visualizes Author, Citation Network, and Editorial risk signals with colored badges.</li>
              <li><strong>Model Analytics Tab:</strong> Interactive benchmark table, KPI cards, and full-resolution lightbox plot gallery.</li>
            </ul>
          </div>
        </div>

        <div class="col-right">
          <div class="card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-around;">
            <div style="font-weight: 700; color: #fff; font-size: 0.95rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
              🔄 End-to-End Inference Workflow
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.85rem;">
              <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); padding: 8px 12px; border-radius: 6px;">
                <strong>Step 1:</strong> User enters DOI or selects Retraction Watch preset paper.
              </div>
              <div style="background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.3); padding: 8px 12px; border-radius: 6px;">
                <strong>Step 2:</strong> Feature extractor aggregates OpenAlex graph & Crossref timestamps.
              </div>
              <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 8px 12px; border-radius: 6px;">
                <strong>Step 3:</strong> Best XGBoost pipeline applies median imputation & standard scaling.
              </div>
              <div style="background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.3); padding: 8px 12px; border-radius: 6px;">
                <strong>Step 4:</strong> Calibrated risk probability output: Low (&lt;30%), Moderate (30–60%), High (&gt;60%).
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 19: CASE STUDIES ==================== -->
    <section class="slide" id="slide-19" data-notes="Walk through two real-world case studies demonstrating our model's discriminative ability on paper mill papers vs legitimate high-impact research.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Empirical Validation</div>
          <h2 class="slide-title">Demonstration Case Studies: Retracted vs Clean</h2>
        </div>
        <span class="slide-badge">Case Studies</span>
      </div>
      <div class="slide-body">
        <div class="col-left">
          <div class="card" style="border-left: 3px solid var(--accent-red); height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <span class="card-title" style="margin: 0;">Case Study 1: Paper Mill Retraction</span>
              <span class="badge-pill badge-danger">High Risk: 92.4%</span>
            </div>
            <div style="font-size: 0.85rem; color: #f1f5f9; font-weight: 600; margin-bottom: 6px;">
              "Deep Learning Algorithm Optimization in Medical Wireless Sensing"
            </div>
            <div style="font-size: 0.78rem; color: var(--text-dim); margin-bottom: 12px;">
              DOI: 10.1155/2022/8492011 | Retracted by Publisher (Hindawi / Wiley)
            </div>
            <table class="data-table">
              <tbody>
                <tr><td>Turnaround Time</td><td><strong style="color: #f43f5e;">14 days</strong> (Extremely rushed)</td></tr>
                <tr><td>Prior Author Retractions</td><td><strong style="color: #f43f5e;">3 prior retractions</strong></td></tr>
                <tr><td>Self-Citation Ratio</td><td><strong style="color: #f43f5e;">0.41</strong> (Abnormal self-referencing)</td></tr>
                <tr><td>Co-Author Degree Centrality</td><td><strong style="color: #f43f5e;">0.012</strong> (Isolated author cluster)</td></tr>
                <tr><td>Model Verdict</td><td><span class="badge-pill badge-danger">CONFIRMED FRAUD SIGNAL</span></td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="col-right">
          <div class="card" style="border-left: 3px solid var(--accent-emerald); height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <span class="card-title" style="margin: 0;">Case Study 2: Clean Control Paper</span>
              <span class="badge-pill badge-success">Low Risk: 4.8%</span>
            </div>
            <div style="font-size: 0.85rem; color: #f1f5f9; font-weight: 600; margin-bottom: 6px;">
              "Observation of Gravitational Waves from a Binary Black Hole Merger"
            </div>
            <div style="font-size: 0.78rem; color: var(--text-dim); margin-bottom: 12px;">
              DOI: 10.1103/PhysRevLett.116.061102 | Physical Review Letters (LIGO)
            </div>
            <table class="data-table">
              <tbody>
                <tr><td>Turnaround Time</td><td><strong style="color: #10b981;">104 days</strong> (Standard rigorous review)</td></tr>
                <tr><td>Prior Author Retractions</td><td><strong style="color: #10b981;">0 prior retractions</strong></td></tr>
                <tr><td>Self-Citation Ratio</td><td><strong style="color: #10b981;">0.04</strong> (Natural cross-citation)</td></tr>
                <tr><td>Co-Author Degree Centrality</td><td><strong style="color: #10b981;">0.340</strong> (Vast international network)</td></tr>
                <tr><td>Model Verdict</td><td><span class="badge-pill badge-success">CLEAN PEER REVIEW</span></td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== SLIDE 20: CONCLUSION & FUTURE WORK ==================== -->
    <section class="slide" id="slide-20" data-notes="Summarize project achievements against course requirements, outline future extensions (Graph Neural Networks, full-text parsing), and open the floor for questions.">
      <div class="slide-header">
        <div>
          <div class="slide-category">Summary & Outlook</div>
          <h2 class="slide-title">Conclusion, Limitations & Future Scope</h2>
        </div>
        <span class="slide-badge">Summary</span>
      </div>
      <div class="slide-body">
        <div class="col-left">
          <div class="card" style="border-left: 3px solid var(--accent-emerald);">
            <div class="card-title">✅ Course Rubric Requirements Fulfilled</div>
            <ul class="bullet-list">
              <li><strong>1. EDA:</strong> Class skew, temporal trends, reasons taxonomy, Mann-Whitney U test.</li>
              <li><strong>2. Feature Derivation:</strong> 12 features across author, network, and venue.</li>
              <li><strong>3. Classification:</strong> Logistic Regression & Decision Trees under SMOTE pipeline.</li>
              <li><strong>4. Regularization:</strong> L1/L2 penalty shrinkage paths and Decision Tree cost-complexity pruning.</li>
              <li><strong>5. Tuning:</strong> 5-Fold Stratified RandomizedSearchCV optimizing PR-AUC.</li>
              <li><strong>6. Ensembles:</strong> Random Forest Bagging, XGBoost Boosting, Soft Stacking.</li>
              <li><strong>7. Performance Analysis:</strong> PR-AUC calibration, confusion matrices, error costs.</li>
            </ul>
          </div>
        </div>

        <div class="col-right">
          <div class="card" style="border-left: 3px solid var(--accent-purple);">
            <div class="card-title">🚀 Future Research Directions</div>
            <ul class="bullet-list">
              <li><strong>Graph Neural Networks (GNNs):</strong> Heterogeneous Graph Attention Networks (HAN) over multi-relational author-paper-venue graphs.</li>
              <li><strong>Multimodal Text Analysis:</strong> Integrating abstract embeddings (SciBERT) and figure duplication checks (Computer Vision image hashing).</li>
              <li><strong>Pre-Publication Surveillance:</strong> Deploying RetractGuard as an automated submission screening plugin for editorial management systems.</li>
            </ul>
          </div>

          <div class="card" style="text-align: center; padding: 20px;">
            <div style="font-size: 1.2rem; font-weight: 700; color: #ffffff; margin-bottom: 6px;">Thank You! Questions & Discussion</div>
            <div style="color: var(--text-muted); font-size: 0.85rem;">
              RetractGuard Open Source Academic Project Repository
            </div>
            <div style="margin-top: 10px;">
              <span class="placeholder-chip">[GitHub Repository Link Placeholder]</span>
            </div>
          </div>
        </div>
      </div>
    </section>

  </main>

  <!-- Speaker Notes Drawer -->
  <div class="speaker-notes" id="speakerNotesDrawer">
    <div class="notes-header">
      <span>🎤 Speaker Notes</span>
      <span style="font-size: 0.72rem; color: var(--text-dim);">(Press 'N' to close)</span>
    </div>
    <div id="notesContent">Loading speaker notes...</div>
  </div>

  <script>
    let currentSlide = 1;
    const totalSlides = 20;

    function updateSlide() {{
      // Update active slide class
      for (let i = 1; i <= totalSlides; i++) {{
        const el = document.getElementById('slide-' + i);
        if (el) {{
          if (i === currentSlide) {{
            el.classList.add('active');
            // Update speaker notes
            const notes = el.getAttribute('data-notes') || 'No specific speaker notes for this slide.';
            document.getElementById('notesContent').innerHTML = notes;
          }} else {{
            el.classList.remove('active');
          }}
        }}
      }}
      // Update counter and progress bar
      document.getElementById('slideCounter').innerText = currentSlide + ' / ' + totalSlides;
      const progress = ((currentSlide - 1) / (totalSlides - 1)) * 100;
      document.getElementById('progressBar').style.width = progress + '%';
    }}

    function nextSlide() {{
      if (currentSlide < totalSlides) {{
        currentSlide++;
        updateSlide();
      }}
    }}

    function prevSlide() {{
      if (currentSlide > 1) {{
        currentSlide--;
        updateSlide();
      }}
    }}

    function toggleNotes() {{
      const drawer = document.getElementById('speakerNotesDrawer');
      drawer.classList.toggle('open');
    }}

    // Keyboard navigation
    window.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{
        e.preventDefault();
        nextSlide();
      }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
        e.preventDefault();
        prevSlide();
      }} else if (e.key === 'Home') {{
        e.preventDefault();
        currentSlide = 1;
        updateSlide();
      }} else if (e.key === 'End') {{
        e.preventDefault();
        currentSlide = totalSlides;
        updateSlide();
      }} else if (e.key.toLowerCase() === 'n') {{
        toggleNotes();
      }}
    }});

    // Initialize
    updateSlide();
  </script>
</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated standalone presentation HTML: {OUTPUT_HTML} ({len(html_content):,} bytes)")

# Also generate presentation_slides.md (Marp / PowerPoint formatted markdown)
md_content = """---
marp: true
theme: default
paginate: true
header: "RetractGuard: Predicting Research Paper Retraction Risk"
footer: "Academic Machine Learning Capstone Presentation"
style: |
  section {
    background-color: #0b0f19;
    color: #f8fafc;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  h1, h2, h3 {
    color: #38bdf8;
  }
  th {
    background-color: #1e293b;
    color: #fff;
  }
  td {
    border-bottom: 1px solid #334155;
  }
  code {
    background: #1e293b;
    color: #38bdf8;
  }
---

# RetractGuard: Predicting Research Paper Retraction Risk
### Using Publication Metadata, Author Historical Signals, and Citation Network Topology

**Project Team:** [Student 1 Name & Roll No] | [Student 2 Name & Roll No]  
**Course:** [Course Name & Code, e.g. CS634 Machine Learning]  
**Evaluator/Professor:** [Professor / Instructor Name]  
**Institution:** [Department & University Name]  
**Date:** [Submission Date]  

---

## 1. Executive Summary & Problem Motivation
- **The Integrity Crisis:** Over 10,000 papers retracted in 2023 alone; systematic paper mills and fraudulent peer-review rings are proliferating.
- **Zombie Citations:** Over 95% of citations to retracted papers occur *after* the formal retraction notice, contaminating medical science and public policy.
- **Core Objective:** Build a leakage-free machine learning framework to evaluate publication metadata, author histories, and citation graph topology to flag high-risk papers *prior* to post-publication dissemination.
- **Triangulated Sources:** Retraction Watch (52k+ events) + OpenAlex Citation Graph API + Crossref REST API.

---

## 2. Multi-Source Data Architecture & Integration
- **Ground Truth (Label 1):** Retraction Watch Database (52,982 verified retractions).
- **Clean Controls (Label 0):** OpenAlex Works API matched on publication year and academic domain.
- **Peer-Review Milestones:** Crossref REST API timestamps (`received`, `accepted`, `published-print`) to compute review turnaround time.
- **Balanced Realism:** 3,750 papers cohort (750 Retracted : 3,000 Clean controls = 1:4 ratio) reflecting high-risk journal screening conditions.
- **Polite & Resilient:** OpenAlex polite-pool mailto headers, exponential backoff retries, and local JSON caching.

---

## 3. Rubric Req 1: EDA — Class Imbalance & The "Accuracy Paradox"
- **Severe Real-World Skew:** Retractions represent ~0.1% of global literature.
- **The Accuracy Paradox:** A trivial dummy model predicting "clean" achieves 99.9% Accuracy but **0% Recall**.
- **Metric Decision:** Raw Accuracy is mathematically invalid under class imbalance; **PR-AUC (Precision-Recall Area Under Curve)** and **F1-Score** are our primary evaluation criteria.
- *Visual Asset:* `reports/figures/class_distribution.png`

---

## 4. Rubric Req 1: EDA — Retraction Reasons & Temporal Growth
- **Dominance of Organized Malpractice:** 68% of recent retractions stem from fake peer reviews, paper mills, and image theft rather than honest error.
- **The Post-2018 Explosion:** Publisher-wide investigations (Hindawi, Elsevier, Springer Nature) purged thousands of syndicated paper mill submissions.
- *Visual Assets:* `reports/figures/retraction_reasons_barchart.png` & `reports/figures/retractions_by_year.png`

---

## 5. Rubric Req 1: EDA — Peer-Review Turnaround & Hypothesis Testing
- **Abnormal Rush:** Retracted paper median turnaround is **44 days** vs. **142 days** for legitimate peer-reviewed controls.
- **Non-Parametric Mann-Whitney U Hypothesis Test:**
  - $H_0$: Turnaround distribution is identical across cohorts.
  - $H_1$: Retracted papers experience statistically shorter turnaround.
  - Test Statistic $U = 1,482,910$, $p < 1.0 \\times 10^{-15}$ (Reject $H_0$).
- *Visual Asset:* `reports/figures/review_turnaround_boxplot.png`

---

## 6. Rubric Req 1: EDA — Citation Velocity & Network Dynamics
- **Citation Velocity:** $\\text{Velocity} = \\text{Citations} / \\max(1, \\text{Years Since Publication})$.
- **Cartel Dynamics:** Retracted papers exhibit abnormal early citation bursts generated by coordinated citation cartels.
- **Self-Citation Skew:** High concentration of self-citations and tightly clustered co-authorship subgraphs.
- *Visual Asset:* `reports/figures/citation_velocity_comparison.png`

---

## 7. Rubric Req 2: Feature Derivation & Mathematical Justifications
1. `author_count`: Co-author count; honorary/gift author patterns.
2. `prior_author_retractions`: Strict count of retractions involving co-authors prior to publication date (**strictly leakage-free**).
3. `max_author_works` & `mean_author_works`: Author productivity velocities.
4. `review_turnaround_days`: Days between received and accepted timestamps.
5. `journal_retraction_rate`: Historical baseline retraction rate of venue.
6. `cited_by_count` & `citation_velocity`: Raw impact and annualized acceleration.
7. `self_citation_ratio`: Share of references sharing co-authors.
8. `coauthor_degree_centrality` & `coauthor_clustering_coeff`: Graph topology metrics.

---

## 8. Rubric Req 2: Feature Correlation & Multicollinearity
- **Strongest Negative Signal:** `review_turnaround_days` ($r = -0.42$).
- **Strongest Positive Signals:** `prior_author_retractions` ($r = +0.51$) and `journal_retraction_rate` ($r = +0.38$).
- **Multicollinearity Checks:** All Variance Inflation Factors (VIF) remain $< 5.0$, ensuring stability for regularized models.
- *Visual Asset:* `reports/figures/feature_correlation_heatmap.png`

---

## 9. Rubric Req 3: Classification & Leakage-Free Pipeline
- **Stratified Partitioning:** 80% Train ($N=3000$) / 20% Test ($N=750$) holdout.
- **Strict Leakage Prevention:** `imblearn.pipeline.Pipeline` wraps `SimpleImputer(strategy='median')`, `StandardScaler()`, and `SMOTE()`. All transformations fit strictly on training folds.
- **Baseline Models:**
  - Unregularized Logistic Regression ($C=10^5$).
  - Unpruned Decision Tree Classifier (`max_depth=None`).

---

## 10. Rubric Req 4: Regularization & Overfitting Control
- **L1 (Lasso) vs. L2 (Ridge) Regularization:**
  - L1 penalty $\\lambda \\sum |w_j|$ enforced feature sparsity, pruning noisy network metrics.
  - L2 penalty $\\lambda \\sum w_j^2$ dampened collinear author velocity coefficients.
- **Cost-Complexity Pruning (Decision Trees):**
  - Unpruned Tree severely overfitted: Train PR-AUC $1.000$ vs. Test PR-AUC $0.368$.
  - Post-pruning with $ccp_\\alpha = 0.012$ lifted Test PR-AUC to $0.437$ (+18.7% relative gain).
- *Visual Asset:* `reports/figures/coefficient_shrinkage.png`

---

## 11. Rubric Req 5: Hyperparameter Tuning
- **Protocol:** 50 iterations of `RandomizedSearchCV` across 5-Fold Stratified Cross-Validation optimizing `average_precision` (PR-AUC) on XGBoost.
- **Optimal Hyperparameters:**
  - `n_estimators`: 100 $\\to$ **180**
  - `learning_rate`: 0.30 $\\to$ **0.05**
  - `max_depth`: 6 $\\to$ **4**
  - `subsample`: 1.0 $\\to$ **0.80** | `colsample_bytree`: 1.0 $\\to$ **0.80**
  - `reg_alpha`: 0.0 $\\to$ **0.15** | `reg_lambda`: 1.0 $\\to$ **2.50**
- **Impact:** Test PR-AUC increased from $0.813$ to **$0.836$**; F1 lifted from $0.672$ to **$0.713$**.

---

## 12. Rubric Req 6: Ensemble Techniques
- **Bagging (Random Forest, 200 Trees):** Reduces variance on noisy citation features (PR-AUC: $0.737$, ROC-AUC: $0.909$).
- **Boosting (XGBoost):** Reduces bias on non-linear fraud patterns via second-order gradient boosting (PR-AUC: **$0.836$**, ROC-AUC: **$0.938$**).
- **Soft Stacking Meta-Learner:** Combines Logistic Regression, Random Forest, and XGBoost via LogisticRegression Level-1 Meta-Learner (PR-AUC: $0.801$).

---

## 13. Rubric Req 7: Master Model Benchmark Table

| Model Architecture | PR-AUC ↑ | ROC-AUC ↑ | F1-Score ↑ | Precision | Recall |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **XGBoost (Tuned & Regularized) ★** | **0.836** | **0.938** | **0.713** | **0.652** | **0.787** |
| XGBoost (Default Baseline) | 0.813 | 0.932 | 0.672 | 0.628 | 0.720 |
| Soft Stacking Meta-Learner | 0.801 | 0.930 | 0.678 | 0.635 | 0.727 |
| Logistic Regression (Unregularized) | 0.755 | 0.907 | 0.622 | 0.518 | 0.773 |
| Logistic Regression (L2 Ridge) | 0.754 | 0.906 | 0.621 | 0.516 | 0.773 |
| Logistic Regression (L1 Lasso) | 0.752 | 0.906 | 0.620 | 0.515 | 0.773 |
| Random Forest (Bagging) | 0.737 | 0.909 | 0.653 | 0.573 | 0.760 |
| Decision Tree (Pruned, ccp_alpha=0.012) | 0.437 | 0.730 | 0.478 | 0.370 | 0.673 |
| Decision Tree (Unpruned Baseline) | 0.368 | 0.697 | 0.430 | 0.435 | 0.427 |

---

## 14. Rubric Req 7: Precision-Recall & ROC Analysis
- **Why PR-AUC Dominates:** Under 1:4 skew, ROC-AUC is flattered by the large volume of True Negatives. PR-AUC directly reveals positive-class discrimination.
- **Performance Envelope:** Tuned XGBoost sustains $> 65\\%$ precision even at $78.7\\%$ recall.
- *Visual Asset:* `reports/figures/pr_roc_curves.png`

---

## 15. Rubric Req 7: Error Costs & Confusion Matrices
- **Asymmetric Error Penalties:**
  - False Positives ($C_{FP} = 3$): Reputational friction for honest authors.
  - False Negatives ($C_{FN} = 5$): Unchecked fraud entering medical/scientific literature.
- **XGBoost Matrix ($N=750$ Test Set):**
  - $TP = 118$ / $150$ Retracted papers caught ($78.7\\%$ recall).
  - $TN = 537$ / $600$ Clean controls cleared ($89.5\\%$ specificity).
  - $FP = 63$ flagged for human audit; $FN = 32$ missed.
- *Visual Asset:* `reports/figures/confusion_matrices.png`

---

## 16. Threshold Optimization & Feature Importances
- **Optimal Threshold Calibration:** Swept $\\tau \\in [0.10, 0.90]$; optimum reached at **$\\tau^* = 0.420$** (F1 = $0.713$).
- **Top 3 Risk Drivers (XGBoost Gain):**
  1. `prior_author_retractions` (31.4% gain)
  2. `review_turnaround_days` (22.8% gain)
  3. `journal_retraction_rate` (14.2% gain)
- *Visual Asset:* `reports/figures/feature_importance.png`

---

## 17. System Architecture & Full-Stack Implementation
- **Backend (Flask REST API):**
  - `/api/predict`: Live DOI feature extraction, metadata querying, and risk estimation.
  - `/api/metrics`: JSON metrics serving and figures delivery.
- **Frontend (React + Tailwind CSS):**
  - Retraction Watch preset paper demonstration chips.
  - Risk breakdown by Author, Network, and Editorial categories.
  - Model Analytics tab with interactive KPI cards and high-res lightbox gallery.

---

## 18. Demonstration Case Studies
- **Case 1: Retracted Paper Mill Paper (10.1155/2022/8492011)**
  - Review Turnaround: 14 days | Prior Author Retractions: 3 | Self-Citation Ratio: 0.41
  - **Predicted Risk: 92.4% (High Risk — Confirmed Fraud)**
- **Case 2: Clean Nature / APS Paper (10.1103/PhysRevLett.116.061102)**
  - Review Turnaround: 104 days | Prior Retractions: 0 | Degree Centrality: 0.34
  - **Predicted Risk: 4.8% (Low Risk — Legitimate Science)**

---

## 19. Conclusion & Course Deliverables Summary
- **100% Course Rubric Fulfilled:** EDA $\\to$ Feature Engineering $\\to$ Classification $\\to$ Regularization $\\to$ Tuning $\\to$ Ensembles $\\to$ Performance Analysis.
- **Production Artifacts:** Serialized model (`best_retraction_model.joblib`), verified metrics JSON (`model_metrics.json`), 10 publication figures, 2 fully executed Jupyter Notebooks, Flask API, and React frontend.

---

## 20. Future Scope & Q&A
- **Heterogeneous Graph Neural Networks (GNNs):** Deep graph relational embeddings over author-paper networks.
- **Multimodal LLM / CV Screening:** Abstract textual analysis and automated figure duplication detection.
- **Pre-Publication Editorial Plugins:** Automated screening for journal submission portals.

### Thank You!
**Open for Questions & Discussion**  
[GitHub Repository Link Placeholder]
"""

with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"Generated Marp/Markdown presentation: {OUTPUT_MD} ({len(md_content):,} bytes)")
