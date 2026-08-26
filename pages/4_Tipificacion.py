import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import glob
import os
import base64
import io

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
SUPERVISOR_COLORS = px.colors.qualitative.Bold
NIVEL1_COLORS     = px.colors.qualitative.Set2

@st.cache_data(show_spinner=False)
def _excel_bytes(df):
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    return buf.getvalue()

def df_descarga(df, nombre_archivo, **kwargs):
    st.dataframe(df, **kwargs)
    b64 = base64.b64encode(_excel_bytes(df)).decode()
    st.markdown(
        f'<div style="text-align:right;margin-top:-6px;margin-bottom:8px">'
        f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" '
        f'download="{nombre_archivo}" '
        f'style="font-size:0.72rem;color:rgba(255,255,255,0.35);text-decoration:none;letter-spacing:0.03em" '
        f'onmouseover="this.style.color=\'rgba(255,255,255,0.75)\'" '
        f'onmouseout="this.style.color=\'rgba(255,255,255,0.35)\'">'
        f'↓ Exportar Excel</a></div>',
        unsafe_allow_html=True,
    )
ORDEN_MESES = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO",
               "JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]
COLOR_PRIMARY = "#28053F"
COLOR_ACCENT  = "#0EA5E9"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER  = "#EF4444"
COLOR_TIPI    = "#EC4899"   # rosa/magenta — color distintivo del módulo de Tipificación

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
    archivos = sorted(glob.glob("Consolidado_T_*.xlsx"), key=_mes_orden)
    if not archivos:
        st.error("No se encontraron archivos Consolidado_T_*.xlsx en la carpeta.")
        st.stop()

    partes = []
    for archivo in archivos:
        df_mes = pd.read_excel(archivo, sheet_name="Consolidado", engine="openpyxl")
        df_mes["_archivo"] = os.path.basename(archivo)
        partes.append(df_mes)

    df = pd.concat(partes, ignore_index=True)
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")

    # Tiempo Conc. / Tiempo Dur. son SUMAS por fila (cada fila agrupa todas las
    # llamadas de un agente en un día con el mismo resultado — ver "Llamadas").
    for col in ["Tiempo Conc.", "Tiempo Dur."]:
        if col in df.columns:
            df[col + "_s"] = pd.to_timedelta(df[col], errors="coerce").dt.total_seconds()

    if "Llamadas" not in df.columns:
        df["Llamadas"] = 1  # compatibilidad con un consolidado viejo sin agregar

    # Solo las llamadas atendidas (Aten.="Si") pueden llegar a tener tipificación;
    # el resto (Aten.="No", incluye Abandonadas y Canceladas) nunca la tiene.
    df["Medible"]    = df["Aten."] == "Si"
    df["Tipificada"] = df["Disp."].notna() & (df["Disp."].astype(str).str.strip() != "")

    if "Semana" in df.columns:
        df["_semana_num"] = df["Semana"]
    # Lunes de la semana de cada fecha, vectorizado (nada de .apply fila por
    # fila): con ~600.000 registros de llamadas, un lambda por fila se nota.
    _lunes = df["Fecha"] - pd.to_timedelta(df["Fecha"].dt.dayofweek, unit="D")
    df["Semana"]   = "Sem " + _lunes.dt.strftime("%d/%m")
    df["Mes"]      = df["Fecha"].dt.to_period("M").astype(str)
    df["FechaStr"] = df["Fecha"].dt.strftime("%d/%m")

    return df, archivos

