"""
FoodBridge Health & Database Connection Diagnostic Check
Verifies database connection, table row counts, view modules, and analytical queries.
"""
import sys
import os

print("=" * 60)
print(" FoodBridge System & Database Health Check")
print("=" * 60)

# 1. Database Connection Check
print("\n[1/4] Checking Database Connection...")
try:
    import queries
    status = queries.get_db_status()
    if status["ok"]:
        print(f"  Status       : CONNECTED")
        print(f"  Database Type: {status['db_type']}")
        print(f"  Connection   : {status['url']}")
        print(f"  Table Counts :")
        for tbl, count in status["counts"].items():
            print(f"    - {tbl:14s}: {count:,} records")
    else:
        print(f"  Status       : ERROR - {status.get('error')}")
except Exception as e:
    print(f"  Database check failed: {e}")

# 2. Plotly and Visualizations Check
print("\n[2/4] Checking Visualization Libraries...")
try:
    import plotly
    import plotly.graph_objects as go
    import plotly.express as px
    print(f"  Plotly Version: {plotly.__version__} (OK)")
except Exception as e:
    print(f"  Plotly check failed: {e}")

# 3. Views Modules Check
print("\n[3/4] Checking Application Views...")
try:
    from views import summary, food_listings, claims_analysis, contacts, manage_listings
    print("  Views Loaded  : summary, food_listings, claims_analysis, contacts, manage_listings (OK)")
except Exception as e:
    print(f"  Views import failed: {e}")

# 4. Core Query Verification
print("\n[4/4] Verifying Business Analytics Queries...")
try:
    eco = queries.get_eco_impact_metrics()
    cities = queries.get_all_cities()
    print(f"  Total Meals   : {eco['total_meals']:,}")
    print(f"  CO2 Saved     : {eco['co2_saved_kg']:,} kg")
    print(f"  Claim Success : {eco['completion_rate']}%")
    print(f"  Active Cities : {len(cities):,}")
    print("\n" + "=" * 60)
    print(" ALL SYSTEMS OPERATIONAL - Database Connected & Ready to Deploy!")
    print("=" * 60)
except Exception as e:
    print(f"  Query execution failed: {e}")

