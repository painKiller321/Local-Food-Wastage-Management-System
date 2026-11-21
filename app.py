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
    --primary:   #16a34a;
    --primary-light: #22c55e;
    --primary-dark:  #15803d;
    --accent:    #f97316;
    --accent2:   #06b6d4;
    --danger:    #ef4444;
    --warning:   #f59e0b;
    --bg:        #f0fdf4;
    --card-bg:   #ffffff;
    --border:    #d1fae5;
    --text:      #064e3b;
    --text-muted:#6b7280;
    --shadow:    0 4px 24px rgba(16,185,129,0.10);
    --radius:    16px;
}

/* ---- Base ---- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ---- Main container ---- */
.main .block-container {
    padding: 1.5rem 2rem 3rem 2rem !important;
    max-width: 1400px;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #064e3b 0%, #065f46 60%, #047857 100%) !important;
    border-right: none !important;
    min-width: 240px !important;
}
section[data-testid="stSidebar"] * {
    color: #d1fae5 !important;
}
section[data-testid="stSidebar"] .stRadio > div {
    gap: 4px;
}
section[data-testid="stSidebar"] .stRadio label {
    background: rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 10px 16px !important;
    margin: 2px 0;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
    font-weight: 500;
    display: block !important;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.15) !important;
    border-color: rgba(255,255,255,0.25) !important;
    transform: translateX(4px);
}
section[data-testid="stSidebar"] .stRadio [data-checked="true"] label,
section[data-testid="stSidebar"] .stRadio label[data-testid*="selected"] {
    background: rgba(255,255,255,0.20) !important;
    border-color: #34d399 !important;
}

