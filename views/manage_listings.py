import streamlit as st
import sqlite3
import os
import pandas as pd
from datetime import date, timedelta
import queries

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "food_waste.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_next_food_id():
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT COALESCE(MAX(Food_ID), 0) + 1 FROM food_listings")
        nid  = cur.fetchone()[0]
        conn.close()
        return int(nid)
    except Exception:
        return 1001

def _success(msg): st.success(f"✅ {msg}")
def _error(msg):   st.error(f"❌ {msg}")
def _warn(msg):    st.warning(f"⚠️ {msg}")

def _show_db_status():
    try:
        conn = get_connection()
        cur  = conn.cursor()
        tables = {t[0]: cur.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
                  for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        rows_html = "".join([
            f"<div style='text-align:center'>"
            f"<div style='color:white;font-weight:800;font-size:1.1rem'>{v:,}</div>"
            f"<div style='color:#6ee7b7;font-size:0.7rem;text-transform:uppercase'>{k}</div>"
            f"</div>"
            for k, v in tables.items()
        ])
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#064e3b,#065f46);border-radius:14px;
                    padding:16px 22px;margin-bottom:20px;display:flex;align-items:center;
                    gap:20px;flex-wrap:wrap'>
            <div style='display:flex;align-items:center;gap:8px'>
                <div style='width:10px;height:10px;background:#34d399;border-radius:50%'></div>
                <span style='color:#a7f3d0;font-weight:700;font-size:0.85rem'>DATABASE CONNECTED</span>
            </div>
            <div style='color:#6ee7b7;font-size:0.75rem'>📂 {DB_PATH}</div>
            <div style='display:flex;gap:16px;flex-wrap:wrap;margin-left:auto'>{rows_html}</div>
        </div>
        """, unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"❌ **Database Error**: {e}\n\n**DB Path**: `{DB_PATH}`")
        return False

def display():
    st.markdown("""
    <div class='page-header'>
        <div class='badge'>⚙️ CRUD Operations</div>
        <h1>⚙️ Manage Food Listings</h1>
        <p>Add new donations, update existing records, delete expired listings, or quickly claim food for a receiver.</p>
    </div>
    """, unsafe_allow_html=True)

    db_ok = _show_db_status()
    if not db_ok:
        st.stop()

    tab_add, tab_update, tab_delete, tab_claim, tab_browse = st.tabs([
        "➕  Add New",
        "✏️  Update",
        "🗑️  Delete",
        "🤝  Claim Food",
        "📋  Browse All"
    ])

    # ── ADD ──────────────────────────────────────────────────────────────────
    with tab_add:
        st.markdown("<div class='section-card'><h3>➕ Post New Food Donation</h3>", unsafe_allow_html=True)
        st.info("💡 **Sample values are pre-filled.** Change any field and click 'Add Listing'.")

        suggested_id  = get_next_food_id()
        default_expiry = date.today() + timedelta(days=3)

        with st.form("add_form"):
            r1c1, r1c2 = st.columns([1, 2])
            with r1c1:
                food_id = st.number_input("Food ID (auto-suggested)",
                    min_value=1, value=suggested_id,
                    help="Auto-suggested next available ID")
            with r1c2:
                food_name = st.text_input("Food Name *", value="Vegetable Biryani",
                    placeholder="e.g. Biryani, Pasta, Sandwiches")

            r2c1, r2c2, r2c3 = st.columns(3)
            with r2c1:
                quantity = st.number_input("Quantity (units) *", min_value=1, value=25,
                    help="Number of meal portions or packets")
            with r2c2:
                expiry = st.date_input("Expiry Date *", value=default_expiry, min_value=date.today())
            with r2c3:
                provider_id = st.number_input("Provider ID", min_value=1, value=101,
                    help="ID of the food donor from providers table")

            r3c1, r3c2, r3c3 = st.columns(3)
            with r3c1:
                provider_type = st.selectbox("Provider Type *",
                    ["Restaurant", "Household", "Supermarket", "Caterer", "Hotel", "Other"])
            with r3c2:
                location = st.text_input("City / Location *", value="Mumbai",
                    placeholder="e.g. Mumbai, Delhi, Pune")
            with r3c3:
                food_type = st.selectbox("Food Type *",
                    ["Vegetarian", "Non-Vegetarian", "Vegan"])

            meal_type = st.selectbox("Meal Type *",
                ["Breakfast", "Lunch", "Dinner", "Snacks"], index=1)

            _, submit_col = st.columns([3, 1])
            with submit_col:
                submit = st.form_submit_button("🚀 Add Listing", use_container_width=True)

        if submit:
            if not food_name.strip() or not location.strip():
                _error("Food Name and Location are required fields.")
            else:
                conn = get_connection()
                try:
                    conn.cursor().execute(
                        """INSERT INTO food_listings
                        (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID,
                         Provider_Type, Location, Food_Type, Meal_Type)
                        VALUES (?,?,?,?,?,?,?,?,?)""",
                        (food_id, food_name.strip(), quantity, str(expiry),
                         provider_id, provider_type, location.strip(), food_type, meal_type)
                    )
                    conn.commit()
                    _success(f"Food item **'{food_name}'** (ID: {food_id}) posted! "
                             f"Quantity: {quantity} units, Location: {location}")
                    st.balloons()
                except sqlite3.IntegrityError:
                    _error(f"Food ID **{food_id}** already exists. "
                           f"The next available ID is **{suggested_id}**.")
                finally:
                    conn.close()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── UPDATE ───────────────────────────────────────────────────────────────
    with tab_update:
        st.markdown("<div class='section-card'><h3>✏️ Update Existing Listing</h3>", unsafe_allow_html=True)
        st.info("💡 Enter any Food ID (try **1**, **2**, or **5**) to load and edit the existing record.")

        food_id_upd = st.number_input("🔍 Food ID to look up:", min_value=1, value=1, key="upd_id")
        item = queries.get_food_item_by_id(food_id_upd)

        if item:
            st.markdown(f"""
            <div style='background:#f0fdf4;border-radius:12px;padding:16px;
                        border:1px solid #d1fae5;margin-bottom:16px'>
                <div style='font-weight:700;color:#064e3b;font-size:1rem;margin-bottom:8px'>
                    📦 Currently: <span style='color:#16a34a'>{item.get("Food_Name","?")}</span>
                    &nbsp;(ID: {food_id_upd})
                </div>
                <div style='display:flex;gap:16px;flex-wrap:wrap;font-size:0.82rem;color:#6b7280'>
                    <span>📍 {item.get("Location","?")}</span>
                    <span>🥗 {item.get("Food_Type","?")}</span>
                    <span>🕐 {item.get("Meal_Type","?")}</span>
                    <span>📦 Qty: <b style='color:#064e3b'>{item.get("Quantity","?")}</b></span>
                    <span>⏰ Expires: {str(item.get("Expiry_Date","?"))[:10]}</span>
                </div>
            </div>""", unsafe_allow_html=True)

            field = st.selectbox("🔧 Field to update:",
                ["Quantity", "Expiry_Date", "Meal_Type", "Food_Type", "Location"])

            if field == "Food_Type":
                current = item.get("Food_Type", "Vegetarian")
                opts = ["Vegetarian", "Non-Vegetarian", "Vegan"]
                new_value = st.selectbox("New Food Type:", opts,
                    index=opts.index(current) if current in opts else 0)
            elif field == "Meal_Type":
                current = item.get("Meal_Type", "Lunch")
                opts = ["Breakfast", "Lunch", "Dinner", "Snacks"]
                new_value = st.selectbox("New Meal Type:", opts,
                    index=opts.index(current) if current in opts else 1)
            elif field == "Expiry_Date":
                new_value = str(st.date_input("New Expiry Date:",
                    value=date.today() + timedelta(days=5), min_value=date.today()))
            elif field == "Quantity":
                curr_qty = int(item.get("Quantity", 10))
                new_value = str(st.number_input("New Quantity:", min_value=1, value=curr_qty))
            else:
                new_value = st.text_input(f"New value for {field}:",
                    value=str(item.get(field, "")))

            if st.button("💾 Save Changes", key="update_btn"):
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(f"UPDATE food_listings SET {field} = ? WHERE Food_ID = ?",
                            (new_value, food_id_upd))
                if cur.rowcount > 0:
                    conn.commit()
                    _success(f"Food ID **{food_id_upd}** updated → `{field}` = `{new_value}`")
                else:
                    _warn("No changes made. Food ID not found.")
                conn.close()
        else:
            st.info("💡 Enter a valid Food ID (1–1000) to load the record for editing.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── DELETE ───────────────────────────────────────────────────────────────
    with tab_delete:
        st.markdown("<div class='section-card'><h3>🗑️ Remove a Food Listing</h3>", unsafe_allow_html=True)
        st.warning("⚠️ **For interview demo**: Enter ID **1001** or any ID you just added. Avoid deleting core data (IDs 1–1000).")

        food_id_del = st.number_input("🔍 Food ID to delete:", min_value=1, value=1001, key="del_id")
        item_del = queries.get_food_item_by_id(food_id_del)

        if item_del:
            st.markdown(f"""
            <div style='background:#fef2f2;border-radius:12px;padding:16px;
                        border:1px solid #fecaca;margin-bottom:16px'>
                <div style='font-weight:700;color:#991b1b;font-size:0.85rem;margin-bottom:6px'>
                    ⚠️ This listing will be permanently removed:
                </div>
                <div style='font-weight:700;color:#064e3b;font-size:1rem;margin-bottom:4px'>
                    🍽️ {item_del.get("Food_Name","?")} &nbsp;(ID: {food_id_del})
                </div>
                <div style='font-size:0.82rem;color:#6b7280'>
                    📍 {item_del.get("Location","?")} &nbsp;|&nbsp;
                    Qty: {item_del.get("Quantity","?")} &nbsp;|&nbsp;
                    Type: {item_del.get("Food_Type","?")}
                </div>
            </div>""", unsafe_allow_html=True)

            confirm = st.checkbox("✅ I confirm I want to permanently delete this listing")
            if st.button("🗑️ Delete Now", key="del_btn"):
                if confirm:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM food_listings WHERE Food_ID = ?", (food_id_del,))
                    conn.commit()
                    conn.close()
                    _success(f"Food listing **ID {food_id_del}** (`{item_del.get('Food_Name')}`) deleted.")
                else:
                    _warn("Please tick the confirmation checkbox first.")
        else:
            st.info("💡 Enter a valid Food ID to preview the record before deletion.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── CLAIM ────────────────────────────────────────────────────────────────
    with tab_claim:
        st.markdown("<div class='section-card'><h3>🤝 Register a New Claim</h3>", unsafe_allow_html=True)
        st.info("💡 **Demo**: Food ID **5** = Soup (14 units, Vegan). Select any receiver and click Register.")

        cl1, cl2 = st.columns(2)
        with cl1:
            claim_food_id = st.number_input("🍱 Food ID to claim:", min_value=1, value=5, key="claim_fid")
            food_preview = queries.get_food_item_by_id(claim_food_id)
            if food_preview:
                st.markdown(f"""
                <div style='font-size:0.85rem;color:#065f46;background:#f0fdf4;padding:12px;
                            border-radius:10px;border:1px solid #d1fae5;margin-top:4px'>
                    <b>🍽️ {food_preview.get('Food_Name','?')}</b><br>
                    📦 {food_preview.get('Quantity','?')} units available<br>
                    📍 {food_preview.get('Location','?')} &nbsp;•&nbsp;
                    🥗 {food_preview.get('Food_Type','?')} &nbsp;•&nbsp;
                    🕐 {food_preview.get('Meal_Type','?')}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div style='font-size:0.8rem;color:#9ca3af;padding:8px'>⚠️ Invalid Food ID</div>",
                    unsafe_allow_html=True)

        with cl2:
            receivers_all = queries.get_all_receivers()
            if not receivers_all.empty:
                recv_options = {
                    f"{row['Name']} — {row['City']} ({row['Type']})": row['Receiver_ID']
                    for _, row in receivers_all.head(100).iterrows()
                }
                selected_recv = st.selectbox("🤝 Select Receiver:", list(recv_options.keys()))
                claim_recv_id = recv_options[selected_recv]
                st.caption(f"Receiver ID: {claim_recv_id}")
            else:
                claim_recv_id = st.number_input("Receiver ID:", min_value=1, value=1)
                selected_recv = f"ID {claim_recv_id}"

        claim_status = st.selectbox("📊 Claim Status:", ["Completed", "Pending"], index=0)

        if st.button("✅ Register Claim", key="claim_btn"):
            if food_preview is None:
                _error("Please enter a valid Food ID first.")
            else:
                try:
                    new_cid = queries.claim_food_item(claim_food_id, claim_recv_id, claim_status)
                    _success(f"Claim **#{new_cid}** registered! "
                             f"{food_preview.get('Food_Name')} → {selected_recv} → Status: {claim_status}")
                    st.balloons()
                except Exception as e:
                    _error(f"Failed: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── BROWSE ───────────────────────────────────────────────────────────────
    with tab_browse:
        st.markdown("<div class='section-card'><h3>📋 Browse All Food Listings</h3>", unsafe_allow_html=True)

        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            b_search = st.text_input("🔎 Search:", placeholder="Name, city, provider...", key="browse_search")
        with bc2:
            b_ftype = st.selectbox("Food Type:", ["All", "Vegetarian", "Non-Vegetarian", "Vegan"], key="browse_ft")
        with bc3:
            b_mtype = st.selectbox("Meal Type:", ["All", "Breakfast", "Lunch", "Dinner", "Snacks"], key="browse_mt")

        browse_df = queries.get_all_food_listings(
            food_type=b_ftype if b_ftype != "All" else None,
            meal_type=b_mtype if b_mtype != "All" else None,
            search_query=b_search.strip() if b_search.strip() else None
        )

        st.markdown(
            f"<p style='color:#6b7280;font-size:0.85rem;margin-bottom:8px'>"
            f"Showing <b>{len(browse_df):,}</b> listings from database</p>",
            unsafe_allow_html=True
        )

        display_df = browse_df.copy()
        display_df.columns = [c.replace('_', ' ') for c in display_df.columns]
        st.dataframe(display_df, use_container_width=True, height=420)

        if not browse_df.empty:
            csv = browse_df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Export CSV", csv, "food_listings_export.csv", "text/csv")

        st.markdown("</div>", unsafe_allow_html=True)
