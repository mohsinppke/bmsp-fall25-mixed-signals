# -*- coding: utf-8 -*-
"""
Constants and Configuration Parameters

This module contains all configuration parameters and constants used
across the entire PPG-HRV analysis pipeline.
"""

# ==========================================
# SAMPLING AND SIGNAL PARAMETERS
# ==========================================
FS = 100                    # Sampling Frequency (Hz)
SEGMENT_DURATION = 120      # Segment duration in seconds
TARGET_SAMPLES = FS * SEGMENT_DURATION
CUTOFF_SAMPLE = 15000       # Cut off the signal here to remove end-noise

# ==========================================
# FILTER SETTINGS
# ==========================================
LOWCUT = 0.5                # Low cutoff frequency (Hz)
HIGHCUT = 8.0               # High cutoff frequency (Hz)
FILTER_ORDER = 4            # Butterworth filter order

# ==========================================
# PEAK DETECTION SETTINGS
# ==========================================
MIN_PEAK_DISTANCE = 0.4     # Minimum distance between peaks in seconds (~150 BPM max)
PEAK_HEIGHT_PERCENTILE = 50 # Adaptive threshold for peak detection (percentile)
PEAK_PROMINENCE = 0.3       # Minimum prominence for peak detection

# ==========================================
# HRV FREQUENCY BANDS
# ==========================================
VLF_BAND = (0.003, 0.04)    # Very Low Frequency (0.003-0.04 Hz)
LF_BAND = (0.04, 0.15)      # Low Frequency (0.04-0.15 Hz) - sympathetic + parasympathetic
HF_BAND = (0.15, 0.4)       # High Frequency (0.15-0.4 Hz) - parasympathetic (respiratory)

# ==========================================
# IBI CLEANING PARAMETERS
# ==========================================
MIN_IBI = 400               # Minimum inter-beat interval (ms) - corresponds to 150 BPM
MAX_IBI = 1500              # Maximum inter-beat interval (ms) - corresponds to 40 BPM
MAX_IBI_CHANGE = 0.2        # Maximum beat-to-beat change (20%)

# ==========================================
# STATISTICAL ANALYSIS PARAMETERS
# ==========================================
ALPHA_SIGNIFICANCE = 0.05   # Standard significance threshold
ALPHA_LF_HF = 0.05          # Significance threshold for LF/HF ratio (stricter)
BONFERRONI_CORRECTION = 3   # Number of pairwise comparisons

# ==========================================
# RESPONSIVENESS CLASSIFICATION
# ==========================================
HIGHLY_RESPONSIVE_THRESHOLD = 3    # >= 3 significant metrics
RESPONSIVE_THRESHOLD = 2           # >= 2 significant metrics
EFFECT_SIZE_LARGE = 20             # Large effect: >20% change
EFFECT_SIZE_MEDIUM = 10            # Medium effect: 10-20% change
EFFECT_SIZE_SMALL = 5              # Small effect: 5-10% change

# ==========================================
# FREQUENCY DOMAIN ANALYSIS
# ==========================================
FREQ_RESAMPLE = 4           # Resampling frequency for FFT (Hz)

# ==========================================
# ARTIFACT DETECTION
# ==========================================
ARTIFACT_THRESHOLD = 150    # Signal values above this are considered artifacts
ARTIFACT_SMOOTHING_ENABLED = True

# ==========================================
# CONDITIONS
# ==========================================
CONDITIONS = ['baseline', 'favorite_song', 'least_favorite_song']
CONDITION_LABELS = {
    'baseline': 'Baseline',
    'favorite_song': 'Favorite Song',
    'least_favorite_song': 'Least Favorite Song'
}

# ==========================================
# DATA ORGANIZATION
# ==========================================
START_ID = 0                # Start ID for subject filtering
MEASUREMENTS_PER_SUBJECT = 3  # Number of measurements per subject (baseline, fav, least_fav)

# ==========================================
# FILE PATHS (DEFAULT)
# ==========================================
DEFAULT_FILEPATH = "/content/GodaMárton_from_25_09_30_to_25_11_18.csv" # :D Change this accordingly!
OUTPUT_DIR = "./"
OUTPUT_FILENAMES = {
    'detailed': "hrv_results_5metrics_detailed.csv",
    'wide': "hrv_results_5metrics_wide.csv",
    'summary': "hrv_results_5metrics_group_summary.csv",
    'anova': "anova_results_5metrics.csv",
    'classifications': "subject_classifications.csv"
}

# ==========================================
# VISUALIZATION PARAMETERS
# ==========================================
PLOT_SHOW_SECONDS = 15      # Number of seconds to show in peak detection plots
FIGURE_DPI = 100
FIGURE_SIZE_DEFAULT = (12, 8)

# ==========================================
# COLORS FOR VISUALIZATION
# ==========================================
COLORS_CONDITION = {
    'baseline': 'gray',
    'favorite_song': 'green',
    'least_favorite_song': 'red'
}

COLORS_CLASSIFICATION = {
    'HIGHLY_RESPONSIVE': '#2ecc71',  # Green
    'RESPONSIVE': '#f39c12',          # Orange
    'NON_RESPONSIVE': '#e74c3c'       # Red
}

# ==========================================
# METRICS
# ==========================================
METRICS_5 = ['mean_hr', 'sdnn', 'rmssd', 'lf_hf_ratio', 'pulse_amplitude']
METRIC_NAMES_5 = {
    'mean_hr': 'Heart Rate',
    'sdnn': 'SDNN',
    'rmssd': 'RMSSD',
    'lf_hf_ratio': 'LF/HF Ratio',
    'pulse_amplitude': 'Pulse Amplitude'
}

METRIC_UNITS = {
    'mean_hr': 'bpm',
    'sdnn': 'ms',
    'rmssd': 'ms',
    'lf_hf_ratio': '',
    'pulse_amplitude': 'normalized'
}
