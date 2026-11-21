import streamlit as st
from views import summary, food_listings, claims_analysis, contacts, manage_listings

st.set_page_config(
    page_title="FoodBridge — Food Wastage Management",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ---- Google Font ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ---- Root Variables ---- */
:root {
    --primary:       #059669;
    --primary-light: #10b981;
    --primary-dark:  #064e3b;
    --accent:        #f97316;
    --accent-light:  #fb923c;
    --accent2:       #0ea5e9;
    --danger:        #ef4444;
    --warning:       #f59e0b;
    --bg:            #f8fafc;
    --card-bg:       #ffffff;
    --border:        #e2e8f0;
    --border-accent: #d1fae5;
    --text:          #0f172a;
    --text-muted:    #64748b;
    --shadow-sm:     0 1px 3px rgba(0,0,0,0.06);
    --shadow:        0 10px 25px -5px rgba(0,0,0,0.05), 0 8px 10px -6px rgba(0,0,0,0.03);
    --shadow-hover:  0 20px 30px -10px rgba(16,185,129,0.22);
    --radius:        16px;
}

/* ---- Base ---- */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ---- Main container ---- */
.main .block-container {
    padding: 1.75rem 2.25rem 3.5rem 2.25rem !important;
    max-width: 1440px;
}

/* ---- Pulse Animation ---- */
@keyframes pulse-dot {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(52, 211, 153, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
}
.pulse-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #34d399;
    animation: pulse-dot 2s infinite ease-in-out;
    margin-right: 6px;
    vertical-align: middle;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #022c22 0%, #064e3b 40%, #065f46 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
    min-width: 250px !important;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stRadio > div {
    gap: 6px;
}
section[data-testid="stSidebar"] .stRadio label {
    background: rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 11px 18px !important;
    margin: 2px 0;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(255,255,255,0.08);
    font-weight: 500;
    font-size: 0.92rem;
    display: block !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.14) !important;
    border-color: rgba(52, 211, 153, 0.4) !important;
    transform: translateX(4px);
}
section[data-testid="stSidebar"] .stRadio [data-checked="true"] label,
section[data-testid="stSidebar"] .stRadio label[data-testid*="selected"] {
    background: linear-gradient(135deg, rgba(16,185,129,0.25), rgba(6,78,59,0.4)) !important;
    border-color: #34d399 !important;
    box-shadow: 0 4px 14px rgba(16,185,129,0.2) !important;
}

/* ---- Page Header ---- */
.page-header {
    background: linear-gradient(135deg, #022c22 0%, #064e3b 50%, #047857 100%);
    border-radius: 20px;
    padding: 32px 38px;
    margin-bottom: 26px;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(6,78,59,0.25);
    border: 1px solid rgba(52,211,153,0.2);
}
.page-header::before {
    content: '';
    position: absolute; top: -50px; right: -50px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(52,211,153,0.18) 0%, transparent 70%);
    border-radius: 50%;
}
.page-header::after {
    content: '';
    position: absolute; bottom: -70px; right: 100px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(249,115,22,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.page-header h1 {
    color: white !important; font-size: 2.1rem !important;
    font-weight: 800 !important; margin: 0 !important;
    letter-spacing: -0.5px;
    line-height: 1.2 !important;
}
.page-header p { color: #a7f3d0; font-size: 0.98rem; margin: 8px 0 0 0; line-height: 1.5; }
.page-header .badge {
    display: inline-block; background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.28);
    backdrop-filter: blur(8px);
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.74rem; font-weight: 700; color: #d1fae5;
    margin-bottom: 12px; letter-spacing: 1px; text-transform: uppercase;
}

/* ---- Metric Cards ---- */
.metric-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
.metric-card {
    flex: 1; min-width: 170px;
    background: white;
    border-radius: var(--radius);
    padding: 22px 24px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border-accent);
    position: relative; overflow: hidden;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.metric-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-hover); border-color: var(--primary-light); }
.metric-card .mc-icon { font-size: 2.2rem; margin-bottom: 10px; }
.metric-card .mc-value {
    font-size: 2rem; font-weight: 800; color: var(--primary-dark);
    line-height: 1.1; margin-bottom: 4px; letter-spacing: -0.5px;
}
.metric-card .mc-label { font-size: 0.78rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.6px; }
.metric-card .mc-delta { font-size: 0.8rem; color: var(--primary); font-weight: 600; margin-top: 6px; }
.metric-card::after {
    content: '';
    position: absolute; right: -12px; top: -12px;
    width: 68px; height: 68px;
    background: var(--mc-color, #d1fae5);
    border-radius: 50%; opacity: 0.55;
    pointer-events: none;
}
.metric-card.green  { --mc-color: #d1fae5; }
.metric-card.orange { --mc-color: #fed7aa; }
.metric-card.blue   { --mc-color: #bae6fd; }
.metric-card.purple { --mc-color: #e9d5ff; }
.metric-card.teal   { --mc-color: #ccfbf1; }
.metric-card.red    { --mc-color: #fee2e2; }

/* ---- Section Cards ---- */
.section-card {
    background: white;
    border-radius: var(--radius);
    padding: 26px 28px;
    box-shadow: var(--shadow);
    border: 1px solid #e2e8f0;
    margin-bottom: 22px;
}
.section-card h3 {
    font-size: 1.15rem; font-weight: 800; color: #0f172a;
    margin: 0 0 18px 0; display: flex; align-items: center; gap: 10px;
    letter-spacing: -0.3px;
}

/* ---- Section Heading ---- */
.section-heading {
    font-size: 1.3rem; font-weight: 800; color: #0f172a;
    margin: 26px 0 14px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--border-accent);
    display: flex; align-items: center; gap: 10px;
}

/* ---- Badges / Tags ---- */
.tag {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 4px 11px;
    border-radius: 20px;
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
.tag-green  { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.tag-orange { background: #ffedd5; color: #c2410c; border: 1px solid #fed7aa; }
.tag-blue   { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
.tag-red    { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
.tag-purple { background: #f3e8ff; color: #7e22ce; border: 1px solid #e9d5ff; }

/* ---- Tables ---- */
.stDataFrame { border-radius: 12px !important; overflow: hidden !important; border: 1px solid #e2e8f0; }
.stDataFrame thead tr th {
    background: #f0fdf4 !important; color: #065f46 !important;
    font-weight: 700 !important; font-size: 0.8rem !important;
    text-transform: uppercase !important; letter-spacing: 0.5px !important;
}

/* ---- Buttons ---- */
.stButton > button {
    border-radius: 11px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 10px 22px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: none !important;
}
.stButton > button[kind="primary"], .stButton > button:not([kind]) {
    background: linear-gradient(135deg, #059669, #047857) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(5,150,105,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(5,150,105,0.42) !important;
}

/* ---- Inputs ---- */
.stTextInput input, .stNumberInput input, .stSelectbox select,
.stTextArea textarea {
    border-radius: 10px !important;
    border: 1.5px solid #d1fae5 !important;
    background: #fafffe !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus,
.stTextArea textarea:focus {
    border-color: #059669 !important;
    box-shadow: 0 0 0 3px rgba(5,150,105,0.15) !important;
    background: white !important;
}

/* ---- Alerts ---- */
.stSuccess { border-radius: 12px !important; border-left: 4px solid #059669 !important; background: #ecfdf5 !important; }
.stError   { border-radius: 12px !important; border-left: 4px solid #ef4444 !important; background: #fef2f2 !important; }
.stWarning { border-radius: 12px !important; border-left: 4px solid #f59e0b !important; background: #fffbeb !important; }
.stInfo    { border-radius: 12px !important; border-left: 4px solid #0ea5e9 !important; background: #f0f9ff !important; }

/* ---- Eco Impact Banner ---- */
.eco-banner {
    background: linear-gradient(135deg, #022c22 0%, #064e3b 50%, #065f46 100%);
    border-radius: 20px; padding: 28px 32px; margin: 20px 0;
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 20px;
    box-shadow: 0 10px 30px rgba(6,78,59,0.3);
    border: 1px solid rgba(52,211,153,0.2);
    position: relative; overflow: hidden;
}
.eco-banner::before {
    content: '🌱';
    position: absolute; right: 24px; top: 50%;
    transform: translateY(-50%);
    font-size: 5rem; opacity: 0.07;
}
.eco-banner .eco-item { flex: 1; min-width: 120px; padding: 0 12px; border-right: 1px solid rgba(255,255,255,0.1); }
.eco-banner .eco-item:last-child { border-right: none; }
.eco-banner .eco-title { color: #6ee7b7; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 700; margin-bottom: 6px; }
.eco-banner .eco-value { color: white; font-size: 1.7rem; font-weight: 800; letter-spacing: -0.5px; }
.eco-banner .eco-sub { color: #a7f3d0; font-size: 0.78rem; margin-top: 3px; }

/* ---- Food Card Grid ---- */
.food-card {
    background: white; border-radius: 16px;
    padding: 20px; border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 10px 15px -3px rgba(0,0,0,0.04);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%; position: relative; overflow: hidden;
}
.food-card:hover { transform: translateY(-5px); box-shadow: 0 20px 30px -10px rgba(5,150,105,0.2); border-color: #10b981; }
.food-card .fc-title { font-size: 1.05rem; font-weight: 800; color: #0f172a; margin-bottom: 6px; letter-spacing: -0.2px; }
.food-card .fc-provider { font-size: 0.8rem; color: #64748b; margin-bottom: 10px; }
.food-card .fc-qty {
    font-size: 1.5rem; font-weight: 800; color: #059669;
    display: inline-block; margin-right: 4px; letter-spacing: -0.5px;
}
.food-card .fc-qty-label { font-size: 0.72rem; color: #94a3b8; font-weight: 600; }
.food-card .fc-tags { margin-top: 10px; display: flex; gap: 6px; flex-wrap: wrap; }
.food-card .fc-expiry { font-size: 0.74rem; color: #94a3b8; margin-top: 10px; }
.food-card .fc-corner {
    position: absolute; top: 0; right: 0;
    width: 54px; height: 54px;
    background: linear-gradient(135deg, transparent 50%, #dcfce7 50%);
    border-top-right-radius: 16px;
}
.food-card .fc-urgency { font-size: 0.72rem; font-weight: 700; color: #dc2626; background: #fee2e2; padding: 2px 8px; border-radius: 999px; display: inline-block; margin-top: 6px; }

/* ---- Progress Bar ---- */
.progress-bar-wrap { margin: 8px 0; }
.progress-bar-label { display: flex; justify-content: space-between; font-size: 0.78rem; color: #64748b; margin-bottom: 5px; font-weight: 600; }
.progress-bar-bg { background: #e2e8f0; border-radius: 999px; height: 8px; overflow: hidden; }
.progress-bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #10b981, #059669); transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); }

/* ---- Leaderboard ---- */
.leader-row {
    display: flex; align-items: center; gap: 14px;
    padding: 12px 16px; border-radius: 12px;
    background: #f8fafc; margin-bottom: 8px;
    border: 1px solid #e2e8f0;
    transition: all 0.2s;
}
.leader-row:hover { background: #ecfdf5; border-color: #bbf7d0; transform: translateX(2px); }
.leader-rank { width: 32px; height: 32px; border-radius: 50%; background: #059669; color: white; font-size: 0.82rem; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.leader-rank.gold   { background: linear-gradient(135deg, #f59e0b, #d97706); box-shadow: 0 4px 10px rgba(245,158,11,0.3); }
.leader-rank.silver { background: linear-gradient(135deg, #94a3b8, #64748b); }
.leader-rank.bronze { background: linear-gradient(135deg, #d97706, #92400e); }
.leader-name { font-weight: 700; font-size: 0.92rem; color: #0f172a; flex: 1; }
.leader-sub  { font-size: 0.75rem; color: #64748b; }
.leader-value { font-weight: 800; font-size: 1rem; color: #059669; white-space: nowrap; }

/* ---- Divider ---- */
.fancy-divider { border: none; height: 1px; background: linear-gradient(90deg, #d1fae5, transparent); margin: 24px 0; }

/* ---- Timeline ---- */
.timeline-item {
    display: flex; gap: 16px; padding: 14px 0;
    border-bottom: 1px solid #f1f5f9;
}
.timeline-item:last-child { border-bottom: none; }
.timeline-dot { width: 12px; height: 12px; border-radius: 50%; margin-top: 5px; flex-shrink: 0; box-shadow: 0 0 0 3px rgba(0,0,0,0.05); }
.timeline-content .tl-title { font-size: 0.92rem; font-weight: 700; color: #0f172a; }
.timeline-content .tl-sub { font-size: 0.76rem; color: #94a3b8; margin-top: 3px; }

/* ---- Plotly override ---- */
.js-plotly-plot .plotly .modebar { display: none !important; }

/* ---- Sidebar Logo area ---- */
.sidebar-logo {
    text-align: center; padding: 24px 10px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;
}
.sidebar-logo .sb-emoji { font-size: 2.6rem; display: block; margin-bottom: 6px; }
.sidebar-logo .sb-title { font-size: 1.4rem; font-weight: 800; color: white; letter-spacing: -0.5px; }
.sidebar-logo .sb-sub { font-size: 0.7rem; color: #6ee7b7; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 2px; }

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 2px solid #e2e8f0 !important; }
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0 !important;
    padding: 10px 22px !important;
    font-weight: 600 !important; font-size: 0.88rem !important;
    color: #64748b !important;
    border: none !important; background: transparent !important;
    transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #059669 !important; background: #f0fdf4 !important; }
.stTabs [aria-selected="true"] {
    color: #064e3b !important; font-weight: 800 !important;
    background: #dcfce7 !important;
    border-bottom: 3px solid #059669 !important;
}

/* ---- Form ---- */
.stForm { background: #f8fafc; border-radius: 16px; padding: 24px; border: 1px solid #e2e8f0; }

/* ---- Expander ---- */
.streamlit-expanderHeader { font-weight: 700 !important; color: #0f172a !important; border-radius: 12px !important; }

/* ---- Scrollbar ---- */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #a7f3d0; border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: #34d399; }

/* ---- Urgency Chip for expiring food ---- */
.chip-urgent { background: #fee2e2; color: #dc2626; border-radius: 999px; padding: 3px 10px; font-size: 0.72rem; font-weight: 700; display: inline-block; }
.chip-ok     { background: #dcfce7; color: #15803d; border-radius: 999px; padding: 3px 10px; font-size: 0.72rem; font-weight: 700; display: inline-block; }

/* ---- Quick Action Panel ---- */
.quick-action {
    background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
    border-radius: 14px; padding: 18px 20px; border: 1px dashed #86efac;
    margin-bottom: 16px; text-align: center;
}
.quick-action h4 { color: #064e3b; font-size: 1rem; font-weight: 800; margin: 0 0 4px 0; }
.quick-action p { color: #64748b; font-size: 0.82rem; margin: 0; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo'>
        <span class='sb-emoji'>🌿</span>
        <div class='sb-title'>FoodBridge</div>
        <div class='sb-sub'>Wastage Management</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        import queries
        db_stat = queries.get_db_status()
        if db_stat.get("is_cloud"):
            db_badge = "<span class='pulse-indicator'></span>Neon Cloud DB"
            badge_border = "rgba(52, 211, 153, 0.4)"
            badge_bg = "rgba(16, 185, 129, 0.15)"
            badge_txt = "#a7f3d0"
        else:
            db_badge = "💻 Local SQLite"
            badge_border = "rgba(245, 158, 11, 0.4)"
            badge_bg = "rgba(245, 158, 11, 0.15)"
            badge_txt = "#fde68a"

        st.markdown(f"""
        <div style='text-align:center;margin:-10px 0 16px 0'>
            <span style='background:{badge_bg};border:1px solid {badge_border};border-radius:20px;
                         padding:4px 12px;font-size:0.68rem;font-weight:700;color:{badge_txt};'>
                {db_badge}
            </span>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass

    tab = st.radio("", [
        "🏠  Dashboard",
        "🍱  Food Listings",
        "📊  Claims Analytics",
        "📞  Contacts",
        "⚙️  Manage Listings",
    ], label_visibility="collapsed")

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.1);margin:18px 0'>", unsafe_allow_html=True)

    # Mini eco impact in sidebar
    try:
        import queries
        eco = queries.get_eco_impact_metrics()
        db_stat2 = queries.get_db_status()
        counts = db_stat2.get("counts", {})
        st.markdown(f"""
        <div style='padding:16px;background:rgba(255,255,255,0.07);border-radius:14px;border:1px solid rgba(255,255,255,0.12)'>
            <div style='font-size:0.68rem;color:#6ee7b7;text-transform:uppercase;letter-spacing:1.2px;font-weight:700;margin-bottom:14px'>
                🌍 Live Impact Stats
            </div>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px'>
                <div>
                    <div style='color:white;font-size:1.15rem;font-weight:800'>{eco["total_meals"]:,}</div>
                    <div style='color:#a7f3d0;font-size:0.68rem'>Meals Listed</div>
                </div>
                <div>
                    <div style='color:white;font-size:1.15rem;font-weight:800'>{eco["co2_saved_kg"]:,.0f}kg</div>
                    <div style='color:#a7f3d0;font-size:0.68rem'>CO₂ Saved</div>
                </div>
                <div>
                    <div style='color:white;font-size:1.15rem;font-weight:800'>{eco["completion_rate"]}%</div>
                    <div style='color:#a7f3d0;font-size:0.68rem'>Success Rate</div>
                </div>
                <div>
                    <div style='color:white;font-size:1.15rem;font-weight:800'>{counts.get("claims",0):,}</div>
                    <div style='color:#a7f3d0;font-size:0.68rem'>Total Claims</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("<div style='padding:18px 0 0;font-size:0.63rem;color:rgba(255,255,255,0.3);text-align:center'>FoodBridge v2.1 • Built with ❤️ for communities</div>", unsafe_allow_html=True)

# ── Route Views ───────────────────────────────────────────────────────────────
page_key = tab.strip().split("  ")[-1]  # strip icon+spaces

if page_key == "Dashboard":
    summary.display()
elif page_key == "Food Listings":
    food_listings.display()
elif page_key == "Claims Analytics":
    claims_analysis.display()
elif page_key == "Contacts":
    contacts.display()
elif page_key == "Manage Listings":
    manage_listings.display()
