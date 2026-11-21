import streamlit as st
import queries
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def _rank_color(i):
    if i == 0: return "gold"
    if i == 1: return "silver"
    if i == 2: return "bronze"
    return "green"

def display():
    st.markdown("""
    <div class='page-header'>
        <div class='badge'>📊 Real-time Intelligence</div>
        <h1>📊 Claims Analytics & Fulfillment</h1>
        <p>Comprehensive tracking of food redistribution efficiency, fulfillment velocity, and community partners.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Load Data ────────────────────────────────────────────────────────────
    eco = queries.get_eco_impact_metrics()
    status = queries.get_claim_status_distribution()
    top_recv = queries.get_top_receivers()
    top_prov = queries.get_top_provider_by_claims()
    avg_qty = queries.get_avg_claim_quantity()
    meal_tp = queries.get_top_meal_type()
    claims_per_food = queries.get_claims_per_food()
    detailed = queries.get_claims_detailed(limit=40)

    # ── KPI Row ──────────────────────────────────────────────────────────────
    total_c = eco['total_claims']
    completed = eco['completed_claims']
    pending = int(status.loc[status['Status'] == 'Pending', 'Count'].sum()) if 'Pending' in status['Status'].values else 0
    cancelled = int(status.loc[status['Status'] == 'Cancelled', 'Count'].sum()) if 'Cancelled' in status['Status'].values else 0

    mc = "<div class='metric-row'>"
    mc += f"<div class='metric-card blue'><div class='mc-icon'>📋</div><div class='mc-value'>{total_c:,}</div><div class='mc-label'>Total Claims</div></div>"
    mc += f"<div class='metric-card green'><div class='mc-icon'>✅</div><div class='mc-value'>{completed:,}</div><div class='mc-label'>Completed</div></div>"
    mc += f"<div class='metric-card orange'><div class='mc-icon'>⏳</div><div class='mc-value'>{pending:,}</div><div class='mc-label'>Pending Review</div></div>"
    mc += f"<div class='metric-card red'><div class='mc-icon'>❌</div><div class='mc-value'>{cancelled:,}</div><div class='mc-label'>Cancelled</div></div>"
    mc += f"<div class='metric-card teal'><div class='mc-icon'>⚡</div><div class='mc-value'>{eco['completion_rate']}%</div><div class='mc-label'>Fulfillment Rate</div></div>"
    mc += "</div>"
    st.markdown(mc, unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊  Fulfillment Overview",
        "🏆  Partner Leaderboards",
        "🍽️  Demand & Categories",
        "🕒  Recent Claims & Status Manager"
    ])

    with tab1:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("<div class='section-card'><h3>📊 Claim Status Distribution</h3>", unsafe_allow_html=True)
            status_colors = {"Completed": "#059669", "Pending": "#f59e0b", "Cancelled": "#ef4444"}
            if not status.empty:
                fig = go.Figure(go.Pie(
                    labels=status['Status'], values=status['Count'], hole=0.6,
                    marker=dict(colors=[status_colors.get(s, "#64748b") for s in status['Status']],
                                line=dict(color='white', width=3)),
                    textinfo='label+percent',
                    textfont=dict(family='Inter', size=12),
                    hovertemplate='<b>%{label}</b><br>%{value} claims<extra></extra>'
                ))
                fig.update_layout(
                    height=280, margin=dict(t=10, b=10, l=10, r=10),
                    paper_bgcolor='rgba(0,0,0,0)', showlegend=False,
                    annotations=[dict(text=f"<b>{total_c:,}</b><br><span style='font-size:11px;color:#64748b'>Total Claims</span>",
                                      showarrow=False,
                                      font=dict(size=15, color='#064e3b', family='Inter'), x=0.5, y=0.5)]
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='section-card'><h3>🍽️ Claims by Meal Category</h3>", unsafe_allow_html=True)
            if not meal_tp.empty:
                meal_colors = {"Breakfast": "#f59e0b", "Lunch": "#059669", "Dinner": "#6366f1", "Snacks": "#06b6d4"}
                fig2 = go.Figure(go.Bar(
                    x=meal_tp['Meal_Type'], y=meal_tp['Total_Claims'],
                    marker=dict(color=[meal_colors.get(m, "#64748b") for m in meal_tp['Meal_Type']],
                                line=dict(color='white', width=1.5)),
                    text=meal_tp['Total_Claims'], textposition='outside',
                    hovertemplate='<b>%{x}</b><br>%{y} claims<extra></extra>'
                ))
                fig2.update_layout(
                    height=280, margin=dict(t=20, b=10, l=10, r=10),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(tickfont=dict(family='Inter', size=12, color='#0f172a'), showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#f1f5f9', showticklabels=False),
                    showlegend=False
                )
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Funnel chart
        st.markdown("<div class='section-card'><h3>🔽 Claim Fulfillment Funnel</h3>", unsafe_allow_html=True)
        funnel_fig = go.Figure(go.Funnel(
            y=["Total Claims Registered", "Completed & Picked Up", "Pending Dispatch", "Cancelled / Unfulfilled"],
            x=[total_c, completed, pending, cancelled],
            textposition="inside", textinfo="value+percent initial",
            marker=dict(color=["#059669", "#10b981", "#f59e0b", "#ef4444"]),
            connector={"line": {"color": "#e2e8f0", "width": 1.5}}
        ))
        funnel_fig.update_layout(
            height=260, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', size=13, color='#0f172a')
        )
        st.plotly_chart(funnel_fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        lb1, lb2 = st.columns(2)
        with lb1:
            st.markdown("<div class='section-card'><h3>🏆 Top Claiming Receivers (NGOs & Shelters)</h3>", unsafe_allow_html=True)
            if not top_recv.empty:
                for i, (_, row) in enumerate(top_recv.head(8).iterrows()):
                    rc = _rank_color(i)
                    city = str(row.get('City', ''))
                    rtype = str(row.get('Type', ''))
                    sub = " • ".join(filter(None, [city, rtype]))
                    st.markdown(f"""
                    <div class='leader-row'>
                        <div class='leader-rank {rc}'>#{i+1}</div>
                        <div style='flex:1'>
                            <div class='leader-name'>{row['Name']}</div>
                            <div class='leader-sub'>{sub}</div>
                        </div>
                        <div class='leader-value'>{int(row['Total_Claims']):,} claims</div>
                    </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with lb2:
            st.markdown("<div class='section-card'><h3>🏅 Top Contributing Providers (Restaurants & Caterers)</h3>", unsafe_allow_html=True)
            if not top_prov.empty:
                for i, (_, row) in enumerate(top_prov.head(8).iterrows()):
                    rc = _rank_color(i)
                    city = str(row.get('City', ''))
                    ptype = str(row.get('Type', ''))
                    sub = " • ".join(filter(None, [city, ptype]))
                    st.markdown(f"""
                    <div class='leader-row'>
                        <div class='leader-rank {rc}'>#{i+1}</div>
                        <div style='flex:1'>
                            <div class='leader-name'>{row['Name']}</div>
                            <div class='leader-sub'>{sub}</div>
                        </div>
                        <div class='leader-value'>{int(row['Successful_Claims']):,} ✓</div>
                    </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Avg quantity chart
        st.markdown("<div class='section-card'><h3>📉 Average Portions Claimed per Organization</h3>", unsafe_allow_html=True)
        if not avg_qty.empty:
            avg_sorted = avg_qty.sort_values('Avg_Quantity')
            fig3 = go.Figure(go.Bar(
                y=avg_sorted['Name'], x=avg_sorted['Avg_Quantity'], orientation='h',
                marker=dict(
                    color=avg_sorted['Avg_Quantity'],
                    colorscale=[[0, '#a7f3d0'], [1, '#059669']],
                    showscale=False, line=dict(color='white', width=1)
                ),
                text=[f"{v:.1f} units" for v in avg_sorted['Avg_Quantity']], textposition='outside',
                hovertemplate='<b>%{y}</b><br>Avg: %{x:.1f} portions<extra></extra>'
            ))
            fig3.update_layout(
                height=320, margin=dict(t=10, b=10, l=10, r=80),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(tickfont=dict(family='Inter', size=11, color='#0f172a'))
            )
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='section-card'><h3>🍛 Most In-Demand Food Items</h3>", unsafe_allow_html=True)
        if not claims_per_food.empty:
            max_claims = claims_per_food['Claims'].max()
            for i, (_, row) in enumerate(claims_per_food.iterrows()):
                pct = (row['Claims'] / max_claims * 100) if max_claims else 0
                bar_color = "#059669" if i < 3 else "#10b981"
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:14px;padding:12px 0;border-bottom:1px solid #f1f5f9'>
                    <div style='width:32px;text-align:center;font-weight:800;color:{"#f59e0b" if i==0 else "#64748b"};font-size:1.1rem'>{medal}</div>
                    <div style='flex:1'>
                        <div style='font-weight:600;color:#0f172a;font-size:0.92rem;margin-bottom:4px'>{row['Food_Name']}</div>
                        <div style='background:#f1f5f9;border-radius:999px;height:7px;overflow:hidden'>
                            <div style='width:{pct}%;height:100%;background:linear-gradient(90deg,{bar_color},{bar_color}cc);border-radius:999px'></div>
                        </div>
                    </div>
                    <div style='font-weight:700;color:#059669;font-size:0.95rem;min-width:80px;text-align:right'>
                        {int(row['Claims']):,} <span style='font-size:0.75rem;font-weight:500;color:#64748b'>claims</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Treemap of provider types
        st.markdown("<div class='section-card'><h3>🗂️ Total Surplus Volume by Provider Category</h3>", unsafe_allow_html=True)
        pt = queries.get_top_provider_type()
        if not pt.empty and 'Total_Quantity' in pt.columns:
            fig_tree = px.treemap(
                pt, path=['Provider_Type'], values='Total_Quantity',
                color='Total_Quantity', color_continuous_scale=[[0, '#d1fae5'], [1, '#064e3b']],
                hover_data={'Total_Quantity': True}
            )
            fig_tree.update_layout(
                height=280, margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False
            )
            fig_tree.update_traces(textfont=dict(family='Inter', size=13))
            st.plotly_chart(fig_tree, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        # ── Quick Status Updater ─────────────────────────────────────────────
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<h3>⚡ Live Claim Status Manager</h3>", unsafe_allow_html=True)
        st.caption("Change claim fulfillment status in real-time to update the global network.")

        pending_claims = detailed[detailed['Status'] == 'Pending'] if not detailed.empty and 'Status' in detailed.columns else pd.DataFrame()
        
        up_c1, up_c2, up_c3 = st.columns([2, 1.5, 1])
        with up_c1:
            if not pending_claims.empty:
                opts = {
                    f"Claim #{r['claim_id']} — {r.get('Food_Name', 'Food')} → {r.get('receiver_name', 'Receiver')}": int(r['claim_id'])
                    for _, r in pending_claims.iterrows()
                }
                selected_claim_label = st.selectbox("Select Pending Claim:", list(opts.keys()), key="mgr_sel_claim")
                target_claim_id = opts[selected_claim_label]
            else:
                target_claim_id = st.number_input("Enter Claim ID to Update:", min_value=1, value=1, step=1, key="mgr_manual_cid")

        with up_c2:
            new_status_val = st.selectbox("Set New Status:", ["Completed", "Cancelled", "Pending"], index=0, key="mgr_new_status")

        with up_c3:
            st.write("")  # Alignment spacer
            st.write("")
            if st.button("💾 Apply Update", use_container_width=True, key="mgr_update_btn"):
                try:
                    success = queries.update_claim_status(target_claim_id, new_status_val)
                    if success:
                        st.success(f"✅ Claim #{target_claim_id} updated to **{new_status_val}**!")
                        st.rerun()
                    else:
                        st.warning(f"Claim #{target_claim_id} was not found.")
                except Exception as ex:
                    st.error(f"Failed to update claim: {ex}")

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Recent Claims Feed ───────────────────────────────────────────────
        st.markdown(f"<div class='section-card'><h3>🕒 Recent {len(detailed)} Claims Activity</h3>", unsafe_allow_html=True)
        if not detailed.empty:
            status_badge = {
                'Completed': "<span class='tag tag-green'>✅ Completed</span>",
                'Pending':   "<span class='tag tag-orange'>⏳ Pending</span>",
                'Cancelled': "<span class='tag tag-red'>❌ Cancelled</span>",
            }
            for _, row in detailed.iterrows():
                badge = status_badge.get(str(row.get('Status', '')), f"<span class='tag tag-blue'>{row.get('Status', '')}</span>")
                ts = str(row.get('timestamp', ''))[:16]
                st.markdown(f"""
                <div class='timeline-item'>
                    <div class='timeline-dot' style='background:{"#059669" if row.get("Status")=="Completed" else "#f59e0b" if row.get("Status")=="Pending" else "#ef4444"}'></div>
                    <div class='timeline-content' style='flex:1'>
                        <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px'>
                            <div class='tl-title'>🍽️ <b>{row.get('Food_Name', 'N/A')}</b> &nbsp;→&nbsp; 🤝 {row.get('receiver_name', 'N/A')}</div>
                            {badge}
                        </div>
                        <div class='tl-sub' style='margin-top:4px;color:#64748b'>
                            📦 <b>{row.get('quantity', '?')} portions</b> &nbsp;•&nbsp; 
                            🏢 Provider: {row.get('provider_name', '?')} &nbsp;•&nbsp; 
                            📍 {row.get('receiver_city', 'Global')} &nbsp;•&nbsp; 
                            🕒 {ts}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Download detailed claims
        if not detailed.empty:
            csv = detailed.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"⬇️ Export Recent {len(detailed)} Claims (CSV)",
                data=csv,
                file_name="recent_claims.csv",
                mime="text/csv",
                use_container_width=True
            )
