#!/usr/bin/env python3
"""
CSV Data Cleaning Script
Cleans CSV files by replacing NULL values with randomly chosen adjacent values
Sorts data appropriately and preserves all records
"""

import pandas as pd
import numpy as np
import random
import os
from pathlib import Path

def clean_csv_file(input_file, output_file, sort_column=None):
    """
    Clean a CSV file by replacing NULL/empty values with randomly chosen adjacent values
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output cleaned CSV file
        sort_column: Column name to sort by (optional)
    """
    print(f"\nProcessing {input_file}...")
    
    try:
        # Read the CSV file
        df = pd.read_csv(input_file, encoding='latin1')
        
        print(f"Successfully read {input_file}")
        print(f"Original shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Count NULL/empty values before cleaning (including empty strings)
        null_count_before = df.isnull().sum().sum() + (df == '').sum().sum() + (df == 'NULL').sum().sum()
        print(f"NULL/empty values before cleaning: {null_count_before}")
        
        # Replace empty strings and 'NULL' strings with NaN for consistent handling
        df = df.replace(['', 'NULL', 'null', 'None'], np.nan)
        
        # Replace NULL values with adjacent values randomly
        total_replaced = 0
        for column in df.columns:
            null_indices = df[df[column].isnull()].index.tolist()
            replaced_in_column = 0
            
            for idx in null_indices:
                # Get adjacent non-null values
                adjacent_values = []
                
                # Check above (look for nearest non-null value above)
                for i in range(idx-1, max(-1, idx-6), -1):
                    if i >= 0 and pd.notna(df.loc[i, column]):
                        adjacent_values.append(df.loc[i, column])
                        break
                
                # Check below (look for nearest non-null value below)
                for i in range(idx+1, min(len(df), idx+6)):
                    if pd.notna(df.loc[i, column]):
                        adjacent_values.append(df.loc[i, column])
                        break
                
                # If we have adjacent values, randomly choose one
                if adjacent_values:
                    df.loc[idx, column] = random.choice(adjacent_values)
                    replaced_in_column += 1
                else:
                    # If no adjacent values, try to find any non-null value in the column
                    non_null_values = df[column].dropna()
                    if not non_null_values.empty:
                        df.loc[idx, column] = random.choice(non_null_values.tolist())
                        replaced_in_column += 1
            
            if replaced_in_column > 0:
                print(f"  Replaced {replaced_in_column} NULL values in '{column}' column")
            total_replaced += replaced_in_column
        
        # Count NULL values after cleaning
        null_count_after = df.isnull().sum().sum() + (df == '').sum().sum()
        print(f"NULL/empty values after cleaning: {null_count_after}")
        
        # Sort the dataframe
        if sort_column and sort_column in df.columns:
            print(f"\nSorting data by '{sort_column}' column...")
            try:
                # For numeric columns, sort numerically
                if df[sort_column].dtype in ['int64', 'float64'] or pd.to_numeric(df[sort_column], errors='coerce').notna().any():
                    df[sort_column] = pd.to_numeric(df[sort_column], errors='coerce')
                    df = df.sort_values(sort_column, ascending=False)  # Descending for scores
                    print(f"Sorted by {sort_column} (descending)")
                else:
                    df = df.sort_values(sort_column)
                    print(f"Sorted by {sort_column} (ascending)")
            except Exception as e:
                print(f"Warning: Could not sort by {sort_column}: {e}")
                print("Proceeding without sorting...")
        elif 'arrival_date_year' in df.columns and 'arrival_date_month' in df.columns:
            # For hotel data, sort by arrival date
            month_map = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            df['month_num'] = df['arrival_date_month'].map(month_map)
            df = df.sort_values(['arrival_date_year', 'month_num'])
            df = df.drop('month_num', axis=1)
            print("Sorted by arrival date")
        
        # Save the cleaned file
        df.to_csv(output_file, index=False, encoding = 'mac-roman', errors='replace')
        print(f"Cleaned file saved to: {output_file}")
        print(f"Replaced {total_replaced} NULL/empty values")
        
        return len(df), total_replaced, null_count_after
        
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")
        return 0, 0, 0

def convert_to_csv(input_file):
    """
    Converts Excel or JSON file to CSV and returns the new CSV file path.
    If input is already CSV, returns the same path.
    """
    ext = os.path.splitext(input_file)[1].lower()
    csv_file = input_file
    if ext in ['.xls', '.xlsx']:
        df = pd.read_excel(input_file)
        csv_file = input_file.rsplit('.', 1)[0] + '.csv'
        df.to_csv(csv_file, index=False)
        print(f"Converted Excel to CSV: {csv_file}")
    elif ext == '.json':
        df = pd.read_json(input_file)
        csv_file = input_file.rsplit('.', 1)[0] + '.csv'
        df.to_csv(csv_file, index=False)
        print(f"Converted JSON to CSV: {csv_file}")
    elif ext == '.csv':
        pass  # Already CSV
    else:
        raise ValueError("Unsupported file type. Please provide a CSV, Excel, or JSON file.")
    return csv_file

def main():
    print("CSV Data Cleaning Tool")
    print("=" * 50)
    
    total_files_processed = 0
    total_records_processed = 0
    total_nulls_replaced = 0

    input_file = input("Enter the path to the input file (CSV, Excel, or JSON): ").strip()
    if not os.path.exists(input_file):
        print(f"File {input_file} does not exist. Please check the path and try again.")
        return

    try:
        csv_input_file = convert_to_csv(input_file)
    except Exception as e:
        print(f"Error: {e}")
        return

    base_name = os.path.basename(csv_input_file)
    description = f"Cleaning '{base_name}'"
    output_file = f"cleaned_{base_name}"

    print(f"\n{'='*60}")
    print(f"Processing: {description}")
    print(f"Input file: {csv_input_file}")
    print(f"Output file: {output_file}")

    records, replaced, remaining = clean_csv_file(csv_input_file, output_file, sort_column=None)
    if records > 0:
        total_files_processed += 1
        total_records_processed += records
        total_nulls_replaced += replaced
        print(f"✓ Successfully processed {description}")
    else:
        print(f"✗ Failed to process {description}")

    # Summary
    print(f"\n{'='*60}")
    print("CLEANING SUMMARY")
    print(f"{'='*60}")
    print(f"Files processed: {total_files_processed}")
    print(f"Total records processed: {total_records_processed}")
    print(f"Total NULL values replaced: {total_nulls_replaced}")
    print(f"\nAll cleaned files are ready for analysis!")

if __name__ == "__main__":
    main()