_firma_archivos = tuple(
    (os.path.basename(a), os.path.getmtime(a))
    for a in sorted(glob.glob("Consolidado_T_*.xlsx"), key=_mes_orden)
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
        os.path.basename(a).replace("Consolidado_T_", "").replace(".xlsx", "").capitalize()
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

    campanas = ["Todas"] + sorted(df["Campaña"].dropna().unique().tolist())
    camp_sel = st.selectbox("Campaña", campanas)

    if "Nivel 1" in df.columns:
        niveles1_disp = ["Todos"] + sorted(df["Nivel 1"].dropna().unique().tolist())
        nivel1_sel = st.selectbox("Categoría (Nivel 1)", niveles1_disp)
    else:
        nivel1_sel = "Todos"

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
        border:1px solid rgba(236,72,153,0.55) !important;border-top-color:rgba(249,168,212,0.62) !important;
        background:linear-gradient(180deg,rgba(236,72,153,0.30),rgba(219,39,119,0.16)) !important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.22),inset 0 -8px 14px -12px rgba(8,3,24,0.42),0 8px 22px -10px rgba(236,72,153,0.50) !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"]::before {{
        content:"";position:absolute;left:8px;top:50%;transform:translateY(-50%);
        width:5px;height:5px;border-radius:50%;background:#F9A8D4;box-shadow:0 0 8px rgba(249,168,212,0.9); }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"]:hover {{
        transform:translateY(-1px) !important;
        background:linear-gradient(180deg,rgba(236,72,153,0.36),rgba(219,39,119,0.20)) !important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.24),0 10px 26px -10px rgba(236,72,153,0.58) !important; }}

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
        background:linear-gradient(135deg,#1b1240 0%,#EC4899 100%)!important;
        color:white!important;font-weight:700!important; }}
    div[data-testid="stDataFrame"] div[role="columnheader"] span {{ color:white!important; }}
    div[data-testid="stDataFrame"] .ag-root-wrapper {{ background:rgba(16,13,36,0.90)!important;border:none!important; }}
    div[data-testid="stDataFrame"] .ag-body-viewport,
    div[data-testid="stDataFrame"] .ag-center-cols-viewport {{ background:transparent!important; }}
    div[data-testid="stDataFrame"] .ag-row {{ background:rgba(16,13,36,0.85)!important;border-color:rgba(255,255,255,0.045)!important; }}
    div[data-testid="stDataFrame"] .ag-row-odd {{ background:rgba(22,18,48,0.80)!important; }}
    div[data-testid="stDataFrame"] .ag-row:hover,
    div[data-testid="stDataFrame"] .ag-row-hover {{ background:rgba(236,72,153,0.10)!important; }}
    div[data-testid="stDataFrame"] .ag-cell {{ color:rgba(225,232,250,0.90)!important;border-color:rgba(255,255,255,0.04)!important; }}
    div[data-testid="stDataFrame"] .ag-header {{ background:transparent!important;border-bottom:1px solid rgba(255,255,255,0.10)!important; }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar {{ width:6px;height:6px; }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar-track {{ background:rgba(255,255,255,0.04); }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {{ background:rgba(236,72,153,0.35);border-radius:99px; }}
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
    archivo_mes = f"Consolidado_T_{mes_sel.upper()}.xlsx"
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
if camp_sel != "Todas":
    mask &= df["Campaña"] == camp_sel
if nivel1_sel != "Todos" and "Nivel 1" in df.columns:
    mask &= df["Nivel 1"] == nivel1_sel

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

n_agentes      = dff["Nombre"].nunique()
n_supervisores = dff["Supervisor"].nunique()

# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
rango    = f"{fecha_ini.strftime('%d/%m/%Y')} – {fecha_fin.strftime('%d/%m/%Y')}"
_home_pg = st.Page("home.py",               title="Inicio",      icon="🏠", default=True)
_adh_pg  = st.Page("pages/1_Adherencia.py", title="Adherencia",  icon="🎯")
_ocu_pg  = st.Page("pages/2_Ocupacion.py",  title="Ocupación",   icon="📊")
_nov_pg  = st.Page("pages/3_Novedades.py",  title="Novedades",   icon="📢")

with st.container(key="hdrbanner"):
    st.markdown(f"""
    <div class='hb-eyebrow'><span class='hb-dot'></span>Centro de Control · Uniminuto 2026</div>
    <div class='hb-title'>Módulo de Tipificación</div>
    <div class='hb-meta'>
        <span class='hb-chip'>📅 <b>{rango}</b></span>
        <span class='hb-chip'>👥 <b>{n_agentes}</b> expertos</span>
    </div>
    <div class='nav-lbl'>⚡ Navegación</div>
    """, unsafe_allow_html=True)
    nb1, nb2, nb3, nb4, nb5 = st.columns([1.0, 1.35, 1.3, 1.45, 1.35], vertical_alignment="center")
    with nb1:
        if st.button("🏠 Inicio",       key="hdr_home", use_container_width=True):
            st.switch_page(_home_pg)
    with nb2:
        if st.button("🎯 Adherencia",   key="hdr_adh",  use_container_width=True):
            st.switch_page(_adh_pg)
    with nb3:
        if st.button("📊 Ocupación",    key="hdr_ocu",  use_container_width=True):
            st.switch_page(_ocu_pg)
    with nb4:
        st.button("🏷️ Tipificación", key="hdr_tip", use_container_width=True, type="primary")
    with nb5:
        if st.button("📢 Novedades",    key="hdr_nov",  use_container_width=True):
            st.switch_page(_nov_pg)

# ─────────────────────────────────────────────
# MÉTRICAS GLOBALES
# ─────────────────────────────────────────────
# Cada fila representa varias llamadas iguales (mismo agente/día/resultado)
# agrupadas — "Llamadas" trae cuántas. Por eso todo se pondera por Llamadas
# en vez de contar filas o promediar filas directamente.
medibles      = dff[dff["Medible"]]
n_medibles    = int(medibles["Llamadas"].sum())
n_tipificadas = int(medibles.loc[medibles["Tipificada"], "Llamadas"].sum()) if n_medibles > 0 else 0
pct_tipif     = (n_tipificadas / n_medibles) if n_medibles > 0 else 0.0

tiempo_conc_prom = (
    medibles["Tiempo Conc._s"].sum() / n_medibles
    if "Tiempo Conc._s" in medibles.columns and n_medibles > 0 else 0.0
)

if n_tipificadas > 0:
    _top_motivo_row = (
        medibles.loc[medibles["Tipificada"]].groupby("Disp.")["Llamadas"].sum()
        .sort_values(ascending=False)
    )
    _top_motivo      = _top_motivo_row.index[0]
    _top_motivo_pct  = _top_motivo_row.iloc[0] / n_tipificadas
else:
    _top_motivo, _top_motivo_pct = "—", 0.0

tipif_color = COLOR_SUCCESS if pct_tipif >= 0.90 else (COLOR_WARNING if pct_tipif >= 0.75 else COLOR_DANGER)

def kpi_bar(pct, color, max_val=100):
    fill = min(pct / max_val * 100, 100) if max_val > 0 else 0
    return f"<div class='kpi-bar-wrap'><div class='kpi-bar-fill' style='width:{fill:.0f}%;background:{color};'></div></div>"

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class='kpi-card' style='--kc:{tipif_color}'>
        <div class='kpi-bg-icon'>🏷️</div>
        <div>
            <div class='kpi-label'>% Tipificación</div>
            <div class='kpi-value' style='color:{tipif_color}'>{pct_tipif:.1%}</div>
            <div class='kpi-sub'>{n_medibles:,} llamadas medibles (Aten.=Sí)</div>
        </div>
        {kpi_bar(pct_tipif * 100, tipif_color)}
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_ACCENT}'>
        <div class='kpi-bg-icon'>📞</div>
        <div>
            <div class='kpi-label'>Llamadas Atendidas</div>
            <div class='kpi-value' style='color:#7DD3FC'>{n_medibles:,}</div>
            <div class='kpi-sub'>Únicas que pueden tipificarse</div>
        </div>
        {kpi_bar(100, COLOR_ACCENT)}
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_TIPI}'>
        <div class='kpi-bg-icon'>⏱️</div>
        <div>
            <div class='kpi-label'>Tiempo Promedio</div>
            <div class='kpi-value' style='color:{COLOR_TIPI}'>{seg_a_hhmmss(tiempo_conc_prom)}</div>
            <div class='kpi-sub'>Por llamada medible</div>
        </div>
        {kpi_bar(100, COLOR_TIPI)}
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class='kpi-card' style='--kc:#8B5CF6'>
        <div class='kpi-bg-icon'>🏆</div>
        <div>
            <div class='kpi-label'>Motivo Más Frecuente</div>
            <div class='kpi-value' style='color:#C4B5FD;font-size:20px'>{_top_motivo}</div>
            <div class='kpi-sub'>{_top_motivo_pct:.1%} de las tipificadas</div>
        </div>
        {kpi_bar(100, "#8B5CF6")}
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECCIÓN 1 · % TIPIFICACIÓN EN EL TIEMPO
# ─────────────────────────────────────────────
st.markdown(f"""
<div class='sec-header' style='--sc:{COLOR_TIPI}'>
    <div class='sec-wash'></div>
    <div class='sec-icon'>🏷️</div>
    <div class='sec-text'>
        <div class='sec-title'>Tipificación</div>
        <div class='sec-desc'>Evolución del % de tipificación por período, desglosado por supervisor.</div>
    </div>
    <div class='sec-meta'>
        <div class='sec-meta-val' style='color:{COLOR_TIPI}'>{pct_tipif:.1%}</div>
        <div class='sec-meta-lab'>Promedio</div>
    </div>
    <span class='sec-tag' style='background:{COLOR_TIPI}'>Calidad de dato</span>
</div>
""", unsafe_allow_html=True)

_tend_base = medibles.groupby(["_periodo", "Supervisor"])["Llamadas"].sum()
_tend_tip  = (
    medibles[medibles["Tipificada"]].groupby(["_periodo", "Supervisor"])["Llamadas"].sum()
)
tend_tipif = (
    (_tend_tip.reindex(_tend_base.index, fill_value=0) / _tend_base)
    .reset_index(name="PctTipif")
)
tend_tipif["_ord"] = tend_tipif["_periodo"].map(_periodo_rank)
tend_tipif = tend_tipif.sort_values(["Supervisor","_ord"]).drop(columns="_ord")

sup_lista   = sorted(tend_tipif["Supervisor"].unique())
colores_sup = {s: SUPERVISOR_COLORS[i % len(SUPERVISOR_COLORS)] for i, s in enumerate(sup_lista)}

st.markdown("""<div class='chart-hdr' style='--cc:#EC4899'>
    <span class='ch-icon'>🏷️</span>
    <div class='ch-texts'>
        <div class='ch-title'>% Tipificación por Supervisor en el Tiempo</div>
        <div class='ch-sub'>Promedio por período · cada línea = un supervisor</div>
    </div>
    <span class='ch-tag' style='color:#EC4899'>Multi-línea</span>
</div>""", unsafe_allow_html=True)

fig_tip = go.Figure()
fig_tip.add_hrect(y0=0.00, y1=0.75, fillcolor="rgba(239,68,68,0.03)",  layer="below", line_width=0)
fig_tip.add_hrect(y0=0.75, y1=0.90, fillcolor="rgba(245,158,11,0.04)", layer="below", line_width=0)
fig_tip.add_hrect(y0=0.90, y1=1.00, fillcolor="rgba(16,185,129,0.04)", layer="below", line_width=0)

for sup in sup_lista:
    sub = tend_tipif[tend_tipif["Supervisor"] == sup]
    nc  = " ".join(sup.split()[:2])
    fig_tip.add_trace(go.Scatter(
        x=sub["_periodo"], y=sub["PctTipif"], name=nc,
        mode="lines+markers",
        line=dict(color=colores_sup[sup], width=2, shape="spline"),
        marker=dict(size=6, color="white", line=dict(color=colores_sup[sup], width=2)),
        hovertemplate=f"<b>{nc}</b><br>%{{x}}: %{{y:.1%}}<extra></extra>"
    ))
fig_tip.update_layout(
    height=390, margin=dict(l=0, r=0, t=10, b=40),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(tickformat=".0%", gridcolor="rgba(255,255,255,0.08)", range=[0.0, 1.00], dtick=0.1,
               tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"), zeroline=False),
    xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"),
               range=[_ini_per, _n_per - 0.5],
               rangeslider=dict(visible=True, thickness=0.08, bgcolor="rgba(255,255,255,0.05)"),
               tickangle=-30, showgrid=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=10, family="Inter"), itemsizing="constant", bgcolor="rgba(0,0,0,0)"),
    font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)")
)
st.plotly_chart(fig_tip, use_container_width=True)

