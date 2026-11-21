import streamlit as st
import queries
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

MEAL_ICONS = {"Breakfast": "🌅", "Lunch": "☀️", "Dinner": "🌙", "Snacks": "🍪"}
FOOD_ICONS = {"Vegetarian": "🥦", "Non-Vegetarian": "🍗", "Vegan": "🌱"}
FOOD_COLORS = {"Vegetarian": "tag-green", "Non-Vegetarian": "tag-red", "Vegan": "tag-blue"}
MEAL_COLORS = {"Breakfast": "tag-orange", "Lunch": "tag-orange", "Dinner": "tag-purple", "Snacks": "tag-blue"}

def display():
    head_c1, head_c2 = st.columns([4, 1])
    with head_c1:
        st.markdown("""
        <div class='page-header' style='margin-bottom:14px'>
            <div class='badge'>🌍 Live Global Inventory</div>
            <h1>🍱 Surplus & Leftover Food Listings</h1>
            <p>Real-time food donations posted by restaurants and providers across all cities worldwide.</p>
        </div>
        """, unsafe_allow_html=True)
    with head_c2:
        st.markdown("<div style='padding-top:20px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True, help="Fetch latest food additions and leftover updates"):
            st.rerun()

    # ── Filter Bar ───────────────────────────────────────────────────────────
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<h3>🔍 Search & Global City Filter</h3>", unsafe_allow_html=True)

    all_cities = queries.get_all_cities()
    city_options = ["All Cities"] + sorted(list(set(all_cities)))

    fc1, fc2, fc3, fc4 = st.columns([2, 1, 1, 1])
    with fc1:
        search = st.text_input("🔎 Search Food, Restaurant, or City", placeholder="e.g. Biryani, Pizza, Hilton, Mumbai...")
    with fc2:
        food_type = st.selectbox("🥗 Dietary Type", ["All", "Vegetarian", "Non-Vegetarian", "Vegan"])
    with fc3:
        meal_type = st.selectbox("🕐 Meal Category", ["All", "Breakfast", "Lunch", "Dinner", "Snacks"])
    with fc4:
        selected_city = st.selectbox("📍 City / Region", city_options)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Load Data ────────────────────────────────────────────────────────────
    city_query = None if selected_city == "All Cities" else selected_city
    df = queries.get_all_food_listings(
        food_type=food_type if food_type != "All" else None,
        meal_type=meal_type if meal_type != "All" else None,
        city=city_query,
        search_query=search.strip() if search.strip() else None,
    )

    # ── Stats Row ────────────────────────────────────────────────────────────
    total_qty = int(df['Quantity'].sum()) if not df.empty else 0
    active_listings = len(df[df['Quantity'] > 0]) if not df.empty else 0

    mc = f"<div class='metric-row'>"
    mc += f"<div class='metric-card green'><div class='mc-icon'>📦</div><div class='mc-value'>{len(df):,}</div><div class='mc-label'>Total Listings</div></div>"
    mc += f"<div class='metric-card teal'><div class='mc-icon'>⚡</div><div class='mc-value'>{active_listings:,}</div><div class='mc-label'>Available Listings</div></div>"
    mc += f"<div class='metric-card orange'><div class='mc-icon'>🍱</div><div class='mc-value'>{total_qty:,}</div><div class='mc-label'>Total Food Portions</div></div>"
    if not df.empty and 'Food_Type' in df.columns:
        veg_pct = round(len(df[df['Food_Type']=='Vegetarian'])/len(df)*100)
        mc += f"<div class='metric-card blue'><div class='mc-icon'>🥦</div><div class='mc-value'>{veg_pct}%</div><div class='mc-label'>Vegetarian Share</div></div>"
    mc += "</div>"
    st.markdown(mc, unsafe_allow_html=True)

    if df.empty:
        st.info("🔍 No food listings match your current filters. If a restaurant just added food, try clearing filters or clicking **'🔄 Refresh Data'**.")
        return

    # ── Tabs: Card View / Table View / Analytics ─────────────────────────────
    tab1, tab2, tab3 = st.tabs(["🃏  Card View", "📋  Table View", "📈  Analytics"])

    with tab1:
        # ── Card Grid ────────────────────────────────────────────────────────
        items_per_page = 12
        page_count = (len(df) - 1) // items_per_page + 1
        page = st.number_input("Page", min_value=1, max_value=max(page_count, 1), value=1, label_visibility="collapsed") if page_count > 1 else 1
        st.caption(f"Showing {min((page-1)*items_per_page+1, len(df))}–{min(page*items_per_page, len(df))} of {len(df):,} listings  |  Page {page}/{page_count}")

        page_df = df.iloc[(page-1)*items_per_page : page*items_per_page]
        cols = st.columns(3)
        for idx, (_, row) in enumerate(page_df.iterrows()):
            ft = str(row.get('Food_Type', ''))
            mt = str(row.get('Meal_Type', ''))
            fi = FOOD_ICONS.get(ft, "🍽️")
            mi = MEAL_ICONS.get(mt, "")
            fc_cls = FOOD_COLORS.get(ft, "tag-green")
            mc_cls = MEAL_COLORS.get(mt, "tag-orange")
            provider = str(row.get('Provider_Name') or row.get('Provider_Type', ''))
            contact = str(row.get('Provider_Contact') or '')
            expiry   = str(row.get('Expiry_Date', 'N/A'))
            city     = str(row.get('Location', ''))
            qty      = int(row['Quantity'])

            qty_badge = f"<span class='fc-qty'>{qty}</span> <span class='fc-qty-label'>units available</span>" if qty > 0 else "<span style='color:#ef4444;font-weight:700;font-size:0.95rem'>🔴 Out of Stock / Claimed</span>"
            contact_html = f"<div style='font-size:0.75rem;color:#047857;margin-top:4px'>📞 {contact}</div>" if contact else ""

            with cols[idx % 3]:
                st.markdown(f"""
                <div class='food-card'>
                    <div class='fc-corner'></div>
                    <div style='font-size:1.5rem;margin-bottom:4px'>{fi}</div>
                    <div class='fc-title'>{row['Food_Name']}</div>
                    <div class='fc-provider'>📍 <b>{city}</b>  •  🏢 {provider}</div>
                    {contact_html}
                    <div style='margin-top:6px'>
                        {qty_badge}
                    </div>
                    <div class='fc-tags' style='margin-top:8px'>
                        <span class='tag {fc_cls}'>{fi} {ft}</span>
                        <span class='tag {mc_cls}'>{mi} {mt}</span>
                    </div>
                    <div class='fc-expiry'>⏰ Best Before: {expiry[:10]}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:12px'></div>", unsafe_allow_html=True)

    with tab2:
        # ── Table View ───────────────────────────────────────────────────────
        st.markdown(f"<p style='color:#6b7280;font-size:0.85rem'>{len(df):,} records found</p>", unsafe_allow_html=True)
        display_df = df.copy()
        display_df.columns = [c.replace('_', ' ') for c in display_df.columns]
        st.dataframe(display_df, use_container_width=True, height=460)

        col_dl1, col_dl2 = st.columns([1, 5])
        with col_dl1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Export CSV", csv, "food_listings.csv", "text/csv", use_container_width=True)

    with tab3:
        # ── Analytics ────────────────────────────────────────────────────────
        a1, a2 = st.columns(2)
        with a1:
            st.markdown("<div class='section-card'><h3>🥗 Dietary Breakdown</h3>", unsafe_allow_html=True)
            ft_counts = df.groupby('Food_Type')['Quantity'].sum().reset_index()
            if not ft_counts.empty:
                colors = {"Vegetarian":"#16a34a","Non-Vegetarian":"#ef4444","Vegan":"#06b6d4"}
                fig = go.Figure(go.Pie(
                    labels=ft_counts['Food_Type'], values=ft_counts['Quantity'], hole=0.5,
                    marker=dict(colors=[colors.get(t,"#6b7280") for t in ft_counts['Food_Type']], line=dict(color='white',width=2)),
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Qty: %{value}<extra></extra>'
                ))
                fig.update_layout(height=250, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        with a2:
            st.markdown("<div class='section-card'><h3>🕐 Meal Portions Distribution</h3>", unsafe_allow_html=True)
            mt_counts = df.groupby('Meal_Type')['Quantity'].sum().reset_index().sort_values('Quantity', ascending=True)
            if not mt_counts.empty:
                meal_colors_list = ["#f59e0b","#16a34a","#06b6d4","#8b5cf6"]
                fig2 = go.Figure(go.Bar(
                    y=mt_counts['Meal_Type'], x=mt_counts['Quantity'], orientation='h',
                    marker_color=meal_colors_list[:len(mt_counts)],
                    text=mt_counts['Quantity'], textposition='outside',
                    hovertemplate='<b>%{y}</b>: %{x} units<extra></extra>'
                ))
                fig2.update_layout(height=250, margin=dict(t=0,b=0,l=0,r=40),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, showticklabels=False),
                    yaxis=dict(tickfont=dict(family='Inter', size=12, color='#064e3b')))
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Top 10 cities chart
        st.markdown("<div class='section-card'><h3>🏙️ Active Cities by Available Quantity</h3>", unsafe_allow_html=True)
        city_grp = df.groupby('Location')['Quantity'].sum().nlargest(10).reset_index()
        if not city_grp.empty:
            fig3 = px.bar(city_grp, x='Location', y='Quantity',
                color='Quantity', color_continuous_scale=[[0,'#86efac'],[1,'#15803d']],
                text='Quantity', template='none')
            fig3.update_traces(textposition='outside', marker_line_color='white', marker_line_width=1,
                hovertemplate='<b>%{x}</b><br>%{y} units<extra></extra>')
            fig3.update_layout(height=280, coloraxis_showscale=False,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(tickfont=dict(size=10, family='Inter'), showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#f0fdf4', showticklabels=False),
                margin=dict(t=10,b=10,l=10,r=10))
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
