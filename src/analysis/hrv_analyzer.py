# -*- coding: utf-8 -*-
"""
HRV Analysis Module

This module performs heart rate variability (HRV) analysis on PPG signals.
Includes peak detection, IBI extraction, and metric calculation.
"""

import numpy as np
from scipy.signal import find_peaks
from scipy.interpolate import interp1d
from ..utils.constants import (
    FS, MIN_PEAK_DISTANCE, PEAK_HEIGHT_PERCENTILE, PEAK_PROMINENCE,
    MIN_IBI, MAX_IBI, MAX_IBI_CHANGE, LF_BAND, HF_BAND, FREQ_RESAMPLE,
    METRICS_5
)


def detect_peaks(signal, fs=FS, min_distance=MIN_PEAK_DISTANCE):
    """
    Detect systolic peaks in PPG signal using SciPy's find_peaks.
    
    Args:
        signal (np.ndarray): Input PPG signal
        fs (int): Sampling frequency in Hz
        min_distance (float): Minimum distance between peaks in seconds
        
    Returns:
        tuple: (peak_indices, inter_beat_intervals_ms)
               - peak_indices: numpy array of peak sample indices
               - ibi_ms: numpy array of inter-beat intervals in milliseconds
    """
    min_samples = int(min_distance * fs)
    height_thresh = np.percentile(signal, PEAK_HEIGHT_PERCENTILE)

    peaks, properties = find_peaks(
        signal,
        distance=min_samples,
        height=height_thresh,
        prominence=PEAK_PROMINENCE
    )

    # Calculate inter-beat intervals (IBI) in milliseconds
    if len(peaks) > 1:
        ibi_samples = np.diff(peaks)
        ibi_ms = (ibi_samples / fs) * 1000
    else:
        ibi_ms = np.array([])

    return peaks, ibi_ms


def clean_ibi(ibi_ms, min_ibi=MIN_IBI, max_ibi=MAX_IBI, max_change=MAX_IBI_CHANGE):
    """
    Remove artifacts from inter-beat interval series.
    
    Applies physiological constraints:
    - IBI range: 400-1500 ms (40-150 BPM)
    - Maximum beat-to-beat change: 20%
    
    Args:
        ibi_ms (np.ndarray): Raw inter-beat intervals in milliseconds
        min_ibi (float): Minimum physiological IBI in ms
        max_ibi (float): Maximum physiological IBI in ms
        max_change (float): Maximum allowed change between consecutive beats
        
    Returns:
        np.ndarray: Cleaned inter-beat intervals
    """
    if len(ibi_ms) < 2:
        return ibi_ms

    clean = []
    for i, ibi in enumerate(ibi_ms):
        # Check physiological limits
        if ibi < min_ibi or ibi > max_ibi:
            continue
        
        # Check beat-to-beat change
        if i > 0 and len(clean) > 0:
            change = abs(ibi - clean[-1]) / clean[-1]
            if change > max_change:
                continue
        
        clean.append(ibi)

    return np.array(clean)


def calculate_time_domain_hrv(ibi_ms):
    """
    Calculate time-domain HRV metrics.
    
    Metrics calculated:
    - mean_hr: Mean heart rate in bpm
    - sdnn: Standard deviation of normal-to-normal intervals (ms)
    - rmssd: Root mean square of successive differences (ms)
    
    Args:
        ibi_ms (np.ndarray): Clean inter-beat intervals in milliseconds
        
    Returns:
        dict: Dictionary with time-domain metrics, or None if insufficient data
    """
    if len(ibi_ms) < 2:
        return None

    diff_ibi = np.diff(ibi_ms)

    metrics = {
        'mean_hr': 60000 / np.mean(ibi_ms),      # BPM
        'mean_ibi': np.mean(ibi_ms),             # ms
        'sdnn': np.std(ibi_ms, ddof=1),          # ms
        'rmssd': np.sqrt(np.mean(diff_ibi ** 2)),  # ms
        'nn50': np.sum(np.abs(diff_ibi) > 50),     # count
        'pnn50': (np.sum(np.abs(diff_ibi) > 50) / len(diff_ibi)) * 100,  # %
        'ibi_range': np.max(ibi_ms) - np.min(ibi_ms),  # ms
        'cv': (np.std(ibi_ms) / np.mean(ibi_ms)) * 100,  # coefficient of variation %
    }

    return metrics


def calculate_frequency_domain_hrv(ibi_ms, fs_resample=FREQ_RESAMPLE):
    """
    Calculate frequency-domain HRV metrics using FFT.
    
    Metrics calculated:
    - lf_power: Low frequency power (ms²)
    - hf_power: High frequency power (ms²)
    - lf_hf_ratio: Sympathovagal balance indicator
    
    Args:
        ibi_ms (np.ndarray): Clean inter-beat intervals in milliseconds
        fs_resample (int): Resampling frequency for FFT in Hz
        
    Returns:
        dict or None: Dictionary with frequency-domain metrics and PSD data,
                     or None if insufficient data
    """
    if len(ibi_ms) < 10:
        return None

    # Create time vector for IBI series
    ibi_times = np.cumsum(ibi_ms) / 1000  # Convert to seconds
    ibi_times = ibi_times - ibi_times[0]  # Start from 0

    # Interpolate to uniform sampling
    interp_func = interp1d(ibi_times, ibi_ms, kind='cubic', fill_value='extrapolate')
    t_uniform = np.arange(0, ibi_times[-1], 1/fs_resample)
    ibi_uniform = interp_func(t_uniform)

    # Detrend (remove mean)
    ibi_uniform = ibi_uniform - np.mean(ibi_uniform)

    # Compute FFT
    n = len(ibi_uniform)
    fft_vals = np.fft.fft(ibi_uniform)
    fft_freq = np.fft.fftfreq(n, 1/fs_resample)

    # Power spectrum (one-sided)
    pos_mask = fft_freq >= 0
    freqs = fft_freq[pos_mask]
    psd = (np.abs(fft_vals[pos_mask]) ** 2) / n

    # Calculate band powers
    def band_power(freqs, psd, band):
        """Calculate power in specified frequency band."""
        mask = (freqs >= band[0]) & (freqs < band[1])
        return np.trapz(psd[mask], freqs[mask]) if np.any(mask) else 0

    lf_power = band_power(freqs, psd, LF_BAND)
    hf_power = band_power(freqs, psd, HF_BAND)

    metrics = {
        'lf_power': lf_power,      # ms²
        'hf_power': hf_power,      # ms²
        'lf_hf_ratio': lf_power / hf_power if hf_power > 0 else 0,
    }

    return metrics, freqs, psd