# ── Volumen: medibles vs tipificadas por período ──────────────────────────
st.markdown("""<div class='chart-hdr' style='--cc:#EC4899;margin-top:18px'>
    <span class='ch-icon'>📊</span>
    <div class='ch-texts'>
        <div class='ch-title'>Volumen: Medibles vs Tipificadas</div>
        <div class='ch-sub'>Cantidad de llamadas por período · la brecha entre barras es lo que falta por tipificar</div>
    </div>
    <span class='ch-tag' style='color:#EC4899'>Barras agrupadas</span>
</div>""", unsafe_allow_html=True)

_vol_medibles = medibles.groupby("_periodo")["Llamadas"].sum()
_vol_tipif    = medibles[medibles["Tipificada"]].groupby("_periodo")["Llamadas"].sum()
vol_per = pd.DataFrame({
    "Medibles":    _vol_medibles,
    "Tipificadas": _vol_tipif.reindex(_vol_medibles.index, fill_value=0),
}).reset_index()
vol_per["_ord"] = vol_per["_periodo"].map(_periodo_rank)
vol_per = vol_per.sort_values("_ord").drop(columns="_ord")

fig_vol = go.Figure()
fig_vol.add_trace(go.Bar(
    name="Medibles", x=vol_per["_periodo"], y=vol_per["Medibles"],
    marker_color="rgba(56,189,248,0.55)", opacity=0.9,
    hovertemplate="<b>Medibles</b><br>%{x}: %{y:,}<extra></extra>"
))
fig_vol.add_trace(go.Bar(
    name="Tipificadas", x=vol_per["_periodo"], y=vol_per["Tipificadas"],
    marker_color=COLOR_TIPI, opacity=0.95,
    hovertemplate="<b>Tipificadas</b><br>%{x}: %{y:,}<extra></extra>"
))
fig_vol.update_layout(
    barmode="group", height=340, margin=dict(l=0, r=0, t=10, b=40),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="rgba(255,255,255,0.08)",
               tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"), zeroline=False),
    xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"),
               rangeslider=dict(visible=True, thickness=0.08, bgcolor="rgba(255,255,255,0.05)"),
               tickangle=-30, showgrid=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=10, family="Inter"), itemsizing="constant", bgcolor="rgba(0,0,0,0)"),
    font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)"),
    bargap=0.20, bargroupgap=0.08
)
st.plotly_chart(fig_vol, use_container_width=True)

