# ---------- utils/DataPreprocessor.py ----------
"""
Cleans and normalizes OHLCV data.
"""
import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna()
    df = df[df['volume'] > 0]
    return df


def normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    return (df - df.mean()) / df.std()
