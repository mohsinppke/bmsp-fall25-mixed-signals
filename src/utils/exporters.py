# -*- coding: utf-8 -*-
"""
Export and Data Management Module

This module handles exporting analysis results to various formats (CSV, etc).
"""

import pandas as pd
import numpy as np
from ..utils.constants import (
    CONDITIONS, METRICS_5, OUTPUT_DIR, OUTPUT_FILENAMES
)


def export_results_to_csv(all_hrv_data, base_filename="hrv_results_5metrics"):
    """
    Export HRV results to three CSV files: detailed, wide, and group summary.
    
    Args:
        all_hrv_data (dict): HRV results for all subjects
        base_filename (str): Base name for output files
        
    Returns:
        tuple: (detailed_df, wide_df, summary_df)
    """
    # 1. Detailed results (one row per subject-condition)
    detailed_rows = []

    for subj_id in sorted(all_hrv_data.keys()):
        hrv_results = all_hrv_data[subj_id]

        for cond in CONDITIONS:
            hrv = hrv_results.get(cond)
            if hrv is None:
                continue

            row = {
                'subject_id': subj_id,
                'condition': cond,
                'n_beats': hrv['n_beats'],
                'mean_hr_bpm': hrv['mean_hr'],
                'sdnn_ms': hrv['sdnn'],
                'rmssd_ms': hrv['rmssd'],
                'lf_hf_ratio': hrv['lf_hf_ratio'],
                'pulse_amplitude': hrv['pulse_amplitude']
            }
            detailed_rows.append(row)

    df_detailed = pd.DataFrame(detailed_rows)
    detailed_filename = f"{base_filename}_detailed.csv"
    df_detailed.to_csv(detailed_filename, index=False)
    print(f"✓ Saved: {detailed_filename}")

    # 2. Wide format (one row per subject)
    wide_rows = []
    metrics = ['mean_hr_bpm', 'sdnn_ms', 'rmssd_ms', 'lf_hf_ratio', 'pulse_amplitude']

    for subj_id in sorted(all_hrv_data.keys()):
        row = {'subject_id': subj_id}

        for cond in CONDITIONS:
            subj_cond_data = df_detailed[(df_detailed['subject_id'] == subj_id) &
                                        (df_detailed['condition'] == cond)]
            if len(subj_cond_data) > 0:
                for metric in metrics:
                    col_name = f"{cond}_{metric}"
                    row[col_name] = subj_cond_data[metric].values[0]

        wide_rows.append(row)

    df_wide = pd.DataFrame(wide_rows)
    wide_filename = f"{base_filename}_wide.csv"
    df_wide.to_csv(wide_filename, index=False)
    print(f"✓ Saved: {wide_filename}")

    # 3. Group summary statistics
    summary_rows = []
    for cond in CONDITIONS:
        cond_data = df_detailed[df_detailed['condition'] == cond]
        row = {'condition': cond}
        for metric in metrics:
            row[f'{metric}_mean'] = cond_data[metric].mean()
            row[f'{metric}_std'] = cond_data[metric].std()
            row[f'{metric}_sem'] = cond_data[metric].std() / np.sqrt(len(cond_data))
        summary_rows.append(row)

    df_summary = pd.DataFrame(summary_rows)
    summary_filename = f"{base_filename}_group_summary.csv"
    df_summary.to_csv(summary_filename, index=False)
    print(f"✓ Saved: {summary_filename}")

    return df_detailed, df_wide, df_summary


def export_anova_results(anova_results, filename="anova_results_5metrics.csv"):
    """
    Export ANOVA results to CSV.
    
    Args:
        anova_results (list): List of ANOVA result dictionaries
        filename (str): Output filename
        
    Returns:
        pd.DataFrame: ANOVA results dataframe
    """
    df = pd.DataFrame(anova_results)
    df.to_csv(filename, index=False)
    print(f"✓ ANOVA results saved to: {filename}")
    return df