# ─────────────────────────────────────────────
# SECCIÓN 2 · DISTRIBUCIÓN Y JERARQUÍA
# ─────────────────────────────────────────────
tipificadas_df = medibles[medibles["Tipificada"]]

st.markdown(f"""
<div class='sec-header' style='--sc:{COLOR_PRIMARY}; background:radial-gradient(ellipse 95% 60% at 6% 0%, rgba(236,72,153,0.28) 0%, transparent 55%), radial-gradient(ellipse 90% 70% at 100% 120%, rgba(129,140,248,0.30) 0%, transparent 55%), radial-gradient(ellipse 80% 70% at 55% 130%, rgba(52,211,153,0.14) 0%, transparent 55%), linear-gradient(150deg, #0B0518 0%, #1a0b34 50%, #0A0414 100%)'>
    <div class='sec-wash'></div>
    <div class='sec-icon' style='background:linear-gradient(135deg,rgba(40,5,63,0.20),rgba(40,5,63,0.06))'>🌳</div>
    <div class='sec-text'>
        <div class='sec-title'>Distribución y Jerarquía</div>
        <div class='sec-desc'>Composición de las llamadas tipificadas por categoría (Nivel 1) y su desglose jerárquico completo.</div>
    </div>
    <div class='sec-meta'>
        <div class='sec-meta-val' style='color:{COLOR_TIPI}'>{n_tipificadas:,}</div>
        <div class='sec-meta-lab'>Tipificadas</div>
    </div>
    <span class='sec-tag' style='background:{COLOR_TIPI}'>Categorías</span>
</div>
""", unsafe_allow_html=True)

