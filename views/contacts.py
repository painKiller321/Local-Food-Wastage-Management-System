import streamlit as st
import queries
import plotly.graph_objects as go
import pandas as pd

TYPE_ICONS = {
    "Restaurant": "🍽️", "Household": "🏠", "Supermarket": "🛒",
    "Caterer": "👨‍🍳", "Hotel": "🏨", "NGO": "🤝", "Shelter": "🏡",
    "Individual": "👤", "School": "🏫", "Hospital": "🏥",
    "Food Bank": "🥫", "Community Center": "🏛️", "Bakery": "🥐"
}

def _contact_card(name, ctype, city, contact, address=""):
    icon = TYPE_ICONS.get(ctype, "🏢")
    addr_line = f"<div style='font-size:0.8rem;color:#475569;margin-bottom:5px'>📍 {address}</div>" if address and address.lower() != 'none' else ""
    phone_clean = "".join([c for c in str(contact) if c.isdigit() or c == '+'])
    tel_link = f"<a href='tel:{phone_clean}' style='color:#059669;font-weight:600;text-decoration:none'>📞 {contact}</a>" if contact else "<span style='color:#94a3b8'>No contact provided</span>"
    
    return f"""
    <div style='background:white;border-radius:16px;padding:20px;border:1px solid #e2e8f0;
                box-shadow:0 2px 10px rgba(0,0,0,0.04);margin-bottom:14px;
                transition:transform 0.15s ease, box-shadow 0.15s ease;'>
        <div style='display:flex;align-items:flex-start;gap:14px'>
            <div style='width:46px;height:46px;background:linear-gradient(135deg,#ecfdf5,#d1fae5);
                        border-radius:12px;display:flex;align-items:center;justify-content:center;
                        font-size:1.35rem;flex-shrink:0;border:1px solid #a7f3d0'>{icon}</div>
            <div style='flex:1;min-width:0'>
                <div style='font-weight:700;font-size:1rem;color:#0f172a;margin-bottom:4px;line-height:1.3'>{name}</div>
                <div style='display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px'>
                    <span class='tag tag-green'>{ctype}</span>
                    <span style='font-size:0.78rem;color:#64748b'>🏙️ {city}</span>
                </div>
                {addr_line}
                <div style='font-size:0.83rem;margin-top:4px'>{tel_link}</div>
            </div>
        </div>
    </div>"""

