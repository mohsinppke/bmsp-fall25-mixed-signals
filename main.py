# -*- coding: utf-8 -*-
"""
Main Entry Point for BMSP Mixed Signals PPG-HRV Analysis

This script orchestrates the complete analysis pipeline:
1. Load and preprocess data
2. Extract signals and organize by subject
3. Perform HRV analysis
4. Generate visualizations
5. Run statistical tests
6. Export results
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

from src.utils.constants import (
    DEFAULT_FILEPATH, CONDITIONS, ALPHA_SIGNIFICANCE
)
from src.data.loader import load_and_preprocess_data
from src.signal_processing.processor import process_all_signals
from src.analysis.hrv_analyzer import analyze_all_subjects
from src.analysis.statistics import (
    run_statistical_tests, perform_repeated_measures_anova,
    classify_subject_responsiveness
)
from src.visualization.visualizer import (
    plot_peaks_detection, plot_subject_5metrics_comparison,
    plot_group_statistics_5metrics, plot_classification_results
)
from src.utils.exporters import (
    export_results_to_csv, export_anova_results,
    export_subject_classifications, create_summary_table,
    create_classification_summary_table
)


def run_complete_analysis(filepath=DEFAULT_FILEPATH):
    """
    Run complete PPG-HRV analysis pipeline.
    
    Args:
        filepath (str): Path to input CSV file
    """
    
    print("\n" + "=" * 80)
    print("COMPLETE PPG-HRV ANALYSIS PIPELINE")
    print("=" * 80)
    print(f"Input file: {filepath}\n")

    # ========== STEP 1: Load and preprocess data ==========
    subjects_data = load_and_preprocess_data(filepath)
    
    if subjects_data is None:
        print("✗ Failed to load data. Exiting.")
        return
    
    # ========== STEP 2: Signal processing ==========
    print("\n[STEP 2] Processing signals through filter pipeline...")
    # Create list of all signal records
    all_records = []
    for subj_id, subj_data in subjects_data.items():
        for cond in CONDITIONS:
            all_records.append(subj_data[cond])
    
    processed_ppg_records = process_all_signals(all_records)
    
    # Reorganize by subject
    proc_subjects_data = {}
    idx = 0
    for subj_id in sorted(subjects_data.keys()):
        proc_subjects_data[subj_id] = {}
        for cond in CONDITIONS:
            if idx < len(processed_ppg_records):
                proc_subjects_data[subj_id][cond] = processed_ppg_records[idx]
                idx += 1
    
    # ========== STEP 3: HRV Analysis ==========
    all_hrv_data = analyze_all_subjects(proc_subjects_data)
    
    # ========== STEP 4: Visualizations ==========
    print("\n[STEP 4] Generating visualizations...")
    
    if 1 in all_hrv_data and all_hrv_data[1].get('baseline') is not None:
        first_subj = proc_subjects_data[1]
        signal = first_subj['baseline']['Signal']
        from src.analysis.hrv_analyzer import detect_peaks
        peaks, ibi = detect_peaks(signal)
        plot_peaks_detection(signal, peaks, ibi, name="Subject 1 - Baseline")
    
    # Show comparisons for first 2 subjects
    for subj_id in [1, 2]:
        if subj_id in all_hrv_data:
            plot_subject_5metrics_comparison(all_hrv_data[subj_id], subj_id)
    
    # ========== STEP 5: Group statistics ==========
    print("\n[STEP 5] Computing group statistics...")
    condition_data = plot_group_statistics_5metrics(all_hrv_data)
    
    # ========== STEP 6: Statistical tests ==========
    stats_results = run_statistical_tests(condition_data)
    
    # ========== STEP 7: Summary table ==========
    print("\n[STEP 7] Creating summary tables...")
    create_summary_table(all_hrv_data)
    
    # ========== STEP 8: ANOVA analysis ==========
    print("\n[STEP 8] Running ANOVA analysis...")
    anova_results = perform_repeated_measures_anova(all_hrv_data)
    
    # ========== STEP 9: Subject classification ==========
    print("\n[STEP 9] Classifying subjects...")
    subject_classifications = classify_subject_responsiveness(all_hrv_data, 
                                                             alpha=ALPHA_SIGNIFICANCE)
    classification_summary = create_classification_summary_table(subject_classifications)
    
    # ========== STEP 10: Visualize classifications ==========
    print("\n[STEP 10] Visualizing classifications...")
    plot_classification_results(subject_classifications)
    
    # ========== STEP 11: Export results ==========
    print("\n[STEP 11] Exporting results...")
    
    print("\nExporting HRV metrics to CSV...")
    export_results_to_csv(all_hrv_data)
    
    print("\nExporting ANOVA results...")
    export_anova_results(anova_results)
    
    print("\nExporting subject classifications...")
    export_subject_classifications(subject_classifications)
    
    # ========== COMPLETION ==========
    print("\n" + "=" * 80)
    print("✓ ANALYSIS COMPLETE!")
    print("=" * 80)
    print("\nGenerated Files:")
    print("  • hrv_results_5metrics_detailed.csv - All 5 metrics, one row per subject-condition")
    print("  • hrv_results_5metrics_wide.csv - One row per subject, conditions as columns")
    print("  • hrv_results_5metrics_group_summary.csv - Group means, SDs, and SEMs")
    print("  • anova_results_5metrics.csv - Statistical ANOVA results")
    print("  • subject_classifications.csv - Individual subject classifications")
    print("\nMetrics Analyzed:")
    print("  1. Heart Rate (bpm)")
    print("  2. SDNN (ms) - Standard deviation of inter-beat intervals")
    print("  3. RMSSD (ms) - Root mean square of successive differences")
    print("  4. LF/HF Ratio - Sympathovagal balance")
    print("  5. Pulse Amplitude - Signal peak heights")
    print("=" * 80 + "\n")
    
    return all_hrv_data, anova_results, subject_classifications


if __name__ == "__main__":
    # Run the complete analysis
    run_complete_analysis(DEFAULT_FILEPATH)