c_pie, c_tree = st.columns([1, 2])

with c_pie:
    st.markdown("""<div class='chart-hdr' style='--cc:#EC4899'>
        <span class='ch-icon'>🥧</span>
        <div class='ch-texts'>
            <div class='ch-title'>Nivel 1</div>
            <div class='ch-sub'>Categoría raíz de la tipificación</div>
        </div>
        <span class='ch-tag' style='color:#EC4899'>Dona</span>
    </div>""", unsafe_allow_html=True)

    if "Nivel 1" in tipificadas_df.columns and len(tipificadas_df) > 0:
        n1_counts = tipificadas_df.groupby("Nivel 1")["Llamadas"].sum().sort_values(ascending=False)
        fig_n1 = go.Figure(go.Pie(
            labels=n1_counts.index, values=n1_counts.values, hole=0.55,
            marker=dict(colors=NIVEL1_COLORS, line=dict(color="rgba(0,0,0,0.35)", width=2)),
            textinfo="percent", textfont=dict(size=11, family="Inter", color="white"),
            hovertemplate="<b>%{label}</b><br>%{value:,} llamadas<br>%{percent}<extra></extra>",
        ))
        fig_n1.update_layout(
            height=360, margin=dict(l=0, r=0, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="top", y=-0.05, font=dict(size=10, family="Inter", color="rgba(255,255,255,0.75)"), bgcolor="rgba(0,0,0,0)"),
            font=dict(family="Inter", color="rgba(255,255,255,0.72)")
        )
        st.plotly_chart(fig_n1, use_container_width=True)
    else:
        st.info("Sin datos de Nivel 1 para el filtro actual.")

