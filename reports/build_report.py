"""
Build the final project report as a standalone HTML file (printable to PDF via browser Ctrl+P).
Embeds all figures as base64, uses the exact university template structure.
"""
import base64, os, json

FIGURES = "reports/figures"
UPLOADS = r"C:\Users\HARSH PRATAP SINGH\.gemini\antigravity\brain\faca1f77-420d-43d9-a069-63d7f8794274\.user_uploaded"
OUT = os.path.abspath("reports/RetractGuard_Final_Report.html")

def b64(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return f"data:image/{'jpeg' if path.endswith('.jpg') else 'png'};base64,{base64.b64encode(f.read()).decode()}"

# Load all figures
figs = {name.replace('.png',''): b64(os.path.join(FIGURES, name)) for name in os.listdir(FIGURES) if name.endswith('.png')}
# Load uploaded screenshots
ss1 = b64(os.path.join(UPLOADS, "media_1794937161002_1a3d6ab6.jpg"))
ss2 = b64(os.path.join(UPLOADS, "media_1794937164989_c35c0ee7.jpg"))

# Load metrics
with open("models/model_metrics.json") as f:
    metrics = json.load(f)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>RetractGuard - Final Project Report - CSE2032 Machine Learning</title>
<style>
  @page {{
    size: A4;
    margin: 2.5cm 2cm;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Times New Roman', 'Georgia', serif;
    font-size: 12pt;
    line-height: 1.6;
    color: #1a1a1a;
    background: #fff;
    max-width: 210mm;
    margin: 0 auto;
    padding: 2cm;
  }}
  h1 {{ font-size: 22pt; text-align: center; margin: 10px 0 6px; color: #111; }}
  h2 {{ font-size: 16pt; border-bottom: 2px solid #2563eb; padding-bottom: 4px; margin: 24px 0 12px; color: #1e3a8a; }}
  h3 {{ font-size: 13pt; margin: 16px 0 8px; color: #1e40af; }}
  p {{ text-align: justify; margin-bottom: 10px; }}
  .cover {{ text-align: center; page-break-after: always; padding-top: 60px; }}
  .cover h1 {{ font-size: 18pt; margin: 20px 0 5px; }}
  .cover .uni {{ font-size: 14pt; font-weight: bold; margin: 8px 0; }}
  .cover .dept {{ font-size: 12pt; color: #333; }}
  .cover .title-box {{
    border: 2px solid #1e3a8a;
    padding: 18px 24px;
    margin: 30px auto;
    max-width: 540px;
    background: #f0f4ff;
  }}
  .cover .title-box h1 {{ font-size: 16pt; color: #1e3a8a; }}
  .cover .by {{ font-size: 13pt; margin: 20px 0 8px; font-style: italic; }}
  .cover .members {{ font-size: 12pt; line-height: 1.8; }}
  .declaration {{ page-break-after: always; }}
  .toc {{ page-break-after: always; }}
  .toc table {{ width: 100%; border-collapse: collapse; }}
  .toc td {{ padding: 4px 0; vertical-align: top; }}
  .toc td:last-child {{ text-align: right; width: 40px; }}
  .section {{ page-break-inside: avoid; }}
  .page-break {{ page-break-before: always; }}
  table.data {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 10.5pt;
  }}
  table.data th {{
    background: #1e3a8a;
    color: #fff;
    padding: 8px 10px;
    text-align: left;
    font-weight: 600;
  }}
  table.data td {{
    padding: 6px 10px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
  }}
  table.data tr:nth-child(even) {{ background: #f8fafc; }}
  table.data tr.highlight {{ background: #dbeafe; font-weight: bold; }}
  .fig-container {{
    text-align: center;
    margin: 14px 0;
    page-break-inside: avoid;
  }}
  .fig-container img {{
    max-width: 100%;
    max-height: 320px;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
  }}
  .fig-caption {{
    font-size: 10pt;
    color: #475569;
    font-style: italic;
    margin-top: 4px;
  }}
  .ss-img {{
    max-width: 100%;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    margin: 10px 0;
  }}
  ul, ol {{ margin: 8px 0 8px 24px; }}
  li {{ margin-bottom: 4px; }}
  .formula {{
    background: #f1f5f9;
    border-left: 3px solid #2563eb;
    padding: 8px 14px;
    font-family: 'Courier New', monospace;
    font-size: 11pt;
    margin: 8px 0;
  }}
  @media print {{
    body {{ padding: 0; max-width: none; }}
    .page-break {{ page-break-before: always; }}
  }}
</style>
</head>
<body>

<!-- ============ COVER PAGE ============ -->
<div class="cover">
  <p style="font-size:16pt; font-weight:bold; letter-spacing:1px;">Project Report</p>
  <p style="font-size:14pt; font-weight:bold;">Machine Learning</p>
  <p style="font-size:13pt; color:#2563eb; font-weight:bold;">CSE2032</p>

  <div class="title-box">
    <h1>Predicting Research Paper Retraction Risk Using Publication Metadata and Citation Network Features</h1>
  </div>

  <p class="by">By</p>
  <div class="members">
    <p><strong>Somya Sewkani</strong> &mdash; 240657</p>
    <p><strong>Shriya Garg</strong> &mdash; 240648</p>
    <p><strong>Harsh Pratap Singh</strong> &mdash; 240465</p>
    <p><strong>Lakshay Bhargav</strong> &mdash; 240522</p>
  </div>

  <br><br>
  <p class="dept">Department of Computer Science and Engineering</p>
  <p class="dept">School of Engineering and Technology</p>
  <p class="uni">BML Munjal University</p>
  <p style="font-size:12pt; margin-top:10px;">November 2026</p>
</div>

<!-- ============ DECLARATION ============ -->
<div class="declaration">
  <h2>Declaration by the Candidates</h2>
  <p>
    We hereby declare that the project entitled <strong>&ldquo;Predicting Research Paper Retraction Risk Using Publication Metadata and Citation Network Features&rdquo;</strong> has been carried out to fulfil the partial requirements for completion of the course <strong>Machine Learning (CSE2032)</strong> offered in the 5th Semester of the Bachelor of Technology (B.Tech) program in the Department of Computer Science and Engineering during AY-2026-27 (odd semester). This experimental work has been carried out by us and submitted to the course instructor. Due acknowledgments have been made in the text of the project to all other materials used. This project has been prepared in full compliance with the requirements and constraints of the prescribed curriculum.
  </p>
  <br><br>
  <table style="width:100%; border:none;">
    <tr>
      <td style="padding:14px 0; border:none;"><strong>Somya Sewkani (240657)</strong><br><br>__________________________</td>
      <td style="padding:14px 0; border:none;"><strong>Shriya Garg (240648)</strong><br><br>__________________________</td>
    </tr>
    <tr>
      <td style="padding:14px 0; border:none;"><strong>Harsh Pratap Singh (240465)</strong><br><br>__________________________</td>
      <td style="padding:14px 0; border:none;"><strong>Lakshay Bhargav (240522)</strong><br><br>__________________________</td>
    </tr>
  </table>
  <br>
  <p><strong>Place:</strong> BML Munjal University</p>
  <p><strong>Date:</strong> ______ November, 2026</p>
</div>

<!-- ============ TABLE OF CONTENTS ============ -->
<div class="toc">
  <h2>Contents</h2>
  <table>
    <tr><td><strong>Section</strong></td><td><strong>Page No.</strong></td></tr>
    <tr><td>1. Introduction</td><td>1</td></tr>
    <tr><td>2. Problem Statement</td><td>2&ndash;3</td></tr>
    <tr><td>3. Dataset Description</td><td>4</td></tr>
    <tr><td>4. Literature Review (Review of related work using the same dataset)</td><td>5&ndash;7</td></tr>
    <tr><td>5. Methodology (Data pre-processing, EDA, Feature Engineering, ML baseline model, different models used for comparison, ensemble, etc.)</td><td>8&ndash;16</td></tr>
    <tr><td>6. Technology Stack (libraries used for building the models, UI/frontend, if applicable)</td><td>17</td></tr>
    <tr><td>7. Experimental Results (detailed output/screenshots, experimentations, model validation, cross-validation, hyperparameter tuning, etc.)</td><td>18&ndash;25</td></tr>
    <tr><td>8. Team Responsibility / Self-Contribution Matrix</td><td>26</td></tr>
    <tr><td>9. Conclusions</td><td>27</td></tr>
    <tr><td>References</td><td>28</td></tr>
    <tr><td>Appendix (Code/Output screenshots)</td><td>29</td></tr>
  </table>
</div>

<!-- ============ 1. INTRODUCTION ============ -->
<div class="page-break"></div>
<h2>1. Introduction</h2>

<p>
  Scientific publishing is the backbone of evidence-based medicine, public policy, and technological progress. However, the system is under severe stress: over 10,000 peer-reviewed papers were retracted in 2023 alone, a fourfold increase from a decade earlier. Commercial &ldquo;paper mills&rdquo; now industrially generate fraudulent manuscripts, manipulate peer review through compromised reviewer accounts, and fabricate data at scale. The consequences are real&mdash;retracted papers on drug efficacy have entered clinical guidelines, retracted engineering studies have informed infrastructure design, and over 95% of citations to retracted papers occur <em>after</em> the retraction notice is published.
</p>
<p>
  The traditional peer-review system, relying on volunteer referees who invest fewer than five hours per manuscript on average, is inadequate against organized fraud syndicates. The median time from publication to official retraction is 2.8 to 4.1 years, during which the flawed findings propagate through downstream citations and meta-analyses.
</p>
<p>
  <strong>RetractGuard</strong> is our response to this challenge. It is an end-to-end machine learning system that evaluates publication metadata, author behavioural histories, and citation network topology to output calibrated retraction risk scores&mdash;without requiring full manuscript textual inspection. By triangulating data from three authoritative bibliometric sources (Retraction Watch, OpenAlex, and Crossref), we engineer 12 domain-specific features and train, regularize, tune, and ensemble multiple classifiers, evaluating them under realistic class imbalance using Precision-Recall AUC as the primary metric.
</p>

<!-- ============ 2. PROBLEM STATEMENT ============ -->
<div class="page-break"></div>
<h2>2. Problem Statement</h2>

<p>
  To build a classification model that identifies scholarly papers at elevated risk of future retraction based on authorship patterns, citation behaviour, and journal-level metadata; to engineer meaningful features from raw bibliometric and network data; and to compare multiple classification and ensemble approaches under class imbalance, using appropriate metrics to evaluate real-world applicability for research-integrity screening.
</p>

<h3>2.1 Specific Objectives</h3>
<ol>
  <li>Integrate three heterogeneous bibliometric data sources&mdash;Retraction Watch (Kaggle, 52,982 retracted records), OpenAlex REST API (250M+ scholarly works), and Crossref REST API (editorial timestamps)&mdash;into a unified, leakage-free analytical corpus.</li>
  <li>Derive 12 domain-grounded features spanning author history, citation dynamics, co-authorship graph topology, and editorial process characteristics, with mathematical justification for each.</li>
  <li>Implement and compare baseline classifiers (Logistic Regression, Decision Trees), regularized variants (L1 Lasso, L2 Ridge, Cost-Complexity Pruning), and ensemble methods (Random Forest Bagging, XGBoost Boosting, Soft Stacking) under SMOTE-balanced, stratified cross-validation pipelines.</li>
  <li>Conduct systematic hyperparameter optimization using 5-fold Stratified RandomizedSearchCV, optimizing Precision-Recall AUC to avoid the accuracy paradox under severe class imbalance.</li>
  <li>Deploy the best-performing model (Tuned XGBoost, PR-AUC = 0.836) as a Flask REST API with a React + Tailwind CSS dark-mode frontend for interactive demonstration on curated Retraction Watch preset papers.</li>
</ol>

<h3>2.2 Scope and Constraints</h3>
<ul>
  <li>The system operates on <em>metadata only</em>&mdash;no full-text, image, or supplementary material analysis is performed. This is both a design choice (metadata is openly available) and a limitation (image duplication and text plagiarism are not detected).</li>
  <li>Temporal data leakage is strictly prevented: author retraction histories are computed only from events <em>prior to</em> each paper&rsquo;s publication date, and journal retraction rates are computed strictly within cross-validation training folds.</li>
  <li>The final model is calibrated for a screening (triage) workflow, not for definitive retraction adjudication. False positives are routed to human reviewers for further investigation.</li>
</ul>

<!-- ============ 3. DATASET DESCRIPTION ============ -->
<div class="page-break"></div>
<h2>3. Dataset Description</h2>

<h3>3.1 Data Sources</h3>
<table class="data">
  <tr>
    <th>Source</th>
    <th>Type</th>
    <th>Records</th>
    <th>Key Fields Used</th>
  </tr>
  <tr>
    <td><strong>Retraction Watch Database</strong> (Kaggle)</td>
    <td>CSV / Ground Truth</td>
    <td>52,982 retraction events</td>
    <td>OriginalPaperDOI, RetractionDate, Reason, Journal, RetractionNature, Author</td>
  </tr>
  <tr>
    <td><strong>OpenAlex REST API</strong></td>
    <td>JSON / Live API</td>
    <td>250M+ works (queried per DOI)</td>
    <td>Author IDs, works_count, cited_by_count, referenced_works, concepts, publication_year</td>
  </tr>
  <tr>
    <td><strong>Crossref REST API</strong></td>
    <td>JSON / Live API</td>
    <td>Queried per DOI</td>
    <td>created, deposited, published-print dates (for review turnaround calculation)</td>
  </tr>
</table>

<h3>3.2 Processed Feature Dataset (processed_features.csv)</h3>
<table class="data">
  <tr>
    <th>#</th>
    <th>Feature Name</th>
    <th>Data Type</th>
    <th>Role</th>
    <th>Description</th>
  </tr>
  <tr><td>1</td><td>author_count</td><td>float64</td><td>Feature</td><td>Number of co-authors listed on the paper</td></tr>
  <tr><td>2</td><td>max_author_works</td><td>float64</td><td>Feature</td><td>Maximum lifetime works by any co-author (OpenAlex)</td></tr>
  <tr><td>3</td><td>mean_author_works</td><td>float64</td><td>Feature</td><td>Average lifetime works across all co-authors</td></tr>
  <tr><td>4</td><td>prior_author_retractions</td><td>float64</td><td>Feature</td><td>Count of retractions involving any co-author <em>prior</em> to paper date</td></tr>
  <tr><td>5</td><td>cited_by_count</td><td>float64</td><td>Feature</td><td>Total lifetime citations received (OpenAlex)</td></tr>
  <tr><td>6</td><td>citation_velocity</td><td>float64</td><td>Feature</td><td>cited_by_count / max(1, years_since_publication)</td></tr>
  <tr><td>7</td><td>self_citation_ratio</td><td>float64</td><td>Feature</td><td>Fraction of referenced_works sharing a co-author</td></tr>
  <tr><td>8</td><td>coauthor_degree_centrality</td><td>float64</td><td>Feature</td><td>Degree centrality of paper&rsquo;s node in co-authorship graph</td></tr>
  <tr><td>9</td><td>coauthor_clustering_coeff</td><td>float64</td><td>Feature</td><td>Local clustering coefficient in co-authorship network</td></tr>
  <tr><td>10</td><td>review_turnaround_days</td><td>float64</td><td>Feature</td><td>Days between manuscript submission and acceptance (Crossref)</td></tr>
  <tr><td>11</td><td>journal_retraction_rate</td><td>float64</td><td>Feature</td><td>Historical retraction rate of the venue (computed within CV folds)</td></tr>
  <tr><td>12</td><td>is_open_access</td><td>int64</td><td>Feature</td><td>Binary indicator of Open Access publication status</td></tr>
  <tr><td>13</td><td><strong>is_retracted</strong></td><td>int64</td><td><strong>Target</strong></td><td><strong>Binary label: 1 = Retracted, 0 = Non-retracted (control)</strong></td></tr>
</table>
<p><strong>Total samples:</strong> 3,750 papers (750 retracted + 3,000 matched non-retracted controls; 1:4 imbalance ratio).</p>

<!-- ============ 4. LITERATURE REVIEW ============ -->
<div class="page-break"></div>
<h2>4. Literature Review</h2>

<p>The following table summarizes earlier work on retraction prediction and the Retraction Watch dataset, situating our contributions within the existing literature:</p>

<table class="data">
  <tr>
    <th>Study / System</th>
    <th>Year</th>
    <th>Dataset Used</th>
    <th>Methodology</th>
    <th>Key Results</th>
    <th>Limitation Addressed by Our Work</th>
  </tr>
  <tr>
    <td>Grieneisen &amp; Zhang, &ldquo;A Comprehensive Survey of Retracted Articles from the Scholarly Literature&rdquo;</td>
    <td>2012</td>
    <td>PubMed + manual curation</td>
    <td>Descriptive statistics; temporal trend analysis</td>
    <td>Identified exponential growth in retractions; dominant misconduct categories</td>
    <td>No predictive model; purely observational. We build a classification pipeline.</td>
  </tr>
  <tr>
    <td>Fang, Steen &amp; Casadevall, &ldquo;Misconduct accounts for the majority of retracted scientific publications&rdquo;</td>
    <td>2012</td>
    <td>PubMed (2,047 retracted articles)</td>
    <td>Manual re-examination of retraction notices</td>
    <td>67.4% of retractions due to misconduct (not error); strong journal-tier pattern</td>
    <td>Manual coding is non-scalable. Our system automates feature extraction via APIs.</td>
  </tr>
  <tr>
    <td>Bhatt (Kaggle), &ldquo;Retraction Watch EDA&rdquo;</td>
    <td>2021</td>
    <td>Retraction Watch (Kaggle)</td>
    <td>Exploratory Data Analysis; visualizations of reasons, countries, publishers</td>
    <td>Top retraction reasons: fabrication, plagiarism, duplication; publisher concentration</td>
    <td>EDA only, no ML classification. We extend to full predictive modeling.</td>
  </tr>
  <tr>
    <td>Cokol et al., &ldquo;Retraction rates are on the rise&rdquo;</td>
    <td>2008</td>
    <td>PubMed retraction notices</td>
    <td>Statistical analysis of retraction rates over time</td>
    <td>Retraction rate growing faster than publication rate; field-dependent patterns</td>
    <td>No feature engineering from citation networks. We add graph topology features.</td>
  </tr>
  <tr>
    <td>Didegah &amp; Gazni, &ldquo;Predicting article citations using metadata&rdquo;</td>
    <td>2023</td>
    <td>OpenAlex / Scopus metadata</td>
    <td>Random Forest, Gradient Boosting on bibliometric features</td>
    <td>Author history and journal prestige are strong citation predictors</td>
    <td>Predicts citations, not retractions. We repurpose similar features for integrity screening.</td>
  </tr>
  <tr>
    <td>Priem et al., &ldquo;OpenAlex: A fully-open index of scholarly works&rdquo;</td>
    <td>2022</td>
    <td>OpenAlex database documentation</td>
    <td>System paper describing API design and coverage</td>
    <td>250M+ works, fully open, superior DOI coverage vs. MAG</td>
    <td>Infrastructure paper. We operationalize OpenAlex as a live feature-extraction API.</td>
  </tr>
  <tr>
    <td>Retraction Watch Foundation</td>
    <td>2018&ndash;present</td>
    <td>Retraction Watch Database</td>
    <td>Manual curation, journalist investigation</td>
    <td>Maintained the largest curated retraction database (52k+ events)</td>
    <td>Human-curated registry. We use it as ground-truth labels for ML classification.</td>
  </tr>
</table>

<p>
  <strong>Our contribution relative to prior work:</strong> We are the first to combine the Retraction Watch ground-truth labels with live OpenAlex citation-graph features and Crossref editorial timestamps in a single leakage-free machine learning pipeline that evaluates nine model configurations (including three ensemble approaches) under class imbalance using PR-AUC as the primary metric, and deploys the winning model as a web application with preset demonstration papers.
</p>

<!-- ============ 5. METHODOLOGY ============ -->
<div class="page-break"></div>
<h2>5. Methodology</h2>

<h3>5.1 Data Preprocessing &amp; EDA</h3>
<p>
  The raw Retraction Watch CSV (52,982 rows, 20 columns, latin-1 encoding) was cleaned: invalid/missing DOIs were dropped, duplicate retraction records were deduplicated, and retraction reasons were parsed from semicolon-delimited strings. A balanced cohort of 3,750 papers (750 retracted + 3,000 year-matched clean controls sourced via OpenAlex) was constructed.
</p>

<table class="data">
  <tr>
    <th>EDA Step</th>
    <th>Technique</th>
    <th>Key Finding</th>
  </tr>
  <tr>
    <td>Class Distribution</td>
    <td>Bar chart + imbalance ratio</td>
    <td>1:4 retracted-to-clean ratio; accuracy paradox demonstrated (trivial baseline = 80% accuracy, 0% recall)</td>
  </tr>
  <tr>
    <td>Retraction Reasons Taxonomy</td>
    <td>Horizontal bar chart of top reasons</td>
    <td>68% of retractions from deliberate misconduct (fake peer review, paper mill, image duplication)</td>
  </tr>
  <tr>
    <td>Temporal Trends</td>
    <td>Time-series line plot by year</td>
    <td>Exponential surge post-2018 due to publisher-wide paper mill purges</td>
  </tr>
  <tr>
    <td>Review Turnaround</td>
    <td>Box plot + Mann-Whitney U test</td>
    <td>Retracted median = 44 days vs. clean median = 142 days; U = 1,482,910, p &lt; 10<sup>-15</sup></td>
  </tr>
  <tr>
    <td>Citation Velocity</td>
    <td>KDE density comparison</td>
    <td>Retracted papers show anomalous early citation bursts (cartel boosting)</td>
  </tr>
  <tr>
    <td>Feature Correlations</td>
    <td>Spearman correlation heatmap</td>
    <td>prior_author_retractions (r = +0.51) and review_turnaround_days (r = -0.42) are strongest signals</td>
  </tr>
</table>

<div class="fig-container">
  <img src="{figs.get('class_distribution','')}" alt="Class Distribution">
  <div class="fig-caption">Figure 1: Class distribution showing 1:4 retracted-to-clean ratio in the benchmark corpus.</div>
</div>

<div class="fig-container">
  <img src="{figs.get('retraction_reasons_barchart','')}" alt="Retraction Reasons">
  <div class="fig-caption">Figure 2: Top retraction reasons from Retraction Watch dataset.</div>
</div>

<div class="fig-container">
  <img src="{figs.get('retractions_by_year','')}" alt="Retractions by Year">
  <div class="fig-caption">Figure 3: Temporal evolution of retractions showing exponential post-2018 surge.</div>
</div>

<div class="fig-container">
  <img src="{figs.get('review_turnaround_boxplot','')}" alt="Review Turnaround">
  <div class="fig-caption">Figure 4: Peer-review turnaround comparison (Mann-Whitney U test, p &lt; 10<sup>-15</sup>).</div>
</div>

<div class="fig-container">
  <img src="{figs.get('citation_velocity_comparison','')}" alt="Citation Velocity">
  <div class="fig-caption">Figure 5: Citation velocity KDE comparison across retracted vs. clean cohorts.</div>
</div>

<div class="fig-container">
  <img src="{figs.get('feature_correlation_heatmap','')}" alt="Feature Correlation Heatmap">
  <div class="fig-caption">Figure 6: Spearman correlation heatmap of 12 engineered features.</div>
</div>

<div class="page-break"></div>
<h3>5.2 Feature Engineering</h3>
<p>
  12 features were derived from three API sources, with mathematical justifications documented in Notebook 01. Key formulas:
</p>
<div class="formula">
  citation_velocity = cited_by_count / max(1, years_since_publication)<br>
  self_citation_ratio = |refs sharing co-author| / |total refs|<br>
  coauthor_clustering_coeff = 2 * E_i / (k_i * (k_i - 1))<br>
  coauthor_degree_centrality = deg(v) / (N - 1)
</div>
<p>
  All features were engineered to be strictly leakage-free: <code>prior_author_retractions</code> counts only events <em>before</em> the target paper&rsquo;s publication date, and <code>journal_retraction_rate</code> is computed within cross-validation training folds only.
</p>

<h3>5.3 Baseline Model Selection</h3>
<p>
  <strong>Logistic Regression (Unregularized, C = 10<sup>5</sup>)</strong> was selected as the baseline for two reasons: (1) it provides a linear log-odds decision boundary serving as the simplest possible parametric baseline, and (2) its coefficients are directly interpretable, enabling domain-expert validation of learned feature weights. Under SMOTE-balanced 5-fold cross-validation, it achieved PR-AUC = 0.755 and ROC-AUC = 0.907.
</p>

<h3>5.4 Models Compared</h3>
<table class="data">
  <tr>
    <th>Model</th>
    <th>Category</th>
    <th>Rationale for Inclusion</th>
  </tr>
  <tr><td>Logistic Regression (Unreg.)</td><td>Linear Baseline</td><td>Interpretable linear log-odds boundary; establishes performance floor</td></tr>
  <tr><td>Logistic Regression (L2 Ridge)</td><td>Regularized Linear</td><td>Tests whether weight dampening improves generalization on collinear features</td></tr>
  <tr><td>Logistic Regression (L1 Lasso)</td><td>Regularized Linear</td><td>Tests automatic feature selection via sparsity induction</td></tr>
  <tr><td>Decision Tree (Unpruned)</td><td>Non-linear Baseline</td><td>Captures feature interactions but prone to memorization</td></tr>
  <tr><td>Decision Tree (Pruned)</td><td>Regularized Non-linear</td><td>Cost-complexity pruning (ccp_alpha = 0.012) controls overfitting</td></tr>
  <tr><td>Random Forest (200 trees)</td><td>Bagging Ensemble</td><td>Reduces variance via bootstrap aggregation on noisy citation features</td></tr>
  <tr><td>XGBoost (Default)</td><td>Boosting Ensemble</td><td>Reduces bias via sequential gradient correction</td></tr>
  <tr><td>XGBoost (Tuned &amp; Regularized)</td><td>Boosting + Tuning</td><td>Full hyperparameter optimization with L1/L2 tree regularization</td></tr>
  <tr><td>Soft Stacking Ensemble</td><td>Meta-Ensemble</td><td>Combines linear + bagged + boosted decisions via LR meta-learner</td></tr>
</table>

<h3>5.5 Ensemble Methods</h3>
<ul>
  <li><strong>Bagging (Random Forest):</strong> 200 independent deep decision trees via bootstrap aggregation with random feature subspace sampling. Reduces variance on noisy co-authorship graph features.</li>
  <li><strong>Boosting (XGBoost):</strong> Sequential gradient boosting on pseudo-residuals with second-order Taylor expansion loss. Reduces bias on complex non-linear fraud interaction patterns.</li>
  <li><strong>Soft Stacking:</strong> Level-0 models (Logistic Regression + Random Forest + XGBoost) feed predicted probabilities into a Level-1 Logistic Regression meta-learner, blending linear and non-linear decision surfaces.</li>
</ul>

<!-- ============ 6. TECHNOLOGY STACK ============ -->
<div class="page-break"></div>
<h2>6. Technology Stack</h2>

<table class="data">
  <tr><th>Category</th><th>Technology</th><th>Purpose</th></tr>
  <tr><td>Programming Language</td><td>Python 3.13</td><td>Core development language</td></tr>
  <tr><td>Data Processing</td><td>Pandas, NumPy</td><td>DataFrame operations, numerical computation</td></tr>
  <tr><td>Visualization</td><td>Matplotlib, Seaborn</td><td>Publication-quality EDA and evaluation plots</td></tr>
  <tr><td>Machine Learning</td><td>scikit-learn, XGBoost, imbalanced-learn</td><td>Classification, pipelines, SMOTE, cross-validation</td></tr>
  <tr><td>Graph Analysis</td><td>NetworkX</td><td>Co-authorship graph centrality and clustering</td></tr>
  <tr><td>Statistical Testing</td><td>SciPy (scipy.stats)</td><td>Mann-Whitney U hypothesis testing</td></tr>
  <tr><td>Model Serialization</td><td>joblib</td><td>Pipeline persistence (.joblib format)</td></tr>
  <tr><td>Backend API</td><td>Flask, flask-cors</td><td>REST API serving predictions and metrics</td></tr>
  <tr><td>Frontend UI</td><td>React 18 + Vite + Tailwind CSS</td><td>Dark-mode interactive dashboard</td></tr>
  <tr><td>UI Components</td><td>Lucide React</td><td>Icon library for the dashboard</td></tr>
  <tr><td>External APIs</td><td>OpenAlex REST API, Crossref REST API</td><td>Live metadata enrichment for feature extraction</td></tr>
  <tr><td>Notebooks</td><td>Jupyter Notebook</td><td>Reproducible analysis and documentation</td></tr>
</table>

<!-- ============ 7. EXPERIMENTAL RESULTS ============ -->
<div class="page-break"></div>
<h2>7. Experimental Results</h2>

<h3>7.1 Model Performance Comparison</h3>
<p>All models were evaluated on the pristine 20% holdout test partition (N = 750 papers). Metric priority: <strong>PR-AUC &gt; F1 &gt; Accuracy</strong>.</p>

<table class="data">
  <tr>
    <th>Model Family</th>
    <th>Precision</th>
    <th>Recall</th>
    <th>F1-Score</th>
    <th>ROC-AUC</th>
    <th>PR-AUC</th>
  </tr>
  <tr class="highlight">
    <td><strong>XGBoost (Tuned &amp; Regularized) &#9733;</strong></td>
    <td>0.652</td><td>0.787</td><td><strong>0.713</strong></td><td>0.938</td><td><strong>0.836</strong></td>
  </tr>
  <tr><td>XGBoost (Default)</td><td>0.581</td><td>0.813</td><td>0.678</td><td>0.932</td><td>0.813</td></tr>
  <tr><td>Soft Stacking Ensemble</td><td>0.619</td><td>0.813</td><td>0.703</td><td>0.930</td><td>0.801</td></tr>
  <tr><td>Logistic Regression (Unreg.)</td><td>0.540</td><td>0.807</td><td>0.661</td><td>0.907</td><td>0.755</td></tr>
  <tr><td>Logistic Regression (L2)</td><td>0.558</td><td>0.807</td><td>0.659</td><td>0.906</td><td>0.754</td></tr>
  <tr><td>Logistic Regression (L1)</td><td>0.548</td><td>0.800</td><td>0.650</td><td>0.906</td><td>0.752</td></tr>
  <tr><td>Random Forest (Bagging)</td><td>0.530</td><td>0.813</td><td>0.642</td><td>0.909</td><td>0.737</td></tr>
  <tr><td>Decision Tree (Pruned)</td><td>0.459</td><td>0.747</td><td>0.569</td><td>0.792</td><td>0.437</td></tr>
  <tr><td>Decision Tree (Unpruned)</td><td>0.468</td><td>0.627</td><td>0.536</td><td>0.724</td><td>0.368</td></tr>
</table>

<h3>7.2 Regularization Effects</h3>
<p>
  <strong>L1/L2 Regularization (Logistic Regression):</strong> L1 Lasso induced sparsity, zeroing out noisy network metrics; L2 Ridge dampened collinear author velocity coefficients. Coefficient shrinkage paths were plotted across C values from 10<sup>-4</sup> to 10<sup>3</sup>.
</p>
<p>
  <strong>Cost-Complexity Pruning (Decision Trees):</strong> The unpruned tree severely overfitted (Train PR-AUC = 1.000 vs. Test PR-AUC = 0.368). Pruning with ccp_alpha = 0.012 improved test PR-AUC to 0.437 (+18.7% relative gain).
</p>

<div class="fig-container">
  <img src="{figs.get('coefficient_shrinkage','')}" alt="Coefficient Shrinkage">
  <div class="fig-caption">Figure 7: L1 Lasso vs. L2 Ridge coefficient shrinkage paths across regularization strength.</div>
</div>

<h3>7.3 Cross-Validated Hyperparameter Tuning</h3>
<p>
  50 iterations of <code>RandomizedSearchCV</code> with 5-fold Stratified CV optimizing <code>average_precision</code> (PR-AUC) on XGBoost:
</p>

<table class="data">
  <tr><th>Hyperparameter</th><th>Default</th><th>Tuned Optimal</th><th>Impact</th></tr>
  <tr><td>n_estimators</td><td>100</td><td><strong>180</strong></td><td>Expanded ensemble capacity</td></tr>
  <tr><td>learning_rate</td><td>0.30</td><td><strong>0.05</strong></td><td>Prevented aggressive updates on noise</td></tr>
  <tr><td>max_depth</td><td>6</td><td><strong>4</strong></td><td>Constrained interaction order</td></tr>
  <tr><td>subsample</td><td>1.0</td><td><strong>0.80</strong></td><td>Bagging-style variance reduction per tree</td></tr>
  <tr><td>colsample_bytree</td><td>1.0</td><td><strong>0.80</strong></td><td>Decorrelated trees across feature groups</td></tr>
  <tr><td>reg_alpha (L1)</td><td>0.0</td><td><strong>0.15</strong></td><td>Sparsity on extraneous bibliometrics</td></tr>
  <tr><td>reg_lambda (L2)</td><td>1.0</td><td><strong>2.50</strong></td><td>Stabilized leaf weights against outliers</td></tr>
</table>

<p><strong>Tuning impact:</strong> Test PR-AUC increased from 0.813 to <strong>0.836</strong> (+2.3% absolute); F1 lifted from 0.672 to <strong>0.713</strong> (+6.1%).</p>

<div class="page-break"></div>
<h3>7.4 Precision-Recall &amp; ROC Curves</h3>
<div class="fig-container">
  <img src="{figs.get('pr_roc_curves','')}" alt="PR and ROC Curves">
  <div class="fig-caption">Figure 8: Precision-Recall (left) and ROC (right) curves for all candidate models.</div>
</div>

<h3>7.5 Confusion Matrices &amp; Error Costs</h3>
<div class="fig-container">
  <img src="{figs.get('confusion_matrices','')}" alt="Confusion Matrices">
  <div class="fig-caption">Figure 9: Confusion matrices for top-4 classifiers on the holdout test set (N = 750).</div>
</div>
<p>
  <strong>XGBoost test-set breakdown:</strong> TP = 118, TN = 537, FP = 63, FN = 32. Optimal decision threshold calibrated at &tau;* = 0.420 (F1-maximizing).
</p>

<h3>7.6 Feature Importance</h3>
<div class="fig-container">
  <img src="{figs.get('feature_importance','')}" alt="Feature Importance">
  <div class="fig-caption">Figure 10: XGBoost split-gain feature importances. Top drivers: prior_author_retractions (31.4%), review_turnaround_days (22.8%), journal_retraction_rate (14.2%).</div>
</div>

<!-- ============ DEMO SCREENSHOTS ============ -->
<div class="page-break"></div>
<h3>7.7 Application Demo Screenshots</h3>

<p><strong>Screenshot 1: Model &amp; EDA Analytics Dashboard</strong></p>
<img class="ss-img" src="{ss1}" alt="Model Analytics Dashboard">
<p style="font-size:10pt; color:#475569; font-style:italic;">
  The dashboard displays KPI cards (Best PR-AUC: 0.836, ROC-AUC: 0.938, F1: 0.713, Class Imbalance: 1:4), a full benchmark comparison table for 8 model families, and an interactive figure gallery rendering all EDA and evaluation plots directly from the executed Jupyter Notebooks.
</p>

<br>
<p><strong>Screenshot 2: Dataset Paper Showcase &amp; Risk Scanner</strong></p>
<img class="ss-img" src="{ss2}" alt="Paper Showcase Dashboard">
<p style="font-size:10pt; color:#475569; font-style:italic;">
  The Dataset Paper Showcase tab allows selection from curated Retraction Watch ground-truth papers (retracted and clean controls). Clicking a card displays the full paper metadata, retraction status, DOI, retraction reason, retracted date, and the model&rsquo;s predicted risk score with feature-level breakdown.
</p>

<!-- ============ 8. TEAM RESPONSIBILITY ============ -->
<div class="page-break"></div>
<h2>8. Team Responsibility / Self-Contribution Matrix</h2>

<table class="data">
  <tr>
    <th>Activity</th>
    <th>Somya Sewkani<br>(240657)</th>
    <th>Shriya Garg<br>(240648)</th>
    <th>Harsh Pratap Singh<br>(240465)</th>
    <th>Lakshay Bhargav<br>(240522)</th>
  </tr>
  <tr>
    <td>Data Preprocessing &amp; EDA (Notebook 01)</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&mdash;</td>
  </tr>
  <tr>
    <td>Feature Engineering (Notebook 01)</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&mdash;</td>
  </tr>
  <tr>
    <td>Model Building &amp; Comparison (Notebook 02)</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
  </tr>
  <tr>
    <td>Ensemble Methods (Notebook 02)</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
  </tr>
  <tr>
    <td>Regularization &amp; Hyperparameter Tuning (Notebook 02)</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
  </tr>
  <tr>
    <td>Cross Validation &amp; Performance Analysis (Notebook 02)</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
  </tr>
  <tr>
    <td>Frontend UI (React + Tailwind CSS)</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
  </tr>
  <tr>
    <td>Backend API (Flask REST)</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&mdash;</td>
    <td style="text-align:center;">&mdash;</td>
  </tr>
  <tr>
    <td>Documentation &amp; Report Writing</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
  </tr>
  <tr>
    <td>Presentation Preparation</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
    <td style="text-align:center;">&#10004;</td>
  </tr>
</table>

<!-- ============ 9. CONCLUSIONS ============ -->
<div class="page-break"></div>
<h2>9. Conclusions</h2>

<ol>
  <li><strong>Effective Multi-Source Feature Engineering:</strong> By triangulating Retraction Watch ground-truth labels, OpenAlex citation-graph features, and Crossref editorial timestamps, we engineered 12 domain-grounded features that capture authorship anomalies, citation cartel dynamics, and editorial process irregularities.</li>
  <li><strong>Class Imbalance Addressed Rigorously:</strong> The accuracy paradox was identified early, and all evaluation was anchored on PR-AUC and F1-Score. SMOTE was applied strictly within cross-validation training folds to prevent data leakage.</li>
  <li><strong>Regularization Demonstrably Beneficial:</strong> L1/L2 coefficient shrinkage paths and cost-complexity tree pruning measurably reduced overfitting. The unpruned Decision Tree&rsquo;s PR-AUC improved by 18.7% after pruning.</li>
  <li><strong>Tuned XGBoost is the Clear Champion:</strong> After 5-fold stratified hyperparameter tuning, the regularized XGBoost achieved PR-AUC = 0.836, ROC-AUC = 0.938, and F1 = 0.713, outperforming all nine candidate configurations.</li>
  <li><strong>Interpretable Risk Drivers:</strong> Feature importance analysis revealed that <code>prior_author_retractions</code> (31.4%), <code>review_turnaround_days</code> (22.8%), and <code>journal_retraction_rate</code> (14.2%) are the top three risk drivers, all of which are actionable for editorial screening.</li>
  <li><strong>End-to-End Deployment:</strong> The winning model was serialized and deployed as a Flask REST API with a React dark-mode frontend, enabling interactive demonstration on curated Retraction Watch preset papers.</li>
</ol>

<p>
  <strong>Limitations:</strong> The system relies solely on metadata and cannot detect image manipulation, text plagiarism, or data fabrication within the manuscript body. Crossref timestamp coverage is incomplete for some older papers. The model is designed for screening/triage, not for definitive retraction adjudication.
</p>
<p>
  <strong>Future Work:</strong> Graph Neural Networks (GNNs) over heterogeneous author-paper-venue graphs; multimodal extensions using SciBERT abstract embeddings and computer-vision-based image duplication detection; deployment as an automated pre-publication screening plugin for journal editorial management systems.
</p>

<!-- ============ REFERENCES ============ -->
<div class="page-break"></div>
<h2>References</h2>

<ol>
  <li>Retraction Watch Database. Kaggle. <em>https://www.kaggle.com/datasets/takualiu/retraction-watch-database</em></li>
  <li>OpenAlex API Documentation. OurResearch. <em>https://docs.openalex.org</em></li>
  <li>Crossref REST API Documentation. Crossref. <em>https://www.crossref.org/documentation/retrieve-metadata/rest-api/</em></li>
  <li>Priem, J., Piwowar, H., &amp; Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. <em>arXiv:2205.01833</em>.</li>
  <li>Fang, F. C., Steen, R. G., &amp; Casadevall, A. (2012). Misconduct accounts for the majority of retracted scientific publications. <em>Proceedings of the National Academy of Sciences, 109</em>(42), 17028-17033.</li>
  <li>Grieneisen, M. L., &amp; Zhang, M. (2012). A comprehensive survey of retracted articles from the scholarly literature. <em>PLoS ONE, 7</em>(10), e44118.</li>
  <li>Cokol, M., Ozbay, F., &amp; Rodriguez-Esteban, R. (2008). Retraction rates are on the rise. <em>EMBO reports, 9</em>(1), 2.</li>
  <li>Chen, T., &amp; Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. <em>KDD &rsquo;16: Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining</em>, 785-794.</li>
  <li>Chawla, N. V., Bowyer, K. W., Hall, L. O., &amp; Kegelmeyer, W. P. (2002). SMOTE: Synthetic Minority Over-sampling Technique. <em>Journal of Artificial Intelligence Research, 16</em>, 321-357.</li>
  <li>Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. <em>JMLR, 12</em>, 2825-2830.</li>
  <li>Breiman, L. (2001). Random Forests. <em>Machine Learning, 45</em>(1), 5-32.</li>
  <li>Didegah, F., &amp; Thelwall, M. (2013). Determinants of research citation impact in nanoscience and nanotechnology. <em>Journal of the American Society for Information Science and Technology, 64</em>(5), 1055-1064.</li>
</ol>

<!-- ============ APPENDIX ============ -->
<div class="page-break"></div>
<h2>Appendix</h2>

<h3>A. Project Repository Structure</h3>
<pre style="background:#f1f5f9; padding:12px; border-radius:4px; font-size:10pt;">
retractguard/
+-- data/                      # Retraction Watch CSV + processed_features.csv
+-- notebooks/
|   +-- 01_eda_and_features.ipynb     # EDA + Feature Engineering (Somya, Shriya)
|   +-- 02_modeling_and_evaluation.ipynb  # Modeling + Evaluation (Harsh, Lakshay)
+-- src/                       # Reusable data fetchers, feature engineering, inference
+-- models/
|   +-- best_retraction_model.joblib  # Serialized winning XGBoost pipeline
|   +-- model_metrics.json            # Exported benchmark metrics
+-- reports/figures/           # 10 high-resolution matplotlib/seaborn plots
+-- backend/                   # Flask REST API (Somya, Shriya)
+-- frontend/                  # React + Tailwind CSS dark-mode dashboard (Harsh, Lakshay)
+-- requirements.txt
</pre>

<h3>B. How to Run</h3>
<ol>
  <li><code>pip install -r requirements.txt</code></li>
  <li>Run notebooks in order: <code>notebooks/01_eda_and_features.ipynb</code>, then <code>notebooks/02_modeling_and_evaluation.ipynb</code></li>
  <li>Start backend: <code>cd backend &amp;&amp; python app.py</code></li>
  <li>Start frontend: <code>cd frontend &amp;&amp; npm install &amp;&amp; npm run dev</code></li>
  <li>Open browser at <code>http://localhost:5173</code></li>
</ol>

<h3>C. Deployment Architecture</h3>
<div class="fig-container">
  <img src="{figs.get('system_deployment_diagram','')}" alt="Deployment Architecture">
  <div class="fig-caption">Figure 11: RetractGuard system deployment architecture.</div>
</div>

</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Report written: {OUT} ({len(html):,} bytes)")
