import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import glob
import os

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard WFM – Uniminuto",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUPERVISOR_COLORS = px.colors.qualitative.Bold

# ─────────────────────────────────────────────
# CARGA Y PREPARACIÓN DE DATOS
# ─────────────────────────────────────────────
ORDEN_MESES = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO",
               "JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]

def _mes_orden(path):
    nombre = os.path.basename(path).upper()
    for i, mes in enumerate(ORDEN_MESES):
        if mes in nombre:
            return i
    return 99

@st.cache_data
def cargar_datos():
    archivos = sorted(glob.glob("Consolidado_*.xlsx"), key=_mes_orden)
    if not archivos:
        st.error("No se encontraron archivos Consolidado_*.xlsx en la carpeta.")
        st.stop()

    partes = []
    for archivo in archivos:
        df_mes = pd.read_excel(archivo, sheet_name="Detalle")
        df_mes["_archivo"] = os.path.basename(archivo)
        partes.append(df_mes)

    df = pd.concat(partes, ignore_index=True)
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    def a_seg(col):
        return pd.to_timedelta(df[col], errors="coerce").dt.total_seconds()

    df["adh_s"]  = a_seg("ADH aplicada")
    df["prog_s"] = a_seg("Tiempo programado")
    df["tard_s"] = a_seg("Tiempo de tardanza")
    df["aus_s"]  = a_seg("Tiempo de ausencia")

    excesos = ["Exceso Almuerzo","Exceso Descanso","Exceso Seguimiento",
               "Exceso Toilette","Exceso Entrenamiento","Exceso Feedback","Exceso Calidad"]
    for c in excesos:
        df[c + "_min"] = pd.to_timedelta(df[c], errors="coerce").dt.total_seconds() / 60

    if "Semana" in df.columns:
        df["_semana_num"] = df["Semana"]
    df["Semana"]    = df["Fecha"].dt.to_period("W").apply(lambda p: f"Sem {p.start_time.strftime('%d/%m')}")
    df["Mes"]       = df["Fecha"].dt.to_period("M").astype(str)
    df["DiaSemana"] = df["Fecha"].dt.day_name()
    df["FechaStr"]  = df["Fecha"].dt.strftime("%d/%m")

    mask = (df["prog_s"] > 0) & (df["Validador Llegada"] != "Ausente")
    df["ADH_pct"] = None
    df.loc[mask, "ADH_pct"] = df.loc[mask, "adh_s"] / df.loc[mask, "prog_s"]

    return df, archivos

df, archivos_cargados = cargar_datos()

# ─────────────────────────────────────────────
# COLORES (fijos)
# ─────────────────────────────────────────────
COLOR_PRIMARY = "#28053F"
COLOR_ACCENT  = "#0EA5E9"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER  = "#EF4444"
COLOR_BG      = "#F0F4F8"