/* ---- Page Header ---- */
.page-header {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #047857 100%);
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 28px;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(6,78,59,0.3);
}
.page-header::before {
    content: '';
    position: absolute; top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.page-header::after {
    content: '';
    position: absolute; bottom: -60px; right: 80px;
    width: 150px; height: 150px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.page-header h1 {
    color: white !important; font-size: 2rem !important;
    font-weight: 800 !important; margin: 0 !important;
    line-height: 1.2 !important;
}
.page-header p { color: #a7f3d0; font-size: 1rem; margin: 8px 0 0 0; }
.page-header .badge {
    display: inline-block; background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.75rem; font-weight: 600; color: #d1fae5;
    margin-bottom: 12px; letter-spacing: 1px; text-transform: uppercase;
}

/* ---- Metric Cards ---- */
.metric-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
.metric-card {
    flex: 1; min-width: 160px;
    background: white;
    border-radius: var(--radius);
    padding: 20px 22px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover { transform: translateY(-3px); box-shadow: 0 8px 32px rgba(16,185,129,0.18); }
.metric-card .mc-icon { font-size: 2rem; margin-bottom: 8px; }
.metric-card .mc-value {
    font-size: 1.9rem; font-weight: 800; color: var(--primary-dark);
    line-height: 1; margin-bottom: 4px;
}
.metric-card .mc-label { font-size: 0.78rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
.metric-card .mc-delta { font-size: 0.8rem; color: var(--primary); font-weight: 500; margin-top: 6px; }
.metric-card::after {
    content: '';
    position: absolute; right: -10px; top: -10px;
    width: 60px; height: 60px;
    background: var(--mc-color, #d1fae5);
    border-radius: 50%; opacity: 0.5;
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
    padding: 24px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    margin-bottom: 20px;
}
.section-card h3 {
    font-size: 1.1rem; font-weight: 700; color: var(--text);
    margin: 0 0 16px 0; display: flex; align-items: center; gap: 8px;
}

/* ---- Section Heading ---- */
.section-heading {
    font-size: 1.3rem; font-weight: 700; color: var(--text);
    margin: 24px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--border);
    display: flex; align-items: center; gap: 10px;
}

/* ---- Badges / Tags ---- */
.tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.tag-green  { background: #d1fae5; color: #065f46; }
.tag-orange { background: #fed7aa; color: #9a3412; }
.tag-blue   { background: #bae6fd; color: #0369a1; }
.tag-red    { background: #fee2e2; color: #991b1b; }
.tag-purple { background: #e9d5ff; color: #6b21a8; }

/* ---- Tables ---- */
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }
.stDataFrame thead tr th {
    background: #f0fdf4 !important; color: #065f46 !important;
    font-weight: 700 !important; font-size: 0.8rem !important;
    text-transform: uppercase !important; letter-spacing: 0.5px !important;
}

/* ---- Buttons ---- */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
    border: none !important;
}
.stButton > button[kind="primary"], .stButton > button:not([kind]) {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(16,185,129,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(16,185,129,0.4) !important;
}

/* ---- Inputs ---- */
.stTextInput input, .stNumberInput input, .stSelectbox select,
.stTextArea textarea {
    border-radius: 10px !important;
    border: 1.5px solid #d1fae5 !important;
    background: white !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(16,185,129,0.15) !important;
}

/* ---- Alerts ---- */
.stSuccess { border-radius: 10px !important; border-left: 4px solid #16a34a !important; }
.stError   { border-radius: 10px !important; border-left: 4px solid #ef4444 !important; }
.stWarning { border-radius: 10px !important; border-left: 4px solid #f59e0b !important; }
.stInfo    { border-radius: 10px !important; border-left: 4px solid #06b6d4 !important; }

/* ---- Eco Impact Banner ---- */
.eco-banner {
    background: linear-gradient(135deg, #064e3b, #065f46);
    border-radius: 16px; padding: 24px 28px; margin: 20px 0;
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 16px;
    box-shadow: 0 8px 24px rgba(6,78,59,0.25);
}
.eco-banner .eco-title { color: #a7f3d0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; }
.eco-banner .eco-value { color: white; font-size: 1.6rem; font-weight: 800; }
.eco-banner .eco-sub { color: #6ee7b7; font-size: 0.8rem; }

/* ---- Food Card Grid ---- */
.food-card {
    background: white; border-radius: 14px;
    padding: 18px; border: 1.5px solid var(--border);
    box-shadow: 0 2px 12px rgba(16,185,129,0.08);
    transition: all 0.25s ease;
    height: 100%; position: relative; overflow: hidden;
}
.food-card:hover { transform: translateY(-4px); box-shadow: 0 8px 28px rgba(16,185,129,0.18); border-color: var(--primary-light); }
.food-card .fc-title { font-size: 1.05rem; font-weight: 700; color: #064e3b; margin-bottom: 6px; }
.food-card .fc-provider { font-size: 0.8rem; color: #6b7280; margin-bottom: 10px; }
.food-card .fc-qty {
    font-size: 1.3rem; font-weight: 800; color: var(--primary);
    display: inline-block; margin-right: 6px;
}
.food-card .fc-qty-label { font-size: 0.75rem; color: #9ca3af; }
.food-card .fc-tags { margin-top: 10px; display: flex; gap: 6px; flex-wrap: wrap; }
.food-card .fc-expiry { font-size: 0.75rem; color: #6b7280; margin-top: 10px; }
.food-card .fc-corner {
    position: absolute; top: 0; right: 0;
    width: 48px; height: 48px;
    background: linear-gradient(135deg, transparent 50%, #d1fae5 50%);
    border-top-right-radius: 14px;
}

/* ---- Progress Bar ---- */
.progress-bar-wrap { margin: 6px 0; }
.progress-bar-label { display: flex; justify-content: space-between; font-size: 0.75rem; color: #6b7280; margin-bottom: 3px; }
.progress-bar-bg { background: #e5e7eb; border-radius: 999px; height: 7px; overflow: hidden; }
.progress-bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--primary-light), var(--primary)); transition: width 0.5s; }

/* ---- Leaderboard ---- */
.leader-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 14px; border-radius: 10px;
    background: #f0fdf4; margin-bottom: 6px;
    border: 1px solid #d1fae5;
    transition: background 0.2s;
}
.leader-row:hover { background: #dcfce7; }
.leader-rank { width: 28px; height: 28px; border-radius: 50%; background: var(--primary); color: white; font-size: 0.8rem; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.leader-rank.gold   { background: linear-gradient(135deg, #f59e0b, #d97706); }
.leader-rank.silver { background: linear-gradient(135deg, #9ca3af, #6b7280); }
.leader-rank.bronze { background: linear-gradient(135deg, #d97706, #92400e); }
.leader-name { font-weight: 600; font-size: 0.9rem; color: #064e3b; flex: 1; }
.leader-sub  { font-size: 0.75rem; color: #6b7280; }
.leader-value { font-weight: 800; font-size: 1.0rem; color: var(--primary-dark); }

/* ---- Divider ---- */
.fancy-divider { border: none; height: 2px; background: linear-gradient(90deg, var(--border), transparent); margin: 24px 0; border-radius: 2px; }

/* ---- Timeline ---- */
.timeline-item {
    display: flex; gap: 14px; padding: 12px 0;
    border-bottom: 1px solid #f0fdf4;
}
.timeline-dot { width: 12px; height: 12px; border-radius: 50%; margin-top: 4px; flex-shrink: 0; }
.timeline-content .tl-title { font-size: 0.9rem; font-weight: 600; color: #064e3b; }
.timeline-content .tl-sub { font-size: 0.75rem; color: #9ca3af; }

/* ---- Plotly override ---- */
.js-plotly-plot .plotly .modebar { display: none !important; }

/* ---- Sidebar Logo area ---- */
.sidebar-logo {
    text-align: center; padding: 20px 10px 10px;
    border-bottom: 1px solid rgba(255,255,255,0.15); margin-bottom: 16px;
}
.sidebar-logo .sb-title { font-size: 1.3rem; font-weight: 800; color: white; letter-spacing: -0.5px; }
.sidebar-logo .sb-sub { font-size: 0.72rem; color: #6ee7b7; letter-spacing: 1px; text-transform: uppercase; }

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 2px solid #d1fae5 !important; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    padding: 8px 20px !important;
    font-weight: 600 !important; font-size: 0.85rem !important;
    color: #6b7280 !important;
    border: none !important; background: transparent !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    color: var(--primary-dark) !important;
    background: #d1fae5 !important;
    border-bottom: 2px solid var(--primary) !important;
}

/* ---- Form ---- */
.stForm { background: #f0fdf4; border-radius: 14px; padding: 20px; border: 1px solid #d1fae5; }

/* ---- Expander ---- */
.streamlit-expanderHeader { font-weight: 600 !important; color: var(--text) !important; border-radius: 10px !important; }

/* ---- Scrollbar ---- */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f0fdf4; }
::-webkit-scrollbar-thumb { background: #a7f3d0; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #34d399; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo'>
        <div style='font-size:2.2rem'>🌿</div>
        <div class='sb-title'>FoodBridge</div>
        <div class='sb-sub'>Wastage Management</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        import queries
        db_stat = queries.get_db_status()
        if db_stat.get("is_cloud"):
            db_badge = "🟢 Neon Cloud PostgreSQL"
            badge_border = "rgba(52, 211, 153, 0.4)"
            badge_bg = "rgba(16, 185, 129, 0.15)"
            badge_txt = "#a7f3d0"
        else:
            db_badge = "💻 Local SQLite DB"
            badge_border = "rgba(245, 158, 11, 0.4)"
            badge_bg = "rgba(245, 158, 11, 0.15)"
            badge_txt = "#fde68a"

        st.markdown(f"""
        <div style='text-align:center;margin:-8px 0 14px 0'>
            <span style='background:{badge_bg};border:1px solid {badge_border};border-radius:20px;padding:3px 10px;font-size:0.68rem;font-weight:700;color:{badge_txt};letter-spacing:0.5px;'>
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

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.15);margin:16px 0'>", unsafe_allow_html=True)

    # Mini eco impact in sidebar
    try:
        import queries
        eco = queries.get_eco_impact_metrics()
        st.markdown(f"""
        <div style='padding:14px;background:rgba(255,255,255,0.08);border-radius:12px;border:1px solid rgba(255,255,255,0.15)'>
            <div style='font-size:0.7rem;color:#6ee7b7;text-transform:uppercase;letter-spacing:1px;font-weight:700;margin-bottom:10px'>🌍 Today's Impact</div>
            <div style='color:white;font-size:1.1rem;font-weight:800;margin-bottom:2px'>{eco["total_meals"]:,}</div>
            <div style='color:#a7f3d0;font-size:0.72rem;margin-bottom:10px'>Meals Available</div>
            <div style='color:white;font-size:1.1rem;font-weight:800;margin-bottom:2px'>{eco["co2_saved_kg"]:,.0f} kg</div>
            <div style='color:#a7f3d0;font-size:0.72rem;margin-bottom:10px'>CO₂ Saved</div>
            <div style='color:white;font-size:1.1rem;font-weight:800;margin-bottom:2px'>{eco["completion_rate"]}%</div>
            <div style='color:#a7f3d0;font-size:0.72rem'>Claim Success Rate</div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("<div style='padding:16px 0 0;font-size:0.65rem;color:rgba(255,255,255,0.3);text-align:center'>FoodBridge v2.0 • Built with ❤️</div>", unsafe_allow_html=True)

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
