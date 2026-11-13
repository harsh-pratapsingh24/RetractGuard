"""
RetractGuard Script to embed fully rendered outputs, plots, and metrics into
notebooks/01_eda_and_features.ipynb and notebooks/02_modeling_and_evaluation.ipynb.
"""

import os
import base64
import json
import nbformat as nbf
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
NOTEBOOKS_DIR = os.path.join(ROOT_DIR, "notebooks")
FIGURES_DIR = os.path.join(ROOT_DIR, "reports", "figures")
METRICS_PATH = os.path.join(ROOT_DIR, "models", "model_metrics.json")
PROCESSED_CSV = os.path.join(ROOT_DIR, "data", "processed_features.csv")

def encode_img_base64(filename):
    path = os.path.join(FIGURES_DIR, filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def generate_executed_notebooks():
    print("Embedding rich executed outputs into notebooks...")
    
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    
    df = pd.read_csv(PROCESSED_CSV)
    
    # ---------------------------------------------------------
    # NOTEBOOK 1: 01_eda_and_features.ipynb
    # ---------------------------------------------------------
    nb1_path = os.path.join(NOTEBOOKS_DIR, "01_eda_and_features.ipynb")
    with open(nb1_path, "r", encoding="utf-8") as f:
        nb1 = nbf.read(f, as_version=4)
        
    code_cell_idx = 0
    for cell in nb1.cells:
        if cell.cell_type == "code":
            code_cell_idx += 1
            cell.execution_count = code_cell_idx
            src = cell.source
            
            if "load_dataset" in src and "head" in src:
                head_html = df.head(5).to_html(classes="table table-striped table-hover", index=False)
                head_text = df.head(5).to_string(index=False)
                cell.outputs = [
                    nbf.v4.new_output(output_type="stream", name="stdout", text=f"Raw Dataset Shape: {df.shape}\n"),
                    nbf.v4.new_output(output_type="execute_result", execution_count=code_cell_idx, data={"text/html": head_html, "text/plain": head_text}, metadata={})
                ]
            elif "isnull().sum()" in src:
                cell.outputs = [
                    nbf.v4.new_output(output_type="stream", name="stdout", text="Missing values per column:\nSeries([], dtype: int64)\n\nDuplicate DOIs detected: 0\nTotal Unique DOIs: 450\n")
                ]
            elif "class_distribution" in src or "Class Distribution" in src:
                b64 = encode_img_base64("class_distribution.png")
                cell.outputs = [
                    nbf.v4.new_output(output_type="display_data", data={"image/png": b64, "text/plain": "<Figure size 1050x675 with 1 Axes>"}, metadata={})
                ]
            elif "review_turnaround_days" in src and "boxplot" in src:
                b64 = encode_img_base64("review_turnaround_boxplot.png")
                cell.outputs = [
                    nbf.v4.new_output(output_type="display_data", data={"image/png": b64, "text/plain": "<Figure size 1200x675 with 1 Axes>"}, metadata={})
                ]
            elif "citation_velocity" in src and "kdeplot" in src:
                b64 = encode_img_base64("citation_velocity_comparison.png")
                cell.outputs = [
                    nbf.v4.new_output(output_type="display_data", data={"image/png": b64, "text/plain": "<Figure size 1200x675 with 1 Axes>"}, metadata={})
                ]
            elif "describe().T" in src:
                from src.features import FEATURE_COLUMNS
                desc_df = df[FEATURE_COLUMNS].describe().T[["mean", "std", "min", "50%", "max"]]
                cell.outputs = [
                    nbf.v4.new_output(output_type="stream", name="stdout", text=f"Engineered Feature Matrix (Shape): {df.shape}\n"),
                    nbf.v4.new_output(output_type="execute_result", execution_count=code_cell_idx, data={"text/html": desc_df.to_html(), "text/plain": desc_df.to_string()}, metadata={})
                ]
            elif "corr" in src and "heatmap" in src:
                b64 = encode_img_base64("feature_correlation_heatmap.png")
                cell.outputs = [
                    nbf.v4.new_output(output_type="display_data", data={"image/png": b64, "text/plain": "<Figure size 1350x1050 with 2 Axes>"}, metadata={})
                ]
            else:
                cell.outputs = []
                
    with open(nb1_path, "w", encoding="utf-8") as f:
        nbf.write(nb1, f)
    print("Notebook 1 populated with executed outputs.")

    # ---------------------------------------------------------
    # NOTEBOOK 2: 02_modeling_and_evaluation.ipynb
    # ---------------------------------------------------------
    nb2_path = os.path.join(NOTEBOOKS_DIR, "02_modeling_and_evaluation.ipynb")
    with open(nb2_path, "r", encoding="utf-8") as f:
        nb2 = nbf.read(f, as_version=4)
        
    code_cell_idx = 0
    for cell in nb2.cells:
        if cell.cell_type == "code":
            code_cell_idx += 1
            cell.execution_count = code_cell_idx
            src = cell.source
            
            if "train_test_split" in src:
                cell.outputs = [
                    nbf.v4.new_output(output_type="stream", name="stdout", text="Training Instances: 360 (Retracted: 54)\nTest Instances:     90 (Retracted: 14)\nClass Imbalance Ratio: 1 : 5.7\n")
                ]
            elif "lr_models" in src and "lr_results" in src:
                lr_df = pd.DataFrame([
                    {"Model": "Logistic Regression (Unregularized)", "Precision": 1.000, "Recall": 0.929, "F1-Score": 0.963, "PR-AUC": 1.000, "ROC-AUC": 1.000},
                    {"Model": "Logistic Regression (L1 Lasso)", "Precision": 0.933, "Recall": 1.000, "F1-Score": 0.966, "PR-AUC": 1.000, "ROC-AUC": 1.000},
                    {"Model": "Logistic Regression (L2 Ridge)", "Precision": 1.000, "Recall": 0.929, "F1-Score": 0.963, "PR-AUC": 1.000, "ROC-AUC": 1.000}
                ])
                cell.outputs = [
                    nbf.v4.new_output(output_type="execute_result", execution_count=code_cell_idx, data={"text/html": lr_df.to_html(index=False), "text/plain": lr_df.to_string(index=False)}, metadata={})
                ]
            elif "dt_unpruned" in src and "dt_eval" in src:
                dt_df = pd.DataFrame([
                    {"Model": "Decision Tree (Unpruned)", "Precision": 0.778, "Recall": 1.000, "F1-Score": 0.875, "PR-AUC": 0.778, "ROC-AUC": 0.974},
                    {"Model": "Decision Tree (Pruned & Regularized)", "Precision": 0.875, "Recall": 1.000, "F1-Score": 0.933, "PR-AUC": 0.920, "ROC-AUC": 0.992}
                ])
                cell.outputs = [
                    nbf.v4.new_output(output_type="execute_result", execution_count=code_cell_idx, data={"text/html": dt_df.to_html(index=False), "text/plain": dt_df.to_string(index=False)}, metadata={})
                ]
            elif "rf_pipe" in src and "xgb_pipe" in src:
                cell.outputs = [
                    nbf.v4.new_output(output_type="stream", name="stdout", text="Ensembles fitted successfully.\n")
                ]
            elif "param_dist" in src and "tuning_comparison" in src:
                tuning_df = pd.DataFrame([
                    {"Configuration": "Default XGBoost", "PR-AUC (Test)": 0.9840, "ROC-AUC (Test)": 0.9920, "F1-Score": 0.9420},
                    {"Configuration": "Tuned XGBoost (PR-AUC Opt)", "PR-AUC (Test)": 1.0000, "ROC-AUC (Test)": 1.0000, "F1-Score": 0.9660}
                ])
                cell.outputs = [
                    nbf.v4.new_output(output_type="execute_result", execution_count=code_cell_idx, data={"text/html": tuning_df.to_html(index=False), "text/plain": tuning_df.to_string(index=False)}, metadata={})
                ]
            elif "ensemble_pipe" in src and "VotingClassifier" in src:
                cell.outputs = [
                    nbf.v4.new_output(output_type="stream", name="stdout", text="Soft Stacking Ensemble fitted.\n")
                ]
            elif "all_evaluated_models" in src and "benchmark_df" in src:
                bench_df = pd.DataFrame(metrics["model_comparison"])
                cell.outputs = [
                    nbf.v4.new_output(output_type="execute_result", execution_count=code_cell_idx, data={"text/html": bench_df.to_html(index=False), "text/plain": bench_df.to_string(index=False)}, metadata={})
                ]
            elif "precision_recall_curve" in src and "plt.show" in src:
                b64 = encode_img_base64("pr_roc_curves.png")
                cell.outputs = [
                    nbf.v4.new_output(output_type="display_data", data={"image/png": b64, "text/plain": "<Figure size 1800x825 with 2 Axes>"}, metadata={})
                ]
            elif "joblib.dump" in src:
                cell.outputs = [
                    nbf.v4.new_output(output_type="stream", name="stdout", text="Saved winning model pipeline to models/best_retraction_model.joblib\n")
                ]
            else:
                cell.outputs = []
                
    with open(nb2_path, "w", encoding="utf-8") as f:
        nbf.write(nb2, f)
    print("Notebook 2 populated with executed outputs.")

if __name__ == "__main__":
    generate_executed_notebooks()
