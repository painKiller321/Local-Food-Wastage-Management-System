import streamlit as st
import queries
import plotly.graph_objects as go

TYPE_ICONS = {
    "Restaurant": "🍽️", "Household": "🏠", "Supermarket": "🛒",
    "Caterer": "👨‍🍳", "Hotel": "🏨", "NGO": "🤝", "Shelter": "🏡",
    "Individual": "👤", "School": "🏫", "Hospital": "🏥"
}

def _contact_card(name, ctype, city, contact, address=""):
    icon = TYPE_ICONS.get(ctype, "📋")
    return f"""
    <div style='background:white;border-radius:14px;padding:18px;border:1.5px solid #d1fae5;
                box-shadow:0 2px 12px rgba(16,185,129,0.08);transition:all 0.2s;margin-bottom:12px'>
        <div style='display:flex;align-items:flex-start;gap:14px'>
            <div style='width:44px;height:44px;background:linear-gradient(135deg,#d1fae5,#a7f3d0);
                        border-radius:12px;display:flex;align-items:center;justify-content:center;
                        font-size:1.3rem;flex-shrink:0'>{icon}</div>
            <div style='flex:1'>
                <div style='font-weight:700;font-size:0.95rem;color:#064e3b;margin-bottom:3px'>{name}</div>
                <div style='font-size:0.75rem;color:#6b7280;margin-bottom:6px'>
                    <span class='tag tag-green' style='margin-right:6px'>{ctype}</span>
                    📍 {city}
                </div>
                {"<div style='font-size:0.8rem;color:#374151;margin-bottom:4px'>🏠 "+address+"</div>" if address else ""}
                <div style='font-size:0.8rem;color:#374151'>📞 {contact}</div>
            </div>
        </div>
    </div>"""

def display():
    st.markdown("""
    <div class='page-header'>
        <div class='badge'>📞 Directory</div>
        <h1>📞 Contacts Directory</h1>
        <p>Find food providers and receivers in any city across the network.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── City Selector ────────────────────────────────────────────────────────
    all_cities = queries.get_all_cities()

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<h3>🔍 Find by City</h3>", unsafe_allow_html=True)
    sc1, sc2 = st.columns([1,1])
    with sc1:
        typed_city = st.text_input("✍️ Type city name:", placeholder="e.g. Springfield, Adambury...")
    with sc2:
        dropdown_city = st.selectbox("📂 Or pick from list:", ["-- Select --"] + all_cities)
    st.markdown("</div>", unsafe_allow_html=True)

    city = typed_city.strip() if typed_city.strip() else (dropdown_city if dropdown_city != "-- Select --" else "")

    if not city:
        # ── Show overview stats when no city selected ─────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<h3>📊 Network Overview</h3>", unsafe_allow_html=True)

        prc = queries.get_providers_receivers_by_city().head(10)
        if not prc.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Providers', x=prc['City'], y=prc['Providers'],
                marker_color='#16a34a', marker_line=dict(color='white',width=1),
                hovertemplate='<b>%{x}</b><br>Providers: %{y}<extra></extra>'))
            fig.add_trace(go.Bar(name='Receivers', x=prc['City'], y=prc['Receivers'],
                marker_color='#06b6d4', marker_line=dict(color='white',width=1),
                hovertemplate='<b>%{x}</b><br>Receivers: %{y}<extra></extra>'))
            fig.update_layout(
                barmode='group', height=300, margin=dict(t=10,b=10,l=10,r=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation='h', y=1.1, font=dict(family='Inter',size=12)),
                xaxis=dict(tickfont=dict(size=10,family='Inter'), showgrid=False),
                yaxis=dict(gridcolor='#f0fdf4', tickfont=dict(family='Inter',size=11))
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

        st.info("⬆️ Type or select a city above to see detailed contact information for providers and receivers.")
        return

    # ── Show results for selected city ────────────────────────────────────
    providers_df = queries.get_providers_by_city(city)
    receivers_df = queries.get_receivers_by_city(city)

    # Summary stats
    mc = "<div class='metric-row'>"
    mc += f"<div class='metric-card green'><div class='mc-icon'>🏢</div><div class='mc-value'>{len(providers_df)}</div><div class='mc-label'>Providers in {city}</div></div>"
    mc += f"<div class='metric-card blue'><div class='mc-icon'>🤝</div><div class='mc-value'>{len(receivers_df)}</div><div class='mc-label'>Receivers in {city}</div></div>"
    mc += f"<div class='metric-card orange'><div class='mc-icon'>📡</div><div class='mc-value'>{len(providers_df)+len(receivers_df)}</div><div class='mc-label'>Total Contacts</div></div>"
    mc += "</div>"
    st.markdown(mc, unsafe_allow_html=True)

    if providers_df.empty and receivers_df.empty:
        st.warning(f"⚠️ No contacts found for **'{city}'**. Try a different spelling or choose from the dropdown.")
        return

    tab1, tab2 = st.tabs([f"🏢  Providers ({len(providers_df)})", f"🤝  Receivers ({len(receivers_df)})"])

    with tab1:
        if providers_df.empty:
            st.info("No providers found in this city.")
        else:
            # Filter by type
            if 'Type' in providers_df.columns:
                types = ["All"] + sorted(providers_df['Type'].dropna().unique().tolist())
                filter_type = st.selectbox("Filter by provider type:", types, key="prov_type_filter")
                if filter_type != "All":
                    providers_df = providers_df[providers_df['Type'] == filter_type]

            csv = providers_df.to_csv(index=False).encode('utf-8')
            st.download_button(f"⬇️ Export {len(providers_df)} Providers CSV", csv, f"providers_{city}.csv", "text/csv")

            cols = st.columns(2)
            for idx, (_, row) in enumerate(providers_df.iterrows()):
                with cols[idx % 2]:
                    st.markdown(_contact_card(
                        row.get('Name','N/A'),
                        str(row.get('Type','')),
                        str(row.get('City',city)),
                        str(row.get('Contact','N/A')),
                        str(row.get('Address',''))
                    ), unsafe_allow_html=True)

    with tab2:
        if receivers_df.empty:
            st.info("No receivers found in this city.")
        else:
            csv2 = receivers_df.to_csv(index=False).encode('utf-8')
            st.download_button(f"⬇️ Export {len(receivers_df)} Receivers CSV", csv2, f"receivers_{city}.csv", "text/csv")

            cols2 = st.columns(2)
            for idx, (_, row) in enumerate(receivers_df.iterrows()):
                with cols2[idx % 2]:
                    st.markdown(_contact_card(
                        row.get('Name','N/A'),
                        str(row.get('Type','')),
                        str(row.get('City',city)),
                        str(row.get('Contact','N/A')),
                    ), unsafe_allow_html=True)
