# Master Prompt for Google Antigravity — RetractGuard

Build a complete, end-to-end Machine Learning web application and academic project repository for **RetractGuard**: *"Predicting Research Paper Retraction Risk Using Publication Metadata and Citation Network Features."*

---

## 1. Repository & Workspace Architecture
Scaffold the following modular directory layout cleanly:

```text
retractguard/
├── data/                  # Place Kaggle retraction_watch.csv here + processed_features.csv
├── notebooks/             # 01_eda_and_features.ipynb & 02_modeling_and_evaluation.ipynb
├── src/                   # Reusable data fetchers, feature engineering & inference modules
├── models/                # Saved best_retraction_model.joblib & model_metrics.json
├── reports/figures/       # Exported high-res matplotlib/seaborn EDA & evaluation plots
├── backend/               # Flask REST API (app.py)
├── frontend/              # React + Tailwind CSS dark-mode dashboard
├── README.md              # Project overview, setup instructions & rubric mapping
└── requirements.txt
```

---

## 2. Phase 1: Data Ingestion, EDA & Feature Derivation (`src/` & `notebooks/01_eda_and_features.ipynb`)

### A. Data Sources & Integration (`src/data_pipeline.py`)
- **Ground Truth (Retracted Papers — Label `1`):** Load `data/retraction_watch.csv` (sourced from `https://www.kaggle.com/datasets/takualiu/retraction-watch-database`). Clean and extract valid DOIs (`OriginalPaperDOI`), retraction dates, journals, and retraction reasons.
- **Control Group (Non-Retracted Papers — Label `0`):** Query the **OpenAlex API** (`https://api.openalex.org/works`) to sample non-retracted papers matched by publication year and domain/concept (maintaining an imbalanced ratio such as `1:10` to reflect real-world class skew).
- **Live/Batch Metadata Enrichment:**
  - **OpenAlex API (`https://docs.openalex.org`):** Fetch author IDs, historical author work counts, co-author lists, citation counts (`cited_by_count`), referenced works (`referenced_works`), and publication year. Include polite pool headers (`mailto: researcher@example.com`), rate limiting (`time.sleep`), exponential backoff retries, and local JSON caching so API calls are fast and resilient.
  - **Crossref REST API (`https://api.crossref.org/works/{doi}`):** Fetch submission/received dates, accepted dates, and published dates (`created`, `deposited`, `published-print`) to compute peer-review turnaround time.
- Include a configurable `SAMPLE_LIMIT = 300` flag for rapid end-to-end testing, plus a fallback bootstrap data generator if `data/retraction_watch.csv` is not yet present in `data/` so the entire pipeline and UI remain runnable out-of-the-box.

### B. Exploratory Data Analysis — Rubric Requirement 1 (`notebooks/01_eda_and_features.ipynb`)
- Analyze missingness, duplicate DOIs, class imbalance ratio, top retraction reasons, publication year trends, and journal skew.
- Generate and save high-resolution plots to `reports/figures/`:
  1. `class_distribution.png`
  2. `review_turnaround_boxplot.png`
  3. `citation_velocity_comparison.png`
  4. `feature_correlation_heatmap.png`
- Include concise markdown commentary under each plot explaining patterns, anomalies, and data quality challenges.

### C. Feature Derivation — Rubric Requirement 2 (`src/features.py` & `notebooks/01_eda_and_features.ipynb`)
Implement a shared `extract_features()` module used identically by both offline training and live Flask inference, accompanied by domain justifications in markdown:
- **Author-Level Signals:**
  - `author_count`: Total co-authors on the paper.
  - `max_author_works` & `mean_author_works`: Historical publication volume/velocity across authors.
  - `prior_author_retractions`: Count of prior retracted papers involving any co-author, **computed strictly prior to the target paper's publication date** to prevent temporal data leakage.
- **Citation & Network Signals (`networkx`):**
  - `cited_by_count`: Total citations received.
  - `citation_velocity`: `cited_by_count / max(1, years_since_publication)`.
  - `self_citation_ratio`: Share of `referenced_works` sharing at least one author with the target paper.
  - `coauthor_degree_centrality` & `coauthor_clustering_coeff`: Graph topology metrics computed over the co-authorship network.
- **Journal & Publication Metadata Signals:**
  - `review_turnaround_days`: Days elapsed between submission (`received`) and acceptance (`accepted`) from Crossref.
  - `journal_retraction_rate`: Historical baseline retraction frequency of the venue (computed strictly within training folds to prevent leakage).
- Save the resulting dataset to `data/processed_features.csv`.

---

## 3. Phase 2: Modeling, Regularization, Tuning & Evaluation (`notebooks/02_modeling_and_evaluation.ipynb`)

Build a well-documented notebook addressing all remaining academic rubric requirements:

