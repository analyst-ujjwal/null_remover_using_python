# null_remover_using_python
Developed a Python program to efficiently detect, handle, and impute null values in datasets using customizable strategies (mean, median, mode, constant, forward/backward fill)


# CSV Data Cleaning Tool

## 📖 Overview
This Python script automates the cleaning of CSV files by:
- Replacing `NULL`, empty strings, or `NaN` values with randomly chosen adjacent values.  
- Sorting the dataset (either by a specified column or default rules like arrival dates).  
- Preserving all records (no rows are deleted).  

It ensures cleaned, sorted CSVs that are ready for analysis or import into databases/BI tools.

---

## ⚙️ Features
- Detects and counts missing values (`NaN`, `''`, `'NULL'`, `'None'`).
- Fills missing values using adjacent row values (above or below).
- Handles sorting by:
  - Custom column (numeric → descending, text → ascending).
  - Special rules for hotel booking data (`arrival_date_year`, `arrival_date_month`).
- Generates cleaned CSVs with all records preserved.
- Provides detailed logs and a summary after cleaning.

---

## 🛠 Requirements
- Python 3.8+
- Pandas
- NumPy

Install dependencies:
```bash
pip install pandas numpy
