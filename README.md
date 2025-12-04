# BMSP Mixed Signals PPG-HRV Analysis Pipeline

## 📋 Overview

This is a comprehensive, modular Python package for analyzing **Photoplethysmography (PPG)** signals and computing **Heart Rate Variability (HRV)** metrics. The pipeline processes raw PPG signals from CSV files, extracts physiological features, and performs statistical analysis to identify how music affects cardiovascular response.

**Version:** 1.0.0  
**Author:** BMSP Lab  
**License:** MIT

---

## 🎯 Key Features

- ✅ **Modular Architecture** - Clean separation of concerns with organized packages
- ✅ **Complete HRV Pipeline** - From raw data to statistical analysis
- ✅ **5 Core Metrics** - Heart Rate, SDNN, RMSSD, LF/HF Ratio, Pulse Amplitude
- ✅ **Statistical Testing** - ANOVA, Wilcoxon tests, individual responsiveness classification
- ✅ **Rich Visualizations** - Peak detection plots, metric comparisons, classification results
- ✅ **Multi-format Export** - CSV export in detailed, wide, and summary formats
- ✅ **Subject Classification** - HIGHLY_RESPONSIVE, RESPONSIVE, NON_RESPONSIVE categories

---

## 📁 Project Structure

```
cccc/
├── main.py                          # Main entry point
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
│
└── src/                            # Source code package
    ├── __init__.py
    │
    ├── data/                       # Data loading and parsing
    │   ├── __init__.py
    │   └── loader.py              # CSV parsing, hex conversion, data organization
    │
    ├── signal_processing/         # Signal filtering and preprocessing
    │   ├── __init__.py
    │   └── processor.py           # Bandpass filter, normalization, segmentation
    │
    ├── analysis/                  # HRV analysis and statistics
    │   ├── __init__.py
    │   ├── hrv_analyzer.py        # Peak detection, IBI calculation, HRV metrics
    │   └── statistics.py          # ANOVA, statistical tests, classification
    │
    ├── visualization/            # Plotting and visualization
    │   ├── __init__.py
    │   └── visualizer.py         # All plotting functions
    │
    └── utils/                    # Utilities and configuration
        ├── __init__.py
        ├── constants.py          # Global constants and parameters
        └── exporters.py          # CSV export functions
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
cd cccc/

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage

```python
from main import run_complete_analysis

# Run the complete pipeline
all_hrv_data, anova_results, classifications = run_complete_analysis(
    filepath="path/to/your/data.csv"
)
```

### 3. Command Line Usage

```bash
# Run from the cccc directory
python main.py
```

---

## 📊 Analysis Pipeline

### Stage 1: Data Loading and Preprocessing
```
CSV File
  ↓
Parse Messy CSV (extract hex data)
  ↓
Clean Hexadecimal (remove artifacts)
  ↓
Convert to Signal Array (bytes → floats)
  ↓
Smooth Artifacts (threshold-based spike removal)
  ↓
Organize by Subject (baseline, favorite, least_favorite)
```

**Module:** `src/data/loader.py`

### Stage 2: Signal Processing
```
Raw PPG Signal
  ↓
Extract Segment (120 seconds, middle section)
  ↓
Bandpass Filter (0.5-8.0 Hz, 4th order Butterworth)
  ↓
Z-score Normalization
  ↓
Processed Signal
```

**Module:** `src/signal_processing/processor.py`

### Stage 3: HRV Analysis
```
Processed Signal
  ↓
Detect Peaks (systolic peaks in PPG)
  ↓
Extract IBI (inter-beat intervals, ms)
  ↓
Clean IBI (remove physiological outliers: 400-1500 ms)
  ↓
Calculate Metrics:
  ├─ Time Domain: HR, SDNN, RMSSD
  ├─ Frequency Domain: LF/HF Ratio (FFT-based)
  └─ Amplitude: Pulse Amplitude
```

**Module:** `src/analysis/hrv_analyzer.py`

### Stage 4: Statistical Analysis
```
HRV Metrics × 3 Conditions × N Subjects
  ↓
Group Statistics (mean, std, SEM)
  ↓
Repeated Measures ANOVA
  ↓
Post-hoc Wilcoxon Pairwise Tests
  ↓
Individual Responsiveness Classification
```

**Module:** `src/analysis/statistics.py`

---

## 📈 Metrics Explained

### 1. **Heart Rate (HR)** [bpm]
- Mean heart rate calculated from inter-beat intervals
- **Range:** 40-150 bpm (physiological)
- **Interpretation:** Basic cardiovascular activity level

### 2. **SDNN** [ms]
- Standard Deviation of Normal-to-Normal intervals
- **Physiological:** Overall HRV magnitude
- **Interpretation:** Higher SDNN = greater parasympathetic activity
- **Clinical:** Reduced in stress, anxiety, relaxation increases it

### 3. **RMSSD** [ms]
- Root Mean Square of Successive Differences
- **Physiological:** Parasympathetic (vagal) tone
- **Interpretation:** Reflects beat-to-beat variability
- **Clinical:** Vagal-mediated component, responsive to relaxation

### 4. **LF/HF Ratio** [dimensionless]
- Low Frequency (0.04-0.15 Hz) to High Frequency (0.15-0.4 Hz) power ratio
- **Physiological:** Sympathovagal balance indicator
- **Interpretation:** 
  - High ratio = sympathetic dominance (stress)
  - Low ratio = parasympathetic dominance (relaxation)
- **Clinical:** Sensitive to emotional/music stimuli

### 5. **Pulse Amplitude** [normalized]
- Mean height of systolic peaks in PPG signal
- **Physiological:** Peripheral perfusion indicator
- **Interpretation:** Related to blood vessel compliance
- **Clinical:** Changes with vascular tone, emotional state

---

## 🔧 Configuration

All parameters are centralized in `src/utils/constants.py`:

```python
# Sampling Parameters
FS = 100                    # Sampling frequency (Hz)
SEGMENT_DURATION = 120      # Analysis segment duration (seconds)