with c_tree:
    st.markdown("""<div class='chart-hdr' style='--cc:#EC4899'>
        <span class='ch-icon'>🌳</span>
        <div class='ch-texts'>
            <div class='ch-title'>Jerarquía Completa (Nivel 1 → 2 → 3)</div>
            <div class='ch-sub'>Tamaño del bloque = cantidad de llamadas · click para explorar</div>
        </div>
        <span class='ch-tag' style='color:#EC4899'>Treemap</span>
    </div>""", unsafe_allow_html=True)

    _cols_tree = [c for c in ["Nivel 1", "Nivel 2", "Nivel 3"] if c in tipificadas_df.columns]
    if _cols_tree and len(tipificadas_df) > 0:
        # Agregar por combinación de niveles ANTES de pasarlo a px.treemap: con
        # cientos de miles de llamadas individuales, construir el árbol fila por
        # fila (en vez de a partir de las pocas combinaciones únicas ya contadas)
        # es el cuello de botella — tanto para Plotly como para el navegador.
        tree_df = (
            tipificadas_df[_cols_tree + ["Llamadas"]].fillna({c: "(Sin detalle)" for c in _cols_tree})
            .groupby(_cols_tree)["Llamadas"].sum().reset_index(name="_conteo")
        )
        fig_tree = px.treemap(
            tree_df, path=_cols_tree, values="_conteo",
            color_discrete_sequence=NIVEL1_COLORS,
        )
        fig_tree.update_traces(
            textfont=dict(family="Inter", size=12, color="white"),
            hovertemplate="<b>%{label}</b><br>%{value:,} llamadas<extra></extra>",
            marker=dict(line=dict(color="rgba(10,8,19,0.85)", width=2)),
        )
        fig_tree.update_layout(
            height=360, margin=dict(l=0, r=0, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="rgba(255,255,255,0.85)")
        )
        st.plotly_chart(fig_tree, use_container_width=True)
    else:
        st.info("Sin datos jerárquicos para el filtro actual.")

# ─────────────────────────────────────────────
# COMPARATIVO POR SUPERVISOR
# ─────────────────────────────────────────────
st.markdown(f"""
<div class='sec-header' style='--sc:{COLOR_PRIMARY}; background:radial-gradient(ellipse 95% 60% at 6% 0%, rgba(236,72,153,0.28) 0%, transparent 55%), radial-gradient(ellipse 90% 70% at 100% 120%, rgba(129,140,248,0.30) 0%, transparent 55%), radial-gradient(ellipse 80% 70% at 55% 130%, rgba(52,211,153,0.14) 0%, transparent 55%), linear-gradient(150deg, #0B0518 0%, #1a0b34 50%, #0A0414 100%)'>
    <div class='sec-wash'></div>
    <div class='sec-icon' style='background:linear-gradient(135deg,rgba(40,5,63,0.20),rgba(40,5,63,0.06))'>👥</div>
    <div class='sec-text'>
        <div class='sec-title'>Comparativo por Supervisor</div>
        <div class='sec-desc'>% de tipificación consolidado por equipo: verde ≥ 90%, amarillo ≥ 75%, rojo &lt; 75%.</div>
    </div>
    <div class='sec-meta'>
        <div class='sec-meta-val' style='color:{COLOR_TIPI}'>{n_supervisores}</div>
        <div class='sec-meta-lab'>Supervisores</div>
    </div>
    <span class='sec-tag'>Equipos</span>
</div>
""", unsafe_allow_html=True)

sup_tip = (
    medibles.groupby("Supervisor")
    .apply(lambda g: pd.Series({
        "Agentes":      g["Nombre"].nunique(),
        "Medibles":     int(g["Llamadas"].sum()),
        "Tipificadas":  int(g.loc[g["Tipificada"], "Llamadas"].sum()),
        "PctTipif":     g.loc[g["Tipificada"], "Llamadas"].sum() / g["Llamadas"].sum() if g["Llamadas"].sum() > 0 else 0.0,
        "TConc_s":      g["Tiempo Conc._s"].sum() / g["Llamadas"].sum() if g["Llamadas"].sum() > 0 else 0.0,
    }))
    .reset_index()
    .sort_values("PctTipif", ascending=True)
)
sup_tip["Color"] = sup_tip["PctTipif"].apply(
    lambda x: COLOR_SUCCESS if x >= 0.90 else (COLOR_WARNING if x >= 0.75 else COLOR_DANGER)
)

c_bar_tip, c_rank_tip = st.columns([3, 2])