def calculate_pulse_amplitude(signal, peaks):
    """
    Calculate pulse amplitude metrics from PPG signal.
    
    Pulse amplitude represents the height of systolic peaks.
    
    Args:
        signal (np.ndarray): PPG signal
        peaks (np.ndarray): Indices of detected peaks
        
    Returns:
        dict or None: Dictionary with amplitude statistics, or None if no peaks
    """
    if len(peaks) == 0:
        return None

    # Extract amplitude values at peak locations
    amplitudes = signal[peaks]

    # Calculate statistics
    mean_amplitude = np.mean(amplitudes)
    std_amplitude = np.std(amplitudes, ddof=1)
    cv_amplitude = (std_amplitude / mean_amplitude * 100) if mean_amplitude > 0 else 0

    return {
        'mean_amplitude': mean_amplitude,
        'std_amplitude': std_amplitude,
        'cv_amplitude': cv_amplitude,
        'amplitudes': amplitudes
    }


def analyze_hrv(signal, fs=FS, name="Signal"):
    """
    Complete HRV analysis pipeline (5 metrics only).
    
    Performs:
    1. Peak detection
    2. IBI extraction and cleaning
    3. Time-domain HRV calculation
    4. Frequency-domain HRV calculation
    5. Pulse amplitude calculation
    
    Args:
        signal (np.ndarray): Preprocessed PPG signal
        fs (int): Sampling frequency in Hz
        name (str): Signal identifier for logging
        
    Returns:
        dict or None: HRV analysis results with 5 metrics, or None if failed
    """
    # Step 1: Detect peaks
    peaks, ibi_ms = detect_peaks(signal, fs)

    if peaks is None or len(peaks) < 10:
        print(f"  ⚠ {name}: Insufficient peaks detected ({len(peaks) if peaks is not None else 0})")
        return None

    # Step 2: Clean IBI
    ibi_clean = clean_ibi(ibi_ms)

    if len(ibi_clean) < 5:
        print(f"  ⚠ {name}: Insufficient clean IBI intervals ({len(ibi_clean)})")
        return None

    # Step 3: Time-domain metrics
    time_metrics = calculate_time_domain_hrv(ibi_clean)
    if time_metrics is None:
        return None

    # Step 4: Frequency-domain metrics
    freq_result = calculate_frequency_domain_hrv(ibi_clean)
    if freq_result is None:
        freq_metrics = {'lf_hf_ratio': np.nan}
        freqs, psd = None, None
    else:
        freq_metrics, freqs, psd = freq_result

    # Step 5: Pulse amplitude
    pulse_amp = calculate_pulse_amplitude(signal, peaks)
    mean_amplitude = pulse_amp['mean_amplitude'] if pulse_amp else np.nan

    # Compile results
    return {
        'name': name,
        'n_beats': len(ibi_clean),
        'ibi_clean': ibi_clean,
        'peaks': peaks,
        # 5 METRICS
        'mean_hr': time_metrics['mean_hr'],
        'sdnn': time_metrics['sdnn'],
        'rmssd': time_metrics['rmssd'],
        'lf_hf_ratio': freq_metrics['lf_hf_ratio'],
        'pulse_amplitude': mean_amplitude,
        # Additional data
        'pulse_amp_data': pulse_amp,
        'psd_freqs': freqs,
        'psd_power': psd
    }


def analyze_all_subjects(subjects_data, fs=FS):
    """
    Run HRV analysis on all subject groups and conditions.
    
    Args:
        subjects_data (dict): Dictionary of organized subject data
        fs (int): Sampling frequency in Hz
        
    Returns:
        dict: Dictionary with HRV results for each subject and condition
    """
    from ..utils.constants import CONDITIONS
    
    all_hrv_data = {}
    
    print(f"\n[STEP 3] Running HRV analysis on {len(subjects_data)} subjects...")

    for subj_id, subj_data in subjects_data.items():
        print(f"\n  Subject {subj_id}:")
        hrv_results = {}

        for cond in CONDITIONS:
            signal = subj_data[cond]['Signal']
            hrv = analyze_hrv(signal, fs, name=f"S{subj_id}-{cond}")
            hrv_results[cond] = hrv

            if hrv:
                print(f"    {cond:20s}: HR={hrv['mean_hr']:.1f} bpm, "
                      f"SDNN={hrv['sdnn']:.1f} ms, RMSSD={hrv['rmssd']:.1f} ms")

        all_hrv_data[subj_id] = hrv_results

    print(f"\n✓ HRV analysis complete for {len(all_hrv_data)} subjects")
    return all_hrv_data
