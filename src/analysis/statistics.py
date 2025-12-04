# -*- coding: utf-8 -*-
"""
Statistical Analysis Module

This module performs statistical testing and subject classification.
Includes ANOVA, pairwise comparisons, and responsiveness classification.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import f_oneway, wilcoxon, friedmanchisquare
from ..utils.constants import (
    CONDITIONS, METRICS_5, METRIC_NAMES_5, METRIC_UNITS,
    ALPHA_SIGNIFICANCE, EFFECT_SIZE_LARGE, EFFECT_SIZE_MEDIUM,
    EFFECT_SIZE_SMALL, HIGHLY_RESPONSIVE_THRESHOLD, RESPONSIVE_THRESHOLD
)


def run_statistical_tests(condition_data):
    """
    Run Friedman ANOVA and Wilcoxon pairwise tests on HRV metrics.
    
    Args:
        condition_data (dict): Dictionary with condition data for each metric
        
    Returns:
        dict: Statistical test results
    """
    print("\n" + "=" * 70)
    print("STATISTICAL ANALYSIS - GROUP LEVEL")
    print("=" * 70)

    metrics = METRICS_5
    results = {}

    for metric in metrics:
        metric_name = METRIC_NAMES_5[metric]
        print(f"\n{metric_name}:")
        print("-" * 50)

        baseline = np.array(condition_data['baseline'][metric])
        favorite = np.array(condition_data['favorite_song'][metric])
        least_fav = np.array(condition_data['least_favorite_song'][metric])

        # Need matched samples
        n = min(len(baseline), len(favorite), len(least_fav))
        if n < 3:
            print("  Insufficient data for statistical tests")
            continue

        baseline = baseline[:n]
        favorite = favorite[:n]
        least_fav = least_fav[:n]

        # Descriptive statistics
        print(f"  Baseline:     {np.mean(baseline):8.2f} ± {np.std(baseline):.2f}")
        print(f"  Favorite:     {np.mean(favorite):8.2f} ± {np.std(favorite):.2f}")
        print(f"  Least Fav:    {np.mean(least_fav):8.2f} ± {np.std(least_fav):.2f}")

        # Friedman test
        try:
            stat, p_friedman = friedmanchisquare(baseline, favorite, least_fav)
            sig = "*" if p_friedman < ALPHA_SIGNIFICANCE else ""
            print(f"\n  Friedman test: χ² = {stat:.3f}, p = {p_friedman:.4f} {sig}")
        except Exception as e:
            print(f"  Friedman test: Error - {e}")
            p_friedman = None

        # Pairwise Wilcoxon tests
        print("\n  Pairwise comparisons (Wilcoxon):")
        pairs = [
            ('Baseline vs Favorite', baseline, favorite),
            ('Baseline vs Least Fav', baseline, least_fav),
            ('Favorite vs Least Fav', favorite, least_fav)
        ]

        for pair_name, g1, g2 in pairs:
            try:
                stat, p = wilcoxon(g1, g2)
                sig = "*" if p < ALPHA_SIGNIFICANCE else ""
                print(f"    {pair_name}: p = {p:.4f} {sig}")
            except Exception as e:
                print(f"    {pair_name}: Error - {e}")

        results[metric] = {
            'baseline': baseline,
            'favorite': favorite,
            'least_fav': least_fav,
            'friedman_p': p_friedman
        }

    return results


def perform_repeated_measures_anova(all_hrv_data):
    """
    Perform repeated measures ANOVA for each of 5 metrics.
    
    Args:
        all_hrv_data (dict): HRV results for all subjects and conditions
        
    Returns:
        list: List of ANOVA results dictionaries
    """
    print("\n" + "=" * 80)
    print("REPEATED MEASURES ANOVA - INDIVIDUAL FEATURE ANALYSIS")
    print("=" * 80)

    thresholds = {
        'mean_hr': ALPHA_SIGNIFICANCE,
        'sdnn': 0.10,
        'rmssd': 0.10,
        'lf_hf_ratio': ALPHA_SIGNIFICANCE,
        'pulse_amplitude': ALPHA_SIGNIFICANCE
    }

    results_summary = []

    print("\n" + "-" * 80)
    print("ANOVA RESULTS BY METRIC")
    print("-" * 80)

    for metric in METRICS_5:
        metric_name = METRIC_NAMES_5[metric]
        unit = METRIC_UNITS.get(metric, '')
        threshold = thresholds[metric]

        print(f"\n{'='*60}")
        print(f"METRIC: {metric_name} {f'({unit})' if unit else ''}")
        print(f"Significance Threshold: p < {threshold}")
        print(f"{'='*60}")

        # Collect data for each condition
        baseline_data = []
        favorite_data = []
        least_fav_data = []

        for subj_id, hrv_results in all_hrv_data.items():
            if (hrv_results.get('baseline') is not None and
                hrv_results.get('favorite_song') is not None and
                hrv_results.get('least_favorite_song') is not None):

                baseline_data.append(hrv_results['baseline'][metric])
                favorite_data.append(hrv_results['favorite_song'][metric])
                least_fav_data.append(hrv_results['least_favorite_song'][metric])

        baseline_data = np.array(baseline_data)
        favorite_data = np.array(favorite_data)
        least_fav_data = np.array(least_fav_data)

        n_subjects = len(baseline_data)
        print(f"\nNumber of subjects: {n_subjects}")

        if n_subjects < 3:
            print(f"⚠ Insufficient data for ANOVA")
            continue

        # Descriptive statistics
        print(f"\nDescriptive Statistics:")
        print(f"  Baseline:       {np.mean(baseline_data):8.2f} ± {np.std(baseline_data, ddof=1):6.2f}")
        print(f"  Favorite:       {np.mean(favorite_data):8.2f} ± {np.std(favorite_data, ddof=1):6.2f}")
        print(f"  Least Favorite: {np.mean(least_fav_data):8.2f} ± {np.std(least_fav_data, ddof=1):6.2f}")

        # Percent changes
        fav_change = ((np.mean(favorite_data) - np.mean(baseline_data)) / 
                     np.mean(baseline_data)) * 100
        least_change = ((np.mean(least_fav_data) - np.mean(baseline_data)) / 
                       np.mean(baseline_data)) * 100

        print(f"\nPercent Change from Baseline:")
        print(f"  Favorite:       {fav_change:+.2f}%")
        print(f"  Least Favorite: {least_change:+.2f}%")

        # ANOVA
        f_stat, p_value = f_oneway(baseline_data, favorite_data, least_fav_data)

        print(f"\n{'*'*60}")
        print(f"ANOVA Results:")
        print(f"  F-statistic: {f_stat:.4f}")
        print(f"  p-value:     {p_value:.6f}")

        is_significant = p_value < threshold

        if is_significant:
            print(f"  Result:      SIGNIFICANT *** (p < {threshold})")
        else:
            print(f"  Result:      NOT SIGNIFICANT (p ≥ {threshold})")
        print(f"{'*'*60}")

        # Store results
        results_summary.append({
            'metric': metric_name,
            'unit': unit,
            'threshold': threshold,
            'n_subjects': n_subjects,
            'baseline_mean': np.mean(baseline_data),
            'baseline_std': np.std(baseline_data, ddof=1),
            'favorite_mean': np.mean(favorite_data),
            'favorite_std': np.std(favorite_data, ddof=1),
            'least_fav_mean': np.mean(least_fav_data),
            'least_fav_std': np.std(least_fav_data, ddof=1),
            'fav_change_pct': fav_change,
            'least_change_pct': least_change,
            'f_statistic': f_stat,
            'p_value': p_value,
            'significant': is_significant
        })

    return results_summary


def classify_subject_responsiveness(all_hrv_data, alpha=ALPHA_SIGNIFICANCE):
    """
    Classify each subject as HIGHLY_RESPONSIVE, RESPONSIVE, or NON_RESPONSIVE.
    
    Based on number of metrics showing significant effect size changes.
    
    Args:
        all_hrv_data (dict): HRV results for all subjects
        alpha (float): Significance threshold
        
    Returns:
        dict: Subject classifications with detailed metric results
    """
    print("\n" + "=" * 80)
    print("INDIVIDUAL SUBJECT RESPONSIVENESS CLASSIFICATION")
    print("=" * 80)

    subject_classifications = {}

    print("\n" + "-" * 80)
    print("CLASSIFICATION DETAILS")
    print("-" * 80)

    for subj_id in sorted(all_hrv_data.keys()):
        hrv_results = all_hrv_data[subj_id]

        # Check for complete data
        if (hrv_results.get('baseline') is None or
            hrv_results.get('favorite_song') is None or
            hrv_results.get('least_favorite_song') is None):
            continue

        print(f"\nSubject {subj_id}:")

        baseline = hrv_results['baseline']
        favorite = hrv_results['favorite_song']
        least_fav = hrv_results['least_favorite_song']

        significant_metrics = []
        metric_results = {}

        for metric in METRICS_5:
            b_val = baseline[metric]
            f_val = favorite[metric]
            l_val = least_fav[metric]

            fav_change = ((f_val - b_val) / b_val * 100) if b_val != 0 else 0
            least_change = ((l_val - b_val) / b_val * 100) if b_val != 0 else 0
            fav_vs_least_change = ((l_val - f_val) / f_val * 100) if f_val != 0 else 0

            mean_change = np.mean([abs(fav_change), abs(least_change), 
                                   abs(fav_vs_least_change)])

            is_significant = mean_change >= EFFECT_SIZE_MEDIUM
            if is_significant:
                significant_metrics.append(METRIC_NAMES_5[metric])

            metric_results[metric] = {
                'baseline': b_val,
                'favorite': f_val,
                'least_fav': l_val,
                'fav_change_pct': fav_change,
                'least_change_pct': least_change,
                'mean_change_pct': mean_change,
                'is_significant': is_significant
            }

        # Classify
        n_significant = len(significant_metrics)

        if n_significant >= HIGHLY_RESPONSIVE_THRESHOLD:
            classification = "HIGHLY RESPONSIVE"
        elif n_significant >= RESPONSIVE_THRESHOLD:
            classification = "RESPONSIVE"
        else:
            classification = "NON_RESPONSIVE"

        print(f"  Classification: {classification} ({n_significant}/5 metrics)")

        subject_classifications[subj_id] = {
            'classification': classification,
            'n_significant': n_significant,
            'significant_metrics': significant_metrics,
            'metric_results': metric_results
        }

    return subject_classifications
