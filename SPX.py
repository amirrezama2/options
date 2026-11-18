
from pathlib import Path
from io import BytesIO

import requests
import pandas as pd
import yfinance as yf

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "Raw"
PROCESSED_DIR = BASE_DIR / "Processed"

RAW_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

START_DATE = "2021-11-14"
END_DATE = "2026-11-14"  # End date is exclusive

# --------------------------------------------------
# 2. DOWNLOAD SPX UNDERLYING INDEX
# --------------------------------------------------

print("Downloading S&P 500 underlying data...")

spx = yf.download(
    "^GSPC",
    start=START_DATE,
    end=END_DATE,
    interval="1d",
    auto_adjust=False,
    progress=False
)

if spx.empty:
    raise RuntimeError(
        "No SPX underlying data received. Check your internet "
        "connection or Yahoo Finance access."
    )

# Handle possible multi-level column names
if isinstance(spx.columns, pd.MultiIndex):
    spx.columns = spx.columns.get_level_values(0)

spx = spx.reset_index()

spx = spx.rename(columns={
    "Date": "date",
    "Datetime": "date",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adjusted_close",
    "Volume": "volume"
})

spx["date"] = pd.to_datetime(spx["date"]).dt.date

spx.to_csv(
    PROCESSED_DIR / "SPX_Underlying_5Y.csv",
    index=False
)

print("SPX underlying observations:", len(spx))


# --------------------------------------------------
# 3. DOWNLOAD COR3M AND COR6M
# --------------------------------------------------

def download_cboe_index(index_name):

    url = (
        "https://cdn.cboe.com/api/global/us_indices/"
        f"daily_prices/{index_name}_History.csv"
    )

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    if "text/csv" not in response.headers.get(
        "Content-Type", ""
    ):
        raise RuntimeError(
            f"Unexpected response for {index_name}"
        )

    # Save original data
    (RAW_DIR / f"{index_name}_Raw.csv").write_bytes(
        response.content
    )

    df = pd.read_csv(BytesIO(response.content))

    df["DATE"] = pd.to_datetime(
        df["DATE"],
        format="%m/%d/%Y",
        errors="coerce"
    )

    df = df.dropna(subset=["DATE"])

    df = df[
        (df["DATE"] >= START_DATE) &
        (df["DATE"] < END_DATE)
    ].copy()

    df = df.sort_values("DATE")

    df = df.rename(columns={
        "DATE": "date",
        "OPEN": "open",
        "HIGH": "high",
        "LOW": "low",
        "CLOSE": "close"
    })

    df.to_csv(
        PROCESSED_DIR / f"{index_name}_5Y.csv",
        index=False
    )

    print(f"{index_name} observations:", len(df))


download_cboe_index("COR3M")
download_cboe_index("COR6M")


# --------------------------------------------------
# 4. SPX OPTIONS DATA
# --------------------------------------------------
# Download your historical SPX options CSV from a
# provider such as Cboe DataShop and place it in Raw.
#
# This section processes the downloaded file.
# It does NOT generate historical option data itself.

options_file = RAW_DIR / "SPX_Options_Raw.csv"

if options_file.exists():

    options = pd.read_csv(options_file)

    # Normalize column names
    options.columns = (
        options.columns.str.strip().str.lower()
    )

    # Identify the underlying symbol column
    underlying_col = next(
        (c for c in ["underlying_symbol", "underlying"]
         if c in options.columns),
        None
    )

    if underlying_col is None:
        raise ValueError(
            "Could not identify the options underlying column."
        )

    # Keep SPX contracts only
    options = options[
        options[underlying_col]
        .astype(str)
        .str.upper()
        .isin(["SPX", "^SPX"])
    ].copy()

    # Identify the trading date column
    date_col = next(
        (c for c in ["quote_date", "quote_datetime",
                     "trade_date", "date"]
         if c in options.columns),
        None
    )

    if date_col is None:
        raise ValueError(
            "Could not identify the options trading date column."
        )

    options[date_col] = pd.to_datetime(
        options[date_col],
        errors="coerce"
    )

    options = options.dropna(subset=[date_col])

    options = options[
        (options[date_col] >= START_DATE) &
        (options[date_col] < END_DATE)
    ].copy()

    options = options.sort_values(date_col)

    options.to_csv(
        PROCESSED_DIR / "SPX_Options_5Y.csv",
        index=False
    )

    print("SPX options observations:", len(options))

else:
    print(
        "SPX options file not found. "
        "Place your downloaded file at: "
        f"{options_file}"
    )


print("\nData collection process completed.")
