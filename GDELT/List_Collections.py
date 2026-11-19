
import os
import pandas as pd
import mediacloud.api
from dotenv import load_dotenv

# ==========================================
# CONFIGURATION
# ==========================================

load_dotenv()

API_KEY = os.getenv("MEDIACLOUD_API_KEY")

if not API_KEY:
    raise ValueError("Media Cloud API Key not found!")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "MediaCloud",
    "00_Metadata"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# CONNECT TO MEDIA CLOUD
# ==========================================

mc = mediacloud.api.DirectoryApi(API_KEY)

# ==========================================
# GET COLLECTIONS
# ==========================================

all_collections = []

offset = 0
limit = 100

while True:

    response = mc.collection_list(
        platform="online_news",
        limit=limit,
        offset=offset
    )

    results = response.get("results", [])

    if not results:
        break

    all_collections.extend(results)

    print(
        f"Downloaded {len(all_collections)} collections"
    )

    if response.get("next") is None:
        break

    offset += len(results)

# ==========================================
# EXPORT
# ==========================================

df = pd.DataFrame(all_collections)

output_path = os.path.join(
    OUTPUT_DIR,
    "Available_Collections.csv"
)

df.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("\nCollection extraction completed!")

print(df.head(10))

print(f"\nTotal collections: {len(df)}")

print(f"Saved to: {output_path}")
