import streamlit as st

NAV_ITEMS = [
    ("app.py", "Application", "🏠"),
    ("pages/ai.py", "IA", "✨"),
    ("pages/campaigns.py", "Campagnes", "📣"),
    ("pages/crm.py", "CRM", "👥"),
    ("pages/dashboard.py", "Tableau de bord", "📊"),
    ("pages/experience.py", "Expérience", "⭐"),
    ("pages/fan360.py", "Fan 360", "👤"),
    ("pages/matches.py", "Matchs", "⚽"),
    ("pages/ticketing.py", "Billetterie", "🎟️"),
]

def _css():
    return r"""
    <style>
    :root{
      --navy:#031126;
      --navy2:#061a35;
      --panel:#081d38;
      --panel2:#0b2444;
      --border:rgba(76,142,222,.30);
      --blue:#1687ff;
      --cyan:#1edcff;
      --green:#27e7a6;
      --purple:#8c5cff;
      --orange:#ffb020;
      --text:#f7fbff;
      --muted:#9db2cc;
    }

    html, body, [class*="css"]{
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp{
      background:
        radial-gradient(circle at 82% 3%, rgba(22,135,255,.18), transparent 25%),
        radial-gradient(circle at 57% 0%, rgba(30,220,255,.08), transparent 23%),
        linear-gradient(180deg,#031126 0%,#05162b 46%,#041326 100%);
      color:var(--text);
    }

    header[data-testid="stHeader"]{
      background:rgba(3,17,38,.72);
      backdrop-filter:blur(16px);
      border-bottom:1px solid rgba(78,137,202,.18);
    }

    .block-container{
      max-width:1540px;
      padding-top:1.0rem;
      padding-bottom:3rem;
    }

    /* hide Streamlit automatic multipage list: we draw our own premium navigation */
    [data-testid="stSidebarNav"]{display:none;}

    [data-testid="stSidebar"]{
      background:
        radial-gradient(circle at 10% 0%,rgba(22,135,255,.22),transparent 24%),
        linear-gradient(180deg,#031126 0%,#04101f 100%);
      border-right:1px solid rgba(61,119,189,.34);
    }

    [data-testid="stSidebarContent"]{
      padding-top:.8rem;
    }

    .fp-brand{
      padding:10px 8px 18px 8px;
    }
    .fp-brand-title{
      font-weight:900;
      font-size:1.55rem;
      color:white;
      line-height:1;
    }
    .fp-brand-title span{
      background:linear-gradient(90deg,#1591ff,#1edcff);
      -webkit-background-clip:text;
      -webkit-text-fill-color:transparent;
    }
    .fp-brand-sub{
      margin-top:8px;
      color:#35cfff;
      font-size:.70rem;
      font-weight:800;
      letter-spacing:.08em;
    }

    [data-testid="stPageLink"] a{
      border-radius:12px !important;
      padding:.58rem .72rem !important;
      margin:.12rem 0 !important;
      color:#e8f2ff !important;
      transition:.16s ease !important;
      border:1px solid transparent !important;
    }
    [data-testid="stPageLink"] a:hover{
      background:rgba(22,135,255,.13) !important;
      border-color:rgba(22,135,255,.34) !important;
      transform:translateX(3px);
    }

    .fp-sidebar-card{
      margin-top:22px;
      min-height:150px;
      border-radius:18px;
      padding:18px;
      border:1px solid rgba(22,135,255,.43);
      background:
        linear-gradient(145deg,rgba(11,41,77,.96),rgba(3,21,43,.98)),
        radial-gradient(circle at 90% 10%,rgba(30,220,255,.20),transparent 35%);
      box-shadow:0 14px 34px rgba(0,0,0,.18);
    }
    .fp-sidebar-card strong{color:white;font-size:1.08rem;}
    .fp-sidebar-card small{color:#a9bfd8;}

    h1,h2,h3,h4{color:#f8fbff !important;letter-spacing:-.02em;}
    p,label,span{color:#d8e4f1;}

    /* Top search */
    .fp-search-wrap{
      margin:0 0 12px 0;
    }
    .fp-search-wrap div[data-baseweb="input"] > div{
      min-height:44px !important;
      background:#0b2343 !important;
      border:1px solid rgba(72,132,203,.45) !important;
      border-radius:13px !important;
      box-shadow:inset 0 1px 0 rgba(255,255,255,.02);
    }

    /* Hero */
    .fp-hero{
      position:relative;
      overflow:hidden;
      min-height:212px;
      border-radius:24px;
      padding:29px 31px;
      margin:4px 0 17px 0;
      border:1px solid rgba(45,139,243,.39);
      background:
        linear-gradient(90deg,rgba(2,20,42,.98) 0%,rgba(5,35,67,.95) 55%,rgba(8,54,97,.75) 100%),
        radial-gradient(circle at 77% 20%,rgba(30,220,255,.25),transparent 25%),
        radial-gradient(circle at 94% 48%,rgba(22,135,255,.32),transparent 25%);
      box-shadow:0 20px 55px rgba(0,0,0,.25);
    }
    .fp-hero:before{
      content:"";
      position:absolute; inset:0;
      background:
        repeating-linear-gradient(115deg,transparent 0 70px,rgba(255,255,255,.018) 72px 73px);
      opacity:.8;
      pointer-events:none;
    }
    .fp-hero-orb{
      position:absolute;
      width:330px;height:330px;
      border-radius:50%;
      right:-80px;top:-95px;
      background:radial-gradient(circle,rgba(30,220,255,.21),rgba(22,135,255,.09) 42%,transparent 70%);
    }
    .fp-badge{
      display:inline-flex;
      align-items:center;
      padding:6px 11px;
      border-radius:999px;
      color:#bff4ff;
      background:rgba(30,220,255,.09);
      border:1px solid rgba(30,220,255,.28);
      font-size:.72rem;
      font-weight:850;
      letter-spacing:.04em;
      margin-bottom:12px;
    }
    .fp-title{
      position:relative;
      z-index:2;
      font-size:clamp(2.4rem,4vw,4rem);
      font-weight:950;
      line-height:.98;
      color:#fff;
      margin-bottom:12px;
    }
    .fp-title span{
      background:linear-gradient(90deg,#21a1ff,#20e2ed,#29e7a5);
      -webkit-background-clip:text;
      -webkit-text-fill-color:transparent;
    }
    .fp-subtitle{
      position:relative;
      z-index:2;
      max-width:720px;
      color:#c8d7e8;
      line-height:1.55;
      font-size:1rem;
    }
    .fp-slogan{
      position:absolute;
      z-index:2;
      right:32px;
      bottom:26px;
      width:250px;
      text-align:right;
      color:white;
      font-style:italic;
      font-size:1.10rem;
      font-weight:800;
      transform:rotate(-2deg);
    }
    .fp-slogan em{color:#29e7a5;font-style:normal;}

    /* KPI */
    .fp-kpi{
      min-height:138px;
      border-radius:19px;
      padding:17px 18px;
      position:relative;
      overflow:hidden;
      background:linear-gradient(145deg,rgba(10,32,61,.98),rgba(5,23,45,.98));
      border:1px solid rgba(62,123,196,.35);
      box-shadow:0 13px 32px rgba(0,0,0,.16);
    }
    .fp-kpi::after{
      content:"";
      position:absolute;
      width:150px;height:150px;
      border-radius:50%;
      right:-55px;bottom:-70px;
      background:radial-gradient(circle,rgba(22,135,255,.18),transparent 67%);
    }
    .fp-kpi.blue{border-color:rgba(22,135,255,.66);}
    .fp-kpi.green{border-color:rgba(39,231,166,.52);}
    .fp-kpi.purple{border-color:rgba(140,92,255,.57);}
    .fp-kpi.orange{border-color:rgba(255,176,32,.53);}
    .fp-kpi-icon{
      float:right;
      padding:8px 10px;
      border-radius:11px;
      font-size:1.20rem;
      background:rgba(22,135,255,.14);
    }
    .fp-kpi-label{color:#a9bcd2;font-size:.88rem;font-weight:700;margin-bottom:8px;}
    .fp-kpi-value{color:white;font-size:2rem;font-weight:900;line-height:1;margin-bottom:10px;}
    .fp-kpi-foot{color:#7f9ab8;font-size:.76rem;}
    .fp-up{color:#29e7a5;font-weight:800;}

    /* glass panels */
    .fp-panel{
      border-radius:20px;
      border:1px solid rgba(71,128,193,.30);
      background:linear-gradient(145deg,rgba(8,28,53,.98),rgba(4,20,39,.98));
      padding:19px;
      box-shadow:0 13px 32px rgba(0,0,0,.14);
      min-height:100px;
      margin-bottom:13px;
    }
    .fp-panel-title{font-size:1.00rem;font-weight:850;color:white;}
    .fp-panel-sub{font-size:.78rem;color:#8fa7c1;margin-top:2px;}

    div[data-testid="stMetric"]{
      background:linear-gradient(145deg,rgba(10,32,61,.98),rgba(5,23,45,.98));
      border:1px solid rgba(62,123,196,.35);
      padding:16px;
      border-radius:18px;
      box-shadow:0 12px 28px rgba(0,0,0,.12);
    }
    div[data-testid="stMetricLabel"] *{color:#9eb3ca !important;}
    div[data-testid="stMetricValue"] *{color:#fff !important;font-weight:850 !important;}

    [data-testid="stDataFrame"]{
      border:1px solid rgba(72,130,194,.32);
      border-radius:15px;
      overflow:hidden;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div{
      background:#081d38 !important;
      border-color:#294e79 !important;
      border-radius:12px !important;
      color:#fff !important;
    }
    input,textarea{color:#fff !important;}

    .stButton > button{
      border-radius:12px;
      min-height:42px;
      font-weight:800;
      color:white;
      background:linear-gradient(90deg,#0f6fe9,#188bff);
      border:1px solid #4ca8ff;
      box-shadow:0 8px 22px rgba(22,135,255,.17);
      transition:.16s ease;
    }
    .stButton > button:hover{
      color:white;
      transform:translateY(-1px);
      border-color:#5be5ff;
      box-shadow:0 10px 28px rgba(22,135,255,.27);
    }

    [data-testid="stAlert"]{border-radius:15px;}
    hr{border-color:rgba(82,134,193,.20);}

    @media(max-width:1050px){
      .fp-slogan{display:none;}
      .fp-hero{min-height:190px;}
    }
    </style>
    """

