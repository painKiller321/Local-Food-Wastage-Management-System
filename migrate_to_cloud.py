"""
migrate_to_cloud.py
Migrate all data from local SQLite (food_waste.db) into Cloud PostgreSQL (Neon) with lowercase columns.
"""
import sys
import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

def migrate(target_db_url):
    target_url = target_db_url.strip().strip("'\"")
    target_url = target_url.replace("&channel_binding=require", "").replace("?channel_binding=require", "")
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif target_url.startswith("postgresql://") and not target_url.startswith("postgresql+"):
        target_url = target_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_path = os.path.join(base_dir, "food_waste.db")

    if not os.path.exists(sqlite_path):
        print(f"Error: {sqlite_path} does not exist.")
        return

    print("=" * 60)
    print("FoodBridge Cloud Database Migration Tool")
    print("=" * 60)
    print(f"Source SQLite : {sqlite_path}")
    print(f"Target Cloud  : {target_url.split('@')[-1]}")
    print("-" * 60)

    sqlite_conn = sqlite3.connect(sqlite_path)
    target_engine = create_engine(target_url, pool_pre_ping=True)

    tables = ["providers", "receivers", "food_listings", "claims"]

    for tbl in tables:
        print(f"\nProcessing table: '{tbl}'...")
        df = pd.read_sql(f"SELECT * FROM {tbl}", sqlite_conn)
        print(f"   Found {len(df):,} rows in local SQLite.")
        
        # Lowercase all column names for PostgreSQL compatibility
        df.columns = [c.lower() for c in df.columns]

        try:
            df.to_sql(tbl, target_engine, if_exists="replace", index=False)
            print(f"   Successfully copied {len(df):,} rows to cloud table '{tbl}'!")
        except Exception as e:
            print(f"   Error copying '{tbl}': {e}")

    sqlite_conn.close()
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "postgresql+psycopg2://neondb_owner:npg_wvF5pq1gZfnO@ep-proud-river-bdk9ig70-pooler.c-8.us-east-2.aws.neon.tech/neondb?sslmode=require"
    migrate(url)
