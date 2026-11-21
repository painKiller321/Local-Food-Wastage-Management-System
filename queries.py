# queries.py
import os
import pandas as pd
from sqlalchemy import create_engine, text

# Robust connection to SQLite database regardless of working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'food_waste.db')
engine = create_engine(f'sqlite:///{DB_PATH}')

# 0. Helper: Get all distinct cities
def get_all_cities():
    query = """
    SELECT DISTINCT City FROM providers WHERE City IS NOT NULL AND City != ''
    UNION
    SELECT DISTINCT City FROM receivers WHERE City IS NOT NULL AND City != ''
    ORDER BY City
    """
    df = pd.read_sql(query, engine)
    return df['City'].tolist()

# 0. Helper: Get all receivers
def get_all_receivers():
    query = "SELECT Receiver_ID, Name, Type, City, Contact FROM receivers ORDER BY Name"
    return pd.read_sql(query, engine)

# 0. Helper: Get all providers
def get_all_providers():
    query = "SELECT Provider_ID, Name, Type, Address, City, Contact FROM providers ORDER BY Name"
    return pd.read_sql(query, engine)

# 0. Helper: Get single food item
def get_food_item_by_id(food_id):
    query = "SELECT * FROM food_listings WHERE Food_ID = :fid"
    df = pd.read_sql(text(query), engine, params={"fid": food_id})
    return df.iloc[0].to_dict() if not df.empty else None

# 0. Helper: Claim food item
def claim_food_item(food_id, receiver_id, status='Completed'):
    with engine.begin() as conn:
        max_claim = conn.execute(text("SELECT COALESCE(MAX(Claim_ID), 0) FROM claims")).scalar()
        new_claim_id = int(max_claim or 0) + 1
        now_str = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(text("""
            INSERT INTO claims (Claim_ID, Food_ID, Receiver_ID, Status, Timestamp)
            VALUES (:cid, :fid, :rid, :status, :ts)
        """), {"cid": new_claim_id, "fid": food_id, "rid": receiver_id, "status": status, "ts": now_str})
        return new_claim_id

# 0. Helper: Get detailed claims log
def get_claims_detailed(limit=50):
    query = """
    SELECT c.Claim_ID, f.Food_Name, f.Food_Type, f.Meal_Type, f.Quantity,
           p.Name AS Provider_Name, r.Name AS Receiver_Name,
           r.City AS Receiver_City, c.Status, c.Timestamp
    FROM claims c
    JOIN food_listings f ON c.Food_ID = f.Food_ID
    JOIN providers p ON f.Provider_ID = p.Provider_ID
    JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
    ORDER BY c.Claim_ID DESC
    LIMIT :limit
    """
    return pd.read_sql(text(query), engine, params={"limit": limit})

# 0. Helper: Eco & Social Impact metrics
def get_eco_impact_metrics():
    total_listings_q = "SELECT SUM(Quantity) AS Total_Qty, COUNT(*) AS Total_Listings FROM food_listings"
    claims_stat_q = """
    SELECT COUNT(*) AS Total_Claims,
           SUM(CASE WHEN Status = 'Completed' THEN 1 ELSE 0 END) AS Completed_Claims
    FROM claims
    """
    df_listings = pd.read_sql(total_listings_q, engine)
    df_claims = pd.read_sql(claims_stat_q, engine)
    
    total_qty = int(df_listings.iloc[0]['Total_Qty'] or 0)
    total_claims = int(df_claims.iloc[0]['Total_Claims'] or 0)
    completed_claims = int(df_claims.iloc[0]['Completed_Claims'] or 0)
    
    # Each meal saved = ~2.5 kg CO2e greenhouse gas reduction
    # Each meal saved = ~950 Liters of water conserved
    co2_saved_kg = round(total_qty * 2.5, 1)
    water_saved_liters = round(total_qty * 950, 0)
    
    return {
        "total_meals": total_qty,
        "total_claims": total_claims,
        "completed_claims": completed_claims,
        "completion_rate": round((completed_claims / total_claims * 100), 1) if total_claims else 0,
        "co2_saved_kg": co2_saved_kg,
        "water_saved_liters": water_saved_liters
    }

