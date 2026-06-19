import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import glob
import os
import base64

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
SUPERVISOR_COLORS = px.colors.qualitative.Bold
ORDEN_MESES = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO",
               "JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]
COLOR_PRIMARY = "#28053F"
COLOR_ACCENT  = "#0EA5E9"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER  = "#EF4444"

def _mes_orden(path):
    nombre = os.path.basename(path).upper()
    for i, mes in enumerate(ORDEN_MESES):
        if mes in nombre:
            return i
    return 99

def seg_a_hhmmss(seg):
    try:
        if pd.isna(seg) or seg < 0:
            return "—"
        h = int(seg // 3600)
        m = int((seg % 3600) // 60)
        s = int(seg % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception:
        return "—"

# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────
@st.cache_data
def cargar_datos(firma):
    archivos = sorted(glob.glob("Consolidado_O_*.xlsx"), key=_mes_orden)
    if not archivos:
        st.error("No se encontraron archivos Consolidado_O_*.xlsx en la carpeta.")
        st.stop()

    partes = []
    for archivo in archivos:
        df_mes = pd.read_excel(archivo, sheet_name="Consolidado", engine="openpyxl", dayfirst=True)
        df_mes["_archivo"] = os.path.basename(archivo)
        partes.append(df_mes)

    df = pd.concat(partes, ignore_index=True)
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")

    for col in ["Total Turno", "Tiempo Efectivo", "Ajuste", "Tiempo Dur. Llamadas", "Disponible"]:
        if col in df.columns:
            df[col + "_s"] = pd.to_timedelta(df[col], errors="coerce").dt.total_seconds()

    if "Semana" in df.columns:
        df["_semana_num"] = df["Semana"]
    df["Semana"]   = df["Fecha"].dt.to_period("W").apply(lambda p: f"Sem {p.start_time.strftime('%d/%m')}")
    df["Mes"]      = df["Fecha"].dt.to_period("M").astype(str)
    df["FechaStr"] = df["Fecha"].dt.strftime("%d/%m")

    return df, archivos

_firma_archivos = tuple(
    (os.path.basename(a), os.path.getmtime(a))
    for a in sorted(glob.glob("Consolidado_O_*.xlsx"), key=_mes_orden)
)
df, archivos_cargados = cargar_datos(_firma_archivos)

# ─────────────────────────────────────────────
# LOGO
# ─────────────────────────────────────────────
_LOGO_PATH = "logo-scala-learning-transformacion-digital-universidades.webp"

@st.cache_data
def _cargar_logo():
    try:
        with open(_LOGO_PATH, "rb") as _f:
            return f"data:image/webp;base64,{base64.b64encode(_f.read()).decode()}"
    except FileNotFoundError:
        return ""

_logo_src = _cargar_logo()

# Detectar columna Campaña (con o sin tilde)
_camp_col = "Campaña" if "Campaña" in df.columns else ("Campana" if "Campana" in df.columns else None)

# ─────────────────────────────────────────────
# SIDEBAR – FILTROS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class='sbc'>
        <div class='sbc-orb sbc-orb-1'></div>
        <div class='sbc-orb sbc-orb-2'></div>
        <div class='sbc-orb sbc-orb-3'></div>
        <div class='sbc-live'><span class='sbc-pulse'></span>LIVE</div>
        <div class='sbc-body'>
            <div class='sbc-logo-wrap'>
                <img src='{_logo_src}' class='sbc-logo-img' />
            </div>
            <div class='sbc-name'>Workforce Management</div>
            <div class='sbc-org'>Uniminuto &nbsp;·&nbsp; Scala Learning</div>
            <div class='sbc-stats'>
                <div class='sbc-stat'><span class='sbc-sv'>2026</span><span class='sbc-sl'>Año</span></div>
                <div class='sbc-sep'></div>
                <div class='sbc-stat'><span class='sbc-sv'>WFM</span><span class='sbc-sl'>Área</span></div>
                <div class='sbc-sep'></div>
                <div class='sbc-stat'><span class='sbc-sv'>COL</span><span class='sbc-sl'>País</span></div>
            </div>
        </div>
        <div class='sbc-bar'></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div class='sbh'>
        <div class='sbh-num' style='color:#38BDF8!important;background:rgba(56,189,248,0.12);border-color:rgba(56,189,248,0.22)'>01</div>
        <div class='sbh-lbl'>Período</div>
        <div class='sbh-rule'></div>
    </div>""", unsafe_allow_html=True)
    tipo_periodo = st.selectbox("Agrupar por", ["Día","Semana","Mes"], index=0)

    meses_disp = ["Todos"] + [
        os.path.basename(a).replace("Consolidado_O_", "").replace(".xlsx", "").capitalize()
        for a in archivos_cargados
    ]
    mes_sel = st.selectbox("Mes", meses_disp)

    if "_semana_num" in df.columns:
        _vals_sem = sorted(df["_semana_num"].dropna().astype(int).unique().tolist())
        semanas_disp = ["Todas"] + [str(v) for v in _vals_sem]
    else:
        semanas_disp = ["Todas"] + sorted(df["Semana"].dropna().unique().tolist())
    sem_sel = st.selectbox("Semana", semanas_disp)

    if "Trimestre" in df.columns:
        trimestres_disp = ["Todos"] + sorted(df["Trimestre"].dropna().astype(str).unique().tolist())
        tri_sel = st.selectbox("Trimestre", trimestres_disp)
    else:
        tri_sel = "Todos"

    if "Semestre" in df.columns:
        semestres_disp = ["Todos"] + sorted(df["Semestre"].dropna().astype(str).unique().tolist())
        semestre_sel = st.selectbox("Semestre", semestres_disp)
    else:
        semestre_sel = "Todos"

    fechas = sorted(df["Fecha"].dt.date.dropna().unique())
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha_ini = st.date_input("Desde", value=fechas[0], min_value=fechas[0], max_value=fechas[-1])
    with col_f2:
        fecha_fin = st.date_input("Hasta", value=fechas[-1], min_value=fechas[0], max_value=fechas[-1])

    st.markdown("""<div class='sbh'>
        <div class='sbh-num' style='color:#34D399!important;background:rgba(52,211,153,0.12);border-color:rgba(52,211,153,0.22)'>02</div>
        <div class='sbh-lbl'>Filtros</div>
        <div class='sbh-rule'></div>
    </div>""", unsafe_allow_html=True)

    if "Coordinador" in df.columns:
        coordinadores = ["Todos"] + sorted(df["Coordinador"].dropna().unique().tolist())
        coord_sel = st.selectbox("Coordinador", coordinadores)
    else:
        coord_sel = "Todos"

    supervisores = ["Todos"] + sorted(df["Supervisor"].dropna().unique().tolist())
    sup_sel = st.selectbox("Supervisor", supervisores)

    expertos = ["Todos"] + sorted(df["Nombre"].dropna().unique().tolist())
    exp_sel = st.selectbox("Experto", expertos)

    if _camp_col:
        campanas = ["Todas"] + sorted(df[_camp_col].dropna().unique().tolist())
        camp_sel = st.selectbox("Campaña", campanas)
    else:
        camp_sel = "Todas"

    st.markdown("""
    <div class='sbf'>
        <div class='sbf-card'>
            <div class='sbf-glow'></div>
            <div class='sbf-row'>
                <div class='sbf-avatar'>GC<span class='sbf-online'></span></div>
                <div class='sbf-info'>
                    <div class='sbf-name'>Guillermo Calderón</div>
                    <div class='sbf-role'>Analista WFM · Scala Learning</div>
                </div>
            </div>
        </div>
        <div class='sbf-credit'><span class='sbf-spark'>⚡</span>Desarrollado por Workforce Management</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');
    * {{ font-family: 'Inter', sans-serif !important; }}
    span[data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="collapsedControl"] span,
    .material-symbols-rounded, .material-symbols-outlined, .material-icons {{
        font-family: 'Material Symbols Rounded','Material Symbols Outlined','Material Icons' !important;
    }}
    [data-testid="stSidebarNav"] {{ display:none !important; }}

    /* ══ Fondo oscuro aurora ══ */
    [data-testid="stAppViewContainer"], .main {{
        background:
            radial-gradient(ellipse 90% 55% at 6% -6%,  rgba(14,165,233,0.16) 0%, transparent 55%),
            radial-gradient(ellipse 80% 55% at 100% 0%, rgba(99,102,241,0.17) 0%, transparent 55%),
            radial-gradient(ellipse 75% 60% at 92% 100%, rgba(52,211,153,0.08) 0%, transparent 55%),
            radial-gradient(ellipse 60% 50% at 0% 100%, rgba(99,102,241,0.07) 0%, transparent 55%),
            linear-gradient(160deg, #0A0813 0%, #0F0B20 45%, #08060F 100%);
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    .block-container {{ padding-top: 2rem; padding-bottom: 1rem; }}

    /* ══ Sidebar collapse button ══ */
    [data-testid="stSidebarCollapseButton"] button,
    div[data-testid="collapsedControl"] button {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 10px !important; transition: all .2s ease !important;
    }}
    div[data-testid="collapsedControl"] button {{
        background: rgba(40,5,63,0.06) !important;
        border: 1px solid rgba(40,5,63,0.15) !important;
    }}
    [data-testid="stSidebarCollapseButton"] button:hover,
    div[data-testid="collapsedControl"] button:hover {{ border-color: rgba(14,165,233,0.45) !important; }}
    [data-testid="stSidebarCollapseButton"] span {{ color: rgba(255,255,255,0.80) !important; font-size:20px !important; }}
    div[data-testid="collapsedControl"] span {{ color: {COLOR_PRIMARY} !important; font-size:20px !important; }}
    div[data-testid="stSidebarContent"] {{ width:100%!important; box-sizing:border-box!important; padding-right:0.75rem!important; }}
    div[data-testid="stSidebarContent"] > div {{ width:100%!important; }}

    /* ══ SIDEBAR BASE ══ */
    section[data-testid="stSidebar"] > div:first-child {{
        background:
            radial-gradient(ellipse 95% 42% at 8% 0%,    rgba(14,165,233,0.30) 0%, transparent 55%),
            radial-gradient(ellipse 90% 42% at 100% 26%, rgba(129,140,248,0.28) 0%, transparent 55%),
            radial-gradient(ellipse 85% 42% at 50% 102%, rgba(52,211,153,0.15) 0%, transparent 55%),
            linear-gradient(160deg, #0B0518 0%, #14082b 45%, #0A0414 100%);
        border-right: 1px solid rgba(255,255,255,0.07);
    }}
    div[data-testid="stSidebarContent"] * {{ color: white !important; }}
    [data-testid="stSidebarHeader"] {{ padding-top:0.6rem!important; padding-bottom:0!important; }}
    [data-testid="stSidebarUserContent"] {{ padding-top:0!important; }}
    section[data-testid="stSidebar"] > div:first-child {{
        display:flex!important; flex-direction:column!important; min-height:100vh!important; }}
    [data-testid="stSidebarUserContent"] {{
        flex:1 1 auto!important; display:flex!important; flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] > div {{ flex:1 1 auto!important; display:flex!important; flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:last-of-type {{ margin-top:auto!important; }}
    div[data-testid="stSidebarContent"] hr {{
        border-color: rgba(255,255,255,0.08);
        margin-top: 4px !important; margin-bottom: 4px !important;
    }}

    /* ══ ANIMATIONS ══ */
    @keyframes sbcBar   {{ 0% {{ background-position:0% 0%; }} 100% {{ background-position:200% 0%; }} }}
    @keyframes sbcPulse {{ 0%,100% {{ opacity:1; transform:scale(1); }} 50% {{ opacity:.3; transform:scale(.6); }} }}

    /* ══ BRAND CARD ══ */
    .sbc {{ position:relative;border-radius:20px;overflow:hidden;margin:0 0 20px;padding:20px 18px 18px;
            background:linear-gradient(145deg,rgba(56,189,248,0.12) 0%,rgba(129,140,248,0.09) 55%,rgba(52,211,153,0.07) 100%),rgba(255,255,255,0.04);
            border:1px solid rgba(255,255,255,0.12); }}
    .sbc-orb {{ position:absolute;border-radius:50%;pointer-events:none; }}
    .sbc-orb-1 {{ width:140px;height:140px;background:radial-gradient(circle,rgba(56,189,248,0.18) 0%,transparent 70%);top:-50px;right:-40px; }}
    .sbc-orb-2 {{ width:90px;height:90px;background:radial-gradient(circle,rgba(129,140,248,0.16) 0%,transparent 70%);bottom:-30px;left:-25px; }}
    .sbc-orb-3 {{ width:60px;height:60px;background:radial-gradient(circle,rgba(52,211,153,0.14) 0%,transparent 70%);top:50%;right:12px; }}
    .sbc-live {{ position:absolute;top:14px;right:14px;display:flex;align-items:center;gap:5px;
                 font-size:8px!important;font-weight:800!important;color:#34D399!important;
                 background:rgba(52,211,153,0.13);border:1px solid rgba(52,211,153,0.30);
                 padding:3px 9px 3px 7px;border-radius:99px;letter-spacing:0.10em;z-index:2; }}
    .sbc-pulse {{ width:5px;height:5px;background:#34D399;border-radius:50%;display:inline-block;animation:sbcPulse 1.8s ease-in-out infinite; }}
    .sbc-body  {{ position:relative;z-index:1;text-align:center; }}
    .sbc-logo-wrap {{ margin-bottom:10px;display:flex;justify-content:center;align-items:center; }}
    .sbc-logo-img  {{ max-width:150px!important;height:auto!important;filter:drop-shadow(0 4px 14px rgba(56,189,248,0.45)) brightness(1.05);display:block; }}
    .sbc-name {{ font-size:13px!important;font-weight:700!important;color:rgba(255,255,255,0.88)!important;letter-spacing:0!important;margin-bottom:4px!important; }}
    .sbc-org  {{ font-size:10px!important;color:rgba(255,255,255,0.35)!important;margin-bottom:16px!important; }}
    .sbc-stats {{ display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.22);border-radius:12px;padding:10px 8px;border:1px solid rgba(255,255,255,0.07); }}
    .sbc-stat  {{ flex:1;text-align:center; }}
    .sbc-sv {{ display:block;font-size:14px!important;font-weight:900!important;color:white!important;line-height:1;margin-bottom:3px; }}
    .sbc-sl {{ display:block;font-size:8px!important;font-weight:700!important;color:rgba(255,255,255,0.28)!important;letter-spacing:0.10em;text-transform:uppercase; }}
    .sbc-sep {{ width:1px;height:28px;background:rgba(255,255,255,0.09);flex-shrink:0; }}
    .sbc-bar {{ position:absolute;bottom:0;left:0;right:0;height:3px;
                background:linear-gradient(90deg,#38BDF8,#818CF8,#34D399,#F59E0B,#38BDF8);
                background-size:300% 100%;animation:sbcBar 4s linear infinite; }}

    /* ══ SECTION HEADERS (sidebar) ══ */
    .sbh {{ display:flex;align-items:center;gap:10px;margin:24px 0 12px; }}
    .sbh-num {{ font-size:10px!important;font-weight:900!important;width:28px;height:22px;border-radius:7px;border:1px solid;
               display:flex;align-items:center;justify-content:center;flex-shrink:0;letter-spacing:0.04em; }}
    .sbh-lbl {{ font-size:10px!important;font-weight:800!important;color:rgba(255,255,255,0.60)!important;
               letter-spacing:0.14em!important;text-transform:uppercase!important;white-space:nowrap!important; }}
    .sbh-rule {{ flex:1;height:1px;background:rgba(255,255,255,0.08); }}

    /* ══ DROPDOWNS ══ */
    div[data-baseweb="popover"] *, div[data-baseweb="menu"] *,
    ul[role="listbox"] *, li[role="option"], li[role="option"] * {{ color: #1E293B !important; }}
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {{ background: #F1F5F9 !important; }}

    /* ══ SELECTBOX ══ */
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] span,
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] div[class*="ValueContainer"] *,
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] input {{ color: white !important; }}
    div[data-testid="stSidebarContent"] input[type="text"] {{ color: white !important; }}
    div[data-testid="stSidebarContent"] label,
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"],
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"] p,
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"] span {{
        font-size: 11px !important; font-weight: 500 !important; color: rgba(255,255,255,0.50) !important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput label,
    div[data-testid="stSidebarContent"] .stDateInput [data-testid="stWidgetLabel"] p {{
        font-size: 11px !important; font-weight: 600 !important; color: #38BDF8 !important;
    }}
    div[data-testid="stSidebarContent"] .stSelectbox > div > div,
    div[data-testid="stSidebarContent"] .stSelectbox > label + div > div {{
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 9px !important; transition: border-color .18s, box-shadow .18s !important;
    }}
    div[data-testid="stSidebarContent"] .stSelectbox > div > div:hover {{
        border-color: rgba(56,189,248,0.50) !important;
        box-shadow: 0 0 0 3px rgba(56,189,248,0.10) !important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput > div > div > input {{
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 9px !important; color: white !important; font-size: 11px !important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput > div > div > input:focus {{
        border-color: rgba(56,189,248,0.50) !important;
        box-shadow: 0 0 0 3px rgba(56,189,248,0.10) !important;
    }}

    /* ══ FOOTER ══ */
    .sbf {{ margin-top:26px;padding:0; }}
    .sbf-card {{ position:relative;overflow:hidden;border-radius:16px;padding:14px 14px;
        background:linear-gradient(150deg,rgba(56,189,248,0.10),rgba(129,140,248,0.06));
        border:1px solid rgba(255,255,255,0.10);box-shadow:inset 0 1px 0 rgba(255,255,255,0.08); }}
    .sbf-glow {{ position:absolute;width:120px;height:120px;border-radius:50%;top:-50px;right:-40px;
        background:radial-gradient(circle,rgba(56,189,248,0.20),transparent 70%);pointer-events:none; }}
    .sbf-row {{ display:flex;align-items:center;gap:12px;position:relative;z-index:1; }}
    .sbf-avatar {{ position:relative;width:42px;height:42px;border-radius:13px;
                   background:linear-gradient(135deg,#38BDF8 0%,#818CF8 100%);
                   display:flex;align-items:center;justify-content:center;font-size:14px!important;font-weight:900!important;
                   color:white!important;flex-shrink:0;letter-spacing:0.5px;
                   box-shadow:0 6px 18px rgba(56,189,248,0.45),inset 0 1px 0 rgba(255,255,255,0.3); }}
    .sbf-online {{ position:absolute;bottom:-2px;right:-2px;width:12px;height:12px;border-radius:50%;
        background:#34D399;border:2.5px solid #130A2B;box-shadow:0 0 8px rgba(52,211,153,0.8);
        animation:sbcPulse 2s ease-in-out infinite; }}
    .sbf-name   {{ font-size:12px!important;font-weight:700!important;color:rgba(255,255,255,0.92)!important;margin-bottom:3px!important; }}
    .sbf-role   {{ font-size:10px!important;color:rgba(255,255,255,0.42)!important;line-height:1.3; }}
    .sbf-credit {{ display:flex;align-items:center;justify-content:center;gap:5px;
        margin-top:12px;font-size:9px!important;font-weight:600!important;
        color:rgba(255,255,255,0.30)!important;text-align:center;letter-spacing:0.06em; }}
    .sbf-spark {{ font-size:10px; }}

    /* ══ HEADER BANNER ══ */
    .st-key-hdrbanner {{
        position:relative;overflow:hidden;
        background:
            radial-gradient(ellipse 70% 130% at 2% -15%,  rgba(14,165,233,0.34) 0%, transparent 60%),
            radial-gradient(ellipse 65% 130% at 100% 120%,rgba(129,140,248,0.34) 0%, transparent 60%),
            radial-gradient(ellipse 55% 110% at 72% 130%, rgba(52,211,153,0.16)  0%, transparent 60%),
            linear-gradient(155deg, #0B0518 0%, #14082b 50%, #0A0414 100%);
        border:1px solid rgba(255,255,255,0.10);border-radius:20px;
        padding:18px 30px;margin-bottom:18px;
        box-shadow:0 18px 46px -18px rgba(0,0,0,0.45),inset 0 1px 0 rgba(255,255,255,0.08);
    }}
    .hb-eyebrow {{ display:inline-flex;align-items:center;gap:8px;
        background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.16);
        border-radius:99px;padding:5px 13px;margin-bottom:11px;
        font-size:10px;font-weight:700;color:rgba(255,255,255,0.78);letter-spacing:0.12em;text-transform:uppercase; }}
    .hb-dot {{ width:7px;height:7px;border-radius:50%;background:#34D399;
        box-shadow:0 0 9px #34D399;animation:sbcPulse 1.8s ease-in-out infinite; }}
    .hb-title {{ font-family:'Space Grotesk',sans-serif!important;
        font-size:29px;font-weight:700;color:white;margin:0 0 9px;letter-spacing:-0.8px;line-height:1.05; }}
    .hb-meta {{ display:flex;flex-wrap:wrap;gap:8px;margin:0 0 2px; }}
    .hb-chip {{ display:inline-flex;align-items:center;gap:6px;
        background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.13);
        border-radius:9px;padding:5px 11px;font-size:11px;font-weight:600;color:rgba(255,255,255,0.74); }}
    .hb-chip b {{ color:#fff;font-weight:700; }}
    .nav-lbl {{ font-size:9px;font-weight:800;letter-spacing:0.16em;text-transform:uppercase;
        color:rgba(255,255,255,0.40);margin:3px 0 7px; }}
    .st-key-hdrbanner [data-testid="stVerticalBlock"] {{ gap:0.5rem !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button {{
        position:relative;z-index:2;overflow:hidden;white-space:nowrap !important;
        color:#CBD3F2 !important;border-radius:9px !important;
        font-size:10px !important;font-weight:700 !important;
        height:32px !important;min-height:32px !important;padding:0 11px !important;
        border:1px solid rgba(255,255,255,0.12) !important;border-top-color:rgba(255,255,255,0.18) !important;
        background:linear-gradient(180deg,rgba(255,255,255,0.085),rgba(255,255,255,0.025)) !important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.10),inset 0 -2px 6px -2px rgba(0,0,0,0.35),0 4px 12px -8px rgba(8,3,24,0.60) !important;
        transition:transform .16s ease,box-shadow .16s ease,background .16s ease,border-color .16s ease,color .16s ease !important;
    }}
    .st-key-hdrbanner [data-testid="stButton"] > button p {{ white-space:nowrap !important;margin:0 !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button:hover {{
        color:#EAF2FF !important;transform:translateY(-1px) !important;
        border-color:rgba(125,211,252,0.42) !important;
        background:linear-gradient(180deg,rgba(125,211,252,0.15),rgba(255,255,255,0.04)) !important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.16),0 8px 20px -10px rgba(56,189,248,0.38) !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button:active {{
        transform:translateY(0) !important;box-shadow:inset 0 2px 5px rgba(0,0,0,0.48) !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"] {{
        color:#F4F9FF !important;padding-left:20px !important;
        border:1px solid rgba(56,189,248,0.55) !important;border-top-color:rgba(186,225,255,0.62) !important;
        background:linear-gradient(180deg,rgba(56,189,248,0.30),rgba(59,130,246,0.16)) !important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.22),inset 0 -8px 14px -12px rgba(8,3,24,0.42),0 8px 22px -10px rgba(56,189,248,0.50) !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"]::before {{
        content:"";position:absolute;left:8px;top:50%;transform:translateY(-50%);
        width:5px;height:5px;border-radius:50%;background:#7DD3FC;box-shadow:0 0 8px rgba(125,211,252,0.9); }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"]:hover {{
        transform:translateY(-1px) !important;
        background:linear-gradient(180deg,rgba(56,189,248,0.36),rgba(59,130,246,0.20)) !important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.24),0 10px 26px -10px rgba(56,189,248,0.58) !important; }}

    /* ══ KPI CARDS ══ */
    .kpi-card {{
        background:linear-gradient(160deg,rgba(255,255,255,0.07) 0%,rgba(255,255,255,0.02) 100%);
        border-radius:20px;padding:22px 22px 18px;
        box-shadow:0 20px 44px -18px rgba(0,0,0,0.7),inset 0 1px 0 rgba(255,255,255,0.08);
        backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
        position:relative;overflow:hidden;min-height:148px;
        display:flex;flex-direction:column;justify-content:space-between;
        border:1px solid rgba(255,255,255,0.10);
        transition:transform 0.24s ease,box-shadow 0.24s ease,border-color 0.24s ease;cursor:default;
    }}
    .kpi-card:hover {{
        transform:translateY(-6px);border-color:var(--kc,{COLOR_ACCENT});
        box-shadow:0 30px 60px -22px rgba(0,0,0,0.8),0 0 36px -12px var(--kc,{COLOR_ACCENT}),inset 0 1px 0 rgba(255,255,255,0.10);
    }}
    .kpi-card::before {{
        content:'';position:absolute;top:0;left:0;right:0;height:4px;
        background:var(--kc,{COLOR_PRIMARY});box-shadow:0 0 18px -2px var(--kc,{COLOR_PRIMARY});
    }}
    .kpi-card::after {{
        content:'';position:absolute;top:-40px;right:-40px;width:120px;height:120px;
        background:radial-gradient(circle,var(--kc,{COLOR_PRIMARY}),transparent 70%);opacity:0.22;border-radius:50%;
    }}
    .kpi-bg-icon {{ position:absolute;bottom:12px;right:16px;font-size:46px;opacity:0.10;line-height:1;pointer-events:none;z-index:0; }}
    .kpi-label {{ font-size:10px;color:rgba(255,255,255,0.50);font-weight:700;text-transform:uppercase;letter-spacing:0.10em;position:relative;z-index:1; }}
    .kpi-value {{ font-family:'Space Grotesk',sans-serif!important;font-size:34px;font-weight:700;line-height:1.1;margin:10px 0 4px;position:relative;z-index:1;letter-spacing:-0.5px;text-shadow:0 2px 16px rgba(0,0,0,0.4); }}
    .kpi-sub   {{ font-size:11px;color:rgba(255,255,255,0.42);position:relative;z-index:1; }}
    .kpi-bar-wrap {{ background:rgba(255,255,255,0.09);border-radius:99px;height:5px;margin-top:12px;overflow:hidden;position:relative;z-index:1; }}
    .kpi-bar-fill {{ height:5px;border-radius:99px;box-shadow:0 0 10px -1px currentColor; }}

    /* ══ SECTION HEADER ══ */
    .sec-header {{
        background:
            radial-gradient(ellipse at 12% 35%,rgba(255,255,255,0.18) 0%,transparent 55%),
            radial-gradient(ellipse at 92% 135%,rgba(0,0,0,0.24) 0%,transparent 55%),
            var(--sc,{COLOR_PRIMARY});
        border-radius:20px;padding:22px 28px;margin:34px 0 18px;
        box-shadow:0 18px 42px -12px rgba(15,23,42,0.45);
        position:relative;overflow:hidden;display:flex;align-items:center;gap:18px;
        border:1px solid rgba(255,255,255,0.14);
    }}
    .sec-header::before {{ content:'';position:absolute;left:-25px;top:-35px;width:130px;height:130px;background:rgba(255,255,255,0.10);border-radius:50%; }}
    .sec-header::after  {{ content:'';position:absolute;right:-35px;bottom:-45px;width:150px;height:150px;background:rgba(255,255,255,0.07);border-radius:50%; }}
    .sec-wash {{ display:none; }}
    .sec-icon {{ width:56px;height:56px;border-radius:16px;display:flex;align-items:center;justify-content:center;
                 font-size:27px;flex-shrink:0;position:relative;z-index:1;
                 background:rgba(255,255,255,0.18)!important;border:1px solid rgba(255,255,255,0.28)!important;
                 box-shadow:0 8px 18px -6px rgba(0,0,0,0.4); }}
    .sec-text {{ flex:1;min-width:0;position:relative;z-index:1; }}
    .sec-title {{ font-size:19px;font-weight:800;color:white;margin:0 0 5px 0;letter-spacing:-0.4px; }}
    .sec-desc  {{ font-size:12px;color:rgba(255,255,255,0.78);margin:0;line-height:1.6; }}
    .sec-meta {{ text-align:center;flex-shrink:0;padding:9px 20px;background:rgba(255,255,255,0.96);
                 border-radius:13px;border:1px solid rgba(255,255,255,0.5);
                 box-shadow:0 6px 16px -6px rgba(0,0,0,0.3);position:relative;z-index:1; }}
    .sec-meta-val {{ font-family:'Space Grotesk',sans-serif!important;font-size:24px;font-weight:700;line-height:1.1;margin-bottom:2px;letter-spacing:-0.5px; }}
    .sec-meta-lab {{ font-size:9px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.08em; }}
    .sec-tag {{ font-size:10px;font-weight:700;color:white;background:rgba(255,255,255,0.20);
                border:1px solid rgba(255,255,255,0.35);padding:5px 14px;border-radius:99px;
                letter-spacing:0.06em;text-transform:uppercase;flex-shrink:0;align-self:flex-start;position:relative;z-index:1; }}

    /* ══ CHART MINI-HEADERS ══ */
    .chart-hdr {{ display:flex;align-items:center;gap:12px;padding:12px 16px;
        background:linear-gradient(180deg,rgba(255,255,255,0.07),rgba(255,255,255,0.025));
        border-radius:14px;border:1px solid rgba(255,255,255,0.10);
        border-left:4px solid var(--cc,{COLOR_ACCENT});
        box-shadow:0 8px 22px -10px rgba(0,0,0,0.6),inset 0 1px 0 rgba(255,255,255,0.06);
        margin-bottom:12px; }}
    .ch-icon {{ font-size:18px;line-height:1;flex-shrink:0;width:36px;height:36px;border-radius:10px;
               display:flex;align-items:center;justify-content:center;
               background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12); }}
    .ch-texts {{ flex:1;min-width:0; }}
    .ch-title {{ font-size:13px;font-weight:800;color:#F1F4FF;margin:0 0 1px;letter-spacing:-0.2px; }}
    .ch-sub   {{ font-size:10.5px;color:rgba(255,255,255,0.45);margin:0; }}
    .ch-tag   {{ margin-left:auto;font-size:9px;font-weight:700;color:var(--cc,{COLOR_ACCENT});
               background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);
               padding:3px 9px;border-radius:99px;letter-spacing:0.05em;flex-shrink:0;text-transform:uppercase; }}

    /* ══ TABLE HEADERS ══ */
    .tbl-hdr {{ padding:14px 20px;border-radius:14px;display:flex;align-items:center;gap:12px;
               margin-bottom:6px;box-shadow:0 4px 18px rgba(0,0,0,0.15);position:relative;overflow:hidden; }}
    .tbl-hdr::before {{ content:'';position:absolute;left:-10px;top:-10px;width:60px;height:60px;background:rgba(255,255,255,0.08);border-radius:50%; }}
    .tbl-hdr::after  {{ content:'';position:absolute;right:-20px;bottom:-20px;width:80px;height:80px;background:rgba(255,255,255,0.10);border-radius:50%; }}
    .tbl-hdr-icon  {{ font-size:24px;flex-shrink:0;position:relative;z-index:1; }}
    .tbl-hdr-body  {{ flex:1;position:relative;z-index:1; }}
    .tbl-hdr-title {{ font-size:14px;font-weight:800;color:white;margin:0 0 2px;letter-spacing:-0.2px; }}
    .tbl-hdr-desc  {{ font-size:11px;color:rgba(255,255,255,0.72);margin:0; }}
    .tbl-hdr-badge {{ font-size:10px;font-weight:700;color:white;background:rgba(255,255,255,0.20);
                      border:1px solid rgba(255,255,255,0.35);padding:4px 12px;border-radius:99px;
                      flex-shrink:0;white-space:nowrap;position:relative;z-index:1; }}

    /* ══ PLOTLY CHART ══ */
    div[data-testid="stPlotlyChart"] {{
        background:linear-gradient(160deg,rgba(255,255,255,0.05),rgba(255,255,255,0.015)) !important;
        border-radius:18px !important;box-shadow:0 16px 38px -16px rgba(0,0,0,0.65) !important;
        border:1px solid rgba(255,255,255,0.09) !important;overflow:hidden !important;padding:10px !important;
    }}

    /* ══ TABLAS ══ */
    div[data-testid="stDataFrame"] {{ border-radius:16px!important;overflow:hidden!important;
        box-shadow:0 16px 38px -16px rgba(0,0,0,0.65)!important;border:1px solid rgba(255,255,255,0.10)!important; }}
    div[data-testid="stDataFrame"] div[role="columnheader"] {{
        background:linear-gradient(135deg,#1b1240 0%,#0EA5E9 100%)!important;
        color:white!important;font-weight:700!important; }}
    div[data-testid="stDataFrame"] div[role="columnheader"] span {{ color:white!important; }}
    div[data-testid="stDataFrame"] .ag-root-wrapper {{ background:rgba(16,13,36,0.90)!important;border:none!important; }}
    div[data-testid="stDataFrame"] .ag-body-viewport,
    div[data-testid="stDataFrame"] .ag-center-cols-viewport {{ background:transparent!important; }}
    div[data-testid="stDataFrame"] .ag-row {{ background:rgba(16,13,36,0.85)!important;border-color:rgba(255,255,255,0.045)!important; }}
    div[data-testid="stDataFrame"] .ag-row-odd {{ background:rgba(22,18,48,0.80)!important; }}
    div[data-testid="stDataFrame"] .ag-row:hover,
    div[data-testid="stDataFrame"] .ag-row-hover {{ background:rgba(14,165,233,0.10)!important; }}
    div[data-testid="stDataFrame"] .ag-cell {{ color:rgba(225,232,250,0.90)!important;border-color:rgba(255,255,255,0.04)!important; }}
    div[data-testid="stDataFrame"] .ag-header {{ background:transparent!important;border-bottom:1px solid rgba(255,255,255,0.10)!important; }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar {{ width:6px;height:6px; }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar-track {{ background:rgba(255,255,255,0.04); }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {{ background:rgba(56,189,248,0.35);border-radius:99px; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# APLICAR FILTROS
# ─────────────────────────────────────────────
mask = (
    (df["Fecha"].dt.date >= fecha_ini) &
    (df["Fecha"].dt.date <= fecha_fin)
)
if mes_sel != "Todos":
    archivo_mes = f"Consolidado_O_{mes_sel.upper()}.xlsx"
    mask &= df["_archivo"] == archivo_mes
if sem_sel != "Todas":
    if "_semana_num" in df.columns:
        mask &= df["_semana_num"].astype(str) == str(sem_sel)
    else:
        mask &= df["Semana"] == sem_sel
if tri_sel != "Todos" and "Trimestre" in df.columns:
    mask &= df["Trimestre"].astype(str) == tri_sel
if semestre_sel != "Todos" and "Semestre" in df.columns:
    mask &= df["Semestre"].astype(str) == semestre_sel
if sup_sel != "Todos":
    mask &= df["Supervisor"] == sup_sel
if coord_sel != "Todos" and "Coordinador" in df.columns:
    mask &= df["Coordinador"] == coord_sel
if exp_sel != "Todos":
    mask &= df["Nombre"] == exp_sel
if camp_sel != "Todas" and _camp_col:
    mask &= df[_camp_col] == camp_sel

dff = df[mask].copy()

if tipo_periodo == "Día":
    dff["_periodo"] = dff["FechaStr"]
elif tipo_periodo == "Semana":
    dff["_periodo"] = dff["Semana"]
else:
    dff["_periodo"] = dff["Mes"]

_periodo_sorted = (
    dff.groupby("_periodo")["Fecha"].min()
    .sort_values().index.tolist()
)
_periodo_rank = {p: i for i, p in enumerate(_periodo_sorted)}
_n_per        = len(_periodo_sorted)
_ini_per      = max(-0.5, _n_per - 15 - 0.5)

n_agentes     = dff["Nombre"].nunique()
n_supervisores = dff["Supervisor"].nunique()

# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
rango    = f"{fecha_ini.strftime('%d/%m/%Y')} – {fecha_fin.strftime('%d/%m/%Y')}"
_home_pg = st.Page("home.py",               title="Inicio",     icon="🏠", default=True)
_adh_pg  = st.Page("pages/1_Adherencia.py", title="Adherencia", icon="🎯")
_nov_pg  = st.Page("pages/3_Novedades.py",  title="Novedades",  icon="📢")

with st.container(key="hdrbanner"):
    st.markdown(f"""
    <div class='hb-eyebrow'><span class='hb-dot'></span>Centro de Control · Uniminuto 2026</div>
    <div class='hb-title'>Módulo de Ocupación</div>
    <div class='hb-meta'>
        <span class='hb-chip'>📅 <b>{rango}</b></span>
        <span class='hb-chip'>👥 <b>{n_agentes}</b> expertos</span>
    </div>
    <div class='nav-lbl'>⚡ Navegación</div>
    """, unsafe_allow_html=True)
    nb1, nb2, nb3, nb4, _nsp = st.columns([1.0, 1.35, 1.3, 1.35, 1.6], vertical_alignment="center")
    with nb1:
        if st.button("🏠 Inicio",     key="hdr_home", use_container_width=True):
            st.switch_page(_home_pg)
    with nb2:
        if st.button("🎯 Adherencia", key="hdr_adh",  use_container_width=True):
            st.switch_page(_adh_pg)
    with nb3:
        st.button("📊 Ocupación", key="hdr_ocu", use_container_width=True, type="primary")
    with nb4:
        if st.button("📢 Novedades",  key="hdr_nov",  use_container_width=True):
            st.switch_page(_nov_pg)

# ─────────────────────────────────────────────
# MÉTRICAS GLOBALES
# ─────────────────────────────────────────────
ocu_avg      = dff["Ocupación Ajuste"].mean() if "Ocupación Ajuste" in dff.columns else 0.0
cont_avg     = dff["% Contacto"].mean()       if "% Contacto"       in dff.columns else 0.0
tot_llamadas = int(dff["Llamadas"].sum())     if "Llamadas"         in dff.columns else 0
tot_abandon  = int(dff["Abandonadas"].sum())  if "Abandonadas"      in dff.columns else 0
pct_abandon  = tot_abandon / tot_llamadas     if tot_llamadas > 0 else 0.0

ocu_color   = COLOR_SUCCESS if ocu_avg    >= 0.85 else (COLOR_WARNING if ocu_avg    >= 0.75 else COLOR_DANGER)
cont_color  = COLOR_SUCCESS if cont_avg   >= 0.80 else (COLOR_WARNING if cont_avg   >= 0.60 else COLOR_DANGER)
aband_color = COLOR_DANGER  if pct_abandon >= 0.08 else (COLOR_WARNING if pct_abandon >= 0.05 else COLOR_SUCCESS)

def kpi_bar(pct, color, max_val=100):
    fill = min(pct / max_val * 100, 100) if max_val > 0 else 0
    return f"<div class='kpi-bar-wrap'><div class='kpi-bar-fill' style='width:{fill:.0f}%;background:{color};'></div></div>"

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class='kpi-card' style='--kc:{ocu_color}'>
        <div class='kpi-bg-icon'>⏱️</div>
        <div>
            <div class='kpi-label'>Ocupación Ajuste</div>
            <div class='kpi-value' style='color:{ocu_color}'>{ocu_avg:.1%}</div>
            <div class='kpi-sub'>Meta referencial: 85%</div>
        </div>
        {kpi_bar(ocu_avg * 100, ocu_color)}
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class='kpi-card' style='--kc:{cont_color}'>
        <div class='kpi-bg-icon'>📞</div>
        <div>
            <div class='kpi-label'>% Contacto</div>
            <div class='kpi-value' style='color:{cont_color}'>{cont_avg:.1%}</div>
            <div class='kpi-sub'>{n_agentes} expertos en período</div>
        </div>
        {kpi_bar(cont_avg * 100, cont_color)}
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_ACCENT}'>
        <div class='kpi-bg-icon'>📲</div>
        <div>
            <div class='kpi-label'>Total Llamadas</div>
            <div class='kpi-value' style='color:#7DD3FC'>{tot_llamadas:,}</div>
            <div class='kpi-sub'>Llamadas ingresadas al sistema</div>
        </div>
        {kpi_bar(100, COLOR_ACCENT)}
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class='kpi-card' style='--kc:{aband_color}'>
        <div class='kpi-bg-icon'>🚫</div>
        <div>
            <div class='kpi-label'>% Abandono</div>
            <div class='kpi-value' style='color:{aband_color}'>{pct_abandon:.1%}</div>
            <div class='kpi-sub'>{tot_abandon:,} llamadas abandonadas</div>
        </div>
        {kpi_bar(pct_abandon * 100, aband_color, 15)}
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECCIÓN 1 · OCUPACIÓN
# ─────────────────────────────────────────────
st.markdown(f"""
<div class='sec-header' style='--sc:#0EA5E9'>
    <div class='sec-wash'></div>
    <div class='sec-icon'>⏱️</div>
    <div class='sec-text'>
        <div class='sec-title'>Ocupación</div>
        <div class='sec-desc'>Evolución del indicador de Ocupación Ajuste por período, desglosado por supervisor y experto.</div>
    </div>
    <div class='sec-meta'>
        <div class='sec-meta-val' style='color:#0EA5E9'>{ocu_avg:.1%}</div>
        <div class='sec-meta-lab'>Promedio</div>
    </div>
    <span class='sec-tag' style='background:#0EA5E9'>Eficiencia</span>
</div>
""", unsafe_allow_html=True)

# Preparar datos de tendencia por supervisor
tend_ocu = (
    dff.groupby(["_periodo", "Supervisor"])["Ocupación Ajuste"]
    .mean().reset_index(name="OcuAjuste")
)
tend_ocu["_ord"] = tend_ocu["_periodo"].map(_periodo_rank)
tend_ocu = tend_ocu.sort_values(["Supervisor","_ord"]).drop(columns="_ord")

sup_lista  = sorted(tend_ocu["Supervisor"].unique())
colores_sup = {s: SUPERVISOR_COLORS[i % len(SUPERVISOR_COLORS)] for i, s in enumerate(sup_lista)}

st.markdown("""<div class='chart-hdr' style='--cc:#0EA5E9'>
    <span class='ch-icon'>⏱️</span>
    <div class='ch-texts'>
        <div class='ch-title'>Ocupación Ajuste por Supervisor en el Tiempo</div>
        <div class='ch-sub'>Promedio por período · cada línea = un supervisor</div>
    </div>
    <span class='ch-tag' style='color:#0EA5E9'>Multi-línea</span>
</div>""", unsafe_allow_html=True)

fig_ocu = go.Figure()
fig_ocu.add_hrect(y0=0,    y1=0.75, fillcolor="rgba(239,68,68,0.03)",   layer="below", line_width=0)
fig_ocu.add_hrect(y0=0.75, y1=0.85, fillcolor="rgba(245,158,11,0.04)",  layer="below", line_width=0)
fig_ocu.add_hrect(y0=0.85, y1=1.10, fillcolor="rgba(16,185,129,0.04)",  layer="below", line_width=0)

for sup in sup_lista:
    sub = tend_ocu[tend_ocu["Supervisor"] == sup]
    nc  = " ".join(sup.split()[:2])
    fig_ocu.add_trace(go.Scatter(
        x=sub["_periodo"], y=sub["OcuAjuste"], name=nc,
        mode="lines+markers",
        line=dict(color=colores_sup[sup], width=2, shape="spline"),
        marker=dict(size=6, color="white", line=dict(color=colores_sup[sup], width=2)),
        hovertemplate=f"<b>{nc}</b><br>%{{x}}: %{{y:.1%}}<extra></extra>"
    ))
fig_ocu.add_hline(y=0.85, line_dash="dot", line_color="rgba(100,116,139,0.6)", line_width=1.5,
                  annotation_text="Meta 85%", annotation_position="top right",
                  annotation_font=dict(color="rgba(255,255,255,0.6)", size=10, family="Inter"))
fig_ocu.update_layout(
    height=390, margin=dict(l=0, r=0, t=10, b=40),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(tickformat=".0%", gridcolor="rgba(255,255,255,0.08)", range=[0, 1.10], dtick=0.10,
               tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"), zeroline=False),
    xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"),
               range=[_ini_per, _n_per - 0.5],
               rangeslider=dict(visible=True, thickness=0.08, bgcolor="rgba(255,255,255,0.05)"),
               tickangle=-30, showgrid=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=10, family="Inter"), itemsizing="constant", bgcolor="rgba(0,0,0,0)"),
    font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)")
)
st.plotly_chart(fig_ocu, use_container_width=True)

# Tabla detalle por agente
n_ocu = dff["Nombre"].nunique()
st.markdown(f"""
<div class='tbl-hdr' style='background:linear-gradient(120deg,#0EA5E9,#3B82F6)'>
    <div class='tbl-hdr-icon'>📋</div>
    <div class='tbl-hdr-body'>
        <div class='tbl-hdr-title'>Detalle por Experto · Ocupación</div>
        <div class='tbl-hdr-desc'>Ocupación Ajuste promedio, Ajuste acumulado y Tiempo en Llamadas</div>
    </div>
    <div class='tbl-hdr-badge'>{n_ocu} expertos</div>
</div>
""", unsafe_allow_html=True)

_agg_ocu = {"OcuAjuste": ("Ocupación Ajuste", "mean")}
if "Ajuste_s"               in dff.columns: _agg_ocu["Ajuste_s"]  = ("Ajuste_s", "sum")
if "Tiempo Dur. Llamadas_s" in dff.columns: _agg_ocu["Llamadas_s"] = ("Tiempo Dur. Llamadas_s", "sum")

tbl_ocu = (
    dff.groupby(["Nombre","Supervisor"])
    .agg(**_agg_ocu)
    .reset_index()
    .sort_values("OcuAjuste", ascending=False)
)
tbl_ocu_disp = {
    "Experto":           tbl_ocu["Nombre"],
    "Supervisor":        tbl_ocu["Supervisor"],
    "Ocupación Ajuste":  tbl_ocu["OcuAjuste"].map(lambda x: f"{x:.1%}"),
}
if "Ajuste_s"  in tbl_ocu.columns: tbl_ocu_disp["Ajuste"]          = tbl_ocu["Ajuste_s"].map(seg_a_hhmmss)
if "Llamadas_s" in tbl_ocu.columns: tbl_ocu_disp["Tiempo Llamadas"] = tbl_ocu["Llamadas_s"].map(seg_a_hhmmss)
st.dataframe(pd.DataFrame(tbl_ocu_disp), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# SECCIÓN 2 · CONTACTO
# ─────────────────────────────────────────────
st.markdown(f"""
<div class='sec-header' style='--sc:#10B981'>
    <div class='sec-wash'></div>
    <div class='sec-icon'>📞</div>
    <div class='sec-text'>
        <div class='sec-title'>Contacto</div>
        <div class='sec-desc'>Porcentaje de contacto efectivo por período. Incluye tiempo disponible y duración de llamadas por experto.</div>
    </div>
    <div class='sec-meta'>
        <div class='sec-meta-val' style='color:#10B981'>{cont_avg:.1%}</div>
        <div class='sec-meta-lab'>Promedio</div>
    </div>
    <span class='sec-tag' style='background:#10B981'>Contacto</span>
</div>
""", unsafe_allow_html=True)

tend_cont = (
    dff.groupby(["_periodo","Supervisor"])["% Contacto"]
    .mean().reset_index(name="PctContacto")
)
tend_cont["_ord"] = tend_cont["_periodo"].map(_periodo_rank)
tend_cont = tend_cont.sort_values(["Supervisor","_ord"]).drop(columns="_ord")

st.markdown("""<div class='chart-hdr' style='--cc:#10B981'>
    <span class='ch-icon'>📞</span>
    <div class='ch-texts'>
        <div class='ch-title'>% Contacto por Supervisor en el Tiempo</div>
        <div class='ch-sub'>Proporción de contacto efectivo · por equipo y período</div>
    </div>
    <span class='ch-tag' style='color:#10B981'>Tendencia</span>
</div>""", unsafe_allow_html=True)

fig_cont = go.Figure()
for sup in sup_lista:
    sub = tend_cont[tend_cont["Supervisor"] == sup]
    if sub.empty:
        continue
    nc = " ".join(sup.split()[:2])
    fig_cont.add_trace(go.Scatter(
        x=sub["_periodo"], y=sub["PctContacto"], name=nc,
        mode="lines+markers",
        line=dict(color=colores_sup.get(sup, "#34D399"), width=2, shape="spline"),
        marker=dict(size=6, color="white", line=dict(color=colores_sup.get(sup, "#34D399"), width=2)),
        hovertemplate=f"<b>{nc}</b><br>%{{x}}: %{{y:.1%}}<extra></extra>"
    ))
fig_cont.update_layout(
    height=390, margin=dict(l=0, r=0, t=10, b=40),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(tickformat=".0%", gridcolor="rgba(255,255,255,0.08)", range=[0, 1.05], dtick=0.10,
               tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"), zeroline=False),
    xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"),
               range=[_ini_per, _n_per - 0.5],
               rangeslider=dict(visible=True, thickness=0.08, bgcolor="rgba(255,255,255,0.05)"),
               tickangle=-30, showgrid=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=10, family="Inter"), itemsizing="constant", bgcolor="rgba(0,0,0,0)"),
    font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)")
)
st.plotly_chart(fig_cont, use_container_width=True)

n_cont = dff["Nombre"].nunique()
st.markdown(f"""
<div class='tbl-hdr' style='background:linear-gradient(120deg,#10B981,#059669)'>
    <div class='tbl-hdr-icon'>📋</div>
    <div class='tbl-hdr-body'>
        <div class='tbl-hdr-title'>Detalle por Experto · Contacto</div>
        <div class='tbl-hdr-desc'>% Contacto promedio, Tiempo Disponible y Duración de Llamadas</div>
    </div>
    <div class='tbl-hdr-badge'>{n_cont} expertos</div>
</div>
""", unsafe_allow_html=True)

_agg_cont = {"PctContacto": ("% Contacto", "mean")}
if "Disponible_s"           in dff.columns: _agg_cont["Disponible_s"] = ("Disponible_s", "sum")
if "Tiempo Dur. Llamadas_s" in dff.columns: _agg_cont["Llamadas_s"]   = ("Tiempo Dur. Llamadas_s", "sum")

tbl_cont = (
    dff.groupby(["Nombre","Supervisor"])
    .agg(**_agg_cont)
    .reset_index()
    .sort_values("PctContacto", ascending=False)
)
tbl_cont_disp = {
    "Experto":    tbl_cont["Nombre"],
    "Supervisor": tbl_cont["Supervisor"],
    "% Contacto": tbl_cont["PctContacto"].map(lambda x: f"{x:.1%}"),
}
if "Disponible_s" in tbl_cont.columns: tbl_cont_disp["Disponible"]       = tbl_cont["Disponible_s"].map(seg_a_hhmmss)
if "Llamadas_s"   in tbl_cont.columns: tbl_cont_disp["Tiempo Llamadas"]  = tbl_cont["Llamadas_s"].map(seg_a_hhmmss)
st.dataframe(pd.DataFrame(tbl_cont_disp), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# SECCIÓN 3 · LLAMADAS
# ─────────────────────────────────────────────
tot_atend  = int(dff["Atendidas"].sum())  if "Atendidas"  in dff.columns else 0
tot_cancel = int(dff["Canceladas"].sum()) if "Canceladas" in dff.columns else 0

st.markdown(f"""
<div class='sec-header' style='--sc:#8B5CF6'>
    <div class='sec-wash'></div>
    <div class='sec-icon'>📲</div>
    <div class='sec-text'>
        <div class='sec-title'>Llamadas</div>
        <div class='sec-desc'>Volumen de llamadas ingresadas, atendidas, abandonadas y canceladas por período.</div>
    </div>
    <div class='sec-meta'>
        <div class='sec-meta-val' style='color:#8B5CF6'>{tot_llamadas:,}</div>
        <div class='sec-meta-lab'>Ingresadas</div>
    </div>
    <span class='sec-tag' style='background:#8B5CF6'>Volumen</span>
</div>
""", unsafe_allow_html=True)

call_cols = [c for c in ["Llamadas","Atendidas","Abandonadas","Canceladas"] if c in dff.columns]
call_per  = (
    dff.groupby("_periodo")[call_cols].sum().reset_index()
)
call_per["_ord"] = call_per["_periodo"].map(_periodo_rank)
call_per = call_per.sort_values("_ord").drop(columns="_ord")

st.markdown("""<div class='chart-hdr' style='--cc:#8B5CF6'>
    <span class='ch-icon'>📲</span>
    <div class='ch-texts'>
        <div class='ch-title'>Volumen de Llamadas por Período</div>
        <div class='ch-sub'>Ingresadas · Atendidas · Abandonadas · Canceladas</div>
    </div>
    <span class='ch-tag' style='color:#8B5CF6'>Barras agrupadas</span>
</div>""", unsafe_allow_html=True)

_CALL_CFG = [
    ("Llamadas",    "#60A5FA", "Ingresadas"),
    ("Atendidas",   "#34D399", "Atendidas"),
    ("Abandonadas", "#F87171", "Abandonadas"),
    ("Canceladas",  "#FBBF24", "Canceladas"),
]
fig_call = go.Figure()
for col, color, label in _CALL_CFG:
    if col in call_per.columns:
        fig_call.add_trace(go.Bar(
            name=label, x=call_per["_periodo"], y=call_per[col],
            marker_color=color, opacity=0.88,
            hovertemplate=f"<b>{label}</b><br>%{{x}}: %{{y:,}}<extra></extra>"
        ))
fig_call.update_layout(
    barmode="group", height=390, margin=dict(l=0, r=0, t=10, b=40),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="rgba(255,255,255,0.08)",
               tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"), zeroline=False),
    xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"),
               tickangle=-30, showgrid=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=10, family="Inter"), itemsizing="constant", bgcolor="rgba(0,0,0,0)"),
    font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)"),
    bargap=0.20, bargroupgap=0.08
)
st.plotly_chart(fig_call, use_container_width=True)

n_call = dff["Nombre"].nunique()
st.markdown(f"""
<div class='tbl-hdr' style='background:linear-gradient(120deg,#8B5CF6,#6D28D9)'>
    <div class='tbl-hdr-icon'>📋</div>
    <div class='tbl-hdr-body'>
        <div class='tbl-hdr-title'>Detalle por Experto · Llamadas</div>
        <div class='tbl-hdr-desc'>Ingresadas, Atendidas, Abandonadas, Canceladas y % Abandono por agente</div>
    </div>
    <div class='tbl-hdr-badge'>{n_call} expertos</div>
</div>
""", unsafe_allow_html=True)

_agg_call = {}
for col in ["Llamadas","Atendidas","Abandonadas","Canceladas"]:
    if col in dff.columns:
        _agg_call[col] = (col, "sum")

tbl_call = (
    dff.groupby(["Nombre","Supervisor"])
    .agg(**_agg_call)
    .reset_index()
    .sort_values("Llamadas" if "Llamadas" in _agg_call else list(_agg_call.keys())[0], ascending=False)
)
tbl_call_disp = {"Experto": tbl_call["Nombre"], "Supervisor": tbl_call["Supervisor"]}
for col in ["Llamadas","Atendidas","Abandonadas","Canceladas"]:
    if col in tbl_call.columns:
        tbl_call_disp[col] = tbl_call[col].astype(int)
if "Abandonadas" in tbl_call.columns and "Llamadas" in tbl_call.columns:
    tbl_call_disp["% Abandono"] = (
        tbl_call["Abandonadas"] / tbl_call["Llamadas"].replace(0, float("nan"))
    ).map(lambda x: f"{x:.1%}" if pd.notna(x) else "—")

st.dataframe(pd.DataFrame(tbl_call_disp), use_container_width=True, hide_index=True)
