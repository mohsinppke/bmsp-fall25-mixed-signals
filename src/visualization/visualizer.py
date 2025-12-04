# -*- coding: utf-8 -*-
"""
Visualization Module

This module handles all plotting and visualization functions for HRV analysis results.
"""

import numpy as np
import matplotlib.pyplot as plt
from ..utils.constants import (
    FS, PLOT_SHOW_SECONDS, CONDITIONS, COLORS_CONDITION,
    METRIC_NAMES_5, METRICS_5, METRIC_UNITS
)


def plot_peaks_detection(signal, peaks, ibi_ms, fs=FS, name="Signal", 
                        show_seconds=PLOT_SHOW_SECONDS):
    """
    Visualize peak detection results with signal and IBI tachogram.
    
    Args:
        signal (np.ndarray): PPG signal
        peaks (np.ndarray): Peak indices
        ibi_ms (np.ndarray): Inter-beat intervals
        fs (int): Sampling frequency
        name (str): Signal identifier
        show_seconds (float): Duration to display in seconds
    """
    samples = int(show_seconds * fs)
    time = np.arange(samples) / fs
    peaks_in_window = peaks[peaks < samples]

    fig, axes = plt.subplots(2, 1, figsize=(14, 6))
    fig.suptitle(f'Peak Detection: {name}', fontsize=12, fontweight='bold')

    # Signal with peaks
    axes[0].plot(time, signal[:samples], 'teal', linewidth=0.8, label='PPG Signal')
    axes[0].scatter(peaks_in_window / fs, signal[peaks_in_window], 
                   color='red', s=50, zorder=5, label='Detected Peaks')
    axes[0].set_ylabel('Normalized Amplitude')
    axes[0].set_xlabel('Time (s)')
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3)

    # IBI tachogram
    if len(ibi_ms) > 0:
        axes[1].plot(ibi_ms, 'o-', color='purple', markersize=4, linewidth=1)
        axes[1].axhline(np.mean(ibi_ms), color='red', linestyle='--',
                       label=f'Mean: {np.mean(ibi_ms):.0f} ms')
        axes[1].set_ylabel('IBI (ms)')
        axes[1].set_xlabel('Beat Number')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_subject_5metrics_comparison(hrv_results, subject_id):
    """
    Plot 5 metrics comparison across 3 conditions for one subject.
    
    Args:
        hrv_results (dict): HRV results for each condition
        subject_id (int): Subject identifier
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(f'Subject {subject_id} - 5 Metrics Comparison', 
                fontsize=16, fontweight='bold')

    labels = ['Baseline', 'Favorite Song', 'Least Favorite']
    colors = ['gray', 'green', 'red']

    hr_vals = [hrv_results[c]['mean_hr'] if hrv_results[c] else np.nan 
              for c in CONDITIONS]
    sdnn_vals = [hrv_results[c]['sdnn'] if hrv_results[c] else np.nan 
                for c in CONDITIONS]
    rmssd_vals = [hrv_results[c]['rmssd'] if hrv_results[c] else np.nan 
                 for c in CONDITIONS]
    lf_hf_vals = [hrv_results[c]['lf_hf_ratio'] if hrv_results[c] else np.nan 
                 for c in CONDITIONS]
    amp_vals = [hrv_results[c]['pulse_amplitude'] if hrv_results[c] else np.nan 
               for c in CONDITIONS]

    # Plot 1: Heart Rate
    axes[0, 0].bar(labels, hr_vals, color=colors, alpha=0.7, edgecolor='black')
    axes[0, 0].set_ylabel('Heart Rate (bpm)')
    axes[0, 0].set_title('Mean Heart Rate')
    axes[0, 0].grid(axis='y', alpha=0.3)

    # Plot 2: SDNN
    axes[0, 1].bar(labels, sdnn_vals, color=colors, alpha=0.7, edgecolor='black')
    axes[0, 1].set_ylabel('SDNN (ms)')
    axes[0, 1].set_title('SDNN')
    axes[0, 1].grid(axis='y', alpha=0.3)

    # Plot 3: RMSSD
    axes[0, 2].bar(labels, rmssd_vals, color=colors, alpha=0.7, edgecolor='black')
    axes[0, 2].set_ylabel('RMSSD (ms)')
    axes[0, 2].set_title('RMSSD')
    axes[0, 2].grid(axis='y', alpha=0.3)

    # Plot 4: LF/HF Ratio
    axes[1, 0].bar(labels, lf_hf_vals, color=colors, alpha=0.7, edgecolor='black')
    axes[1, 0].set_ylabel('LF/HF Ratio')
    axes[1, 0].set_title('LF/HF Ratio')
    axes[1, 0].grid(axis='y', alpha=0.3)

    # Plot 5: Pulse Amplitude
    axes[1, 1].bar(labels, amp_vals, color=colors, alpha=0.7, edgecolor='black')
    axes[1, 1].set_ylabel('Pulse Amplitude')
    axes[1, 1].set_title('Mean Pulse Amplitude')
    axes[1, 1].grid(axis='y', alpha=0.3)

    axes[1, 2].axis('off')

    plt.tight_layout()
    plt.show()


def plot_group_statistics_5metrics(all_hrv_data):
    """
    Plot group statistics for 5 metrics across conditions.
    
    Args:
        all_hrv_data (dict): HRV results for all subjects
        
    Returns:
        dict: Organized condition data for export
    """
    condition_data = {cond: {
        'mean_hr': [],
        'sdnn': [],
        'rmssd': [],
        'lf_hf_ratio': [],
        'pulse_amplitude': []
    } for cond in CONDITIONS}

    for subj_id, hrv_results in all_hrv_data.items():
        for cond in CONDITIONS:
            hrv = hrv_results.get(cond)
            if hrv is not None:
                condition_data[cond]['mean_hr'].append(hrv['mean_hr'])
                condition_data[cond]['sdnn'].append(hrv['sdnn'])
                condition_data[cond]['rmssd'].append(hrv['rmssd'])
                condition_data[cond]['lf_hf_ratio'].append(hrv['lf_hf_ratio'])
                condition_data[cond]['pulse_amplitude'].append(hrv['pulse_amplitude'])

    # Plot
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Group Statistics - 5 Metrics (Mean ± SEM)', 
                fontsize=16, fontweight='bold')

    metrics = METRICS_5
    metric_labels = [METRIC_NAMES_5[m] for m in metrics]
    titles = ['Mean Heart Rate', 'SDNN', 'RMSSD', 'LF/HF Ratio', 'Mean Pulse Amplitude']

    colors = ['gray', 'green', 'red']
    labels = ['Baseline', 'Favorite', 'Least Fav']

    for idx, (metric, ylabel, title) in enumerate(zip(metrics, metric_labels, titles)):
        row = idx // 3
        col = idx % 3

        means = [np.mean(condition_data[cond][metric]) for cond in CONDITIONS]
        sems = [np.std(condition_data[cond][metric]) / 
               np.sqrt(len(condition_data[cond][metric]))
               for cond in CONDITIONS]

        axes[row, col].bar(labels, means, yerr=sems, color=colors, alpha=0.7,
                          edgecolor='black', capsize=5, error_kw={'linewidth': 2})
        axes[row, col].set_ylabel(ylabel)
        axes[row, col].set_title(title)
        axes[row, col].grid(axis='y', alpha=0.3)

        # Print statistics
        print(f"\n{title}:")
        for cond, label in zip(CONDITIONS, labels):
            data = condition_data[cond][metric]
            print(f"  {label:12s}: {np.mean(data):7.2f} ± "
                 f"{np.std(data)/np.sqrt(len(data)):6.2f} (n={len(data)})")

    axes[1, 2].axis('off')

    plt.tight_layout()
    plt.show()

    return condition_data


def plot_classification_results(subject_classifications):
    """
    Plot subject classification distribution and metrics responsiveness.
    
    Args:
        subject_classifications (dict): Classification results for each subject
    """
    # Figure 1: Classification Distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Subject Responsiveness Classification Overview', 
                fontsize=16, fontweight='bold')

    classifications = [result['classification'] 
                      for result in subject_classifications.values()]
    classification_counts = pd.Series(classifications).value_counts()

    colors_map = {
        'HIGHLY RESPONSIVE': '#2ecc71',
        'RESPONSIVE': '#f39c12',
        'NON_RESPONSIVE': '#e74c3c'
    }
    colors = [colors_map.get(cls, '#95a5a6') for cls in classification_counts.index]

    ax1.pie(classification_counts.values, labels=classification_counts.index,
            autopct='%1.1f%%', startangle=90, colors=colors, 
            textprops={'fontsize': 12})
    ax1.set_title('Distribution of Classifications', fontsize=14, fontweight='bold')

    # Bar chart
    sig_counts = [result['n_significant'] 
                 for result in subject_classifications.values()]
    subjects_ids = list(subject_classifications.keys())

    bar_colors = [colors_map.get(subject_classifications[sid]['classification'], '#95a5a6')
                  for sid in subjects_ids]

    ax2.bar(range(len(sig_counts)), sig_counts, color=bar_colors, 
           edgecolor='black', linewidth=1.5)
    ax2.axhline(y=2, color='red', linestyle='--', linewidth=2, 
               label='Responsive Threshold (≥2)')
    ax2.set_xlabel('Subject ID', fontsize=12)
    ax2.set_ylabel('Number of Significant Metrics (out of 5)', fontsize=12)
    ax2.set_title('Significant Metrics per Subject', fontsize=14, fontweight='bold')
    ax2.set_xticks(range(len(subjects_ids)))
    ax2.set_xticklabels(subjects_ids, rotation=0)
    ax2.set_ylim(0, 5.5)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.show()