with c_bar_tip:
    st.markdown(f"""<div class='chart-hdr' style='--cc:{COLOR_TIPI}'>
        <span class='ch-icon'>📊</span>
        <div class='ch-texts'>
            <div class='ch-title'>% Tipificación por Supervisor</div>
            <div class='ch-sub'>Menor a mayor · Zona verde = ≥ 90%</div>
        </div>
        <span class='ch-tag' style='color:{COLOR_TIPI}'>Barras</span>
    </div>""", unsafe_allow_html=True)

    sup_tip_short = sup_tip.copy()
    sup_tip_short["Supervisor"] = sup_tip_short["Supervisor"].apply(lambda n: " ".join(n.split()[:2]))
    n_sup_tip = len(sup_tip)

    fig_bar_tip = go.Figure()
    fig_bar_tip.add_vrect(x0=0.90, x1=1.02, fillcolor="rgba(16,185,129,0.06)", layer="below", line_width=0)
    fig_bar_tip.add_trace(go.Bar(
        x=[1.0] * n_sup_tip, y=sup_tip_short["Supervisor"], orientation="h",
        marker=dict(color="rgba(255,255,255,0.07)", line=dict(width=0)),
        showlegend=False, hoverinfo="skip", width=0.55
    ))
    fig_bar_tip.add_trace(go.Bar(
        x=sup_tip["PctTipif"], y=sup_tip_short["Supervisor"], orientation="h",
        marker=dict(color=sup_tip["Color"], line=dict(width=0)),
        text=sup_tip["PctTipif"].apply(lambda x: f"{x:.1%}"),
        textposition="outside",
        constraintext="none",
        textfont=dict(size=11, color="#CBD3F2", family="Inter"),
        hovertemplate="<b>%{y}</b><br>Tipificación: %{x:.1%}<extra></extra>",
        width=0.55
    ))
    fig_bar_tip.update_layout(
        barmode="overlay", height=400,
        margin=dict(l=0, r=55, t=20, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickformat=".0%", range=[0, 1.10], gridcolor="rgba(255,255,255,0.08)",
                   showgrid=True, tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)")),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11, family="Inter", color="rgba(255,255,255,0.75)")),
        showlegend=False, font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)")
    )
    st.plotly_chart(fig_bar_tip, use_container_width=True)

with c_rank_tip:
    st.markdown("""<div class='tbl-hdr' style='background:linear-gradient(135deg,#28053F 0%,#EC4899 100%)'>
        <span class='tbl-hdr-icon'>🏆</span>
        <div class='tbl-hdr-body'>
            <div class='tbl-hdr-title'>Ranking Supervisores</div>
            <div class='tbl-hdr-desc'>% Tipificación, agentes y tiempo promedio</div>
        </div>
        <span class='tbl-hdr-badge'>Resumen</span>
    </div>""", unsafe_allow_html=True)
    tbl_sup_tip = sup_tip.sort_values("PctTipif", ascending=False)[
        ["Supervisor", "PctTipif", "Agentes", "Medibles", "Tipificadas", "TConc_s"]
    ].copy()
    tbl_sup_tip["Supervisor"] = tbl_sup_tip["Supervisor"].apply(lambda n: " ".join(n.split()[:2]))
    tbl_sup_tip["PctTipif"]   = tbl_sup_tip["PctTipif"].apply(lambda x: f"{x:.1%}")
    tbl_sup_tip["TConc_s"]    = tbl_sup_tip["TConc_s"].apply(seg_a_hhmmss)
    tbl_sup_tip.columns = ["Supervisor", "% Tipif.", "Agentes", "Medibles", "Tipificadas", "T. Promedio"]
    st.dataframe(tbl_sup_tip, use_container_width=True, hide_index=True, height=400)

# ── Tiempo promedio por supervisor ──────────────────────────────────────
# Complementa el % de tipificación con la otra cara del dato: un equipo
# puede tipificar casi todo pero tardarse demasiado (o muy poco, señal de
# que están tipificando sin cuidado) en cada llamada.
st.markdown(f"""<div class='chart-hdr' style='--cc:{COLOR_TIPI};margin-top:18px'>
    <span class='ch-icon'>⏱️</span>
    <div class='ch-texts'>
        <div class='ch-title'>Tiempo Promedio por Supervisor</div>
        <div class='ch-sub'>Segundos que tarda en promedio cada llamada medible en tipificarse</div>
    </div>
    <span class='ch-tag' style='color:{COLOR_TIPI}'>Barras</span>
</div>""", unsafe_allow_html=True)

sup_tconc = sup_tip.sort_values("TConc_s", ascending=True).copy()
sup_tconc["SupCorta"] = sup_tconc["Supervisor"].apply(lambda n: " ".join(n.split()[:2]))
fig_tconc = go.Figure(go.Bar(
    x=sup_tconc["TConc_s"], y=sup_tconc["SupCorta"], orientation="h",
    marker=dict(color=sup_tconc["TConc_s"], colorscale="Magenta", line=dict(width=0)),
    text=sup_tconc["TConc_s"].apply(seg_a_hhmmss), textposition="outside",
    hovertemplate="<b>%{y}</b><br>%{text} promedio<extra></extra>",
))
fig_tconc.update_layout(
    height=max(260, 28 * len(sup_tconc)), margin=dict(l=0, r=50, t=10, b=20),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="rgba(255,255,255,0.08)", tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)")),
    yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11, family="Inter", color="rgba(255,255,255,0.75)")),
    showlegend=False, font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)")
)
st.plotly_chart(fig_tconc, use_container_width=True)

