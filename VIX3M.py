
from pathlib import Path

import pandas as pd
import yfinance as yf

# -----------------------------
# Settings
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "Raw"
PROCESSED_DIR = BASE_DIR / "Processed"

RAW_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

START_DATE = "2021-11-14"
END_DATE = "2026-11-14"  # Exclusive

# -----------------------------
# Download VIX3M Data
# -----------------------------

print("Downloading VIX3M historical data...")

vix3m = yf.download(
    "^VIX3M",
    start=START_DATE,
    end=END_DATE,
    interval="1d",
    auto_adjust=False,
    progress=False
)

if vix3m.empty:
    raise RuntimeError(
        "No VIX3M data received. Check your internet connection "
        "or Yahoo Finance access."
    )

# Handle MultiIndex columns
if isinstance(vix3m.columns, pd.MultiIndex):
    vix3m.columns = vix3m.columns.get_level_values(0)

# Reset index
vix3m = vix3m.reset_index()

# Rename columns
vix3m = vix3m.rename(columns={
    "Date": "date",
    "Datetime": "date",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adjusted_close",
    "Volume": "volume"
})

# Format date
vix3m["date"] = pd.to_datetime(vix3m["date"]).dt.date

# Sort observations
vix3m = vix3m.sort_values("date")

# -----------------------------
# Save CSV Files
# -----------------------------

vix3m.to_csv(
    RAW_DIR / "VIX3M_Raw.csv",
    index=False
)

vix3m.to_csv(
    PROCESSED_DIR / "VIX3M_5Y.csv",
    index=False
)

# -----------------------------
# Summary
# -----------------------------

print("\nVIX3M data successfully downloaded.")

print("Number of observations:", len(vix3m))
print("Start date:", vix3m["date"].min())
print("End date:", vix3m["date"].max())

print("\nFirst 5 observations:")
print(vix3m.head())

print("\nFiles saved:")
print(RAW_DIR / "VIX3M_Raw.csv")
print(PROCESSED_DIR / "VIX3M_5Y.csv")