# 0. Helper: Get food listings with optional filters and join provider info
def get_all_food_listings(food_type=None, meal_type=None, city=None, search_query=None):
    conditions = []
    params = {}
    if food_type and food_type != "All":
        conditions.append("f.Food_Type = :food_type")
        params["food_type"] = food_type
    if meal_type and meal_type != "All":
        conditions.append("f.Meal_Type = :meal_type")
        params["meal_type"] = meal_type
    if city and city != "All":
        conditions.append("LOWER(f.Location) LIKE LOWER(:city)")
        params["city"] = f"%{city.strip()}%"
    if search_query and search_query.strip():
        conditions.append("(LOWER(f.Food_Name) LIKE LOWER(:sq) OR LOWER(f.Location) LIKE LOWER(:sq) OR LOWER(p.Name) LIKE LOWER(:sq))")
        params["sq"] = f"%{search_query.strip()}%"

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
    SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, 
           f.Food_Type, f.Meal_Type, f.Location, f.Provider_Type,
           p.Name AS Provider_Name, p.Contact AS Provider_Contact
    FROM food_listings f
    LEFT JOIN providers p ON f.Provider_ID = p.Provider_ID
    {where_clause} 
    ORDER BY f.Food_ID DESC
    """
    return pd.read_sql(text(query), engine, params=params)

# 1. Number of providers and receivers in each city
def get_providers_receivers_by_city():
    query = """
    SELECT City, 
           COUNT(DISTINCT Provider_ID) AS Providers, 
           (SELECT COUNT(*) FROM receivers r WHERE r.City = p.City) AS Receivers
    FROM providers p
    GROUP BY City
    ORDER BY Providers DESC
    """
    return pd.read_sql(query, engine)

# 2. Type of provider contributing most food
def get_top_provider_type():
    query = """
    SELECT Provider_Type, COUNT(*) AS Total, SUM(Quantity) AS Total_Quantity
    FROM food_listings 
    GROUP BY Provider_Type 
    ORDER BY Total DESC
    """
    return pd.read_sql(query, engine)

# 3. Contact info of providers in a city
def get_providers_by_city(city):
    query = """
    SELECT Name, Type, Contact, City, Address 
    FROM providers 
    WHERE LOWER(City) = LOWER(:city) OR LOWER(City) LIKE LOWER(:city_wildcard)
    """
    return pd.read_sql(text(query), engine, params={"city": city.strip(), "city_wildcard": f"%{city.strip()}%"})

# 3b. Contact info of receivers in a city
def get_receivers_by_city(city):
    query = """
    SELECT Name, Type, Contact, City 
    FROM receivers 
    WHERE LOWER(City) = LOWER(:city) OR LOWER(City) LIKE LOWER(:city_wildcard)
    """
    return pd.read_sql(text(query), engine, params={"city": city.strip(), "city_wildcard": f"%{city.strip()}%"})

# 4. Receivers who claimed the most food
def get_top_receivers():
    query = """
    SELECT r.Name, r.City, r.Type, COUNT(c.Claim_ID) AS Total_Claims
    FROM claims c
    JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
    GROUP BY r.Name, r.City, r.Type
    ORDER BY Total_Claims DESC
    LIMIT 10
    """
    return pd.read_sql(query, engine)

# 5. Total quantity of food available
def get_total_food_quantity():
    query = "SELECT SUM(Quantity) AS Total_Quantity FROM food_listings"
    return pd.read_sql(query, engine)

# 6. City with highest food listings
def get_top_city_by_listings():
    query = """
    SELECT Location AS City, COUNT(*) AS Listings, SUM(Quantity) AS Total_Food_Units 
    FROM food_listings 
    GROUP BY Location 
    ORDER BY Listings DESC
    LIMIT 15
    """
    return pd.read_sql(query, engine)

# 7. Most commonly available food types
def get_common_food_types():
    query = """
    SELECT Food_Type, COUNT(*) AS Listings, SUM(Quantity) AS Total_Quantity 
    FROM food_listings 
    GROUP BY Food_Type 
    ORDER BY Listings DESC
    """
    return pd.read_sql(query, engine)

# 8. Number of claims per food item
def get_claims_per_food():
    query = """
    SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claims, SUM(f.Quantity) AS Available_Units
    FROM claims c
    JOIN food_listings f ON c.Food_ID = f.Food_ID
    GROUP BY f.Food_Name
    ORDER BY Claims DESC
    LIMIT 10
    """
    return pd.read_sql(query, engine)

# 9. Provider with highest successful claims
def get_top_provider_by_claims():
    query = """
    SELECT p.Name, p.City, p.Type, COUNT(c.Claim_ID) AS Successful_Claims
    FROM claims c
    JOIN food_listings f ON c.Food_ID = f.Food_ID
    JOIN providers p ON f.Provider_ID = p.Provider_ID
    WHERE c.Status = 'Completed'
    GROUP BY p.Name, p.City, p.Type
    ORDER BY Successful_Claims DESC
    LIMIT 10
    """
    return pd.read_sql(query, engine)

# 10. Status distribution of claims
def get_claim_status_distribution():
    query = """
    SELECT Status, COUNT(*) AS Count 
    FROM claims 
    GROUP BY Status
    """
    return pd.read_sql(query, engine)

# 11. Avg quantity of food claimed per receiver
def get_avg_claim_quantity():
    query = """
    SELECT r.Name, r.City, ROUND(AVG(f.Quantity), 1) AS Avg_Quantity, COUNT(c.Claim_ID) AS Total_Claims
    FROM claims c
    JOIN food_listings f ON c.Food_ID = f.Food_ID
    JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
    GROUP BY r.Name, r.City
    ORDER BY Avg_Quantity DESC
    LIMIT 10
    """
    return pd.read_sql(query, engine)

# 12. Most claimed meal type
def get_top_meal_type():
    query = """
    SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
    FROM claims c
    JOIN food_listings f ON c.Food_ID = f.Food_ID
    GROUP BY f.Meal_Type
    ORDER BY Total_Claims DESC
    """
    return pd.read_sql(query, engine)

# 13. Total quantity of food donated by provider
def get_quantity_by_provider():
    query = """
    SELECT p.Name, p.City, p.Type, SUM(f.Quantity) AS Total_Quantity
    FROM food_listings f
    JOIN providers p ON f.Provider_ID = p.Provider_ID
    GROUP BY p.Name, p.City, p.Type
    ORDER BY Total_Quantity DESC
    LIMIT 15
    """
    return pd.read_sql(query, engine)