def export_subject_classifications(subject_classifications, 
                                   filename="subject_classifications.csv"):
    """
    Export subject classifications and metric results to CSV.
    
    Args:
        subject_classifications (dict): Classification results
        filename (str): Output filename
        
    Returns:
        pd.DataFrame: Classification data
    """
    rows = []

    for subj_id, result in subject_classifications.items():
        for metric, metric_data in result['metric_results'].items():
            rows.append({
                'subject_id': subj_id,
                'classification': result['classification'],
                'n_significant_metrics': result['n_significant'],
                'metric': metric,
                'baseline': metric_data['baseline'],
                'favorite': metric_data['favorite'],
                'least_favorite': metric_data['least_fav'],
                'fav_change_pct': metric_data['fav_change_pct'],
                'least_change_pct': metric_data['least_change_pct'],
                'mean_change_pct': metric_data['mean_change_pct'],
                'is_significant': metric_data['is_significant']
            })

    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    print(f"✓ Classifications saved to: {filename}")

    return df


def create_summary_table(all_hrv_data):
    """
    Create and print a summary table of HRV metrics for all subjects.
    
    Args:
        all_hrv_data (dict): HRV results for all subjects
    """
    print("\n" + "=" * 95)
    print("INDIVIDUAL SUBJECT SUMMARY TABLE - 5 METRICS")
    print("=" * 95)

    header = f"{'Subj':<5} {'Condition':<20} {'HR':>10} {'SDNN':>10} {'RMSSD':>10} {'LF/HF':>10} {'PulseAmp':>10}"
    print(header)
    print("-" * 95)

    for subj_id in sorted(all_hrv_data.keys()):
        hrv_results = all_hrv_data[subj_id]

        for cond in CONDITIONS:
            hrv = hrv_results.get(cond)
            if hrv is None:
                continue

            cond_display = {
                'baseline': 'Baseline',
                'favorite_song': 'Favorite',
                'least_favorite_song': 'Least Fav'
            }

            print(f"{subj_id:<5} {cond_display[cond]:<20} {hrv['mean_hr']:>10.2f} "
                 f"{hrv['sdnn']:>10.2f} {hrv['rmssd']:>10.2f} {hrv['lf_hf_ratio']:>10.3f} "
                 f"{hrv['pulse_amplitude']:>10.2f}")

        print()

    print("-" * 95)


def create_classification_summary_table(subject_classifications):
    """
    Create and print classification summary table.
    
    Args:
        subject_classifications (dict): Classification results
        
    Returns:
        pd.DataFrame: Summary dataframe
    """
    print("\n" + "=" * 100)
    print("SUBJECT CLASSIFICATION SUMMARY TABLE")
    print("=" * 100)

    header = f"{'Subject':<10} {'Classification':<25} {'# Sig':<10} {'Responsive Metrics':<50}"
    print(header)
    print("-" * 100)

    summary_data = []

    for subj_id in sorted(subject_classifications.keys()):
        result = subject_classifications[subj_id]
        metrics_str = ', '.join(result['significant_metrics']) \
                     if result['significant_metrics'] else 'None'

        print(f"{subj_id:<10} {result['classification']:<25} {result['n_significant']}/5{'':<6} "
             f"{metrics_str:<50}")

        summary_data.append({
            'subject_id': subj_id,
            'classification': result['classification'],
            'n_significant_metrics': result['n_significant'],
            'responsive_metrics': metrics_str
        })

    print("-" * 100)

    # Count classifications
    classifications_count = {}
    for result in subject_classifications.values():
        cls = result['classification']
        classifications_count[cls] = classifications_count.get(cls, 0) + 1

    print(f"\nClassification Distribution:")
    total = len(subject_classifications)
    for cls, count in sorted(classifications_count.items()):
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {cls}: {count} subjects ({pct:.1f}%)")

    print("=" * 100)

    return pd.DataFrame(summary_data)