# Filter Settings
LOWCUT = 0.5               # Low cutoff frequency (Hz)
HIGHCUT = 8.0              # High cutoff frequency (Hz)
FILTER_ORDER = 4           # Butterworth filter order

# Peak Detection
MIN_PEAK_DISTANCE = 0.4    # Minimum peak distance (seconds)
PEAK_HEIGHT_PERCENTILE = 50 # Peak detection threshold

# IBI Cleaning
MIN_IBI = 400              # Minimum IBI (ms) → 150 bpm
MAX_IBI = 1500             # Maximum IBI (ms) → 40 bpm
MAX_IBI_CHANGE = 0.2       # Max beat-to-beat change (20%)

# Statistical
ALPHA_SIGNIFICANCE = 0.05  # p-value threshold
RESPONSIVE_THRESHOLD = 2   # Metrics for classification
```

To modify parameters:
1. Edit `src/utils/constants.py`
2. Re-run analysis with `python main.py`

---

## 📊 Output Files

### 1. HRV Metrics (Detailed)
**File:** `hrv_results_5metrics_detailed.csv`

```
subject_id,condition,n_beats,mean_hr_bpm,sdnn_ms,rmssd_ms,lf_hf_ratio,pulse_amplitude
1,baseline,87,72.41,45.32,32.15,1.82,0.156
1,favorite_song,89,75.23,38.12,28.44,2.15,0.142
1,least_favorite_song,86,78.15,32.45,22.33,2.89,0.128
```

### 2. HRV Metrics (Wide Format)
**File:** `hrv_results_5metrics_wide.csv`

```
subject_id,baseline_mean_hr_bpm,baseline_sdnn_ms,...,favorite_song_mean_hr_bpm,...
1,72.41,45.32,32.15,1.82,0.156,75.23,38.12,28.44,2.15,0.142,...
```

### 3. Group Statistics
**File:** `hrv_results_5metrics_group_summary.csv`

```
condition,mean_hr_bpm_mean,mean_hr_bpm_std,mean_hr_bpm_sem,...
baseline,72.15,8.32,2.15,...
favorite_song,74.82,9.45,2.44,...
least_favorite_song,76.23,10.12,2.62,...
```

### 4. ANOVA Results
**File:** `anova_results_5metrics.csv`

```
metric,threshold,n_subjects,baseline_mean,favorite_mean,...,p_value,significant
Heart Rate,0.05,10,72.15,74.82,76.23,0.0234,True
SDNN,0.1,10,45.23,38.12,32.45,0.0456,True
```

### 5. Subject Classifications
**File:** `subject_classifications.csv`

```
subject_id,classification,n_significant_metrics,metric,baseline,favorite,...
1,RESPONSIVE,2,mean_hr,72.41,75.23,78.15,3.89,-8.16,-7.91
1,RESPONSIVE,2,sdnn,45.32,38.12,32.45,-15.84,-28.38,14.89
```

---

## 📈 Usage Examples

### Example 1: Basic Analysis
```python
from main import run_complete_analysis

# Run complete pipeline
all_hrv_data, anova_results, classifications = run_complete_analysis(
    filepath="/path/to/data.csv"
)

# Access individual subject data
subject_1_hrv = all_hrv_data[1]
baseline_hr = subject_1_hrv['baseline']['mean_hr']
```

### Example 2: Custom Analysis
```python
from src.data.loader import load_and_preprocess_data
from src.signal_processing.processor import process_all_signals
from src.analysis.hrv_analyzer import analyze_all_subjects

# Step-by-step control
subjects_data = load_and_preprocess_data("data.csv")
processed = process_all_signals(subjects_data)
hrv_results = analyze_all_subjects(processed)

print(f"Analyzed {len(hrv_results)} subjects")
```

### Example 3: Statistical Analysis Only
```python
from src.analysis.statistics import perform_repeated_measures_anova

# Assuming hrv_data already loaded
anova_results = perform_repeated_measures_anova(all_hrv_data)

for result in anova_results:
    print(f"{result['metric']}: p = {result['p_value']:.4f}")