def setup(title, subtitle=None):
    st.set_page_config(
        page_title=f"{title} | FanPulse 360",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_css(), unsafe_allow_html=True)
    sidebar()

def sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="fp-brand">
              <div class="fp-brand-title">⚡ FanPulse <span>360</span></div>
              <div class="fp-brand-sub">FANS • DATA • EXPÉRIENCE • IA</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if hasattr(st, "page_link"):
            for path, label, icon in NAV_ITEMS:
                st.page_link(path, label=label, icon=icon)
        else:
            st.warning("Mets Streamlit à jour pour afficher le nouveau menu.")
        st.markdown(
            """
            <div class="fp-sidebar-card">
              <strong>⚡ FanPulse 360</strong><br>
              <small>Le fandom au cœur de la performance.</small><br><br>
              <span style="color:#29e7a5;font-weight:800">● Plateforme active</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

def hero(title="FanPulse", accent="360", subtitle=None, badge="FAN EXPERIENCE PLATFORM"):
    subtitle = subtitle or (
        "CRM, campagnes, billetterie, expérience des fans et IA. "
        "Toutes vos données supporters dans une seule plateforme."
    )
    st.markdown(
        f"""
        <div class="fp-hero">
          <div class="fp-hero-orb"></div>
          <div class="fp-badge">⚡ {badge}</div>
          <div class="fp-title">{title} <span>{accent}</span></div>
          <div class="fp-subtitle">{subtitle}</div>
          <div class="fp-slogan">Plus qu'un club,<br><em>une communauté.</em></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def page_header(icon, title, subtitle):
    st.markdown(
        f"""
        <div class="fp-panel" style="padding:21px 23px;margin-bottom:18px;">
          <div style="display:flex;gap:13px;align-items:center">
            <div style="font-size:1.8rem">{icon}</div>
            <div>
              <div style="font-size:1.55rem;font-weight:900;color:#fff">{title}</div>
              <div class="fp-panel-sub">{subtitle}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def kpi_card(label, value, icon="⚡", tone="blue", foot="Données en temps réel"):
    st.markdown(
        f"""
        <div class="fp-kpi {tone}">
          <span class="fp-kpi-icon">{icon}</span>
          <div class="fp-kpi-label">{label}</div>
          <div class="fp-kpi-value">{value}</div>
          <div class="fp-kpi-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def panel_title(title, subtitle=""):
    st.markdown(
        f"""
        <div style="margin-bottom:10px">
          <div class="fp-panel-title">{title}</div>
          <div class="fp-panel-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def fan_label(row):
    score = float(row.get("score_engagement", 0) or 0)
    return f'{row.get("prenom","")} {row.get("nom","")} — {row.get("segment_crm","")} — {score:.0f}/100'

def safe_switch(page_path):
    try:
        st.switch_page(page_path)
    except Exception:
        st.info("La sélection est mémorisée. Ouvre la page correspondante dans le menu.")
