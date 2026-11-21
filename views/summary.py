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

def _progress(label, val, total, color="#16a34a"):
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
    eco   = queries.get_eco_impact_metrics()
    ptypes = queries.get_top_provider_type()
    cities = queries.get_top_city_by_listings()
    ftypes = queries.get_common_food_types()
    status = queries.get_claim_status_distribution()

    db_status = queries.get_db_status()
    total_providers = db_status.get("counts", {}).get("providers", 1000)
    total_receivers = db_status.get("counts", {}).get("receivers", 1000)

    # ── KPI Metric Row ───────────────────────────────────────────────────────
    cards_html = "<div class='metric-row'>"
    cards_html += _metric_card("🍽️", f"{eco['total_meals']:,}", "Meals Available", "Units of food listed", "green")
    cards_html += _metric_card("📋", f"{eco['total_claims']:,}", "Total Claims", f"{eco['completion_rate']}% completed", "blue")
    cards_html += _metric_card("✅", f"{eco['completed_claims']:,}", "Successful Deliveries", "Claims completed", "teal")
    cards_html += _metric_card("🌍", f"{eco['co2_saved_kg']:,.0f} kg", "CO₂ Saved", "Est. greenhouse gas offset", "orange")
    cards_html += _metric_card("💧", f"{eco['water_saved_liters']/1_000_000:.1f}M L", "Water Conserved", "Est. water savings", "purple")
    cards_html += _metric_card("🏙️", f"{len(queries.get_all_cities()):,}", "Cities Active", "Across the network", "red")
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── Eco Impact Banner ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class='eco-banner'>
        <div>
            <div class='eco-title'>🌱 Environmental Impact This Season</div>
            <div class='eco-value'>{eco['co2_saved_kg']:,.0f} kg CO₂ Offset</div>
            <div class='eco-sub'>Equivalent to planting ~{int(eco['co2_saved_kg']/21):,} trees 🌳</div>
        </div>
        <div>
            <div class='eco-title'>💧 Water Footprint Saved</div>
            <div class='eco-value'>{eco['water_saved_liters']/1_000_000:.1f}M Litres</div>
            <div class='eco-sub'>Enough for {int(eco['water_saved_liters']/2):,} people/day</div>
        </div>
        <div>
            <div class='eco-title'>🤝 Community Connections</div>
            <div class='eco-value'>{total_providers + total_receivers:,}</div>
            <div class='eco-sub'>{total_providers:,} Donors + {total_receivers:,} Recipients</div>
        </div>
        <div>
            <div class='eco-title'>📈 Fulfillment Rate</div>
            <div class='eco-value'>{eco['completion_rate']}%</div>
            <div class='eco-sub'>Of all claims successfully completed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts Row 1 ─────────────────────────────────────────────────────────
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<h3>🏢 Provider Type Contributions</h3>", unsafe_allow_html=True)
        if not ptypes.empty:
            colors = ["#16a34a","#22c55e","#4ade80","#86efac"]
            fig = go.Figure(go.Pie(
                labels=ptypes['Provider_Type'],
                values=ptypes['Total'],
                hole=0.55,
                marker=dict(colors=colors[:len(ptypes)], line=dict(color='white', width=3)),
                textinfo='percent+label',
                textfont=dict(family='Inter', size=12, color='white'),
                hovertemplate='<b>%{label}</b><br>Listings: %{value}<br>Share: %{percent}<extra></extra>'
            ))
            fig.update_layout(
                showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
                height=240, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                annotations=[dict(text=f"<b>{ptypes['Total'].sum()}</b><br>Total", showarrow=False, font=dict(size=14, color='#064e3b', family='Inter'), x=0.5, y=0.5)]
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<h3>📊 Claim Status Breakdown</h3>", unsafe_allow_html=True)
        if not status.empty:
            status_colors = {"Completed": "#16a34a", "Pending": "#f59e0b", "Cancelled": "#ef4444"}
            colors_list = [status_colors.get(s, "#6b7280") for s in status['Status']]
            fig2 = go.Figure(go.Bar(
                x=status['Count'], y=status['Status'], orientation='h',
                marker=dict(color=colors_list, line=dict(color='white', width=2)),
                text=[f"{v:,}" for v in status['Count']], textposition='outside',
                textfont=dict(family='Inter', size=13, color='#064e3b'),
                hovertemplate='<b>%{y}</b>: %{x:,}<extra></extra>'
            ))
            fig2.update_layout(
                height=240, margin=dict(t=10, b=10, l=10, r=60),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(tickfont=dict(family='Inter', size=13, color='#064e3b'), gridcolor='#f0fdf4'),
            )
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Charts Row 2 ─────────────────────────────────────────────────────────
    c3, c4 = st.columns([1.4, 1])

    with c3:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<h3>🏙️ Top Cities by Food Listings</h3>", unsafe_allow_html=True)
        top15 = cities.head(12)
        if not top15.empty:
            fig3 = go.Figure(go.Bar(
                x=top15['City'], y=top15['Listings'],
                marker=dict(
                    color=top15['Listings'],
                    colorscale=[[0,'#86efac'],[0.5,'#22c55e'],[1,'#15803d']],
                    showscale=False,
                    line=dict(color='white', width=1)
                ),
                text=top15['Listings'], textposition='outside',
                textfont=dict(family='Inter', size=11, color='#064e3b'),
                hovertemplate='<b>%{x}</b><br>Listings: %{y}<extra></extra>'
            ))
            fig3.update_layout(
                height=280, margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(tickfont=dict(size=10, family='Inter'), gridcolor='#f0fdf4', showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#f0fdf4', showticklabels=False),
            )
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<h3>🥗 Food Type Distribution</h3>", unsafe_allow_html=True)
        if not ftypes.empty:
            total_ft = ftypes['Listings'].sum()
            type_colors = {"Vegetarian": "#16a34a", "Non-Vegetarian": "#ef4444", "Vegan": "#06b6d4"}
            for _, row in ftypes.iterrows():
                col = type_colors.get(row['Food_Type'], "#6b7280")
                st.markdown(_progress(row['Food_Type'], row['Listings'], total_ft, col), unsafe_allow_html=True)
                st.markdown(f"<div style='margin-bottom:12px'></div>", unsafe_allow_html=True)

            fig4 = go.Figure(go.Pie(
                labels=ftypes['Food_Type'],
                values=ftypes['Listings'],
                hole=0.6,
                marker=dict(colors=[type_colors.get(t,"#6b7280") for t in ftypes['Food_Type']], line=dict(color='white',width=3)),
                textinfo='none',
                hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
            ))
            fig4.update_layout(
                height=160, margin=dict(t=0,b=0,l=0,r=0),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Provider vs Receiver comparison bar ──────────────────────────────────
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<h3>📍 Top Cities — Providers vs Receivers</h3>", unsafe_allow_html=True)
    prc = queries.get_providers_receivers_by_city().head(10)
    if not prc.empty:
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(name='Providers', x=prc['City'], y=prc['Providers'],
            marker_color='#16a34a', marker_line=dict(color='white', width=1),
            hovertemplate='<b>%{x}</b><br>Providers: %{y}<extra></extra>'))
        fig5.add_trace(go.Bar(name='Receivers', x=prc['City'], y=prc['Receivers'],
            marker_color='#06b6d4', marker_line=dict(color='white', width=1),
            hovertemplate='<b>%{x}</b><br>Receivers: %{y}<extra></extra>'))
        fig5.update_layout(
            barmode='group', height=300, margin=dict(t=10,b=10,l=10,r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation='h', y=1.1, font=dict(family='Inter', size=12)),
            xaxis=dict(tickfont=dict(size=10, family='Inter'), gridcolor='#f0fdf4'),
            yaxis=dict(gridcolor='#f0fdf4', tickfont=dict(family='Inter', size=11)),
        )
        st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)
