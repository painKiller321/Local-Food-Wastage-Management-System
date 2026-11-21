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
    cloud_badge = "🌐 LIVE CLOUD DB (Neon PostgreSQL)" if status["is_cloud"] else "💻 LOCAL DB (Offline SQLite)"
    badge_bg = "#059669" if status["is_cloud"] else "#0284c7"
    
    rows_html = "".join([
        f"<div style='text-align:center'>"
        f"<div style='color:white;font-weight:800;font-size:1.15rem'>{v:,}</div>"
        f"<div style='color:#a7f3d0;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.04em'>{k}</div>"
        f"</div>"
        for k, v in counts.items()
    ])
    
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#064e3b,#065f46);border-radius:16px;
                padding:18px 24px;margin-bottom:24px;display:flex;align-items:center;
                gap:20px;flex-wrap:wrap;box-shadow:0 4px 15px rgba(6,78,59,0.15)'>
        <div style='display:flex;align-items:center;gap:10px'>
            <div style='width:12px;height:12px;background:#34d399;border-radius:50%;box-shadow:0 0 10px #34d399'></div>
            <span style='background:{badge_bg};color:white;padding:4px 10px;border-radius:8px;font-weight:700;font-size:0.78rem'>{cloud_badge}</span>
        </div>
        <div style='color:#d1fae5;font-size:0.78rem'>🔌 Engine: <b>{status['db_type']}</b> &nbsp;•&nbsp; Status: <b>Online</b></div>
        <div style='display:flex;gap:20px;flex-wrap:wrap;margin-left:auto'>{rows_html}</div>
    </div>
    """, unsafe_allow_html=True)
    return True

def display():
    st.markdown("""
    <div class='page-header'>
        <div class='badge'>⚙️ Inventory & Operations</div>
        <h1>⚙️ Manage Food Listings & Distribution</h1>
        <p>Post fresh surplus food, update real-time leftover quantities, fulfill charity claims, and manage the live database.</p>
    </div>
    """, unsafe_allow_html=True)

    db_ok = _show_db_status()
    if not db_ok:
        st.stop()

    tab_add, tab_update, tab_delete, tab_claim, tab_browse = st.tabs([
        "➕  Post Surplus Food",
        "✏️  Update Leftover Status",
        "🗑️  Delete Listing",
        "🤝  Fulfill Charity Claim",
        "📋  Live Global Inventory"
    ])

    # ── TAB 1: POST SURPLUS FOOD ────────────────────────────────────────────────
    with tab_add:
        st.markdown("<div class='section-card'><h3>➕ Post Surplus / Leftover Food</h3>", unsafe_allow_html=True)
        st.caption("Whether you are a restaurant, hotel, caterer, or bakery, add available food items here so charities can claim them immediately.")

        providers_df = queries.get_all_providers()
        prov_mode = st.radio(
            "🏢 Provider Account:", 
            ["Select Existing Registered Provider", "➕ Register New Restaurant / Provider"],
            horizontal=True
        )

        provider_id = None
        provider_name = ""
        provider_type = "Restaurant"
        location = ""

        if prov_mode == "Select Existing Registered Provider":
            if not providers_df.empty:
                prov_dict = {
                    f"{row['Name']} — {row['City']} ({row['Type']}) [ID: {row['Provider_ID']}]": row
                    for _, row in providers_df.iterrows()
                }
                selected_label = st.selectbox("Search & Select Provider:", list(prov_dict.keys()))
                sel_row = prov_dict[selected_label]
                provider_id = int(sel_row['Provider_ID'])
                provider_name = sel_row['Name']
                provider_type = sel_row['Type']
                location = sel_row['City']
                st.caption(f"📍 Location: **{location}** | 📞 Contact: **{sel_row.get('Contact', 'N/A')}**")
            else:
                st.warning("No existing providers found in database. Please register as a new provider below.")
                prov_mode = "➕ Register New Restaurant / Provider"

        if prov_mode == "➕ Register New Restaurant / Provider":
            st.markdown("<div style='background:#f0fdf4;padding:16px;border-radius:12px;border:1.5px dashed #34d399;margin-bottom:16px'>", unsafe_allow_html=True)
            st.markdown("<h4 style='margin:0 0 10px 0;color:#065f46'>📝 New Provider Registration</h4>", unsafe_allow_html=True)
            np_c1, np_c2 = st.columns(2)
            with np_c1:
                new_prov_name = st.text_input("Business / Restaurant Name *", placeholder="e.g. Green Leaf Cafe, Marriott Hotel")
                new_prov_type = st.selectbox("Category *", ["Restaurant", "Hotel / Resort", "Caterer", "Bakery", "Supermarket", "Household", "Other"])
            with np_c2:
                new_prov_city = st.text_input("City / Region *", placeholder="e.g. Springfield, Chicago, London")
                new_prov_contact = st.text_input("Phone / Contact *", placeholder="e.g. +1-555-0199 or info@business.com")
            new_prov_addr = st.text_input("Street Address / Landmark (Optional)", placeholder="e.g. 100 Main Street, Suite 4")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<h4 style='color:#065f46;margin-top:16px'>🍱 Food Listing Details</h4>", unsafe_allow_html=True)
        default_expiry = date.today() + timedelta(days=2)

        with st.form("add_food_form"):
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                food_name = st.text_input("Food Item Name *", placeholder="e.g. Vegetable Biryani, Assorted Bagels, Fresh Green Salad")
            with f_col2:
                quantity = st.number_input("Quantity (Available Portions / Meals) *", min_value=1, value=25)

            c_type1, c_type2, c_type3 = st.columns(3)
            with c_type1:
                food_type = st.selectbox("Dietary Type *", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            with c_type2:
                meal_type = st.selectbox("Meal Category *", ["Lunch", "Dinner", "Breakfast", "Snacks"])
            with c_type3:
                expiry = st.date_input("Expiry / Best Before Date *", value=default_expiry, min_value=date.today())

            food_location = st.text_input("City / Pickup Location *", value=location, placeholder="e.g. Springfield, Downtown")

            submit_food = st.form_submit_button("🚀 Publish Food Listing to Live Network", use_container_width=True)

        # Live Card Preview
        st.markdown("#### 👁️ Live Listing Preview (How charities will see this):")
        dietary_tag_class = "tag-green" if food_type == "Vegetarian" else "tag-blue" if food_type == "Vegan" else "tag-orange"
        preview_food_name = food_name.strip() if food_name.strip() else "Your Food Item Name"
        preview_prov = (new_prov_name if prov_mode != "Select Existing Registered Provider" else provider_name) or "Your Organization"
        preview_loc = food_location.strip() or location or "City Location"
        
        st.markdown(f"""
        <div style='background:white;border-radius:16px;padding:20px;border:1px solid #d1fae5;
                    box-shadow:0 4px 15px rgba(5,150,105,0.08);max-width:480px;margin-bottom:16px'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px'>
                <div style='font-weight:700;font-size:1.1rem;color:#0f172a'>🍱 {preview_food_name}</div>
                <span class='chip-ok'>⚡ Available</span>
            </div>
            <div style='display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px'>
                <span class='tag {dietary_tag_class}'>{food_type}</span>
                <span class='tag tag-blue'>{meal_type}</span>
                <span class='tag tag-green'>🏢 {preview_prov}</span>
            </div>
            <div style='font-size:0.85rem;color:#475569;margin-bottom:4px'>📍 <b>Location:</b> {preview_loc}</div>
            <div style='font-size:0.85rem;color:#475569;margin-bottom:4px'>📦 <b>Available:</b> <span style='font-weight:700;color:#059669'>{quantity} portions</span></div>
            <div style='font-size:0.85rem;color:#475569'>⏰ <b>Best Before:</b> {expiry.strftime('%b %d, %Y')}</div>
        </div>
        """, unsafe_allow_html=True)

        if submit_food:
            if not food_name.strip():
                _error("Food Item Name is required.")
            elif not food_location.strip():
                _error("City / Pickup Location is required.")
            else:
                try:
                    if prov_mode == "➕ Register New Restaurant / Provider":
                        if not new_prov_name.strip() or not new_prov_city.strip() or not new_prov_contact.strip():
                            _error("Please fill in Business Name, City, and Contact number.")
                            st.stop()
                        provider_id = queries.register_provider(
                            name=new_prov_name.strip(),
                            ptype=new_prov_type,
                            city=new_prov_city.strip(),
                            contact=new_prov_contact.strip(),
                            address=new_prov_addr.strip()
                        )
                        provider_type = new_prov_type
                        provider_name = new_prov_name
                        food_location = food_location or new_prov_city

                    new_food_id = queries.add_food_listing(
                        food_name=food_name.strip(),
                        quantity=int(quantity),
                        expiry_date=expiry,
                        provider_id=provider_id,
                        provider_type=provider_type,
                        location=food_location.strip(),
                        food_type=food_type,
                        meal_type=meal_type
                    )

                    _success(f"🎉 **Listing Published!** Food item **'{food_name}'** (Listing ID: #{new_food_id}) is now active in the database.")
                    st.info(f"📍 **Location:** {food_location} | 🏢 **Provider:** {provider_name} | 📦 **Quantity:** {quantity} portions | ⏰ **Expiry:** {expiry}")
                    st.balloons()
                except Exception as e:
                    _error(f"Failed to publish food listing: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 2: UPDATE LEFTOVER STATUS ───────────────────────────────────────────
    with tab_update:
        st.markdown("<div class='section-card'><h3>✏️ Live Leftover Status Update</h3>", unsafe_allow_html=True)
        st.caption("Update remaining portion counts or edit dietary/expiry info in real time.")

        lookup_mode = st.radio("Find listing by:", ["🔍 Search by Food / City / Restaurant", "🔢 Direct Listing ID"], horizontal=True)

        target_food_id = None
        if lookup_mode == "🔢 Direct Listing ID":
            target_food_id = st.number_input("Enter Listing ID:", min_value=1, value=1, step=1)
        else:
            srch_term = st.text_input("Type Food Name, Restaurant, or City:", placeholder="e.g. Biryani, Salad, Springfield, Pizza...")
            if srch_term.strip():
                matches = queries.get_all_food_listings(search_query=srch_term.strip())
                if not matches.empty:
                    opts = {
                        f"#{r['food_id']}: {r['food_name']} ({r['quantity']} portions) — {r['location']} ({r.get('provider_name') or r.get('provider_type')})": int(r['food_id'])
                        for _, r in matches.head(25).iterrows()
                    }
                    selected_match = st.selectbox("Select Listing to Edit:", list(opts.keys()))
                    target_food_id = opts[selected_match]
                else:
                    st.info("No matching food listings found. Try a different search keyword.")
            else:
                st.caption("💡 Enter a search keyword above or switch to Direct Listing ID.")

        if target_food_id:
            item = queries.get_food_item_by_id(target_food_id)
            if item:
                curr_qty = int(item.get('quantity', 0))
                stock_chip = "<span class='chip-urgent'>⚠️ Out of Stock</span>" if curr_qty <= 0 else f"<span class='chip-ok'>{curr_qty} Available</span>"
                
                st.markdown(f"""
                <div style='background:#f8fafc;border-radius:14px;padding:18px;border:1px solid #e2e8f0;margin:16px 0'>
                    <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'>
                        <div style='font-weight:700;color:#0f172a;font-size:1.15rem'>
                            🍱 {item.get('food_name')} <span style='font-size:0.85rem;color:#64748b'>(Listing #{target_food_id})</span>
                        </div>
                        {stock_chip}
                    </div>
                    <div style='display:flex;gap:18px;flex-wrap:wrap;font-size:0.85rem;color:#334155'>
                        <span>🏢 <b>Provider:</b> {item.get('provider_name') or item.get('provider_type')}</span>
                        <span>📍 <b>City:</b> {item.get('location')}</span>
                        <span>🥗 <b>Type:</b> {item.get('food_type')}</span>
                        <span>🕐 <b>Meal:</b> {item.get('meal_type')}</span>
                        <span>⏰ <b>Expiry:</b> {str(item.get('expiry_date'))[:10]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("#### ⚡ Quick Quantity Actions")
                qcol1, qcol2, qcol3 = st.columns([1.5, 1, 1])
                with qcol1:
                    new_leftover_qty = st.number_input("Set Remaining Leftover Portions:", min_value=0, value=curr_qty, step=1)
                    if st.button("💾 Save Exact Quantity", use_container_width=True):
                        try:
                            queries.update_food_listing_field(target_food_id, "quantity", new_leftover_qty)
                            _success(f"Listing #{target_food_id} updated to **{new_leftover_qty} portions**.")
                            st.rerun()
                        except Exception as e:
                            _error(f"Error: {e}")

                with qcol2:
                    st.write("Adjustment:")
                    if st.button("➕ Add +5 Portions", use_container_width=True):
                        try:
                            queries.update_food_listing_field(target_food_id, "quantity", curr_qty + 5)
                            _success(f"Added +5 portions (Now: {curr_qty + 5}).")
                            st.rerun()
                        except Exception as e:
                            _error(f"Error: {e}")

                with qcol3:
                    st.write("Mark Depleted:")
                    if st.button("🛑 Mark Out of Stock (0)", use_container_width=True):
                        try:
                            queries.update_food_listing_field(target_food_id, "quantity", 0)
                            _success(f"Listing #{target_food_id} marked Out of Stock.")
                            st.rerun()
                        except Exception as e:
                            _error(f"Error: {e}")

                st.markdown("---")
                st.markdown("#### ✏️ Edit Other Fields")
                field_to_edit = st.selectbox("Select attribute to modify:", ["food_name", "expiry_date", "food_type", "meal_type", "location"])

                if field_to_edit == "food_type":
                    current_ft = item.get("food_type", "Vegetarian")
                    ft_opts = ["Vegetarian", "Non-Vegetarian", "Vegan"]
                    new_val = st.selectbox("New Dietary Type:", ft_opts, index=ft_opts.index(current_ft) if current_ft in ft_opts else 0)
                elif field_to_edit == "meal_type":
                    current_mt = item.get("meal_type", "Lunch")
                    mt_opts = ["Breakfast", "Lunch", "Dinner", "Snacks"]
                    new_val = st.selectbox("New Meal Category:", mt_opts, index=mt_opts.index(current_mt) if current_mt in mt_opts else 1)
                elif field_to_edit == "expiry_date":
                    new_val = str(st.date_input("New Expiry Date:", value=date.today() + timedelta(days=2), min_value=date.today()))
                elif field_to_edit == "location":
                    new_val = st.text_input("New City / Location:", value=str(item.get("location", "")))
                else:
                    new_val = st.text_input("New Food Name:", value=str(item.get("food_name", "")))

                if st.button("💾 Save Field Modification", key="save_field_btn"):
                    try:
                        queries.update_food_listing_field(target_food_id, field_to_edit, new_val)
                        _success(f"Listing #{target_food_id} updated: `{field_to_edit}` = `{new_val}`")
                        st.rerun()
                    except Exception as e:
                        _error(f"Update failed: {e}")
            else:
                st.info(f"Listing #{target_food_id} was not found.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 3: DELETE LISTING ───────────────────────────────────────────────────
    with tab_delete:
        st.markdown("<div class='section-card'><h3>🗑️ Remove Food Listing</h3>", unsafe_allow_html=True)
        st.caption("Permanently delete a food listing from the live database.")

        food_id_del = st.number_input("Enter Listing ID to delete:", min_value=1, value=1001, key="del_id")
        item_del = queries.get_food_item_by_id(food_id_del)

        if item_del:
            st.markdown(f"""
            <div style='background:#fef2f2;border-radius:14px;padding:18px;border:1px solid #fecaca;margin-bottom:16px'>
                <div style='font-weight:700;color:#991b1b;font-size:0.92rem;margin-bottom:6px'>
                    ⚠️ You are about to permanently remove this listing:
                </div>
                <div style='font-weight:700;color:#0f172a;font-size:1.1rem'>
                    🍱 {item_del.get("food_name")} &nbsp;(ID: #{food_id_del})
                </div>
                <div style='font-size:0.85rem;color:#64748b;margin-top:6px'>
                    📍 {item_del.get("location")} | 📦 Qty: {item_del.get("quantity")} portions | 🏢 {item_del.get("provider_name") or item_del.get("provider_type")}
                </div>
            </div>""", unsafe_allow_html=True)

            confirm = st.checkbox("✅ Yes, permanently delete this record from database")
            if st.button("🗑️ Delete Listing Permanently", key="del_btn"):
                if confirm:
                    try:
                        queries.delete_food_listing(food_id_del)
                        _success(f"Food listing **#{food_id_del}** (`{item_del.get('food_name')}`) has been deleted.")
                        st.rerun()
                    except Exception as e:
                        _error(f"Failed to delete: {e}")
                else:
                    _warn("Please check the confirmation box before deleting.")
        else:
            st.info(f"Listing #{food_id_del} not found in database.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 4: CLAIM FOOD (DEDUCTION ENABLED) ────────────────────────────────────
    with tab_claim:
        st.markdown("<div class='section-card'><h3>🤝 Register a Charity Claim</h3>", unsafe_allow_html=True)
        st.caption("Receiving organizations, shelters, and food banks can claim available portions. The claimed amount is automatically deducted from inventory.")

        cl1, cl2 = st.columns(2)
        with cl1:
            claim_food_id = st.number_input("🍱 Listing ID to claim:", min_value=1, value=5, key="claim_fid")
            food_preview = queries.get_food_item_by_id(claim_food_id)
            available_qty = int(food_preview.get('quantity', 0)) if food_preview else 0
            
            if food_preview:
                stock_tag = f"<span class='chip-ok'>{available_qty} In Stock</span>" if available_qty > 0 else "<span class='chip-urgent'>Out of Stock</span>"
                st.markdown(f"""
                <div style='font-size:0.85rem;color:#064e3b;background:#f0fdf4;padding:14px;
                            border-radius:12px;border:1px solid #d1fae5;margin-top:6px'>
                    <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:4px'>
                        <b>🍽️ {food_preview.get('food_name')}</b>
                        {stock_tag}
                    </div>
                    <div>📍 {food_preview.get('location')} &nbsp;•&nbsp; 🥗 {food_preview.get('food_type')} &nbsp;•&nbsp; 🕐 {food_preview.get('meal_type')}</div>
                    <div style='color:#64748b;font-size:0.78rem;margin-top:4px'>🏢 Provider: {food_preview.get('provider_name') or food_preview.get('provider_type')}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div style='font-size:0.82rem;color:#ef4444;padding:8px'>⚠️ Listing ID not found</div>", unsafe_allow_html=True)

        with cl2:
            receivers_all = queries.get_all_receivers()
            if not receivers_all.empty:
                recv_options = {
                    f"{row['Name']} — {row['City']} ({row['Type']})": int(row['Receiver_ID'])
                    for _, row in receivers_all.head(100).iterrows()
                }
                selected_recv = st.selectbox("🤝 Select Claiming Charity / Receiver:", list(recv_options.keys()))
                claim_recv_id = recv_options[selected_recv]
            else:
                claim_recv_id = st.number_input("Receiver ID:", min_value=1, value=1)
                selected_recv = f"Receiver #{claim_recv_id}"

        c_qty_col, c_st_col = st.columns(2)
        with c_qty_col:
            max_claimable = max(1, available_qty)
            claim_qty = st.number_input(
                "Portions to Claim *",
                min_value=1,
                max_value=max_claimable if available_qty > 0 else 9999,
                value=min(10, max_claimable) if available_qty > 0 else 1
            )
        with c_st_col:
            claim_status = st.selectbox("Claim Fulfillment Status:", ["Completed", "Pending"], index=0)

        if available_qty <= 0 and food_preview:
            st.warning("⚠️ This listing currently has **0 portions** available. Registering a claim may exceed listed stock.")

        if st.button("✅ Confirm & Log Claim", use_container_width=True, key="claim_btn"):
            if food_preview is None:
                _error("Please enter a valid Listing ID.")
            else:
                try:
                    new_cid = queries.claim_food_item(
                        food_id=claim_food_id,
                        receiver_id=claim_recv_id,
                        quantity=claim_qty,
                        status=claim_status
                    )
                    remaining = max(0, available_qty - claim_qty)
                    _success(f"Claim **#{new_cid}** registered successfully! "
                             f"Claimed **{claim_qty} portions** of '{food_preview.get('food_name')}' for {selected_recv}. "
                             f"Remaining stock updated to **{remaining} portions**.")
                    st.balloons()
                except Exception as e:
                    _error(f"Failed to log claim: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 5: BROWSE ALL INVENTORY ─────────────────────────────────────────────
    with tab_browse:
        st.markdown("<div class='section-card'><h3>📋 Live Global Inventory Explorer</h3>", unsafe_allow_html=True)

        bc1, bc2, bc3, bc4 = st.columns(4)
        with bc1:
            b_search = st.text_input("🔎 Search:", placeholder="Food, City, Provider...", key="browse_search")
        with bc2:
            b_ftype = st.selectbox("Dietary:", ["All", "Vegetarian", "Non-Vegetarian", "Vegan"], key="browse_ft")
        with bc3:
            b_mtype = st.selectbox("Meal:", ["All", "Breakfast", "Lunch", "Dinner", "Snacks"], key="browse_mt")
        with bc4:
            b_sort = st.selectbox(
                "Sort by:",
                ["Newest First", "Expiring Soonest", "Highest Quantity", "Lowest Quantity", "Name A-Z"],
                key="browse_sort"
            )

        sort_param_map = {
            "Newest First": "newest",
            "Expiring Soonest": "expiring_soon",
            "Highest Quantity": "qty_high",
            "Lowest Quantity": "qty_low",
            "Name A-Z": "name_asc"
        }

        b_instock = st.checkbox("Show In-Stock Only (> 0 units)", value=False, key="browse_instock")

        browse_df = queries.get_all_food_listings(
            food_type=b_ftype if b_ftype != "All" else None,
            meal_type=b_mtype if b_mtype != "All" else None,
            search_query=b_search.strip() if b_search.strip() else None,
            in_stock_only=b_instock,
            sort_by=sort_param_map.get(b_sort, "newest")
        )

        st.markdown(
            f"<p style='color:#64748b;font-size:0.85rem;margin-bottom:8px'>"
            f"Showing <b>{len(browse_df):,}</b> listings matching criteria</p>",
            unsafe_allow_html=True
        )

        display_df = browse_df.copy()
        display_df.columns = [c.replace('_', ' ').title() for c in display_df.columns]
        st.dataframe(display_df, use_container_width=True, height=440)

        if not browse_df.empty:
            csv = browse_df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Export Filtered Inventory (CSV)", csv, "live_food_inventory.csv", "text/csv")

        st.markdown("</div>", unsafe_allow_html=True)
