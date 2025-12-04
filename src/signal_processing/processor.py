# -*- coding: utf-8 -*-
"""
Signal Processing Module

This module handles signal filtering, normalization, and segmentation
for PPG (photoplethysmography) signal analysis.
"""

import numpy as np
from scipy.signal import butter, filtfilt
from ..utils.constants import (
    FS, SEGMENT_DURATION, LOWCUT, HIGHCUT, FILTER_ORDER
)


def bandpass_filter(signal, fs=FS, lowcut=LOWCUT, highcut=HIGHCUT, order=FILTER_ORDER):
    """
    Apply Butterworth bandpass filter to signal.
    
    Args:
        signal (np.ndarray): Input signal
        fs (int): Sampling frequency in Hz
        lowcut (float): Low cutoff frequency in Hz
        highcut (float): High cutoff frequency in Hz
        order (int): Filter order
        
    Returns:
        np.ndarray: Filtered signal
    """
    nyquist = fs / 2
    low = lowcut / nyquist
    high = highcut / nyquist
    
    # Ensure normalized frequencies are valid
    low = np.clip(low, 0.001, 0.999)
    high = np.clip(high, 0.001, 0.999)
    
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)


def normalize_signal(signal, method='zscore'):
    """
    Normalize signal using specified method.
    
    Args:
        signal (np.ndarray): Input signal
        method (str): 'zscore' or 'minmax'
        
    Returns:
        np.ndarray: Normalized signal
    """
    if method == 'zscore':
        mean = np.mean(signal)
        std = np.std(signal)
        if std == 0:
            return signal - mean
        return (signal - mean) / std
    
    elif method == 'minmax':
        min_val = np.min(signal)
        max_val = np.max(signal)
        if max_val - min_val == 0:
            return signal - min_val
        return (signal - min_val) / (max_val - min_val)
    
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def extract_segment(signal, duration_sec=SEGMENT_DURATION, fs=FS, method='middle'):
    """
    Extract a segment of specified duration from the signal.
    
    Args:
        signal (np.ndarray): Input signal
        duration_sec (float): Desired segment duration in seconds
        fs (int): Sampling frequency in Hz
        method (str): 'start', 'middle', or 'end' - where to extract from
        
    Returns:
        np.ndarray or None: Extracted segment, or None if signal is too short
    """
    target_samples = int(duration_sec * fs)
    
    if len(signal) < target_samples:
        return None
    
    if method == 'middle':
        start = (len(signal) - target_samples) // 2
    elif method == 'start':
        start = 0
    elif method == 'end':
        start = len(signal) - target_samples
    else:
        raise ValueError(f"Unknown extraction method: {method}")
    
    return signal[start:start + target_samples]


def process_ppg_for_hrv(signal, fs=FS, segment_duration=SEGMENT_DURATION, method='middle'):
    """
    Complete preprocessing pipeline for PPG signal HRV analysis.
    
    Steps:
    1. Extract segment of specified duration
    2. Apply bandpass filter
    3. Normalize using z-score
    
    Args:
        signal (np.ndarray): Raw PPG signal
        fs (int): Sampling frequency in Hz
        segment_duration (float): Duration to extract in seconds
        method (str): Segment extraction method ('start', 'middle', 'end')
        
    Returns:
        tuple: (raw_segment, normalized_segment) or (None, None) if failed
    """
    # Extract segment
    segment = extract_segment(signal, segment_duration, fs, method)
    if segment is None:
        return None, None
    
    # Keep copy of raw segment
    raw_segment = segment.copy()
    
    # Filter
    filtered = bandpass_filter(segment, fs)
    
    # Normalize
    normalized = normalize_signal(filtered, method='zscore')
    
    return raw_segment, normalized


def process_all_signals(processed_records, fs=FS, segment_duration=SEGMENT_DURATION):
    """
    Process all signal records through the preprocessing pipeline.
    
    Args:
        processed_records (list): List of signal records with 'Name' and 'Signal'
        fs (int): Sampling frequency in Hz
        segment_duration (float): Segment duration in seconds
        
    Returns:
        list: List of preprocessed records with 'Name', 'Signal', and 'Raw'
    """
    processed_ppg_records = []
    
    print(f"\nProcessing {len(processed_records)} signals through filter pipeline...")

    for i, record in enumerate(processed_records):
        name = record['Name']
        raw_signal = record['Signal']
        
        raw_segment, processed_signal = process_ppg_for_hrv(
            raw_signal, fs, segment_duration
        )

        if processed_signal is not None:
            processed_ppg_records.append({
                'Name': name,
                'Signal': processed_signal,
                'Raw': raw_segment
            })
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(processed_records)} signals")

    print(f"✓ Successfully processed {len(processed_ppg_records)} signals")
    return processed_ppg_records
