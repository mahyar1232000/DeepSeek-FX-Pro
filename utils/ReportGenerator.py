# ---------- utils/ReportGenerator.py ----------
"""
Generates performance reports and trade summaries.
"""
import pandas as pd


def generate_report(trades: list, output_file: str) -> None:
    df = pd.DataFrame(trades)
    df.to_csv(output_file, index=False)
