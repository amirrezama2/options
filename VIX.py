
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
# Download VIX Data
# -----------------------------

print("Downloading VIX historical data...")

vix = yf.download(
    "^VIX",
    start=START_DATE,
    end=END_DATE,
    interval="1d",
    auto_adjust=False,
    progress=False
)

if vix.empty:
    raise RuntimeError(
        "No VIX data received. Check your internet connection "
        "or Yahoo Finance access."
    )

# Handle MultiIndex columns
if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.get_level_values(0)

# Reset index
vix = vix.reset_index()

# Rename columns
vix = vix.rename(columns={
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
vix["date"] = pd.to_datetime(vix["date"]).dt.date

# Sort observations
vix = vix.sort_values("date")

# -----------------------------
# Save CSV Files
# -----------------------------

vix.to_csv(RAW_DIR / "VIX_Raw.csv", index=False)

vix.to_csv(
    PROCESSED_DIR / "VIX_5Y.csv",
    index=False
)

# -----------------------------
# Summary
# -----------------------------

print("\nVIX data successfully downloaded.")

print("Number of observations:", len(vix))
print("Start date:", vix["date"].min())
print("End date:", vix["date"].max())

print("\nFirst 5 observations:")
print(vix.head())

print("\nFiles saved:")
print(RAW_DIR / "VIX_Raw.csv")
print(PROCESSED_DIR / "VIX_5Y.csv")
