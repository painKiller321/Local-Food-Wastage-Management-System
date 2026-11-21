# queries.py
import os
import pandas as pd
from sqlalchemy import create_engine, text

def normalize_url(url: str) -> str:
    """Normalize database URL for SQLAlchemy and remove problematic parameters."""
    url = url.strip().strip("'\"")
    url = url.replace("&channel_binding=require", "").replace("?channel_binding=require", "")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url

def get_candidate_db_urls(raw_url: str):
    """Generate prioritized SQLAlchemy connection URLs with driver fallbacks."""
    url = raw_url.strip().strip("'\"")
    url = url.replace("&channel_binding=require", "").replace("?channel_binding=require", "")
    if "postgres" not in url.lower():
        return [url]
    
    # Extract portion after scheme
    if "://" in url:
        _, rest = url.split("://", 1)
    else:
        rest = url
    
    # Try psycopg2 first, then psycopg 3, then pure-python pg8000
    return [
        f"postgresql+psycopg2://{rest}",
        f"postgresql+psycopg://{rest}",
        f"postgresql+pg8000://{rest}",
    ]

def get_sqlite_url():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'food_waste.db')
    return f'sqlite:///{db_path}'

def create_db_engine():
    """Create DB engine from Streamlit secrets, env var, or secrets.toml, with fallback to local SQLite."""
    candidate_url = None
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
            candidate_url = str(st.secrets["DATABASE_URL"]).strip()
    except Exception:
        pass

    if not candidate_url:
        candidate_url = os.environ.get("DATABASE_URL", "").strip()

    if not candidate_url:
        # Fallback: check local .streamlit/secrets.toml directly
        base_dir = os.path.dirname(os.path.abspath(__file__))
        secrets_file = os.path.join(base_dir, ".streamlit", "secrets.toml")
        if os.path.isfile(secrets_file):
            try:
                import tomllib
                with open(secrets_file, "rb") as f:
                    data = tomllib.load(f)
                    if "DATABASE_URL" in data:
                        candidate_url = str(data["DATABASE_URL"]).strip()
            except Exception:
                try:
                    with open(secrets_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip().startswith("DATABASE_URL"):
                                parts = line.split("=", 1)
                                if len(parts) == 2:
                                    candidate_url = parts[1].strip().strip("'\"")
                                    break
                except Exception:
                    pass

    if candidate_url:
        url_candidates = get_candidate_db_urls(candidate_url)
        last_error = None
        for try_url in url_candidates:
            try:
                connect_args = {"connect_timeout": 5} if ("psycopg2" in try_url or "psycopg" in try_url) else {}
                eng = create_engine(try_url, pool_pre_ping=True, connect_args=connect_args)
                with eng.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return eng
            except Exception as e:
                last_error = e
                continue
        print(f"[WARN] Cloud DB connection failed: {last_error}. Falling back to local SQLite.")

    return create_engine(get_sqlite_url(), pool_pre_ping=True)

engine = create_db_engine()

# Standard column mapping dictionary
STANDARD_COL_MAP = {
    'provider_id': 'Provider_ID',
    'receiver_id': 'Receiver_ID',
    'food_id': 'Food_ID',
    'claim_id': 'Claim_ID',
    'food_name': 'Food_Name',
    'food_type': 'Food_Type',
    'meal_type': 'Meal_Type',
    'provider_type': 'Provider_Type',
    'provider_name': 'Provider_Name',
    'provider_contact': 'Provider_Contact',
    'receiver_name': 'Receiver_Name',
    'receiver_city': 'Receiver_City',
    'quantity': 'Quantity',
    'expiry_date': 'Expiry_Date',
    'location': 'Location',
    'name': 'Name',
    'type': 'Type',
    'address': 'Address',
    'city': 'City',
    'contact': 'Contact',
    'status': 'Status',
    'timestamp': 'Timestamp',
    'total': 'Total',
    'total_quantity': 'Total_Quantity',
    'total_qty': 'Total_Qty',
    'total_listings': 'Total_Listings',
    'total_claims': 'Total_Claims',
    'completed_claims': 'Completed_Claims',
    'providers': 'Providers',
    'receivers': 'Receivers',
    'listings': 'Listings',
    'total_food_units': 'Total_Food_Units',
    'claims': 'Claims',
    'available_units': 'Available_Units',
    'successful_claims': 'Successful_Claims',
    'count': 'Count',
    'avg_quantity': 'Avg_Quantity',
}

def safe_read_sql(sql_str, params=None):
    """Executes query and normalizes DataFrame column casing for cross-DB compatibility."""
    stmt = text(sql_str) if params or isinstance(sql_str, str) else sql_str
    df = pd.read_sql(stmt, engine, params=params)
    df.columns = [STANDARD_COL_MAP.get(str(c).lower(), str(c)) for c in df.columns]
    return df

def get_db_status():
    """Returns information about active database connection."""
    url = str(engine.url)
    is_cloud = "sqlite" not in url.lower()
    db_type = "Cloud PostgreSQL (Neon)" if is_cloud else "Local SQLite"
    
    masked_url = url
    if "@" in masked_url:
        masked_url = masked_url.split("@")[-1]
    
    counts = {}
    try:
        with engine.connect() as conn:
            for tbl in ["providers", "receivers", "food_listings", "claims"]:
                try:
                    c = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
                    counts[tbl] = int(c or 0)
                except Exception:
                    counts[tbl] = 0
        return {"ok": True, "db_type": db_type, "is_cloud": is_cloud, "url": masked_url, "counts": counts}
    except Exception as e:
        return {"ok": False, "error": str(e), "db_type": db_type, "is_cloud": is_cloud, "url": masked_url, "counts": {}}

# 0. Helper: Get all distinct cities across providers, receivers, and food listings
def get_all_cities():
    query = """
    SELECT DISTINCT city AS City FROM providers WHERE city IS NOT NULL AND city != ''
    UNION
    SELECT DISTINCT city AS City FROM receivers WHERE city IS NOT NULL AND city != ''
    UNION
    SELECT DISTINCT location AS City FROM food_listings WHERE location IS NOT NULL AND location != ''
    ORDER BY City
    """
    df = safe_read_sql(query)
    return df['City'].dropna().tolist()

# 0. Helper: Get all receivers
def get_all_receivers():
    query = "SELECT receiver_id, name, type, city, contact FROM receivers ORDER BY name"
    return safe_read_sql(query)

# 0. Helper: Get all providers
def get_all_providers():
    query = "SELECT provider_id, name, type, address, city, contact FROM providers ORDER BY name"
    return safe_read_sql(query)

# 0. Helper: Register a new provider/restaurant
def register_provider(name, ptype, city, contact, address=""):
    with engine.begin() as conn:
        max_id = conn.execute(text("SELECT COALESCE(MAX(provider_id), 0) FROM providers")).scalar()
        new_id = int(max_id or 0) + 1
        conn.execute(text("""
            INSERT INTO providers (provider_id, name, type, address, city, contact)
            VALUES (:pid, :name, :type, :address, :city, :contact)
        """), {
            "pid": new_id,
            "name": name.strip(),
            "type": ptype.strip(),
            "address": address.strip() if address else city.strip(),
            "city": city.strip(),
            "contact": contact.strip()
        })
        return new_id

# 0. Helper: Add a new food listing
def add_food_listing(food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type):
    with engine.begin() as conn:
        max_id = conn.execute(text("SELECT COALESCE(MAX(food_id), 0) FROM food_listings")).scalar()
        new_id = int(max_id or 0) + 1
        conn.execute(text("""
            INSERT INTO food_listings (food_id, food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
            VALUES (:fid, :fname, :qty, :exp, :pid, :ptype, :loc, :ftype, :mtype)
        """), {
            "fid": new_id,
            "fname": food_name.strip(),
            "qty": int(quantity),
            "exp": str(expiry_date),
            "pid": int(provider_id),
            "ptype": provider_type.strip(),
            "loc": location.strip(),
            "ftype": food_type.strip(),
            "mtype": meal_type.strip()
        })
        return new_id

# 0. Helper: Update an existing food listing
def update_food_listing_field(food_id, field_name, new_value):
    col_name = str(field_name).strip().lower()
    allowed_cols = ["food_name", "quantity", "expiry_date", "food_type", "meal_type", "location"]
    if col_name not in allowed_cols:
        raise ValueError(f"Field {field_name} is not allowed to be updated.")
    with engine.begin() as conn:
        query = text(f"UPDATE food_listings SET {col_name} = :val WHERE food_id = :fid")
        res = conn.execute(query, {"val": new_value, "fid": int(food_id)})
        return res.rowcount > 0

# 0. Helper: Delete food listing
def delete_food_listing(food_id):
    with engine.begin() as conn:
        res = conn.execute(text("DELETE FROM food_listings WHERE food_id = :fid"), {"fid": int(food_id)})
        return res.rowcount > 0

# 0. Helper: Get single food item
def get_food_item_by_id(food_id):
    query = """
    SELECT f.*, p.name AS provider_name, p.contact AS provider_contact
    FROM food_listings f
    LEFT JOIN providers p ON f.provider_id = p.provider_id
    WHERE f.food_id = :fid
    """
    df = safe_read_sql(query, params={"fid": int(food_id)})
    return df.iloc[0].to_dict() if not df.empty else None

# 0. Helper: Claim food item
def claim_food_item(food_id, receiver_id, status='Completed'):
    with engine.begin() as conn:
        max_claim = conn.execute(text("SELECT COALESCE(MAX(claim_id), 0) FROM claims")).scalar()
        new_claim_id = int(max_claim or 0) + 1
        now_str = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(text("""
            INSERT INTO claims (claim_id, food_id, receiver_id, status, timestamp)
            VALUES (:cid, :fid, :rid, :status, :ts)
        """), {"cid": new_claim_id, "fid": int(food_id), "rid": int(receiver_id), "status": status, "ts": now_str})
        return new_claim_id

# 0. Helper: Get detailed claims log
def get_claims_detailed(limit=50):
    query = """
    SELECT c.claim_id, f.food_name, f.food_type, f.meal_type, f.quantity,
           p.name AS provider_name, r.name AS receiver_name,
           r.city AS receiver_city, c.status, c.timestamp
    FROM claims c
    JOIN food_listings f ON c.food_id = f.food_id
    JOIN providers p ON f.provider_id = p.provider_id
    JOIN receivers r ON c.receiver_id = r.receiver_id
    ORDER BY c.claim_id DESC
    LIMIT :limit
    """
    return safe_read_sql(query, params={"limit": limit})

# 0. Helper: Eco & Social Impact metrics
def get_eco_impact_metrics():
    total_listings_q = "SELECT SUM(quantity) AS Total_Qty, COUNT(*) AS Total_Listings FROM food_listings"
    claims_stat_q = """
    SELECT COUNT(*) AS Total_Claims,
           SUM(CASE WHEN LOWER(status) = 'completed' THEN 1 ELSE 0 END) AS Completed_Claims
    FROM claims
    """
    df_listings = safe_read_sql(total_listings_q)
    df_claims = safe_read_sql(claims_stat_q)
    
    total_qty = int(df_listings.iloc[0]['Total_Qty'] or 0) if not df_listings.empty else 0
    total_claims = int(df_claims.iloc[0]['Total_Claims'] or 0) if not df_claims.empty else 0
    completed_claims = int(df_claims.iloc[0]['Completed_Claims'] or 0) if not df_claims.empty else 0
    
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
        conditions.append("LOWER(f.food_type) = LOWER(:food_type)")
        params["food_type"] = food_type
    if meal_type and meal_type != "All":
        conditions.append("LOWER(f.meal_type) = LOWER(:meal_type)")
        params["meal_type"] = meal_type
    if city and city != "All":
        conditions.append("LOWER(f.location) LIKE LOWER(:city)")
        params["city"] = f"%{city.strip()}%"
    if search_query and search_query.strip():
        conditions.append("(LOWER(f.food_name) LIKE LOWER(:sq) OR LOWER(f.location) LIKE LOWER(:sq) OR LOWER(p.name) LIKE LOWER(:sq))")
        params["sq"] = f"%{search_query.strip()}%"

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
    SELECT f.food_id, f.food_name, f.quantity, f.expiry_date, 
           f.food_type, f.meal_type, f.location, f.provider_type,
           p.name AS provider_name, p.contact AS provider_contact
    FROM food_listings f
    LEFT JOIN providers p ON f.provider_id = p.provider_id
    {where_clause} 
    ORDER BY f.food_id DESC
    """
    return safe_read_sql(query, params=params)

# 1. Number of providers and receivers in each city
def get_providers_receivers_by_city():
    query = """
    SELECT p.city AS City, 
           COUNT(DISTINCT p.provider_id) AS Providers, 
           (SELECT COUNT(*) FROM receivers r WHERE LOWER(r.city) = LOWER(p.city)) AS Receivers
    FROM providers p
    GROUP BY p.city
    ORDER BY Providers DESC
    """
    return safe_read_sql(query)

# 2. Type of provider contributing most food
def get_top_provider_type():
    query = """
    SELECT provider_type AS Provider_Type, COUNT(*) AS Total, SUM(quantity) AS Total_Quantity
    FROM food_listings 
    GROUP BY provider_type 
    ORDER BY Total DESC
    """
    return safe_read_sql(query)

# 3. Contact info of providers in a city
def get_providers_by_city(city):
    query = """
    SELECT name AS Name, type AS Type, contact AS Contact, city AS City, address AS Address 
    FROM providers 
    WHERE LOWER(city) = LOWER(:city) OR LOWER(city) LIKE LOWER(:city_wildcard)
    """
    return safe_read_sql(query, params={"city": city.strip(), "city_wildcard": f"%{city.strip()}%"})

# 3b. Contact info of receivers in a city
def get_receivers_by_city(city):
    query = """
    SELECT name AS Name, type AS Type, contact AS Contact, city AS City 
    FROM receivers 
    WHERE LOWER(city) = LOWER(:city) OR LOWER(city) LIKE LOWER(:city_wildcard)
    """
    return safe_read_sql(query, params={"city": city.strip(), "city_wildcard": f"%{city.strip()}%"})

# 4. Receivers who claimed the most food
def get_top_receivers():
    query = """
    SELECT r.name AS Name, r.city AS City, r.type AS Type, COUNT(c.claim_id) AS Total_Claims
    FROM claims c
    JOIN receivers r ON c.receiver_id = r.receiver_id
    GROUP BY r.name, r.city, r.type
    ORDER BY Total_Claims DESC
    LIMIT 10
    """
    return safe_read_sql(query)

# 5. Total quantity of food available
def get_total_food_quantity():
    query = "SELECT SUM(quantity) AS Total_Quantity FROM food_listings"
    return safe_read_sql(query)

# 6. City with highest food listings
def get_top_city_by_listings():
    query = """
    SELECT location AS City, COUNT(*) AS Listings, SUM(quantity) AS Total_Food_Units 
    FROM food_listings 
    GROUP BY location 
    ORDER BY Listings DESC
    LIMIT 15
    """
    return safe_read_sql(query)

# 7. Most commonly available food types
def get_common_food_types():
    query = """
    SELECT food_type AS Food_Type, COUNT(*) AS Listings, SUM(quantity) AS Total_Quantity 
    FROM food_listings 
    GROUP BY food_type 
    ORDER BY Listings DESC
    """
    return safe_read_sql(query)

# 8. Number of claims per food item
def get_claims_per_food():
    query = """
    SELECT f.food_name AS Food_Name, COUNT(c.claim_id) AS Claims, SUM(f.quantity) AS Available_Units
    FROM claims c
    JOIN food_listings f ON c.food_id = f.food_id
    GROUP BY f.food_name
    ORDER BY Claims DESC
    LIMIT 10
    """
    return safe_read_sql(query)

# 9. Provider with highest successful claims
def get_top_provider_by_claims():
    query = """
    SELECT p.name AS Name, p.city AS City, p.type AS Type, COUNT(c.claim_id) AS Successful_Claims
    FROM claims c
    JOIN food_listings f ON c.food_id = f.food_id
    JOIN providers p ON f.provider_id = p.provider_id
    WHERE LOWER(c.status) = 'completed'
    GROUP BY p.name, p.city, p.type
    ORDER BY Successful_Claims DESC
    LIMIT 10
    """
    return safe_read_sql(query)

# 10. Status distribution of claims
def get_claim_status_distribution():
    query = """
    SELECT status AS Status, COUNT(*) AS Count 
    FROM claims 
    GROUP BY status
    """
    return safe_read_sql(query)

# 11. Avg quantity of food claimed per receiver
def get_avg_claim_quantity():
    query = """
    SELECT r.name AS Name, r.city AS City, ROUND(AVG(f.quantity), 1) AS Avg_Quantity, COUNT(c.claim_id) AS Total_Claims
    FROM claims c
    JOIN food_listings f ON c.food_id = f.food_id
    JOIN receivers r ON c.receiver_id = r.receiver_id
    GROUP BY r.name, r.city
    ORDER BY Avg_Quantity DESC
    LIMIT 10
    """
    return safe_read_sql(query)

# 12. Most claimed meal type
def get_top_meal_type():
    query = """
    SELECT f.meal_type AS Meal_Type, COUNT(c.claim_id) AS Total_Claims
    FROM claims c
    JOIN food_listings f ON c.food_id = f.food_id
    GROUP BY f.meal_type
    ORDER BY Total_Claims DESC
    """
    return safe_read_sql(query)

# 13. Total quantity of food donated by provider
def get_quantity_by_provider():
    query = """
    SELECT p.name AS Name, p.city AS City, p.type AS Type, SUM(f.quantity) AS Total_Quantity
    FROM food_listings f
    JOIN providers p ON f.provider_id = p.provider_id
    GROUP BY p.name, p.city, p.type
    ORDER BY Total_Quantity DESC
    LIMIT 15
    """
    return safe_read_sql(query)
