# -*- coding: utf-8 -*-
"""
Data Loading and Parsing Module

This module handles CSV file parsing and data preprocessing for PPG signal data.
Includes functions for parsing messy CSV files and organizing data by subject.
"""

import numpy as np
import re
import pandas as pd
from ..utils.constants import START_ID, MEASUREMENTS_PER_SUBJECT, ARTIFACT_THRESHOLD


def load_csv_file(filepath):
    """
    Verify file can be loaded using pandas.
    
    Args:
        filepath (str): Path to CSV file
        
    Returns:
        bool: True if file loaded successfully, False otherwise
    """
    try:
        data = pd.read_csv(filepath)
        print(f"✓ File found and verified: {filepath}")
        return True
    except Exception as e:
        print(f"✗ Warning: File not found at {filepath}")
        print(f"  Error: {e}")
        return False


def parse_messy_csv(filepath):
    """
    Parse messy CSV file with hex data records.
    
    The CSV format contains records with hex data that may span multiple lines.
    Each new record starts with a line containing '0x' marker.
    
    Args:
        filepath (str): Path to CSV file
        
    Returns:
        list: List of dictionaries with 'Name' and 'Hex' keys
    """
    parsed_data = []
    current_name = None
    current_hex = ""

    # Read file content
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        file_content = f.read().splitlines()

    for line in file_content:
        line = line.strip()
        if not line:
            continue

        # Check if this is a NEW record (contains '0x')
        if '0x' in line:
            # Save the PREVIOUS record
            if current_name is not None:
                parsed_data.append({'Name': current_name, 'Hex': current_hex})

            # Start NEW record
            parts = line.split(',')
            current_name = parts[0].strip()

            # Extract Hex part
            hex_split = line.split('0x')
            if len(hex_split) > 1:
                current_hex = hex_split[1].strip()
            else:
                current_hex = ""
        else:
            # Continuation line - append to current hex
            current_hex += line

    # Save the LAST entry
    if current_name is not None:
        parsed_data.append({'Name': current_name, 'Hex': current_hex})

    print(f"✓ Successfully parsed {len(parsed_data)} records from CSV")
    return parsed_data


def clean_hex_data(raw_hex):
    """
    Clean hexadecimal string by removing non-hex characters and ensuring even length.
    
    Args:
        raw_hex (str): Raw hexadecimal string
        
    Returns:
        str: Cleaned hexadecimal string
    """
    # Remove all non-hex characters
    clean_hex = re.sub(r'[^0-9A-Fa-f]', '', raw_hex)
    
    # Ensure even length
    if len(clean_hex) % 2 != 0:
        clean_hex = clean_hex[:-1]
    
    return clean_hex


def hex_to_signal(clean_hex):
    """
    Convert hexadecimal string to numpy array signal.
    
    Args:
        clean_hex (str): Cleaned hexadecimal string
        
    Returns:
        np.ndarray or None: Signal array, or None if conversion failed
    """
    try:
        data_bytes = bytes.fromhex(clean_hex)
        signal = np.array(list(data_bytes), dtype=float)
        return signal
    except Exception as e:
        print(f"✗ Error converting hex to signal: {e}")
        return None


def smooth_artifacts(signal, threshold=ARTIFACT_THRESHOLD):
    """
    Apply artifact smoothing by replacing high-amplitude spikes with interpolated values.
    
    Args:
        signal (np.ndarray): Input signal
        threshold (float): Amplitude threshold above which values are considered artifacts
        
    Returns:
        np.ndarray: Smoothed signal
    """
    signal = signal.copy()
    
    # Find indices where signal exceeds threshold
    peak_indices = np.where(signal > threshold)[0]
    
    # Smooth each peak
    for idx in peak_indices:
        if idx > 0 and idx < len(signal) - 1:
            # Replace with average of neighbors
            signal[idx] = (signal[idx - 1] + signal[idx + 1]) / 2
        else:
            # Edge case: set to zero
            signal[idx] = 0
    
    return signal


