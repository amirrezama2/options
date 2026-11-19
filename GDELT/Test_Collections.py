
import os
import pandas as pd
import mediacloud.api

from dotenv import load_dotenv
from datetime import date

# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH, override=True)

API_KEY = os.getenv("MEDIACLOUD_API_KEY")

if not API_KEY:
    raise ValueError("Media Cloud API Key not found!")

COLLECTION_ID = 38379429

START_DATE = date(2021, 1, 1)
END_DATE = date.today()

OUTPUT_DIR = os.path.join(BASE_DIR, "MediaCloud_Test_38379429")
os.makedirs(OUTPUT_DIR, exist_ok=True)

mc = mediacloud.api.SearchApi(API_KEY)

# ==========================================
# 2. RESEARCH QUERIES
# ==========================================

QUERIES = {
    "Stock_Market": (
        '"S&P 500" OR "stock market" OR '
        '"equity market" OR "Wall Street"'
    ),

    "Monetary_Policy": (
        '"Federal Reserve" OR "monetary policy" OR '
        '"interest rates" OR FOMC'
    ),

    "Macroeconomics": (
        '"US economy" OR "economic growth" OR '
        'GDP OR recession'
    ),

    "Financial_Crisis": (
        '"financial crisis" OR "market crash" OR '
        '"banking crisis" OR "bank failure"'
    )
}

# ==========================================
# 3. TEST COLLECTION
# ==========================================

summary = []

for topic, query in QUERIES.items():

    print("\n" + "=" * 60)
    print("Testing:", topic)
    print("Collection ID:", COLLECTION_ID)
    print("=" * 60)

    try:

        # Total matching stories
        total = mc.story_count(
            query=query,
            start_date=START_DATE,
            end_date=END_DATE,
            collection_ids=[COLLECTION_ID]
        )

        print("Total count response:", total)

        # Count over time
        time_data = mc.story_count_over_time(
            query=query,
            start_date=START_DATE,
            end_date=END_DATE,
            collection_ids=[COLLECTION_ID]
        )

        df_time = pd.DataFrame(time_data)

        if not df_time.empty:
            df_time.to_csv(
                os.path.join(
                    OUTPUT_DIR,
                    f"{topic}_Count_Over_Time.csv"
                ),
                index=False
            )

        # Distribution by news source
        source_data = mc.sources(
            query=query,
            start_date=START_DATE,
            end_date=END_DATE,
            collection_ids=[COLLECTION_ID],
            limit=100
        )

        df_sources = pd.DataFrame(source_data)

        if not df_sources.empty:
            df_sources.to_csv(
                os.path.join(
                    OUTPUT_DIR,
                    f"{topic}_Sources.csv"
                ),
                index=False
            )

        # Sample news stories
        stories = mc.story_sample(
            query=query,
            start_date=START_DATE,
            end_date=END_DATE,
            collection_ids=[COLLECTION_ID],
            limit=100
        )

        df_stories = pd.DataFrame(stories)

        if not df_stories.empty:
            df_stories.to_csv(
                os.path.join(
                    OUTPUT_DIR,
                    f"{topic}_Story_Sample.csv"
                ),
                index=False
            )

        summary.append({
            "Topic": topic,
            "Collection_ID": COLLECTION_ID,
            "Total_Count_Response": str(total),
            "Time_Records": len(df_time),
            "Sources_Returned": len(df_sources),
            "Sample_Stories": len(df_stories),
            "Status": "Success"
        })

        print("Time records:", len(df_time))
        print("Sources returned:", len(df_sources))
        print("Sample stories:", len(df_stories))

        if not df_time.empty:
            print("Time data preview:")
            print(df_time.head())

        if not df_stories.empty:
            print("\nStory sample:")
            print(
                df_stories[
                    ["publish_date", "media_name", "title"]
                ].head(5).to_string(index=False)
            )

    except Exception as e:

        print("ERROR:", repr(e))

        summary.append({
            "Topic": topic,
            "Collection_ID": COLLECTION_ID,
            "Total_Count_Response": None,
            "Time_Records": 0,
            "Sources_Returned": 0,
            "Sample_Stories": 0,
            "Status": f"Failed: {str(e)}"
        })

# ==========================================
# 4. SAVE SUMMARY
# ==========================================

df_summary = pd.DataFrame(summary)

df_summary.to_csv(
    os.path.join(OUTPUT_DIR, "Collection_Test_Summary.csv"),
    index=False
)

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)

print(df_summary.to_string(index=False))

print("\nOutput folder:")
print(OUTPUT_DIR)