```

---

## 🔍 Subject Classification

Subjects are classified based on responsive to music stimuli:

### Classification Criteria
- **HIGHLY RESPONSIVE** (≥3 metrics with ≥10% mean change)
  - Strong physiological response to musical stimuli
  - Significant changes across multiple HRV domains
  
- **RESPONSIVE** (2 metrics with ≥10% mean change)
  - Moderate physiological response
  - Changes in select HRV metrics
  
- **NON_RESPONSIVE** (<2 metrics with ≥10% mean change)
  - Minimal physiological response
  - Stable HRV across conditions

### Effect Size Classification
- **Large Effect:** >20% change from baseline
- **Medium Effect:** 10-20% change from baseline
- **Small Effect:** 5-10% change from baseline

---

## 📚 Modular Components

### Data Module (`src/data/`)
```python
from src.data.loader import (
    load_csv_file,          # Verify CSV file
    parse_messy_csv,        # Parse hex data
    clean_hex_data,         # Clean hex strings
    hex_to_signal,          # Convert hex to array
    smooth_artifacts,       # Remove spikes
    process_raw_records,    # Complete preprocessing
    organize_by_subject,    # Group by subject
    load_and_preprocess_data # Full pipeline
)
```

### Signal Processing Module (`src/signal_processing/`)
```python
from src.signal_processing.processor import (
    bandpass_filter,        # Apply Butterworth filter
    normalize_signal,       # Z-score or minmax
    extract_segment,        # Extract duration from signal
    process_ppg_for_hrv,    # Complete preprocessing
    process_all_signals     # Batch process
)
```

### Analysis Module (`src/analysis/`)
```python
from src.analysis.hrv_analyzer import (
    detect_peaks,           # Find systolic peaks
    clean_ibi,             # Remove IBI outliers
    calculate_time_domain_hrv,    # SDNN, RMSSD
    calculate_frequency_domain_hrv, # LF/HF ratio
    calculate_pulse_amplitude,    # Peak heights
    analyze_hrv,           # Complete HRV analysis
    analyze_all_subjects   # Batch analysis
)

from src.analysis.statistics import (
    run_statistical_tests,  # ANOVA, Wilcoxon
    perform_repeated_measures_anova,  # Group tests
    classify_subject_responsiveness   # Classification
)
```

### Visualization Module (`src/visualization/`)
```python
from src.visualization.visualizer import (
    plot_peaks_detection,           # Peak detection plots
    plot_subject_5metrics_comparison, # Individual metrics
    plot_group_statistics_5metrics,   # Group stats
    plot_classification_results      # Classification overview
)
```

### Utilities (`src/utils/`)
```python
from src.utils.constants import *  # All parameters
from src.utils.exporters import (
    export_results_to_csv,          # Export HRV
    export_anova_results,           # Export ANOVA
    export_subject_classifications, # Export classifications
    create_summary_table,           # Print tables
    create_classification_summary_table
)
```

---

## 🐛 Troubleshooting

### Issue: "File not found"
```python
# Ensure filepath is correct
filepath = "/absolute/path/to/file.csv"  # Use absolute paths
```

### Issue: "Insufficient peaks detected"
- Check if signal duration is sufficient (120+ seconds)
- Verify filter parameters are appropriate
- Ensure input signal has adequate amplitude

### Issue: "No significant differences found"
- May indicate no physiological response to music
- Check if subject is truly responding to stimuli
- Verify data quality and sensor placement

### Issue: Import errors
```bash
# Ensure PYTHONPATH includes src directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python main.py
```

---

## 📋 Dependencies

```
numpy>=1.21.0           # Numerical computing
scipy>=1.7.0            # Scientific computing (signal processing)
pandas>=1.3.0           # Data manipulation
matplotlib>=3.4.0       # Plotting
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## 🔬 Scientific Background

### Photoplethysmography (PPG)
- Non-invasive optical measurement of blood perfusion
- Captures heartbeat-induced blood volume changes
- Commonly used in pulse oximeters and smartwatches

### Heart Rate Variability (HRV)
- Variation in time intervals between heartbeats
- Reflects autonomic nervous system (sympathetic/parasympathetic) balance
- Non-invasive marker of cardiovascular health and emotional state

### Sympathetic vs Parasympathetic
- **Sympathetic:** "Fight or flight" - increases HR, reduces HRV
- **Parasympathetic:** "Rest and digest" - decreases HR, increases HRV
- **Music stimulus:** Can modulate autonomic balance

---

## 📞 Support

For issues, questions, or contributions:
1. Check the troubleshooting section above
2. Review the code comments and docstrings
3. Examine the example usage in `main.py`
4. Consult scientific literature on PPG/HRV analysis

---

## 📄 Citation

If you use this pipeline in research, please cite:

```
BMSP Mixed Signals PPG-HRV Analysis Pipeline (2025)
BMSP Laboratory
```

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## ✨ Key Advantages of This Modular Design

1. **Easy to Maintain** - Changes to one module don't affect others
2. **Reusable Components** - Use individual modules in other projects
3. **Clear Documentation** - Each module has detailed docstrings
4. **Scalable** - Easy to add new analysis methods or visualizations
5. **Testable** - Individual components can be unit tested
6. **Professional Structure** - Follows Python best practices and GitHub conventions

---

**Last Updated:** December 2025  
**Status:** Production Ready ✓