def display():
    st.markdown("""
    <div class='page-header'>
        <div class='badge'>📞 Community Directory</div>
        <h1>📞 Food Rescue Partners Directory</h1>
        <p>Explore verified restaurants, caterers, food banks, and shelters cooperating across our network.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── City Selector ────────────────────────────────────────────────────────
    all_cities = queries.get_all_cities()

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<h3>🔍 Search Directory by City</h3>", unsafe_allow_html=True)
    st.caption("Select your region to locate local donors and beneficiary organizations.")

    sc1, sc2 = st.columns([1, 1])
    with sc1:
        typed_city = st.text_input("✍️ Type city or region name:", placeholder="e.g. Springfield, Adambury, Chicago...")
    with sc2:
        dropdown_city = st.selectbox("📂 Or select from registered cities:", ["-- All / Select City --"] + all_cities)

    st.markdown("</div>", unsafe_allow_html=True)

    city = typed_city.strip() if typed_city.strip() else (dropdown_city if dropdown_city != "-- All / Select City --" else "")

    if not city:
        # ── Show network overview when no city selected ─────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<h3>🌐 Nationwide Partner Distribution</h3>", unsafe_allow_html=True)
        st.caption("Top 12 cities by registered food providers and receiving charities.")

        prc = queries.get_providers_receivers_by_city().head(12)
        if not prc.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Food Providers', x=prc['City'], y=prc['Providers'],
                marker_color='#059669', marker_line=dict(color='white', width=1.5),
                hovertemplate='<b>%{x}</b><br>Providers: %{y}<extra></extra>'
            ))
            fig.add_trace(go.Bar(
                name='Receiving Charities', x=prc['City'], y=prc['Receivers'],
                marker_color='#0284c7', marker_line=dict(color='white', width=1.5),
                hovertemplate='<b>%{x}</b><br>Receivers: %{y}<extra></extra>'
            ))
            fig.update_layout(
                barmode='group', height=340, margin=dict(t=20, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation='h', y=1.1, x=0, font=dict(family='Inter', size=12)),
                xaxis=dict(tickfont=dict(size=11, family='Inter', color='#0f172a'), showgrid=False),
                yaxis=dict(gridcolor='#f1f5f9', tickfont=dict(family='Inter', size=11, color='#64748b'))
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

        st.info("💡 **Quick Start:** Select or type any city above to view contact cards, phone numbers, and export lists.")
        return

    # ── Show results for selected city ────────────────────────────────────
    providers_df = queries.get_providers_by_city(city)
    receivers_df = queries.get_receivers_by_city(city)

    # Summary metrics
    n_prov = len(providers_df)
    n_recv = len(receivers_df)
    total_contacts = n_prov + n_recv

    mc = "<div class='metric-row'>"
    mc += f"<div class='metric-card green'><div class='mc-icon'>🏢</div><div class='mc-value'>{n_prov}</div><div class='mc-label'>Providers in {city}</div></div>"
    mc += f"<div class='metric-card blue'><div class='mc-icon'>🤝</div><div class='mc-value'>{n_recv}</div><div class='mc-label'>Receivers in {city}</div></div>"
    mc += f"<div class='metric-card orange'><div class='mc-icon'>📡</div><div class='mc-value'>{total_contacts}</div><div class='mc-label'>Total Verified Contacts</div></div>"
    mc += "</div>"
    st.markdown(mc, unsafe_allow_html=True)

    if n_prov == 0 and n_recv == 0:
        st.warning(f"⚠️ No verified partners found in **'{city}'**. Please check spelling or select from the dropdown above.")
        return

    tab1, tab2 = st.tabs([f"🏢  Food Providers ({n_prov})", f"🤝  Receiving Charities ({n_recv})"])

    with tab1:
        if providers_df.empty:
            st.info(f"No food providers registered in {city} yet.")
        else:
            fc1, fc2 = st.columns([1, 1])
            with fc1:
                p_search = st.text_input("Filter providers by name:", placeholder="e.g. Bakery, Bistro...", key="p_srch")
            with fc2:
                types = ["All"] + sorted(providers_df['Type'].dropna().unique().tolist())
                filter_type = st.selectbox("Filter by category:", types, key="prov_type_filter")

            filtered_p = providers_df.copy()
            if p_search.strip():
                filtered_p = filtered_p[filtered_p['Name'].str.contains(p_search.strip(), case=False, na=False)]
            if filter_type != "All":
                filtered_p = filtered_p[filtered_p['Type'] == filter_type]

            csv = filtered_p.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"⬇️ Export {len(filtered_p)} Providers (CSV)",
                data=csv,
                file_name=f"providers_{city.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.write(f"Showing **{len(filtered_p)}** providers:")
            p_cols = st.columns(2)
            for idx, (_, row) in enumerate(filtered_p.iterrows()):
                with p_cols[idx % 2]:
                    st.markdown(_contact_card(
                        name=row.get('Name', 'N/A'),
                        ctype=str(row.get('Type', 'Provider')),
                        city=str(row.get('City', city)),
                        contact=str(row.get('Contact', '')),
                        address=str(row.get('Address', ''))
                    ), unsafe_allow_html=True)

    with tab2:
        if receivers_df.empty:
            st.info(f"No charity receivers registered in {city} yet.")
        else:
            rc1, rc2 = st.columns([1, 1])
            with rc1:
                r_search = st.text_input("Filter receivers by name:", placeholder="e.g. Shelter, Hope, Church...", key="r_srch")
            with rc2:
                r_types = ["All"] + sorted(receivers_df['Type'].dropna().unique().tolist()) if 'Type' in receivers_df.columns else ["All"]
                filter_r_type = st.selectbox("Filter by charity type:", r_types, key="recv_type_filter")

            filtered_r = receivers_df.copy()
            if r_search.strip():
                filtered_r = filtered_r[filtered_r['Name'].str.contains(r_search.strip(), case=False, na=False)]
            if filter_r_type != "All":
                filtered_r = filtered_r[filtered_r['Type'] == filter_r_type]

            csv2 = filtered_r.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"⬇️ Export {len(filtered_r)} Receivers (CSV)",
                data=csv2,
                file_name=f"receivers_{city.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.write(f"Showing **{len(filtered_r)}** receiving organizations:")
            r_cols = st.columns(2)
            for idx, (_, row) in enumerate(filtered_r.iterrows()):
                with r_cols[idx % 2]:
                    st.markdown(_contact_card(
                        name=row.get('Name', 'N/A'),
                        ctype=str(row.get('Type', 'Charity')),
                        city=str(row.get('City', city)),
                        contact=str(row.get('Contact', '')),
                    ), unsafe_allow_html=True)
