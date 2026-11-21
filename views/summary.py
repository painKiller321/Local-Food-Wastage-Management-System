import streamlit as st
import queries
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def _metric_card(icon, value, label, delta="", color_cls="green"):
    return f"""
    <div class='metric-card {color_cls}'>
        <div class='mc-icon'>{icon}</div>
        <div class='mc-value'>{value}</div>
        <div class='mc-label'>{label}</div>
        {"<div class='mc-delta'>"+delta+"</div>" if delta else ""}
    </div>"""

def _progress(label, val, total, color="#059669"):
    pct = round(val / total * 100, 1) if total else 0
    return f"""
    <div class='progress-bar-wrap'>
        <div class='progress-bar-label'><span>{label}</span><span>{val:,} ({pct}%)</span></div>
        <div class='progress-bar-bg'>
            <div class='progress-bar-fill' style='width:{pct}%;background:{color}'></div>
        </div>
    </div>"""

def display():
    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='page-header'>
        <div class='badge'>📊 Live Dashboard</div>
        <h1>🌿 FoodBridge Dashboard</h1>
        <p>Real-time overview of food donations, claims, and community impact across all cities.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Load Data ────────────────────────────────────────────────────────────
    with st.spinner("Loading dashboard data..."):
        eco    = queries.get_eco_impact_metrics()
        ptypes = queries.get_top_provider_type()
        cities = queries.get_top_city_by_listings()
        ftypes = queries.get_common_food_types()
        status = queries.get_claim_status_distribution()
        db_status = queries.get_db_status()
        expiring  = queries.get_expiring_soon_listings(limit=5)

    total_providers = db_status.get("counts", {}).get("providers", 1000)
    total_receivers = db_status.get("counts", {}).get("receivers", 1000)
    total_listings  = db_status.get("counts", {}).get("food_listings", 0)

    # ── KPI Metric Row ───────────────────────────────────────────────────────
    cards_html = "<div class='metric-row'>"
    cards_html += _metric_card("🍽️", f"{eco['total_meals']:,}", "Total Food Units", f"{total_listings:,} listings active", "green")
    cards_html += _metric_card("📋", f"{eco['total_claims']:,}", "Total Claims", f"{eco['completion_rate']}% completed", "blue")
    cards_html += _metric_card("✅", f"{eco['completed_claims']:,}", "Successful Deliveries", "Claims completed", "teal")
    cards_html += _metric_card("🌍", f"{eco['co2_saved_kg']:,.0f} kg", "CO₂ Offset", "Est. greenhouse gas saved", "orange")
    cards_html += _metric_card("💧", f"{eco['water_saved_liters']/1_000_000:.1f}M L", "Water Conserved", "Est. water savings", "purple")
    cards_html += _metric_card("🏙️", f"{len(queries.get_all_cities()):,}", "Active Cities", "Network coverage", "red")
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── Eco Impact Banner ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class='eco-banner'>
        <div class='eco-item'>
            <div class='eco-title'>🌱 CO₂ Offset This Season</div>
            <div class='eco-value'>{eco['co2_saved_kg']:,.0f} kg</div>
            <div class='eco-sub'>≈ {int(eco['co2_saved_kg']/21):,} trees planted 🌳</div>
        </div>
        <div class='eco-item'>
            <div class='eco-title'>💧 Water Footprint Saved</div>
            <div class='eco-value'>{eco['water_saved_liters']/1_000_000:.1f}M L</div>
            <div class='eco-sub'>Enough for {int(eco['water_saved_liters']/2):,} people/day</div>
        </div>
        <div class='eco-item'>
            <div class='eco-title'>🤝 Community Network</div>
            <div class='eco-value'>{total_providers + total_receivers:,}</div>
            <div class='eco-sub'>{total_providers:,} Donors + {total_receivers:,} Recipients</div>
        </div>
        <div class='eco-item'>
            <div class='eco-title'>📈 Claim Fulfillment Rate</div>
            <div class='eco-value'>{eco['completion_rate']}%</div>
            <div class='eco-sub'>Of all claims successfully completed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Expiring Soon Alert ──────────────────────────────────────────────────
    if not expiring.empty:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#fffbeb,#fef3c7);border-radius:14px;
                    padding:16px 20px;border:1px solid #fcd34d;margin-bottom:20px'>
            <div style='font-weight:800;color:#92400e;font-size:0.95rem;margin-bottom:10px'>
                ⏰ Expiring Soon — Needs Urgent Claiming
            </div>
        """, unsafe_allow_html=True)

        exp_cols = st.columns(min(len(expiring), 5))
        for idx, (_, row) in enumerate(expiring.iterrows()):
            if idx >= 5:
                break
            with exp_cols[idx]:
                st.markdown(f"""
                <div style='background:white;border-radius:10px;padding:12px;border:1px solid #fcd34d;
                            text-align:center;box-shadow:0 2px 8px rgba(245,158,11,0.1)'>
                    <div style='font-weight:700;color:#0f172a;font-size:0.85rem;margin-bottom:4px'>{str(row.get("Food_Name",""))[:22]}</div>
                    <div style='font-size:0.72rem;color:#64748b;margin-bottom:6px'>📍 {str(row.get("Location",""))[:18]}</div>
                    <div style='font-weight:800;color:#059669;font-size:1.1rem'>{int(row.get("Quantity",0))} units</div>
                    <div style='font-size:0.7rem;font-weight:700;color:#dc2626;background:#fee2e2;border-radius:999px;padding:2px 6px;margin-top:4px;display:inline-block'>
                        ⏳ {str(row.get("Expiry_Date",""))[:10]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Charts Row 1 ─────────────────────────────────────────────────────────
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<h3>🏢 Provider Type Contributions</h3>", unsafe_allow_html=True)
        if not ptypes.empty:
            colors = ["#059669","#10b981","#34d399","#6ee7b7"]
            fig = go.Figure(go.Pie(
                labels=ptypes['Provider_Type'],
                values=ptypes['Total'],
                hole=0.6,
                marker=dict(colors=colors[:len(ptypes)], line=dict(color='white', width=3)),
                textinfo='percent+label',
                textfont=dict(family='Inter', size=12, color='white'),
                hovertemplate='<b>%{label}</b><br>Listings: %{value:,}<br>Share: %{percent}<extra></extra>'
            ))
            fig.update_layout(
                showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
                height=240, paper_bgcolor='rgba(0,0,0,0)',
                annotations=[dict(
                    text=f"<b>{ptypes['Total'].sum():,}</b><br>Total",
                    showarrow=False,
                    font=dict(size=14, color='#064e3b', family='Inter'), x=0.5, y=0.5
                )]
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<h3>📊 Claim Status Breakdown</h3>", unsafe_allow_html=True)
        if not status.empty:
            status_colors = {"Completed": "#059669", "Pending": "#f59e0b", "Cancelled": "#ef4444"}
            colors_list = [status_colors.get(s, "#64748b") for s in status['Status']]
            fig2 = go.Figure(go.Bar(
                x=status['Count'], y=status['Status'], orientation='h',
                marker=dict(color=colors_list, line=dict(color='white', width=2)),
                text=[f"{v:,}" for v in status['Count']], textposition='outside',
                textfont=dict(family='Inter', size=14, color='#0f172a'),
                hovertemplate='<b>%{y}</b>: %{x:,}<extra></extra>'
            ))
            fig2.update_layout(
                height=240, margin=dict(t=10, b=10, l=10, r=70),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(tickfont=dict(family='Inter', size=14, color='#0f172a')),
            )
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Charts Row 2 ─────────────────────────────────────────────────────────
    c3, c4 = st.columns([1.5, 1])

    with c3:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<h3>🏙️ Top Cities by Food Listings</h3>", unsafe_allow_html=True)
        top12 = cities.head(12)
        if not top12.empty:
            fig3 = go.Figure(go.Bar(
                x=top12['City'], y=top12['Listings'],
                marker=dict(
                    color=top12['Listings'],
                    colorscale=[[0,'#86efac'],[0.5,'#10b981'],[1,'#064e3b']],
                    showscale=False,
                    line=dict(color='white', width=1.5)
                ),
                text=top12['Listings'], textposition='outside',
                textfont=dict(family='Inter', size=11, color='#0f172a'),
                hovertemplate='<b>%{x}</b><br>Listings: %{y:,}<extra></extra>'
            ))
            fig3.update_layout(
                height=290, margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(tickfont=dict(size=10, family='Inter', color='#64748b'), showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9', showticklabels=False),
            )
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<h3>🥗 Food Type Distribution</h3>", unsafe_allow_html=True)
        if not ftypes.empty:
            total_ft = ftypes['Listings'].sum()
            type_colors = {"Vegetarian": "#059669", "Non-Vegetarian": "#ef4444", "Vegan": "#0ea5e9"}
            for _, row in ftypes.iterrows():
                col = type_colors.get(row['Food_Type'], "#64748b")
                st.markdown(_progress(row['Food_Type'], row['Listings'], total_ft, col), unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:12px'></div>", unsafe_allow_html=True)

            # Mini donut
            fig4 = go.Figure(go.Pie(
                labels=ftypes['Food_Type'], values=ftypes['Listings'], hole=0.65,
                marker=dict(colors=[type_colors.get(t,"#64748b") for t in ftypes['Food_Type']],
                            line=dict(color='white', width=3)),
                textinfo='none',
                hovertemplate='<b>%{label}</b>: %{value:,}<extra></extra>'
            ))
            fig4.update_layout(
                height=140, margin=dict(t=0,b=0,l=0,r=0),
                showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Provider vs Receiver Comparison ──────────────────────────────────────
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<h3>📍 Top Cities — Providers vs Receivers</h3>", unsafe_allow_html=True)
    prc = queries.get_providers_receivers_by_city().head(10)
    if not prc.empty:
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(name='🏢 Providers', x=prc['City'], y=prc['Providers'],
            marker=dict(color='#059669', line=dict(color='white', width=1.5)),
            hovertemplate='<b>%{x}</b><br>Providers: %{y:,}<extra></extra>'))
        fig5.add_trace(go.Bar(name='🤝 Receivers', x=prc['City'], y=prc['Receivers'],
            marker=dict(color='#0ea5e9', line=dict(color='white', width=1.5)),
            hovertemplate='<b>%{x}</b><br>Receivers: %{y:,}<extra></extra>'))
        fig5.update_layout(
            barmode='group', height=300, margin=dict(t=10,b=10,l=10,r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation='h', y=1.1, font=dict(family='Inter', size=12, color='#0f172a'),
                        bgcolor='rgba(0,0,0,0)'),
            xaxis=dict(tickfont=dict(size=11, family='Inter', color='#64748b'), showgrid=False),
            yaxis=dict(gridcolor='#f1f5f9', tickfont=dict(family='Inter', size=11, color='#64748b')),
        )
        st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Quick Stats Footer ───────────────────────────────────────────────────
    st.markdown(f"""
    <div style='text-align:center;padding:16px 0;color:#94a3b8;font-size:0.8rem'>
        🌐 Live data from <b>Cloud PostgreSQL</b> •
        {total_listings:,} listings •
        {total_providers:,} donors •
        {total_receivers:,} recipients •
        {len(queries.get_all_cities()):,} cities active
    </div>
    """, unsafe_allow_html=True)
