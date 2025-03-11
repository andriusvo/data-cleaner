import pandas as pd
import numpy as np
import streamlit as st

def detect_missing_values(df):
    missing_values = df.isnull().sum()
    missing_percent = (missing_values / len(df)) * 100
    missing_stats = pd.DataFrame({
        'Column': missing_values.index,
        'Missing Values': missing_values.values,
        'Missing %': missing_percent.values
    })
    return missing_stats[missing_stats['Missing Values'] > 0].reset_index(drop=True)

def drop_missing_values(df, columns=None):
    original_shape = df.shape

    if columns is not None:
        valid_columns = [col for col in columns if col in df.columns]
        if valid_columns:
            df = df.dropna(subset=valid_columns)
            dropped_rows = original_shape[0] - df.shape[0]
            st.session_state.report.append(f"Dropped {dropped_rows} rows with missing values in columns: {', '.join(valid_columns)}")
        else:
            st.session_state.report.append("No valid columns specified for dropping missing values.")
    else:
        original_row_count = df.shape[0]
        df = df.dropna()
        dropped_rows = original_row_count - df.shape[0]
        st.session_state.report.append(f"Dropped {dropped_rows} rows with any missing values")
    
    return df

def fill_missing_with_mean(df, columns=None):
    if columns is None:
        numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
    else:
        numeric_columns = [col for col in columns if col in df.columns and col in df.select_dtypes(include=np.number).columns]
        if not numeric_columns and columns:
            st.session_state.report.append("No valid numeric columns specified for filling missing values.")
    
    for col in numeric_columns:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            mean_value = df[col].mean()
            rounded_mean = round(mean_value, 2)
            df[col] = df[col].fillna(rounded_mean)
            st.session_state.report.append(f"Filled {missing_count} missing values in '{col}' with mean: {rounded_mean:.2f}")
    
    return df

def detect_outliers(df, threshold=3):
    if threshold is not None and isinstance(threshold, str):
        if threshold.lower() == 'none' or threshold == '' or threshold == '_':
            threshold = 3
        else:
            try:
                threshold = float(threshold)
            except (ValueError, TypeError):
                threshold = 3
            
    numeric_columns = df.select_dtypes(include=np.number).columns
    outlier_info = []
    
    for col in numeric_columns:
        if df[col].count() > 1:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outlier_count = (z_scores > threshold).sum()
            if outlier_count > 0:
                outlier_info.append({
                    'Column': col,
                    'Outlier Count': outlier_count,
                    'Outlier %': (outlier_count / len(df)) * 100,
                    'Mean': df[col].mean(),
                    'Std Dev': df[col].std(),
                    'Min': df[col].min(),
                    'Max': df[col].max()
                })
    
    return pd.DataFrame(outlier_info)

def remove_outliers(df, columns=None, threshold=3):
    if columns is None:
        columns = df.select_dtypes(include=np.number).columns
    else:
        columns = [col for col in columns if col in df.columns and col in df.select_dtypes(include=np.number).columns]
        if not columns:
            st.session_state.report.append("No valid numeric columns specified for removing outliers.")
            return df
    
    original_shape = df.shape
    for col in columns:
        if df[col].count() > 1:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            mask = z_scores <= threshold
            df = df[mask]
            removed_count = original_shape[0] - df.shape[0]
            if removed_count > 0:
                st.session_state.report.append(f"Removed {removed_count} outliers from column '{col}' using Z-score > {threshold}")
            original_shape = df.shape
    
    return df

def remove_duplicates(df, subset=None):
    original_shape = df.shape
    
    if subset:
        valid_subset = [col for col in subset if col in df.columns]
        if not valid_subset:
            st.session_state.report.append("No valid columns specified for removing duplicates.")
            return df
        subset = valid_subset
    
    df = df.drop_duplicates(subset=subset, keep='first')
    removed_count = original_shape[0] - df.shape[0]
    if removed_count > 0:
        if subset:
            st.session_state.report.append(f"Removed {removed_count} duplicate rows based on columns: {', '.join(subset)}")
        else:
            st.session_state.report.append(f"Removed {removed_count} duplicate rows")
    return df