1. **Preprocessing & Imbalance Handling:**
   - Perform a stratified 80/20 train-test split *before* any imputation, scaling, or resampling.
   - Build leakage-free pipelines using `imblearn.pipeline.Pipeline` with `SimpleImputer(strategy="median")`, `StandardScaler()`, and `SMOTE()`.
2. **Classification & Regularization — Rubric Requirements 3 & 4:**
   - **Logistic Regression:** Compare unregularized/weakly regularized (`C=1e5`) vs. **L1 (Lasso)** and **L2 (Ridge)** regularization across a grid of `C` values. Plot coefficient shrinkage and train-vs-test F1/PR-AUC gaps to justify how regularization controls overfitting.
   - **Decision Tree Classifier:** Compare an unpruned tree (`max_depth=None`) vs. a regularized tree (`max_depth`, `min_samples_leaf`, and `ccp_alpha` cost-complexity pruning).
3. **Ensemble Techniques — Rubric Requirement 6:**
   - Train **Random Forest** (Bagging) and **XGBoost** (Gradient Boosting with `reg_alpha` and `reg_lambda`).
   - Build a **Soft Voting / Stacking Ensemble** combining Regularized Logistic Regression, Random Forest, and XGBoost. Include markdown explaining how bagging reduces variance and boosting reduces bias on noisy bibliometric graphs.
4. **Hyperparameter Tuning — Rubric Requirement 5:**
   - Run `RandomizedSearchCV` with `StratifiedKFold(n_splits=5)` optimizing `average_precision` (PR-AUC) on XGBoost (`max_depth`, `learning_rate`, `n_estimators`, `subsample`, `colsample_bytree`, `reg_alpha`, `reg_lambda`). Display a before-vs-after tuning comparison table.
5. **Performance Analysis — Rubric Requirement 7:**
   - Evaluate all models on the untouched test set across **Precision, Recall, F1-Score, ROC-AUC, and PR-AUC** (with explicit justification of why PR-AUC and F1 are prioritized over raw Accuracy under severe class imbalance).
   - Export `confusion_matrices.png`, `pr_roc_curves.png`, and `feature_importance.png` to `reports/figures/`.
   - Serialize the winning pipeline to `models/best_retraction_model.joblib` and export all metrics, feature importances, and dataset summary stats to `models/model_metrics.json`.

---

## 4. Phase 3: Flask Backend (`backend/app.py`)
Create a clean, well-structured Flask server (`flask-cors` enabled) with:
- `POST /api/predict`: Accepts `{"doi": "..."}`, queries OpenAlex and Crossref live for that DOI, executes `src/features.py`, runs `models/best_retraction_model.joblib`, and returns JSON containing:
  - `doi`, `paper_title`, `authors`, `journal`, `publication_year`
  - `risk_score` (0–100%), `risk_level` (`Low`, `Moderate`, `High`)
  - `extracted_features` (grouped by Author, Citation Network, and Journal Metadata)
  - `risk_contributions` (top features driving the predicted probability)
- `GET /api/metrics`: Returns `models/model_metrics.json` and serves static visualization images from `reports/figures/`.
- `GET /api/health`: Health check endpoint.

---

## 5. Phase 4: Dark-Mode React + Tailwind Frontend (`frontend/`)
Build a sleek, modern **dark-mode** React dashboard (Vite + Tailwind CSS + Lucide React + Recharts) branded **"RetractGuard"** with two primary tabs:

1. **Single Paper Risk Scanner:**
   - Clean DOI search bar with one-click sample DOI chips (1 known retracted paper and 2 clean papers for live demo reliability).
   - Radial Risk Probability Gauge (`0–100%`) with color-coded `Low / Moderate / High Risk` badge and paper metadata header.
   - 3-column signal breakdown cards: **Author Signals**, **Citation Network Dynamics**, and **Journal & Review Metadata**.
   - Horizontal bar chart showing the top risk factors contributing to the paper's score.
2. **Model & EDA Analytics:**
   - Top KPI summary cards (Best PR-AUC, Best ROC-AUC, Best F1-Score, Class Imbalance Ratio).
   - Interactive Model Comparison Table spanning Logistic Regression (Unregularized vs. L1/L2), Regularized Decision Tree, Random Forest, Tuned XGBoost, and Stacking Ensemble.
   - Visual gallery displaying the generated EDA, Regularization, and Precision-Recall Curve plots from `reports/figures/`.

---

## 6. Execution & Verification Steps
1. Create a Python virtual environment, install `requirements.txt`, and run the data/training pipeline to verify `models/best_retraction_model.joblib`, `models/model_metrics.json`, and `reports/figures/*.png` are generated cleanly.
2. Execute both Jupyter notebooks (`jupyter nbconvert --to notebook --execute --inplace`) so all outputs and plots are saved inside the `.ipynb` files for academic submission.
3. Install frontend dependencies (`npm install`), start both the Flask backend (`localhost:5000`) and Vite frontend (`localhost:5173`), and verify end-to-end DOI prediction and analytics rendering.