def process_raw_records(parsed_data):
    """
    Convert parsed CSV records to processed signal records.
    
    Includes hex cleaning, conversion to signal array, and artifact smoothing.
    
    Args:
        parsed_data (list): List of dictionaries with 'Name' and 'Hex' keys
        
    Returns:
        list: List of dictionaries with 'Name' and 'Signal' keys
    """
    processed_records = []

    print(f"\nProcessing {len(parsed_data)} records...")

    for i, record in enumerate(parsed_data):
        raw_hex = record['Hex']

        # Clean hex data
        clean_hex = clean_hex_data(raw_hex)

        # Convert to signal
        signal = hex_to_signal(clean_hex)

        if signal is not None:
            # Apply artifact smoothing
            signal = smooth_artifacts(signal)

            processed_records.append({
                'Name': record['Name'],
                'Signal': signal
            })

            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(parsed_data)} records")

    print(f"✓ Successfully processed {len(processed_records)} records")
    return processed_records


def extract_file_number(name):
    """
    Extract numerical ID from record name using regex.
    
    Args:
        name (str): Record name string
        
    Returns:
        int or None: Extracted number, or None if not found
    """
    match = re.search(r'(\d+)', name)
    return int(match.group(1)) if match else None


def organize_by_subject(processed_records, start_id=START_ID, 
                       measurements_per_subject=MEASUREMENTS_PER_SUBJECT):
    """
    Organize processed records into subject groups (baseline, favorite, least_favorite).
    
    Assumes records are sequentially ordered as groups of 3:
    (baseline, favorite_song, least_favorite_song)
    
    Args:
        processed_records (list): List of processed signal records
        start_id (int): Minimum file ID to include
        measurements_per_subject (int): Expected measurements per subject (default: 3)
        
    Returns:
        dict: Dictionary with subject_id as key, containing baseline/favorite/least_favorite signals
    """
    subjects = {}
    
    # Sort records by file number
    sorted_records = sorted(processed_records, 
                           key=lambda x: extract_file_number(x['Name']) or 0)
    
    # Filter by start_id
    filtered_records = [r for r in sorted_records 
                       if (extract_file_number(r['Name']) or 0) >= start_id]

    print(f"✓ Found {len(filtered_records)} records starting from ID {start_id}")

    subject_num = 1
    for i in range(0, len(filtered_records), measurements_per_subject):
        subject_measurements = filtered_records[i:i + measurements_per_subject]
        
        # Only process complete subject groups
        if len(subject_measurements) == measurements_per_subject:
            subjects[subject_num] = {
                'baseline': subject_measurements[0],
                'favorite_song': subject_measurements[1],
                'least_favorite_song': subject_measurements[2],
                'file_ids': [extract_file_number(m['Name']) 
                            for m in subject_measurements]
            }
            subject_num += 1

    print(f"✓ Organized into {len(subjects)} subject groups")
    return subjects


def load_and_preprocess_data(filepath):
    """
    Complete data loading and preprocessing pipeline.
    
    Orchestrates: file loading -> CSV parsing -> hex cleaning -> 
    signal conversion -> artifact removal -> subject organization
    
    Args:
        filepath (str): Path to CSV file
        
    Returns:
        dict: Dictionary of organized subject data, or None if failed
    """
    print("=" * 70)
    print("DATA LOADING AND PREPROCESSING")
    print("=" * 70)
    
    # Step 1: Verify file
    if not load_csv_file(filepath):
        return None
    
    # Step 2: Parse CSV
    print("\n[STEP 1] Parsing CSV file...")
    parsed_data = parse_messy_csv(filepath)
    
    # Step 3: Process records
    print("\n[STEP 2] Processing hex data and converting to signals...")
    processed_records = process_raw_records(parsed_data)
    
    # Step 4: Organize by subject
    print("\n[STEP 3] Organizing records into subject groups...")
    subjects_data = organize_by_subject(processed_records)
    
    print("\n" + "=" * 70)
    print(f"✓ DATA PREPROCESSING COMPLETE")
    print(f"  Total subjects: {len(subjects_data)}")
    print("=" * 70)
    
    return subjects_data