# Tabla detalle por agente
n_det = dff["Nombre"].nunique()
st.markdown(f"""
<div class='tbl-hdr' style='background:linear-gradient(120deg,#EC4899,#BE185D)'>
    <div class='tbl-hdr-icon'>📋</div>
    <div class='tbl-hdr-body'>
        <div class='tbl-hdr-title'>Detalle por Experto · Tipificación</div>
        <div class='tbl-hdr-desc'>Llamadas medibles, tipificadas, % de tipificación y tiempo promedio</div>
    </div>
    <div class='tbl-hdr-badge'>{n_det} expertos</div>
</div>
""", unsafe_allow_html=True)

tbl_det = (
    medibles.groupby(["Nombre", "Supervisor"])
    .apply(lambda g: pd.Series({
        "Medibles":    int(g["Llamadas"].sum()),
        "Tipificadas": int(g.loc[g["Tipificada"], "Llamadas"].sum()),
        "PctTipif":    g.loc[g["Tipificada"], "Llamadas"].sum() / g["Llamadas"].sum() if g["Llamadas"].sum() > 0 else 0.0,
        "TConc_s":     g["Tiempo Conc._s"].sum() / g["Llamadas"].sum() if g["Llamadas"].sum() > 0 else 0.0,
    }))
    .reset_index()
    .sort_values("PctTipif", ascending=False)
)
tbl_det_disp = pd.DataFrame({
    "Experto":        tbl_det["Nombre"],
    "Supervisor":     tbl_det["Supervisor"],
    "Medibles":       tbl_det["Medibles"].astype(int),
    "Tipificadas":    tbl_det["Tipificadas"].astype(int),
    "% Tipificación": tbl_det["PctTipif"].map(lambda x: f"{x:.1%}"),
    "T. Promedio": tbl_det["TConc_s"].map(seg_a_hhmmss),
})
df_descarga(tbl_det_disp, "tipificacion_detalle.xlsx", use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# TOP MOTIVOS DE TIPIFICACIÓN
# ─────────────────────────────────────────────
st.markdown(f"""
<div class='sec-header' style='--sc:#8B5CF6'>
    <div class='sec-wash'></div>
    <div class='sec-icon'>🔖</div>
    <div class='sec-text'>
        <div class='sec-title'>Top Motivos</div>
        <div class='sec-desc'>Los 12 motivos de tipificación (Disp.) más frecuentes en el rango seleccionado.</div>
    </div>
    <div class='sec-meta'>
        <div class='sec-meta-val' style='color:#8B5CF6'>{tipificadas_df["Disp."].nunique() if len(tipificadas_df) else 0}</div>
        <div class='sec-meta-lab'>Motivos distintos</div>
    </div>
    <span class='sec-tag' style='background:#8B5CF6'>Ranking</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""<div class='chart-hdr' style='--cc:#8B5CF6'>
    <span class='ch-icon'>🔖</span>
    <div class='ch-texts'>
        <div class='ch-title'>Motivos Más Frecuentes</div>
        <div class='ch-sub'>Cantidad de llamadas por tipificación (Disp.)</div>
    </div>
    <span class='ch-tag' style='color:#8B5CF6'>Top 12</span>
</div>""", unsafe_allow_html=True)

if len(tipificadas_df) > 0:
    top_motivos = (
        tipificadas_df.groupby("Disp.")["Llamadas"].sum()
        .sort_values(ascending=False).head(12).sort_values(ascending=True)
    )
    fig_motivos = go.Figure(go.Bar(
        x=top_motivos.values, y=top_motivos.index, orientation="h",
        marker=dict(color=px.colors.sample_colorscale("Magenta", [i/max(len(top_motivos)-1,1) for i in range(len(top_motivos))])),
        text=top_motivos.values, textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x:,} llamadas<extra></extra>",
    ))
    fig_motivos.update_layout(
        height=420, margin=dict(l=0, r=40, t=10, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)", tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)")),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11, family="Inter", color="rgba(255,255,255,0.75)")),
        font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)")
    )
    st.plotly_chart(fig_motivos, use_container_width=True)
else:
    st.info("Sin llamadas tipificadas para el filtro actual.")