# ─────────────────────────────────────────────
# SIDEBAR – FILTROS
# ─────────────────────────────────────────────
with st.sidebar:
    _, _c, _ = st.columns([1, 9, 1])
    with _c:
        st.image("logo-scala-learning-transformacion-digital-universidades.webp", use_container_width=True)

    st.markdown("""
    <div class='sb-brand-v2'>
        <div class='sb-bv2-gradient'></div>
        <div class='sb-bv2-inner'>
            <div class='sb-bv2-title'>Workforce Management</div>
            <div class='sb-bv2-sub'>Uniminuto · Scala Learning</div>
            <div class='sb-bv2-tags'>
                <span class='sb-bv2-tag'>2026</span>
                <span class='sb-bv2-tag'>Dashboard</span>
                <span class='sb-bv2-tag'>WFM</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div class='sb-sec-hdr'>
        <span class='sb-sec-dot' style='background:#0EA5E9'></span>
        <span class='sb-sec-label'>Período</span>
        <span class='sb-sec-line'></span>
    </div>""", unsafe_allow_html=True)
    tipo_periodo = st.selectbox("Agrupar por", ["Día","Semana","Mes"], index=0)

    # Selector de mes (generado dinámicamente desde los archivos cargados)
    meses_disp = ["Todos"] + [
        os.path.basename(a).replace("Consolidado_", "").replace(".xlsx", "").capitalize()
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

    fechas = sorted(df["Fecha"].dt.date.unique())
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fecha_ini = st.date_input("Desde", value=fechas[0], min_value=fechas[0], max_value=fechas[-1])
    with col_f2:
        fecha_fin = st.date_input("Hasta", value=fechas[-1], min_value=fechas[0], max_value=fechas[-1])

    st.markdown("""<div class='sb-sec-hdr'>
        <span class='sb-sec-dot' style='background:#10B981'></span>
        <span class='sb-sec-label'>Filtros</span>
        <span class='sb-sec-line'></span>
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

    campanas = ["Todas"] + sorted(df["Campana"].dropna().unique().tolist())
    camp_sel = st.selectbox("Campaña", campanas)

    st.markdown("""
    <div class='sb-footer-v2'>
        <div class='sb-fv2-text'>
            Desarrollado por el equipo de<br><b>Workforce Management</b>
        </div>
        <div class='sb-fv2-divider'></div>
        <div class='sb-fv2-name'>Guillermo Steban Calderón Arrieta</div>
        <div class='sb-fv2-role'>Analista WFM · Scala Learning</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    * {{ font-family: 'Inter', sans-serif !important; }}

    /* ── Fondo con patrón de puntos ── */
    .main {{
        background-color: {COLOR_BG};
        background-image: radial-gradient(circle, #C8D6E3 1px, transparent 1px);
        background-size: 28px 28px;
    }}
    .block-container {{ padding-top: 2rem; padding-bottom: 1rem; }}

    /* ── Sidebar collapse/expand button: ícono transparente ── */
    div[data-testid="stSidebarCollapseButton"] button span,
    button[data-testid="baseButton-headerNoPadding"] span,
    div[data-testid="collapsedControl"] button span,
    div[data-testid="collapsedControl"] span {{
        color: transparent !important;
    }}
    div[data-testid="stSidebarCollapseButton"] button,
    button[data-testid="baseButton-headerNoPadding"],
    div[data-testid="collapsedControl"] button {{
        background: transparent !important;
        border: none !important;
    }}
    /* ── Ocultar texto/ícono gris al colapsar sidebar ── */
    div[data-testid="collapsedControl"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    div[data-testid="collapsedControl"] * {{
        color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    /* ── Sidebar: eliminar espacio sobrante al ensanchar ── */
    div[data-testid="stSidebarContent"] {{
        width: 100% !important;
        box-sizing: border-box !important;
        padding-right: 0.75rem !important;
    }}
    div[data-testid="stSidebarContent"] > div {{
        width: 100% !important;
    }}

    /* ── Header banner ── */
    .header-banner {{
        background:
            repeating-linear-gradient(
                -45deg,
                rgba(255,255,255,0) 0px, rgba(255,255,255,0) 12px,
                rgba(255,255,255,0.025) 12px, rgba(255,255,255,0.025) 13px
            ),
            radial-gradient(ellipse at 15% 50%, rgba(255,255,255,0.14) 0%, transparent 55%),
            radial-gradient(ellipse at 85% 80%, rgba(0,0,0,0.20) 0%, transparent 55%),
            linear-gradient(120deg, {COLOR_PRIMARY} 0%, #0EA5E9 100%);
        border-radius: 16px;
        padding: 30px 40px;
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 24px;
        box-shadow: 0 6px 28px rgba(40,5,63,0.30);
    }}
    .header-left  {{ flex: 1; min-width: 0; }}
    .header-title {{
        font-size: 22px; font-weight: 800; color: white; margin: 0 0 7px 0;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        letter-spacing: -0.3px;
    }}
    .header-sub   {{
        font-size: 13px; color: rgba(255,255,255,0.80); margin: 0;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .header-right {{ display: flex; gap: 10px; flex-shrink: 0; align-items: center; }}
    .header-badge {{
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.32);
        border-radius: 20px;
        padding: 7px 18px;
        font-size: 12px; font-weight: 700; color: white;
        white-space: nowrap; letter-spacing: 0.02em;
    }}

    /* ── KPI cards ── */
    .kpi-card {{
        background: white;
        border-radius: 18px;
        padding: 22px 22px 18px;
        box-shadow: 0 6px 28px rgba(0,0,0,0.10);
        position: relative;
        overflow: hidden;
        min-height: 148px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border: 1px solid rgba(0,0,0,0.04);
        transition: transform 0.22s ease, box-shadow 0.22s ease;
        cursor: default;
    }}
    .kpi-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 14px 44px rgba(0,0,0,0.15);
    }}
    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 5px;
        background: var(--kc, {COLOR_PRIMARY});
        border-radius: 18px 18px 0 0;
    }}
    .kpi-card::after {{
        content: '';
        position: absolute;
        top: -28px; right: -28px;
        width: 90px; height: 90px;
        background: var(--kc, {COLOR_PRIMARY});
        opacity: 0.08;
        border-radius: 50%;
    }}
    .kpi-bg-icon {{
        position: absolute;
        bottom: 14px; right: 18px;
        font-size: 44px;
        opacity: 0.09;
        line-height: 1;
        pointer-events: none;
        z-index: 0;
    }}
    .kpi-label {{ font-size: 10px; color: #94A3B8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.09em; position: relative; z-index: 1; }}
    .kpi-value {{ font-size: 36px; font-weight: 900; line-height: 1.1; margin: 10px 0 4px; position: relative; z-index: 1; }}
    .kpi-sub   {{ font-size: 11px; color: #CBD5E1; position: relative; z-index: 1; }}
    .kpi-bar-wrap {{ background: #F1F5F9; border-radius: 99px; height: 5px; margin-top: 12px; overflow: hidden; position: relative; z-index: 1; }}
    .kpi-bar-fill {{ height: 5px; border-radius: 99px; }}

    /* ── Section header cards ── */
    .sec-header {{
        background: white;
        border-radius: 16px;
        padding: 18px 24px 16px;
        margin: 24px 0 18px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        gap: 16px;
        border: 1px solid rgba(0,0,0,0.04);
    }}
    .sec-header::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: var(--sc, {COLOR_PRIMARY});
        border-radius: 16px 16px 0 0;
    }}
    .sec-header::after {{
        content: '';
        position: absolute;
        right: -24px; top: -24px;
        width: 110px; height: 110px;
        background: var(--sc, {COLOR_PRIMARY});
        opacity: 0.05;
        border-radius: 50%;
    }}
    /* Lavado de color desde la izquierda */
    .sec-wash {{
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 220px;
        background: linear-gradient(90deg, var(--sc, {COLOR_PRIMARY}), transparent);
        opacity: 0.07;
        pointer-events: none;
        z-index: 0;
    }}
    .sec-icon {{
        width: 52px; height: 52px;
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 26px;
        flex-shrink: 0;
        position: relative; z-index: 1;
    }}
    .sec-text {{ flex: 1; min-width: 0; position: relative; z-index: 1; }}
    .sec-title {{
        font-size: 17px; font-weight: 800;
        color: #1E293B; margin: 0 0 5px 0;
        letter-spacing: -0.4px;
    }}
    .sec-desc {{ font-size: 12px; color: #94A3B8; margin: 0; line-height: 1.6; }}
    /* Mini-métrica derecha */
    .sec-meta {{
        text-align: center;
        flex-shrink: 0;
        padding: 8px 18px;
        background: #F8FAFC;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        position: relative; z-index: 1;
    }}
    .sec-meta-val {{
        font-size: 22px; font-weight: 900;
        line-height: 1.1; margin-bottom: 2px;
    }}
    .sec-meta-lab {{
        font-size: 9px; font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase; letter-spacing: 0.08em;
    }}
    .sec-tag {{
        font-size: 10px; font-weight: 700;
        color: white;
        background: var(--sc, {COLOR_PRIMARY});
        padding: 5px 14px; border-radius: 99px;
        letter-spacing: 0.06em; text-transform: uppercase;
        flex-shrink: 0; align-self: flex-start;
        position: relative; z-index: 1;
    }}

    /* ── Chart mini-headers ── */
    .chart-hdr {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        background: #F8FAFC;
        border-radius: 10px;
        border-left: 4px solid var(--cc, {COLOR_ACCENT});
        margin-bottom: 10px;
    }}
    .ch-icon {{ font-size: 18px; line-height: 1; flex-shrink: 0; }}
    .ch-texts {{ flex: 1; min-width: 0; }}
    .ch-title {{ font-size: 12px; font-weight: 700; color: #334155; margin: 0 0 1px; }}
    .ch-sub {{ font-size: 10px; color: #94A3B8; margin: 0; }}
    .ch-tag {{
        margin-left: auto;
        font-size: 9px; font-weight: 700;
        color: var(--cc, {COLOR_ACCENT});
        background: white;
        border: 1px solid #E2E8F0;
        padding: 2px 8px; border-radius: 99px;
        letter-spacing: 0.05em; flex-shrink: 0;
        text-transform: uppercase;
    }}

    /* ── Table section headers ── */
    .tbl-hdr {{
        padding: 14px 20px;
        border-radius: 14px;
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 6px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.15);
        position: relative; overflow: hidden;
    }}
    .tbl-hdr::before {{
        content: '';
        position: absolute;
        left: -10px; top: -10px;
        width: 60px; height: 60px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }}
    .tbl-hdr::after {{
        content: '';
        position: absolute;
        right: -20px; bottom: -20px;
        width: 80px; height: 80px;
        background: rgba(255,255,255,0.10);
        border-radius: 50%;
    }}
    .tbl-hdr-icon {{ font-size: 24px; flex-shrink: 0; position: relative; z-index: 1; }}
    .tbl-hdr-body {{ flex: 1; position: relative; z-index: 1; }}
    .tbl-hdr-title {{ font-size: 14px; font-weight: 800; color: white; margin: 0 0 2px; letter-spacing: -0.2px; }}
    .tbl-hdr-desc {{ font-size: 11px; color: rgba(255,255,255,0.72); margin: 0; }}
    .tbl-hdr-badge {{
        font-size: 10px; font-weight: 700; color: white;
        background: rgba(255,255,255,0.20);
        border: 1px solid rgba(255,255,255,0.35);
        padding: 4px 12px; border-radius: 99px;
        flex-shrink: 0; white-space: nowrap;
        position: relative; z-index: 1;
    }}

    /* ── Plotly chart: card styling ── */
    div[data-testid="stPlotlyChart"] {{
        background: white !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.07) !important;
        border: 1px solid rgba(0,0,0,0.04) !important;
        overflow: hidden !important;
        padding: 4px !important;
    }}

    /* ── Encabezados de tablas ── */
    div[data-testid="stDataFrame"] div[role="columnheader"] {{
        background-color: {COLOR_PRIMARY} !important;
        color: white !important; font-weight: 700 !important;
    }}
    div[data-testid="stDataFrame"] div[role="columnheader"] span {{
        color: white !important;
    }}

    /* ── Sidebar – fondo degradado difuminado ── */
    section[data-testid="stSidebar"] > div:first-child {{
        background:
            radial-gradient(ellipse at 20% 10%, rgba(255,255,255,0.10) 0%, transparent 55%),
            radial-gradient(ellipse at 80% 80%, rgba(0,0,0,0.25) 0%, transparent 60%),
            linear-gradient(175deg, rgba(255,255,255,0.06) 0%, rgba(0,0,0,0.08) 100%),
            {COLOR_PRIMARY};
        border-right: none;
    }}
    div[data-testid="stSidebarContent"] * {{ color: white !important; }}
    div[data-testid="stSidebarContent"] hr {{
        border-color: rgba(255,255,255,0.12);
        margin-top: 4px !important; margin-bottom: 4px !important;
    }}

    /* ── Logo glow ── */
    div[data-testid="stSidebarContent"] [data-testid="stImage"] img {{
        filter: drop-shadow(0 6px 22px rgba(14,165,233,0.40));
    }}

    /* ── Dropdown options: texto oscuro ── */
    div[data-baseweb="popover"] *, div[data-baseweb="menu"] *,
    ul[role="listbox"] *, li[role="option"], li[role="option"] * {{
        color: #1E293B !important;
    }}
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {{ background: #F1F5F9 !important; }}

    /* ── Sidebar – selectbox valor seleccionado ── */
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] span,
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] div[class*="ValueContainer"] *,
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] input {{ color: white !important; }}
    div[data-testid="stSidebarContent"] input[type="text"] {{ color: white !important; }}

    /* ── Sidebar – brand card v2 ── */
    .sb-brand-v2 {{
        background: rgba(255,255,255,0.07);
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.12);
        overflow: hidden;
        margin: 10px 0 16px;
    }}
    @keyframes gradientFlow {{
        0%   {{ background-position: 0% 50%;   }}
        50%  {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%;   }}
    }}
    .sb-bv2-gradient {{
        height: 4px;
        background: linear-gradient(90deg, #0EA5E9, #10B981, #F59E0B, #8B5CF6, #EF4444, #0EA5E9);
        background-size: 300% 100%;
        animation: gradientFlow 7s ease-in-out infinite;
    }}
    .sb-bv2-inner {{ padding: 14px 16px 16px; text-align: center; }}
    .sb-bv2-title {{
        font-size: 15px !important; font-weight: 800 !important;
        color: white !important; letter-spacing: -0.3px !important; margin-bottom: 4px;
    }}
    .sb-bv2-sub {{
        font-size: 12px !important;
        color: rgba(255,255,255,0.55) !important; margin-bottom: 12px;
    }}
    .sb-bv2-tags {{ display: flex; gap: 6px; justify-content: center; flex-wrap: wrap; }}
    .sb-bv2-tag {{
        font-size: 9px !important; font-weight: 700 !important;
        color: rgba(255,255,255,0.80) !important;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.22);
        padding: 3px 10px; border-radius: 99px;
        letter-spacing: 0.06em !important; text-transform: uppercase;
    }}

    /* ── Sidebar – section headers ── */
    .sb-sec-hdr {{ display: flex; align-items: center; gap: 8px; margin: 18px 0 8px; }}
    .sb-sec-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; display: inline-block; }}
    .sb-sec-label {{
        font-size: 10px !important; font-weight: 700 !important;
        color: rgba(255,255,255,0.55) !important;
        letter-spacing: 0.10em !important; text-transform: uppercase; white-space: nowrap;
    }}
    .sb-sec-line {{ flex: 1; height: 1px; background: rgba(255,255,255,0.10); display: block; }}

    /* ── Sidebar – widget labels ── */
    div[data-testid="stSidebarContent"] label,
    div[data-testid="stSidebarContent"] .stSelectbox label,
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"],
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"] p,
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"] span {{
        font-size: 11px !important; font-weight: 400 !important;
        color: rgba(255,255,255,0.72) !important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput label,
    div[data-testid="stSidebarContent"] .stDateInput [data-testid="stWidgetLabel"],
    div[data-testid="stSidebarContent"] .stDateInput [data-testid="stWidgetLabel"] p {{
        font-size: 11px !important; font-weight: 500 !important;
        color: {COLOR_ACCENT} !important;
    }}
    div[data-testid="stSidebarContent"] .stSelectbox > div > div,
    div[data-testid="stSidebarContent"] .stSelectbox > label + div > div {{
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput > div > div > input {{
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 8px !important; color: white !important;
        font-size: 11px !important;
    }}

    /* ── Sidebar – footer card v2 ── */
    .sb-footer-v2 {{
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 14px; text-align: center;
        margin-top: 20px; position: relative; overflow: hidden;
    }}
    .sb-footer-v2::before {{
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #0EA5E9, #8B5CF6, #10B981);
    }}
    .sb-fv2-text {{ font-size: 10px !important; color: rgba(255,255,255,0.42) !important; line-height: 1.7; margin-bottom: 10px; }}
    .sb-fv2-divider {{ height: 1px; background: rgba(255,255,255,0.08); margin: 8px 0; }}
    .sb-fv2-name {{ font-size: 11px !important; font-weight: 700 !important; color: rgba(255,255,255,0.72) !important; margin-bottom: 3px; }}
    .sb-fv2-role {{ font-size: 10px !important; color: rgba(255,255,255,0.35) !important; }}
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
    archivo_mes = f"Consolidado_{mes_sel.upper()}.xlsx"
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
    mask &= df["Campana"] == camp_sel

dff = df[mask].copy()

if tipo_periodo == "Día":
    dff["_periodo"] = dff["FechaStr"]
elif tipo_periodo == "Semana":
    dff["_periodo"] = dff["Semana"]
else:
    dff["_periodo"] = dff["Mes"]

# ─────────────────────────────────────────────
# MÉTRICAS GLOBALES
# ─────────────────────────────────────────────
dff_validos = dff[(dff["prog_s"] > 0) & (dff["Validador Llegada"] != "Ausente")]
total_agentes   = dff["Nombre"].nunique()
total_registros = len(dff_validos)
n_supervisores  = dff_validos["Supervisor"].nunique()

adh_global = dff_validos["adh_s"].sum() / dff_validos["prog_s"].sum() if dff_validos["prog_s"].sum() > 0 else 0

llegada_counts = dff["Validador Llegada"].value_counts()
total_prog_valid = (llegada_counts.get("Llegada a tiempo", 0) + llegada_counts.get("Llegada tarde", 0)
                   + llegada_counts.get("Llegada antes", 0) + llegada_counts.get("Ausente", 0))
pct_ausentes = llegada_counts.get("Ausente", 0) / total_prog_valid * 100 if total_prog_valid > 0 else 0
pct_tarde    = llegada_counts.get("Llegada tarde", 0) / total_prog_valid * 100 if total_prog_valid > 0 else 0
pct_tiempo   = llegada_counts.get("Llegada a tiempo", 0) / total_prog_valid * 100 if total_prog_valid > 0 else 0

adh_color = COLOR_SUCCESS if adh_global >= 0.90 else (COLOR_WARNING if adh_global >= 0.80 else COLOR_DANGER)

# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
rango = f"{fecha_ini.strftime('%d/%m/%Y')} – {fecha_fin.strftime('%d/%m/%Y')}"
filtro_txt = (f"{'Todos los supervisores' if sup_sel == 'Todos' else sup_sel} · "
              f"{'Todos los expertos' if exp_sel == 'Todos' else exp_sel} · "
              f"{'Todas las campañas' if camp_sel == 'Todas' else camp_sel}")
st.markdown(f"""
<div class='header-banner'>
    <div class='header-left'>
        <div class='header-title'>TABLERO DE SEGUIMIENTO WORKFORCE MANAGEMENT · UNIMINUTO 2026</div>
        <div class='header-sub'>📅 {rango} &nbsp;|&nbsp; 👤 {filtro_txt}</div>
    </div>
    <div class='header-right'>
        <span class='header-badge'>Uniminuto</span>
        <span class='header-badge'>Scala Learning</span>
        <span class='header-badge'>2026</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPIs GLOBALES
# ─────────────────────────────────────────────
def kpi_bar(pct, color, max_val=100):
    fill = min(pct / max_val * 100, 100)
    return f"<div class='kpi-bar-wrap'><div class='kpi-bar-fill' style='width:{fill:.0f}%;background:{color};'></div></div>"

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""<div class='kpi-card' style='--kc:{adh_color}'>
        <div class='kpi-bg-icon'>🎯</div>
        <div>
            <div class='kpi-label'>Adherencia</div>
            <div class='kpi-value' style='color:{adh_color}'>{adh_global:.1%}</div>
            <div class='kpi-sub'>Meta: 90%</div>
        </div>
        {kpi_bar(adh_global * 100, adh_color, 100)}
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_ACCENT}'>
        <div class='kpi-bg-icon'>👥</div>
        <div>
            <div class='kpi-label'>Expertos</div>
            <div class='kpi-value' style='color:{COLOR_PRIMARY}'>{total_agentes}</div>
            <div class='kpi-sub'>{total_registros} registros</div>
        </div>
        {kpi_bar(total_registros, COLOR_ACCENT, max(total_registros, 1))}
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_SUCCESS}'>
        <div class='kpi-bg-icon'>✅</div>
        <div>
            <div class='kpi-label'>Llegada a tiempo</div>
            <div class='kpi-value' style='color:{COLOR_SUCCESS}'>{pct_tiempo:.1f}%</div>
            <div class='kpi-sub'>{llegada_counts.get("Llegada a tiempo", 0)} registros</div>
        </div>
        {kpi_bar(pct_tiempo, COLOR_SUCCESS)}
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_WARNING}'>
        <div class='kpi-bg-icon'>⏰</div>
        <div>
            <div class='kpi-label'>Llegadas tarde</div>
            <div class='kpi-value' style='color:{COLOR_WARNING}'>{pct_tarde:.1f}%</div>
            <div class='kpi-sub'>{llegada_counts.get("Llegada tarde", 0)} registros</div>
        </div>
        {kpi_bar(pct_tarde, COLOR_WARNING)}
    </div>""", unsafe_allow_html=True)
with k5:
    st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_DANGER}'>
        <div class='kpi-bg-icon'>🚨</div>
        <div>
            <div class='kpi-label'>Ausentes</div>
            <div class='kpi-value' style='color:{COLOR_DANGER}'>{pct_ausentes:.1f}%</div>
            <div class='kpi-sub'>{llegada_counts.get("Ausente", 0)} registros</div>
        </div>
        {kpi_bar(pct_ausentes, COLOR_DANGER)}
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TENDENCIA + DISTRIBUCIÓN LLEGADAS
# ─────────────────────────────────────────────
st.markdown(f"""
<div class='sec-header' style='--sc:{COLOR_ACCENT}'>
    <div class='sec-wash'></div>
    <div class='sec-icon' style='background:linear-gradient(135deg,rgba(14,165,233,0.20),rgba(14,165,233,0.06))'>📈</div>
    <div class='sec-text'>
        <div class='sec-title'>Tendencia de Adherencia</div>
        <div class='sec-desc'>Evolución de la adherencia del equipo y distribución de tipos de llegada en el período.</div>
    </div>
    <div class='sec-meta'>
        <div class='sec-meta-val' style='color:{adh_color}'>{adh_global:.1%}</div>
        <div class='sec-meta-lab'>Adherencia global</div>
    </div>
    <span class='sec-tag'>Análisis</span>
</div>
""", unsafe_allow_html=True)

tend = (
    dff_validos
    .groupby("_periodo")
    .apply(lambda g: g["adh_s"].sum() / g["prog_s"].sum() if g["prog_s"].sum() > 0 else 0)
    .reset_index(name="ADH")
)

c1, c2 = st.columns([3, 2])
with c1:
    st.markdown(f"""<div class='chart-hdr' style='--cc:{COLOR_ACCENT}'>
        <span class='ch-icon'>📈</span>
        <div class='ch-texts'>
            <div class='ch-title'>Evolución de Adherencia</div>
            <div class='ch-sub'>Por período seleccionado · Meta 90%</div>
        </div>
        <span class='ch-tag'>Tendencia</span>
    </div>""", unsafe_allow_html=True)
    fig_tend = go.Figure()
    fig_tend.add_trace(go.Scatter(
        x=tend["_periodo"], y=tend["ADH"],
        mode="lines+markers+text",
        line=dict(color=COLOR_ACCENT, width=1.25, shape="spline"),
        marker=dict(size=7, color=COLOR_PRIMARY),
        text=tend["ADH"].apply(lambda x: f"{x:.0%}"),
        textposition="top center",
        textfont=dict(size=9, color=COLOR_PRIMARY, family="Inter"),
        fill="tozeroy",
        fillcolor="rgba(14,165,233,0.07)",
        hovertemplate="%{x}<br><b>%{y:.1%}</b><extra></extra>"
    ))
    fig_tend.add_hline(y=0.90, line_dash="dot", line_color=COLOR_SUCCESS,
                       annotation_text="Meta 90%", annotation_position="top right",
                       annotation_font=dict(color=COLOR_SUCCESS, size=11))
    _n_tend = len(tend)
    _ini_tend = max(-0.5, _n_tend - 15 - 0.5)
    fig_tend.update_layout(
        height=360, margin=dict(l=0, r=10, t=24, b=40),
        paper_bgcolor="white", plot_bgcolor="white",
        yaxis=dict(tickformat=".0%", gridcolor="#F1F5F9", range=[0.10, 1.05], dtick=0.05, tickfont=dict(size=10)),
        xaxis=dict(
            gridcolor="#F1F5F9", tickfont=dict(size=10),
            range=[_ini_tend, _n_tend - 0.5],
            rangeslider=dict(visible=True, thickness=0.08, bgcolor="#F8FAFC"),
            tickangle=-30
        ),
        font=dict(family="Inter", size=11)
    )
    st.plotly_chart(fig_tend, use_container_width=True)

with c2:
    st.markdown(f"""<div class='chart-hdr' style='--cc:{COLOR_SUCCESS}'>
        <span class='ch-icon'>🍩</span>
        <div class='ch-texts'>
            <div class='ch-title'>Distribución de Llegadas</div>
            <div class='ch-sub'>Puntualidad en el período seleccionado</div>
        </div>
        <span class='ch-tag'>Donut</span>
    </div>""", unsafe_allow_html=True)
    llegadas_plot = dff["Validador Llegada"].value_counts().reset_index()
    llegadas_plot.columns = ["Estado","Cantidad"]
    llegadas_plot = llegadas_plot[llegadas_plot["Estado"] != "No programado"]
    color_map = {
        "Llegada a tiempo": COLOR_SUCCESS,
        "Llegada antes":    COLOR_ACCENT,
        "Llegada tarde":    COLOR_WARNING,
        "Ausente":          COLOR_DANGER
    }
    lp_labels = llegadas_plot["Estado"].tolist()
    lp_values = llegadas_plot["Cantidad"].tolist()
    lp_colors = [color_map.get(l, "#94A3B8") for l in lp_labels]
    max_idx = lp_values.index(max(lp_values)) if lp_values else 0
    pull = [0.06 if i == max_idx else 0 for i in range(len(lp_values))]

    fig_pie = go.Figure(go.Pie(
        labels=lp_labels, values=lp_values, hole=0.62,
        marker=dict(colors=lp_colors, line=dict(color="white", width=3)),
        pull=pull, textinfo="percent", textposition="inside",
        textfont=dict(size=12, color="white", family="Inter"),
        hovertemplate="<b>%{label}</b><br>%{value} registros · %{percent}<extra></extra>",
        sort=False
    ))
    fig_pie.add_annotation(
        text=f"<b>{pct_tiempo:.1f}%</b><br>a tiempo", x=0.5, y=0.5,
        font=dict(size=15, color=COLOR_SUCCESS, family="Inter"),
        showarrow=False, align="center"
    )
    fig_pie.update_layout(
        height=320, margin=dict(l=0, r=0, t=24, b=0),
        paper_bgcolor="white", showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0,
                    font=dict(size=10, family="Inter"), itemsizing="constant"),
        font=dict(family="Inter", size=11)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ─────────────────────────────────────────────
# COMPARATIVO POR SUPERVISOR
# ─────────────────────────────────────────────
st.markdown(f"""
<div class='sec-header' style='--sc:{COLOR_PRIMARY}'>
    <div class='sec-wash'></div>
    <div class='sec-icon' style='background:linear-gradient(135deg,rgba(40,5,63,0.20),rgba(40,5,63,0.06))'>👥</div>
    <div class='sec-text'>
        <div class='sec-title'>Comparativo por Supervisor</div>
        <div class='sec-desc'>Adherencia consolidada por equipo: verde ≥ 90%, amarillo ≥ 80%, rojo &lt; 80%.</div>
    </div>
    <div class='sec-meta'>
        <div class='sec-meta-val' style='color:{COLOR_PRIMARY}'>{n_supervisores}</div>
        <div class='sec-meta-lab'>Supervisores</div>
    </div>
    <span class='sec-tag'>Equipos</span>
</div>
""", unsafe_allow_html=True)

sup_stats = (
    dff_validos.groupby("Supervisor")
    .apply(lambda g: pd.Series({
        "ADH":      g["adh_s"].sum() / g["prog_s"].sum() if g["prog_s"].sum() > 0 else 0,
        "Agentes":  g["Nombre"].nunique(),
        "Registros": len(g)
    }))
    .reset_index()
    .sort_values("ADH", ascending=True)
)

aus_sup   = dff[dff["Validador Llegada"] == "Ausente"].groupby("Supervisor").size().reset_index(name="Ausentes")
tarde_sup = dff[dff["Validador Llegada"] == "Llegada tarde"].groupby("Supervisor").size().reset_index(name="Tardes")
sup_stats = sup_stats.merge(aus_sup, on="Supervisor", how="left").merge(tarde_sup, on="Supervisor", how="left")
sup_stats["Ausentes"] = sup_stats["Ausentes"].fillna(0).astype(int)
sup_stats["Tardes"]   = sup_stats["Tardes"].fillna(0).astype(int)

c_bar, c_gauge = st.columns([3, 2])

with c_bar:
    st.markdown(f"""<div class='chart-hdr' style='--cc:{COLOR_PRIMARY}'>
        <span class='ch-icon'>📊</span>
        <div class='ch-texts'>
            <div class='ch-title'>Adherencia por Supervisor</div>
            <div class='ch-sub'>Menor a mayor · Zona verde = meta cumplida</div>
        </div>
        <span class='ch-tag'>Barras</span>
    </div>""", unsafe_allow_html=True)
    sup_stats["Color"] = sup_stats["ADH"].apply(
        lambda x: COLOR_SUCCESS if x >= 0.90 else (COLOR_WARNING if x >= 0.80 else COLOR_DANGER)
    )
    sup_short = sup_stats.copy()
    sup_short["Supervisor"] = sup_short["Supervisor"].apply(lambda n: " ".join(n.split()[:2]))
    n_sup = len(sup_stats)

    fig_bar = go.Figure()
    fig_bar.add_vrect(x0=0.90, x1=1.02, fillcolor="rgba(16,185,129,0.06)", layer="below", line_width=0)
    fig_bar.add_trace(go.Bar(
        x=[1.0] * n_sup, y=sup_short["Supervisor"], orientation="h",
        marker=dict(color="rgba(226,232,240,0.9)", line=dict(width=0)),
        showlegend=False, hoverinfo="skip", width=0.55
    ))
    fig_bar.add_trace(go.Bar(
        x=sup_stats["ADH"], y=sup_short["Supervisor"], orientation="h",
        marker=dict(color=sup_stats["Color"], line=dict(width=0)),
        text=sup_stats["ADH"].apply(lambda x: f"{x:.1%}"),
        textposition="outside",
        constraintext="none",
        textfont=dict(size=11, color=COLOR_PRIMARY, family="Inter"),
        hovertemplate="<b>%{y}</b><br>Adherencia: %{x:.1%}<extra></extra>",
        width=0.55
    ))
    fig_bar.add_vline(x=0.90, line_dash="dot", line_color=COLOR_PRIMARY, line_width=1.5,
                      annotation_text="Meta 90%",
                      annotation_font=dict(size=10, color=COLOR_PRIMARY),
                      annotation_position="top left")
    fig_bar.update_layout(
        barmode="overlay", height=400,
        margin=dict(l=0, r=55, t=20, b=0),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(tickformat=".0%", range=[0, 1.10], gridcolor="#F1F5F9",
                   showgrid=True, tickfont=dict(size=10, family="Inter")),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11, family="Inter")),
        showlegend=False, font=dict(family="Inter", size=11)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with c_gauge:
    st.markdown("""<div class='tbl-hdr' style='background:linear-gradient(135deg,#28053F 0%,#0EA5E9 100%)'>
        <span class='tbl-hdr-icon'>🏆</span>
        <div class='tbl-hdr-body'>
            <div class='tbl-hdr-title'>Ranking Supervisores</div>
            <div class='tbl-hdr-desc'>Adherencia, agentes, ausencias y tardanzas</div>
        </div>
        <span class='tbl-hdr-badge'>Resumen</span>
    </div>""", unsafe_allow_html=True)
    tabla_sup = sup_stats.sort_values("ADH", ascending=False)[
        ["Supervisor","ADH","Agentes","Ausentes","Tardes"]
    ].copy()
    tabla_sup["ADH"] = tabla_sup["ADH"].apply(lambda x: f"{x:.1%}")
    tabla_sup["Supervisor"] = tabla_sup["Supervisor"].apply(lambda n: " ".join(n.split()[:2]))
    tabla_sup.columns = ["Supervisor","ADH%","Agentes","Ausentes","Tardes"]
    st.dataframe(tabla_sup, use_container_width=True, hide_index=True, height=400)

# ─────────────────────────────────────────────
# GRÁFICAS POR SUPERVISOR (TENDENCIA)
# ─────────────────────────────────────────────
st.markdown(f"""
<div class='sec-header' style='--sc:#8B5CF6'>
    <div class='sec-wash'></div>
    <div class='sec-icon' style='background:linear-gradient(135deg,rgba(139,92,246,0.20),rgba(139,92,246,0.06))'>📉</div>
    <div class='sec-text'>
        <div class='sec-title'>Tendencia por Supervisor</div>
        <div class='sec-desc'>Comparación de la evolución de adherencia de cada supervisor a lo largo del período.</div>
    </div>
    <div class='sec-meta'>
        <div class='sec-meta-val' style='color:#8B5CF6'>{n_supervisores}</div>
        <div class='sec-meta-lab'>Equipos</div>
    </div>
    <span class='sec-tag' style='background:#8B5CF6'>Evolución</span>
</div>
""", unsafe_allow_html=True)

tend_sup = (
    dff_validos
    .groupby(["_periodo","Supervisor"])
    .apply(lambda g: g["adh_s"].sum() / g["prog_s"].sum() if g["prog_s"].sum() > 0 else 0)
    .reset_index(name="ADH")
)

sup_lista = sorted(tend_sup["Supervisor"].unique())
colores_sup = {s: SUPERVISOR_COLORS[i % len(SUPERVISOR_COLORS)] for i, s in enumerate(sup_lista)}

st.markdown("""<div class='chart-hdr' style='--cc:#8B5CF6'>
    <span class='ch-icon'>📉</span>
    <div class='ch-texts'>
        <div class='ch-title'>Adherencia por Supervisor en el Tiempo</div>
        <div class='ch-sub'>Cada línea representa un supervisor · Meta 90%</div>
    </div>
    <span class='ch-tag' style='color:#8B5CF6'>Multi-línea</span>
</div>""", unsafe_allow_html=True)

fig_sup = go.Figure()
for sup in sup_lista:
    sub = tend_sup[tend_sup["Supervisor"] == sup]
    nombre_corto = " ".join(sup.split()[:2])
    fig_sup.add_trace(go.Scatter(
        x=sub["_periodo"], y=sub["ADH"],
        name=nombre_corto,
        mode="lines+markers",
        line=dict(color=colores_sup[sup], width=1.25, shape="spline"),
        marker=dict(size=5),
        hovertemplate=f"<b>{nombre_corto}</b><br>%{{x}}: %{{y:.1%}}<extra></extra>"
    ))
fig_sup.add_hline(y=0.90, line_dash="dot", line_color="#9CA3AF",
                  annotation_text="Meta 90%", annotation_position="top right")
_periodos_sup = tend_sup["_periodo"].unique().tolist()
_n_sup_per    = len(_periodos_sup)
_ini_sup      = max(-0.5, _n_sup_per - 15 - 0.5)
fig_sup.update_layout(
    height=380, margin=dict(l=0,r=0,t=10,b=40),
    paper_bgcolor="white", plot_bgcolor="white",
    yaxis=dict(tickformat=".0%", gridcolor="#F3F4F6", range=[0, 1.2]),
    xaxis=dict(
        gridcolor="#F3F4F6",
        range=[_ini_sup, _n_sup_per - 0.5],
        rangeslider=dict(visible=True, thickness=0.08, bgcolor="#F8FAFC"),
        tickangle=-30
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
    font=dict(family="Inter", size=11)
)
st.plotly_chart(fig_sup, use_container_width=True)

# ─────────────────────────────────────────────
# DETALLE POR AGENTE
# ─────────────────────────────────────────────
st.markdown(f"""
<div class='sec-header' style='--sc:{COLOR_SUCCESS}'>
    <div class='sec-wash'></div>
    <div class='sec-icon' style='background:linear-gradient(135deg,rgba(16,185,129,0.20),rgba(16,185,129,0.06))'>🔍</div>
    <div class='sec-text'>
        <div class='sec-title'>Detalle por Agente</div>
        <div class='sec-desc'>Adherencia, planificación y excesos por experto. Filtra por agente desde la barra lateral.</div>
    </div>
    <div class='sec-meta'>
        <div class='sec-meta-val' style='color:{COLOR_SUCCESS}'>{total_agentes}</div>
        <div class='sec-meta-lab'>Expertos</div>
    </div>
    <span class='sec-tag' style='background:{COLOR_SUCCESS}'>Tablas</span>
</div>
""", unsafe_allow_html=True)

def seg_a_hhmmss(s):
    if pd.isna(s) or s <= 0:
        return "-"
    s = int(s)
    h, r = divmod(s, 3600)
    m, sec = divmod(r, 60)
    return f"{h}:{m:02d}:{sec:02d}"

def fmt_plan(v):
    if pd.isna(v):
        return "-"
    s = str(v).strip()
    if hasattr(v, "total_seconds"):
        return seg_a_hhmmss(v.total_seconds())
    return s

# ── Tabla 1: Resumen General ──────────────────
st.markdown(f"""<div class='tbl-hdr' style='background:linear-gradient(135deg,{COLOR_SUCCESS} 0%,#059669 100%)'>
    <span class='tbl-hdr-icon'>📋</span>
    <div class='tbl-hdr-body'>
        <div class='tbl-hdr-title'>Resumen General</div>
        <div class='tbl-hdr-desc'>Adherencia, retardos, ausencias y tiempos por experto y fecha</div>
    </div>
    <span class='tbl-hdr-badge'>{dff["Nombre"].nunique()} expertos · {len(dff)} registros</span>
</div>""", unsafe_allow_html=True)

t1 = dff.copy()
t1["Fecha"]             = t1["Fecha"].dt.strftime("%d/%m/%Y")
t1["Retardo"]           = t1["Validador Llegada"].apply(lambda x: "Sí" if x == "Llegada tarde" else "No")
t1["Ausencia"]          = t1["Validador Llegada"].apply(lambda x: "Sí" if x == "Ausente" else "No")
t1["Tiempo de retardo"] = t1.apply(lambda r: seg_a_hhmmss(r["tard_s"]) if r["Retardo"] == "Sí" else "-", axis=1)
t1["T. Programado"]     = t1["prog_s"].apply(seg_a_hhmmss)
t1["Fuera de ADH"]      = (t1["prog_s"] - t1["adh_s"]).clip(lower=0).apply(seg_a_hhmmss)
t1["ADH Aplicada"]      = t1["adh_s"].apply(seg_a_hhmmss)
t1["Adherencia %"]      = t1["ADH_pct"].fillna(0) * 100

t1_show = (
    t1.rename(columns={"Nombre": "Agente", "Campana": "Campaña"})[
        ["Fecha", "Agente", "Supervisor", "Campaña", "Adherencia %",
         "Retardo", "Tiempo de retardo", "Ausencia",
         "T. Programado", "Fuera de ADH", "ADH Aplicada"]
    ].sort_values(["Fecha", "Agente"]).reset_index(drop=True)
)
st.dataframe(
    t1_show,
    column_config={
        "Adherencia %": st.column_config.ProgressColumn(
            "Adherencia %", format="%.1f%%", min_value=0, max_value=100
        ),
        "Agente":            st.column_config.TextColumn("Agente"),
        "Supervisor":        st.column_config.TextColumn("Supervisor"),
        "Campaña":           st.column_config.TextColumn("Campaña"),
        "Retardo":           st.column_config.TextColumn("Retardo"),
        "Ausencia":          st.column_config.TextColumn("Ausencia"),
        "Tiempo de retardo": st.column_config.TextColumn("T. Retardo"),
        "T. Programado":     st.column_config.TextColumn("T. Programado"),
        "Fuera de ADH":      st.column_config.TextColumn("Fuera ADH"),
        "ADH Aplicada":      st.column_config.TextColumn("ADH Aplicada"),
    },
    use_container_width=True, hide_index=True, height=350
)

# ── Tabla 2: Planificación ────────────────────
st.markdown(f"""<div class='tbl-hdr' style='background:linear-gradient(135deg,{COLOR_ACCENT} 0%,#0284C7 100%);margin-top:20px'>
    <span class='tbl-hdr-icon'>📅</span>
    <div class='tbl-hdr-body'>
        <div class='tbl-hdr-title'>Planificación</div>
        <div class='tbl-hdr-desc'>Turnos, breaks, lunch, seguimiento y capacitación por experto</div>
    </div>
    <span class='tbl-hdr-badge'>Horarios</span>
</div>""", unsafe_allow_html=True)

plan_cols = ["Turno inicio", "Turno fin", "Break inicio", "Break fin",
             "Lunch inicio", "Lunch fin", "Ini Segui", "Fin Segui",
             "Ini Preturno", "Fin Preturno", "Capa inicio", "Capa fin"]
plan_disponibles = [c for c in plan_cols if c in dff.columns]

t2 = dff.rename(columns={"Nombre": "Agente", "Campana": "Campaña"})[
    ["Fecha", "Agente", "Supervisor", "Campaña"] + plan_disponibles
].copy()
t2["Fecha"] = t2["Fecha"].dt.strftime("%d/%m/%Y")
for c in plan_disponibles:
    t2[c] = t2[c].apply(fmt_plan)

st.dataframe(
    t2.sort_values(["Fecha", "Agente"]).reset_index(drop=True),
    use_container_width=True, hide_index=True, height=350
)

# ── Tabla 3: Estados y Excesos ────────────────
st.markdown(f"""<div class='tbl-hdr' style='background:linear-gradient(135deg,{COLOR_DANGER} 0%,#DC2626 100%);margin-top:20px'>
    <span class='tbl-hdr-icon'>⚠️</span>
    <div class='tbl-hdr-body'>
        <div class='tbl-hdr-title'>Estados y Excesos</div>
        <div class='tbl-hdr-desc'>Tiempos excedidos por actividad · Total excesos consolidado en h:mm:ss</div>
    </div>
    <span class='tbl-hdr-badge'>Excesos</span>
</div>""", unsafe_allow_html=True)

exc_cols     = ["Exceso Almuerzo", "Exceso Descanso", "Exceso Seguimiento",
                "Exceso Toilette", "Exceso Entrenamiento", "Exceso Feedback", "Exceso Calidad"]
exc_min_cols = [c + "_min" for c in exc_cols]
exc_min_disp = [c for c in exc_min_cols if c in dff.columns]

t3 = dff.rename(columns={"Nombre": "Agente", "Campana": "Campaña"}).copy()
t3["Fecha"] = t3["Fecha"].dt.strftime("%d/%m/%Y")
exc_fmt_cols = []
for orig, min_col in zip(exc_cols, exc_min_cols):
    if min_col in t3.columns:
        t3[orig] = (t3[min_col] * 60).apply(seg_a_hhmmss)
        exc_fmt_cols.append(orig)

if exc_min_disp:
    total_s = t3[exc_min_disp].sum(axis=1) * 60
    t3["Total excesos"] = total_s.apply(seg_a_hhmmss)

cols_t3 = ["Fecha", "Agente", "Supervisor", "Campaña"] + exc_fmt_cols + (["Total excesos"] if exc_min_disp else [])
t3_show = t3[cols_t3].sort_values(["Fecha", "Agente"]).reset_index(drop=True)
st.dataframe(t3_show, use_container_width=True, hide_index=True, height=350)

st.caption(f"📋 {dff['Nombre'].nunique()} agentes · {len(dff)} registros en el período seleccionado")
