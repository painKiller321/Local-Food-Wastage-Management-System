import streamlit as st
import pandas as pd
from datetime import date, timedelta
import queries

def _success(msg): st.success(f"✅ {msg}")
def _error(msg):   st.error(f"❌ {msg}")
def _warn(msg):    st.warning(f"⚠️ {msg}")

def _show_db_status():
    status = queries.get_db_status()
    if not status["ok"]:
        st.error(f"❌ **Database Connection Error**: {status.get('error')}")
        return False
    
    counts = status["counts"]
    cloud_badge = "🌐 LIVE CLOUD DB" if status["is_cloud"] else "💻 LOCAL DB (Offline Mode)"
    badge_bg = "#047857" if status["is_cloud"] else "#065f46"
    
    rows_html = "".join([
        f"<div style='text-align:center'>"
        f"<div style='color:white;font-weight:800;font-size:1.1rem'>{v:,}</div>"
        f"<div style='color:#6ee7b7;font-size:0.7rem;text-transform:uppercase'>{k}</div>"
        f"</div>"
        for k, v in counts.items()
    ])
    
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#064e3b,#065f46);border-radius:14px;
                padding:16px 22px;margin-bottom:20px;display:flex;align-items:center;
                gap:20px;flex-wrap:wrap'>
        <div style='display:flex;align-items:center;gap:8px'>
            <div style='width:10px;height:10px;background:#34d399;border-radius:50%'></div>
            <span style='background:{badge_bg};color:#a7f3d0;padding:3px 8px;border-radius:6px;font-weight:700;font-size:0.78rem'>{cloud_badge}</span>
        </div>
        <div style='color:#a7f3d0;font-size:0.75rem'>🔌 Engine: <b>{status['db_type']}</b> ({status['url']})</div>
        <div style='display:flex;gap:16px;flex-wrap:wrap;margin-left:auto'>{rows_html}</div>
    </div>
    """, unsafe_allow_html=True)
    return True

def display():
    st.markdown("""
    <div class='page-header'>
        <div class='badge'>🌍 Global Restaurant Network</div>
        <h1>⚙️ Manage Food & Leftover Listings</h1>
        <p>Any restaurant or food provider from any city globally can post surplus food, update remaining leftover quantities, or claim donations in real time.</p>
    </div>
    """, unsafe_allow_html=True)

    db_ok = _show_db_status()
    if not db_ok:
        st.stop()

    tab_add, tab_update, tab_delete, tab_claim, tab_browse = st.tabs([
        "➕  Post Surplus Food",
        "✏️  Update Leftover Status",
        "🗑️  Delete Listing",
        "🤝  Claim Food",
        "📋  Live Global Inventory"
    ])

    # ── TAB 1: POST SURPLUS FOOD (ANY RESTAURANT, ANY CITY) ──────────────────────
    with tab_add:
        st.markdown("<div class='section-card'><h3>➕ Post Surplus / Leftover Food</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#6b7280;font-size:0.88rem'>Whether you are a restaurant in Mumbai, New York, Tokyo, London, or any local town, add extra food here so it immediately appears live for NGOs and communities.</p>", unsafe_allow_html=True)

        providers_df = queries.get_all_providers()
        prov_mode = st.radio("🏢 Restaurant / Provider Identity:", 
                             ["Select Existing Registered Provider", "➕ Register New Restaurant / Provider"],
                             horizontal=True)

        provider_id = None
        provider_name = ""
        provider_type = "Restaurant"
        location = ""

        if prov_mode == "Select Existing Registered Provider":
            if not providers_df.empty:
                # Build lookup dictionary
                prov_dict = {
                    f"{row['Name']} — {row['City']} ({row['Type']}) [ID: {row['Provider_ID']}]": row
                    for _, row in providers_df.iterrows()
                }
                selected_label = st.selectbox("Search & Select Restaurant / Provider:", list(prov_dict.keys()))
                sel_row = prov_dict[selected_label]
                provider_id = int(sel_row['Provider_ID'])
                provider_name = sel_row['Name']
                provider_type = sel_row['Type']
                location = sel_row['City']
                st.caption(f"📍 Location: **{location}** | 📞 Contact: **{sel_row['Contact']}**")
            else:
                st.warning("No existing providers found in database. Please register as a new restaurant below.")
                prov_mode = "➕ Register New Restaurant / Provider"

        if prov_mode == "➕ Register New Restaurant / Provider":
            st.markdown("<div style='background:#f0fdf4;padding:14px;border-radius:10px;border:1px dashed #34d399;margin-bottom:12px'>", unsafe_allow_html=True)
            st.markdown("<h4 style='margin:0 0 8px 0;color:#065f46'>📝 New Restaurant / Provider Details</h4>", unsafe_allow_html=True)
            np_c1, np_c2 = st.columns(2)
            with np_c1:
                new_prov_name = st.text_input("Restaurant / Business Name *", placeholder="e.g. Olive Garden, Saravanaa Bhavan, Subway")
                new_prov_type = st.selectbox("Provider Category *", ["Restaurant", "Hotel / Resort", "Caterer", "Bakery", "Supermarket", "Household", "Other"])
            with np_c2:
                new_prov_city = st.text_input("City / Town / Global Region *", placeholder="e.g. Paris, Chicago, Bengaluru, Dubai")
                new_prov_contact = st.text_input("Phone / WhatsApp / Email *", placeholder="e.g. +1-555-0199 or info@restaurant.com")
            new_prov_addr = st.text_input("Street Address / Landmark (Optional)", placeholder="e.g. 124 Main Street, Downtown")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<h4 style='color:#065f46;margin-top:10px'>🍱 Food Details</h4>", unsafe_allow_html=True)
        default_expiry = date.today() + timedelta(days=2)

        with st.form("add_food_form"):
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                food_name = st.text_input("Food Item Name *", placeholder="e.g. Vegetable Biryani, Assorted Sandwiches, Fresh Croissants")
            with f_col2:
                quantity = st.number_input("Quantity (Portions / Meals / Packets) *", min_value=1, value=20)

            c_type1, c_type2, c_type3 = st.columns(3)
            with c_type1:
                food_type = st.selectbox("Dietary Type *", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            with c_type2:
                meal_type = st.selectbox("Meal Category *", ["Lunch", "Dinner", "Breakfast", "Snacks"])
            with c_type3:
                expiry = st.date_input("Expiry / Best Before Date *", value=default_expiry, min_value=date.today())

            food_location = st.text_input("City / Pickup Location *", value=location, placeholder="e.g. Mumbai, Berlin, Singapore")

            submit_food = st.form_submit_button("🚀 Publish Food Listing to Live Network", use_container_width=True)

        if submit_food:
            if not food_name.strip():
                _error("Food Item Name is required.")
            elif not food_location.strip():
                _error("City / Pickup Location is required.")
            else:
                try:
                    # Register new provider if required
                    if prov_mode == "➕ Register New Restaurant / Provider":
                        if not new_prov_name.strip() or not new_prov_city.strip() or not new_prov_contact.strip():
                            _error("Please fill in Restaurant Name, City, and Contact information.")
                            st.stop()
                        provider_id = queries.register_provider(
                            name=new_prov_name,
                            ptype=new_prov_type,
                            city=new_prov_city,
                            contact=new_prov_contact,
                            address=new_prov_addr
                        )
                        provider_type = new_prov_type
                        provider_name = new_prov_name
                        food_location = food_location or new_prov_city

                    # Add food listing
                    new_food_id = queries.add_food_listing(
                        food_name=food_name,
                        quantity=quantity,
                        expiry_date=expiry,
                        provider_id=provider_id,
                        provider_type=provider_type,
                        location=food_location,
                        food_type=food_type,
                        meal_type=meal_type
                    )

                    _success(f"🎉 **Listing Published Live!** Food item **'{food_name}'** (ID: {new_food_id}) is now visible worldwide.")
                    st.info(f"📍 **Location:** {food_location} | 🏢 **Provider:** {provider_name} | 📦 **Quantity:** {quantity} units | ⏰ **Expiry:** {expiry}")
                    st.balloons()
                except Exception as e:
                    _error(f"Failed to publish food listing: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 2: UPDATE LEFTOVER FOOD STATUS (GLOBAL UPDATES) ──────────────────────
    with tab_update:
        st.markdown("<div class='section-card'><h3>✏️ Live Leftover Status Update</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#6b7280;font-size:0.88rem'>Restaurants can update their leftover quantities at any time — as food is given away, portions decrease, or extra surplus becomes available.</p>", unsafe_allow_html=True)

        lookup_mode = st.radio("Find listing to update by:", ["🔍 Search by Food / City / Restaurant", "🔢 Direct Food ID"], horizontal=True)

        target_food_id = None
        if lookup_mode == "🔢 Direct Food ID":
            target_food_id = st.number_input("Enter Food ID:", min_value=1, value=1, step=1)
        else:
            srch_term = st.text_input("Type Food Name, Restaurant, or City:", placeholder="e.g. Biryani, Pizza, Mumbai, Salad")
            if srch_term.strip():
                matches = queries.get_all_food_listings(search_query=srch_term.strip())
                if not matches.empty:
                    opts = {
                        f"ID {r['Food_ID']}: {r['Food_Name']} ({r['Quantity']} units) — {r['Location']} ({r.get('Provider_Name') or r.get('Provider_Type')})": int(r['Food_ID'])
                        for _, r in matches.head(25).iterrows()
                    }
                    selected_match = st.selectbox("Select Listing to Edit:", list(opts.keys()))
                    target_food_id = opts[selected_match]
                else:
                    st.info("No matching food listings found. Try another search term.")
            else:
                st.caption("💡 Enter search term above or switch to Direct Food ID.")

        if target_food_id:
            item = queries.get_food_item_by_id(target_food_id)
            if item:
                st.markdown(f"""
                <div style='background:#f0fdf4;border-radius:12px;padding:16px;
                            border:1px solid #d1fae5;margin:16px 0'>
                    <div style='font-weight:700;color:#064e3b;font-size:1.1rem;margin-bottom:6px'>
                        🍱 {item.get('Food_Name')} <span style='font-size:0.85rem;color:#6b7280'>(Food ID: #{target_food_id})</span>
                    </div>
                    <div style='display:flex;gap:18px;flex-wrap:wrap;font-size:0.85rem;color:#374151'>
                        <span>🏢 <b>Provider:</b> {item.get('Provider_Name') or item.get('Provider_Type')}</span>
                        <span>📍 <b>City:</b> {item.get('Location')}</span>
                        <span>📦 <b>Available:</b> <b style='color:#16a34a'>{item.get('Quantity')} units</b></span>
                        <span>🥗 <b>Type:</b> {item.get('Food_Type')}</span>
                        <span>🕐 <b>Meal:</b> {item.get('Meal_Type')}</span>
                        <span>⏰ <b>Expiry:</b> {str(item.get('Expiry_Date'))[:10]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("#### ⚡ Quick Leftover Actions")
                qcol1, qcol2 = st.columns(2)
                with qcol1:
                    new_leftover_qty = st.number_input("Update Remaining Leftover Portions:", min_value=0, value=int(item.get('Quantity', 0)), step=1)
                    if st.button("💾 Update Leftover Quantity", use_container_width=True):
                        try:
                            queries.update_food_listing_field(target_food_id, "Quantity", new_leftover_qty)
                            _success(f"Updated Food #{target_food_id} leftover quantity to **{new_leftover_qty} units**.")
                            st.rerun()
                        except Exception as e:
                            _error(f"Error: {e}")

                with qcol2:
                    st.write("Mark Listing Status:")
                    if st.button("🛑 Mark as All Claimed / Out of Stock (0 units)", use_container_width=True):
                        try:
                            queries.update_food_listing_field(target_food_id, "Quantity", 0)
                            _success(f"Food #{target_food_id} marked as Out of Stock.")
                            st.rerun()
                        except Exception as e:
                            _error(f"Error: {e}")

                st.markdown("---")
                st.markdown("#### ✏️ Update Other Details")
                field_to_edit = st.selectbox("Select detail to edit:", ["Food_Name", "Expiry_Date", "Food_Type", "Meal_Type", "Location"])

                if field_to_edit == "Food_Type":
                    current_ft = item.get("Food_Type", "Vegetarian")
                    ft_opts = ["Vegetarian", "Non-Vegetarian", "Vegan"]
                    new_val = st.selectbox("New Food Type:", ft_opts, index=ft_opts.index(current_ft) if current_ft in ft_opts else 0)
                elif field_to_edit == "Meal_Type":
                    current_mt = item.get("Meal_Type", "Lunch")
                    mt_opts = ["Breakfast", "Lunch", "Dinner", "Snacks"]
                    new_val = st.selectbox("New Meal Type:", mt_opts, index=mt_opts.index(current_mt) if current_mt in mt_opts else 1)
                elif field_to_edit == "Expiry_Date":
                    new_val = str(st.date_input("New Expiry Date:", value=date.today() + timedelta(days=2), min_value=date.today()))
                elif field_to_edit == "Location":
                    new_val = st.text_input("New City / Location:", value=str(item.get("Location", "")))
                else:
                    new_val = st.text_input("New Food Name:", value=str(item.get("Food_Name", "")))

                if st.button("💾 Save Field Update"):
                    try:
                        queries.update_food_listing_field(target_food_id, field_to_edit, new_val)
                        _success(f"Food ID **{target_food_id}** updated → `{field_to_edit}` = `{new_val}`")
                        st.rerun()
                    except Exception as e:
                        _error(f"Update failed: {e}")
            else:
                st.info(f"Food item with ID #{target_food_id} was not found.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 3: DELETE LISTING ──────────────────────────────────────────────────
    with tab_delete:
        st.markdown("<div class='section-card'><h3>🗑️ Remove Food Listing</h3>", unsafe_allow_html=True)
        food_id_del = st.number_input("Enter Food ID to delete:", min_value=1, value=1001, key="del_id")
        item_del = queries.get_food_item_by_id(food_id_del)

        if item_del:
            st.markdown(f"""
            <div style='background:#fef2f2;border-radius:12px;padding:16px;border:1px solid #fecaca;margin-bottom:16px'>
                <div style='font-weight:700;color:#991b1b;font-size:0.9rem;margin-bottom:4px'>
                    ⚠️ You are about to permanently delete:
                </div>
                <div style='font-weight:700;color:#064e3b;font-size:1.05rem'>
                    🍱 {item_del.get("Food_Name")} &nbsp;(ID: #{food_id_del})
                </div>
                <div style='font-size:0.85rem;color:#6b7280;margin-top:4px'>
                    📍 {item_del.get("Location")} | 📦 Qty: {item_del.get("Quantity")} units | 🏢 {item_del.get("Provider_Name") or item_del.get("Provider_Type")}
                </div>
            </div>""", unsafe_allow_html=True)

            confirm = st.checkbox("✅ Yes, permanently delete this listing from database")
            if st.button("🗑️ Delete Listing Now", key="del_btn"):
                if confirm:
                    try:
                        queries.delete_food_listing(food_id_del)
                        _success(f"Food listing **ID {food_id_del}** (`{item_del.get('Food_Name')}`) has been deleted.")
                    except Exception as e:
                        _error(f"Failed to delete: {e}")
                else:
                    _warn("Please check the confirmation box first.")
        else:
            st.info(f"Listing ID #{food_id_del} not found in database.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 4: CLAIM FOOD ──────────────────────────────────────────────────────
    with tab_claim:
        st.markdown("<div class='section-card'><h3>🤝 Register a Food Claim</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#6b7280;font-size:0.85rem'>Receivers, NGOs, and food banks can claim surplus food for distribution.</p>", unsafe_allow_html=True)

        cl1, cl2 = st.columns(2)
        with cl1:
            claim_food_id = st.number_input("🍱 Food ID to claim:", min_value=1, value=5, key="claim_fid")
            food_preview = queries.get_food_item_by_id(claim_food_id)
            if food_preview:
                st.markdown(f"""
                <div style='font-size:0.85rem;color:#065f46;background:#f0fdf4;padding:12px;
                            border-radius:10px;border:1px solid #d1fae5;margin-top:4px'>
                    <b>🍽️ {food_preview.get('Food_Name')}</b><br>
                    📦 {food_preview.get('Quantity')} units available<br>
                    📍 {food_preview.get('Location')} &nbsp;•&nbsp;
                    🥗 {food_preview.get('Food_Type')} &nbsp;•&nbsp;
                    🕐 {food_preview.get('Meal_Type')}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div style='font-size:0.8rem;color:#9ca3af;padding:8px'>⚠️ Invalid Food ID</div>", unsafe_allow_html=True)

        with cl2:
            receivers_all = queries.get_all_receivers()
            if not receivers_all.empty:
                recv_options = {
                    f"{row['Name']} — {row['City']} ({row['Type']})": int(row['Receiver_ID'])
                    for _, row in receivers_all.head(100).iterrows()
                }
                selected_recv = st.selectbox("🤝 Select Receiver Organization:", list(recv_options.keys()))
                claim_recv_id = recv_options[selected_recv]
            else:
                claim_recv_id = st.number_input("Receiver ID:", min_value=1, value=1)
                selected_recv = f"ID {claim_recv_id}"

        claim_status = st.selectbox("📊 Claim Status:", ["Completed", "Pending"], index=0)

        if st.button("✅ Confirm Claim Registration", key="claim_btn"):
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

    # ── TAB 5: BROWSE ALL ──────────────────────────────────────────────────────
    with tab_browse:
        st.markdown("<div class='section-card'><h3>📋 Live Global Inventory</h3>", unsafe_allow_html=True)

        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            b_search = st.text_input("🔎 Search by Name, City, or Provider:", placeholder="e.g. Rice, Tokyo, Hilton...", key="browse_search")
        with bc2:
            b_ftype = st.selectbox("Dietary Type:", ["All", "Vegetarian", "Non-Vegetarian", "Vegan"], key="browse_ft")
        with bc3:
            b_mtype = st.selectbox("Meal Category:", ["All", "Breakfast", "Lunch", "Dinner", "Snacks"], key="browse_mt")

        browse_df = queries.get_all_food_listings(
            food_type=b_ftype if b_ftype != "All" else None,
            meal_type=b_mtype if b_mtype != "All" else None,
            search_query=b_search.strip() if b_search.strip() else None
        )

        st.markdown(
            f"<p style='color:#6b7280;font-size:0.85rem;margin-bottom:8px'>"
            f"Showing <b>{len(browse_df):,}</b> live listings from database</p>",
            unsafe_allow_html=True
        )

        display_df = browse_df.copy()
        display_df.columns = [c.replace('_', ' ') for c in display_df.columns]
        st.dataframe(display_df, use_container_width=True, height=420)

        if not browse_df.empty:
            csv = browse_df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Export Live CSV", csv, "live_food_listings.csv", "text/csv")

        st.markdown("</div>", unsafe_allow_html=True)
