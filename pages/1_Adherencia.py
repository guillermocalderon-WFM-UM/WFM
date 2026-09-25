import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import glob
import os
import base64
import io

import _ui

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
SUPERVISOR_COLORS = px.colors.qualitative.Bold

@st.cache_data(show_spinner=False)
def _excel_bytes(df):
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    return buf.getvalue()

def df_descarga(df, nombre_archivo, **kwargs):
    """Muestra la tabla y deja el Excel listo bajo demanda: generarlo con openpyxl es
    lento y antes se ejecutaba en cada cambio de filtro para las 3 tablas, aunque nadie
    descargara nada. Ahora solo se calcula cuando el usuario hace clic en 'Preparar'."""
    if not _ui.toggle_dataframe(df, nombre_archivo.replace(".xlsx", ""), f"table_{nombre_archivo}", **kwargs):
        return
    _sig = (len(df), len(df.columns))
    _bytes_key = f"_xlsx_bytes_{nombre_archivo}"
    _sig_key = f"_xlsx_sig_{nombre_archivo}"
    if st.session_state.get(_sig_key) != _sig:
        st.session_state.pop(_bytes_key, None)

    _, col_dl = st.columns([6, 1])
    with col_dl:
        if _bytes_key not in st.session_state:
            if st.button("↓ Preparar Excel", key=f"prep_{nombre_archivo}", use_container_width=True):
                st.session_state[_bytes_key] = _excel_bytes(df)
                st.session_state[_sig_key] = _sig
                st.rerun()
        else:
            st.download_button(
                "⬇ Descargar Excel", data=st.session_state[_bytes_key],
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_{nombre_archivo}", use_container_width=True,
            )

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
def cargar_datos(firma):
    # firma = (nombre, fecha_modificación) de cada archivo → el caché se invalida
    #         automáticamente cuando agregas/actualizas un Consolidado_*.xlsx.
    archivos = sorted(
        [f for f in glob.glob("Consolidado_*.xlsx")
         if "_O_" not in os.path.basename(f) and "_T_" not in os.path.basename(f)],
        key=_mes_orden
    )
    if not archivos:
        st.error("No se encontraron archivos Consolidado_*.xlsx en la carpeta.")
        st.stop()

    partes = []
    for archivo in archivos:
        df_mes = pd.read_excel(archivo, sheet_name="Detalle", engine="openpyxl")
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

    mask = (df["prog_s"] > 0)
    df["ADH_pct"] = None
    df.loc[mask, "ADH_pct"] = df.loc[mask, "adh_s"] / df.loc[mask, "prog_s"]

    return df, archivos

_firma_archivos = tuple(
    (os.path.basename(a), os.path.getmtime(a))
    for a in sorted(
        [f for f in glob.glob("Consolidado_*.xlsx")
         if "_O_" not in os.path.basename(f) and "_T_" not in os.path.basename(f)],
        key=_mes_orden
    )
)
df, archivos_cargados = cargar_datos(_firma_archivos)

# ─────────────────────────────────────────────
# COLORES (fijos)
# ─────────────────────────────────────────────
COLOR_PRIMARY = "#28053F"
COLOR_ACCENT  = "#0EA5E9"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER  = "#EF4444"
COLOR_BG      = "#F0F4F8"

def _adh_color(v):
    return COLOR_SUCCESS if v >= 0.90 else (COLOR_WARNING if v >= 0.80 else COLOR_DANGER)

# ─────────────────────────────────────────────
# LOGO BASE64
# ─────────────────────────────────────────────
_LOGO_PATH = "logo-scala-learning-transformacion-digital-universidades.webp"
try:
    with open(_LOGO_PATH, "rb") as _f:
        _logo_b64 = base64.b64encode(_f.read()).decode()
    _logo_src = f"data:image/webp;base64,{_logo_b64}"
except FileNotFoundError:
    _logo_src = ""

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

    campanas = ["Todas"] + sorted(df["Campana"].dropna().unique().tolist())
    camp_sel = st.selectbox("Campaña", campanas)

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
    /* restaurar la fuente de íconos Material (si no, sale el texto "keyboard_double_arrow_right") */
    span[data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="collapsedControl"] span,
    .material-symbols-rounded, .material-symbols-outlined, .material-icons {{
        font-family: 'Material Symbols Rounded','Material Symbols Outlined','Material Icons' !important;
    }}
    /* ocultar el menú automático del sidebar */
    [data-testid="stSidebarNav"] {{ display:none !important; }}

    /* ── Fondo OSCURO con aurora (dark-glass · estilo home) ── */
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

    /* ── Botón colapsar/expandir sidebar: ícono limpio ── */
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
    div[data-testid="collapsedControl"] button:hover {{
        border-color: rgba(14,165,233,0.45) !important;
    }}
    /* ícono blanco dentro del sidebar oscuro; oscuro cuando está colapsado sobre el fondo claro */
    [data-testid="stSidebarCollapseButton"] span {{ color: rgba(255,255,255,0.80) !important; font-size:20px !important; }}
    div[data-testid="collapsedControl"] span {{ color: {COLOR_PRIMARY} !important; font-size:20px !important; }}
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
    /* ── HEADER · banner (idéntico a Ocupación) ── */
    .st-key-hdrbanner {{
        position: relative; overflow: hidden;
        background:
            radial-gradient(ellipse 70% 130% at 2% -15%,  rgba(14,165,233,0.34) 0%, transparent 60%),
            radial-gradient(ellipse 65% 130% at 100% 120%, rgba(129,140,248,0.34) 0%, transparent 60%),
            radial-gradient(ellipse 55% 110% at 72% 130%,  rgba(52,211,153,0.16) 0%, transparent 60%),
            linear-gradient(155deg, #0B0518 0%, #14082b 50%, #0A0414 100%);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 20px; padding: 18px 30px; margin-bottom: 18px;
        box-shadow: 0 18px 46px -18px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.08);
    }}
    .hb-eyebrow {{ display:inline-flex;align-items:center;gap:8px;
        background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.16);
        border-radius:99px;padding:5px 13px;margin-bottom:11px;
        font-size:10px;font-weight:700;color:rgba(255,255,255,0.78);
        letter-spacing:0.12em;text-transform:uppercase; }}
    .hb-dot {{ width:7px;height:7px;border-radius:50%;background:#34D399;
        box-shadow:0 0 9px #34D399;animation:sbcPulse 1.8s ease-in-out infinite; }}
    .hb-title {{ font-family:'Space Grotesk',sans-serif!important;
        font-size:29px;font-weight:700;color:white;margin:0 0 9px;
        letter-spacing:-0.8px;line-height:1.05; }}
    .hb-sub {{ font-size:13px;color:rgba(255,255,255,0.62);margin:0;line-height:1.5; }}
    .hb-sub b {{ color:rgba(255,255,255,0.92);font-weight:700; }}
    .hb-meta {{ display:flex;flex-wrap:wrap;gap:8px;margin:0 0 2px; }}
    .hb-chip {{ display:inline-flex;align-items:center;gap:6px;
        background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.13);
        border-radius:9px;padding:5px 11px;font-size:11px;font-weight:600;color:rgba(255,255,255,0.74); }}
    .hb-chip b {{ color:#fff;font-weight:700; }}
    .nav-lbl {{ font-size:9px;font-weight:800;letter-spacing:0.16em;text-transform:uppercase;
        color:rgba(255,255,255,0.40);margin:3px 0 7px; }}
    .st-key-hdrbanner [data-testid="stVerticalBlock"] {{ gap: 0.5rem !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button {{
        position:relative; z-index:2; overflow:hidden; white-space:nowrap !important;
        color:#CBD3F2 !important; border-radius:9px !important;
        font-size:10px !important; font-weight:700 !important;
        height:32px !important; min-height:32px !important; padding:0 11px !important;
        border:1px solid rgba(255,255,255,0.12) !important; border-top-color:rgba(255,255,255,0.18) !important;
        background:linear-gradient(180deg, rgba(255,255,255,0.085), rgba(255,255,255,0.025)) !important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.10), inset 0 -2px 6px -2px rgba(0,0,0,0.35), 0 4px 12px -8px rgba(8,3,24,0.60) !important;
        transition:transform .16s ease, box-shadow .16s ease, background .16s ease, border-color .16s ease, color .16s ease !important;
    }}
    .st-key-hdrbanner [data-testid="stButton"] > button p {{ white-space:nowrap !important; margin:0 !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button:hover {{
        color:#EAF2FF !important; transform:translateY(-1px) !important;
        border-color:rgba(125,211,252,0.42) !important;
        background:linear-gradient(180deg, rgba(125,211,252,0.15), rgba(255,255,255,0.04)) !important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.16), 0 8px 20px -10px rgba(56,189,248,0.38) !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button:active {{
        transform:translateY(0) !important; box-shadow:inset 0 2px 5px rgba(0,0,0,0.48) !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"] {{
        color:#F4F9FF !important; padding-left:20px !important;
        border:1px solid rgba(56,189,248,0.55) !important; border-top-color:rgba(186,225,255,0.62) !important;
        background:linear-gradient(180deg, rgba(56,189,248,0.30), rgba(59,130,246,0.16)) !important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.22), inset 0 -8px 14px -12px rgba(8,3,24,0.42), 0 8px 22px -10px rgba(56,189,248,0.50) !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"]::before {{
        content:""; position:absolute; left:8px; top:50%; transform:translateY(-50%);
        width:5px; height:5px; border-radius:50%; background:#7DD3FC; box-shadow:0 0 8px rgba(125,211,252,0.9); }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"]:hover {{
        transform:translateY(-1px) !important;
        background:linear-gradient(180deg, rgba(56,189,248,0.36), rgba(59,130,246,0.20)) !important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.24), 0 10px 26px -10px rgba(56,189,248,0.58) !important; }}

    /* keyframes del header */
    @keyframes hbBar {{ 0% {{ background-position:0% 0; }} 100% {{ background-position:220% 0; }} }}
    @keyframes hbShine {{ 0% {{ background-position:0% center; }} 100% {{ background-position:200% center; }} }}
    @keyframes hbPulse {{ 0% {{ box-shadow:0 0 0 0 rgba(52,211,153,0.55); }} 70% {{ box-shadow:0 0 0 6px rgba(52,211,153,0); }} 100% {{ box-shadow:0 0 0 0 rgba(52,211,153,0); }} }}
    @keyframes hbRadar {{ 0% {{ transform:scale(.6); opacity:1; }} 100% {{ transform:scale(2.3); opacity:0; }} }}

    /* ── KPI cards · vidrio oscuro ── */
    .kpi-card {{
        background: linear-gradient(160deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.02) 100%);
        border-radius: 20px;
        padding: 22px 22px 18px;
        box-shadow: 0 20px 44px -18px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.08);
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
        min-height: 148px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border: 1px solid rgba(255,255,255,0.10);
        transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease;
        cursor: default;
    }}
    .kpi-card:hover {{
        transform: translateY(-6px);
        border-color: var(--kc, {COLOR_ACCENT});
        box-shadow: 0 30px 60px -22px rgba(0,0,0,0.8), 0 0 36px -12px var(--kc, {COLOR_ACCENT}), inset 0 1px 0 rgba(255,255,255,0.10);
    }}
    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: var(--kc, {COLOR_PRIMARY});
        box-shadow: 0 0 18px -2px var(--kc, {COLOR_PRIMARY});
    }}
    .kpi-card::after {{
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 120px; height: 120px;
        background: radial-gradient(circle, var(--kc, {COLOR_PRIMARY}), transparent 70%);
        opacity: 0.22;
        border-radius: 50%;
    }}
    .kpi-bg-icon {{
        position: absolute;
        bottom: 12px; right: 16px;
        font-size: 46px;
        opacity: 0.10;
        line-height: 1;
        pointer-events: none;
        z-index: 0;
    }}
    .kpi-label {{ font-size: 10px; color: rgba(255,255,255,0.50); font-weight: 700; text-transform: uppercase; letter-spacing: 0.10em; position: relative; z-index: 1; }}
    .kpi-value {{ font-family:'Space Grotesk',sans-serif!important; font-size: 34px; font-weight: 700; line-height: 1.1; margin: 10px 0 4px; position: relative; z-index: 1; letter-spacing:-0.5px; text-shadow:0 2px 16px rgba(0,0,0,0.4); }}
    .kpi-sub   {{ font-size: 11px; color: rgba(255,255,255,0.42); position: relative; z-index: 1; }}
    .kpi-bar-wrap {{ background: rgba(255,255,255,0.09); border-radius: 99px; height: 5px; margin-top: 12px; overflow: hidden; position: relative; z-index: 1; }}
    .kpi-bar-fill {{ height: 5px; border-radius: 99px; box-shadow:0 0 10px -1px currentColor; }}

    /* ── Section header · banner con degradado de color ── */
    .sec-header {{
        background:
            radial-gradient(ellipse at 12% 35%, rgba(255,255,255,0.18) 0%, transparent 55%),
            radial-gradient(ellipse at 92% 135%, rgba(0,0,0,0.24) 0%, transparent 55%),
            var(--sc, {COLOR_PRIMARY});
        border-radius: 20px;
        padding: 22px 28px;
        margin: 34px 0 18px;
        box-shadow: 0 18px 42px -12px rgba(15,23,42,0.45);
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        gap: 18px;
        border: 1px solid rgba(255,255,255,0.14);
    }}
    .sec-header::before {{
        content: '';
        position: absolute;
        left: -25px; top: -35px;
        width: 130px; height: 130px;
        background: rgba(255,255,255,0.10);
        border-radius: 50%;
    }}
    .sec-header::after {{
        content: '';
        position: absolute;
        right: -35px; bottom: -45px;
        width: 150px; height: 150px;
        background: rgba(255,255,255,0.07);
        border-radius: 50%;
    }}
    .sec-wash {{ display: none; }}
    .sec-icon {{
        width: 56px; height: 56px;
        border-radius: 16px;
        display: flex; align-items: center; justify-content: center;
        font-size: 27px;
        flex-shrink: 0;
        position: relative; z-index: 1;
        background: rgba(255,255,255,0.18) !important;
        border: 1px solid rgba(255,255,255,0.28) !important;
        box-shadow: 0 8px 18px -6px rgba(0,0,0,0.4);
    }}
    .sec-text {{ flex: 1; min-width: 0; position: relative; z-index: 1; }}
    .sec-title {{
        font-size: 19px; font-weight: 800;
        color: white; margin: 0 0 5px 0;
        letter-spacing: -0.4px;
    }}
    .sec-desc {{ font-size: 12px; color: rgba(255,255,255,0.78); margin: 0; line-height: 1.6; }}
    .sec-meta {{
        text-align: center;
        flex-shrink: 0;
        padding: 9px 20px;
        background: rgba(255,255,255,0.96);
        border-radius: 13px;
        border: 1px solid rgba(255,255,255,0.5);
        box-shadow: 0 6px 16px -6px rgba(0,0,0,0.3);
        position: relative; z-index: 1;
    }}
    .sec-meta-val {{
        font-family:'Space Grotesk',sans-serif!important;
        font-size: 24px; font-weight: 700;
        line-height: 1.1; margin-bottom: 2px; letter-spacing:-0.5px;
    }}
    .sec-meta-lab {{
        font-size: 9px; font-weight: 700;
        color: #64748B;
        text-transform: uppercase; letter-spacing: 0.08em;
    }}
    .sec-tag {{
        font-size: 10px; font-weight: 700;
        color: white;
        background: rgba(255,255,255,0.20);
        border: 1px solid rgba(255,255,255,0.35);
        padding: 5px 14px; border-radius: 99px;
        letter-spacing: 0.06em; text-transform: uppercase;
        flex-shrink: 0; align-self: flex-start;
        position: relative; z-index: 1;
    }}

    /* ── Chart mini-headers · vidrio oscuro ── */
    .chart-hdr {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        background: linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.025));
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.10);
        border-left: 4px solid var(--cc, {COLOR_ACCENT});
        box-shadow: 0 8px 22px -10px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.06);
        margin-bottom: 12px;
    }}
    .ch-icon {{ font-size: 18px; line-height: 1; flex-shrink: 0;
        width: 36px; height: 36px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12); }}
    .ch-texts {{ flex: 1; min-width: 0; }}
    .ch-title {{ font-size: 13px; font-weight: 800; color: #F1F4FF; margin: 0 0 1px; letter-spacing:-0.2px; }}
    .ch-sub {{ font-size: 10.5px; color: rgba(255,255,255,0.45); margin: 0; }}
    .ch-tag {{
        margin-left: auto;
        font-size: 9px; font-weight: 700;
        color: var(--cc, {COLOR_ACCENT});
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.14);
        padding: 3px 9px; border-radius: 99px;
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

    /* ── Leaderboard mini-cards (Top/Bottom expertos) ── */
    .lb-card {{
        background: linear-gradient(160deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.015) 100%);
        border-radius: 18px;
        padding: 20px 22px 16px;
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 16px 34px -16px rgba(0,0,0,0.6);
        height: 328px;
        box-sizing: border-box;
        overflow: hidden;
    }}
    .lb-head {{
        display:flex; align-items:center; gap:10px; margin-bottom:14px;
        padding-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.08);
    }}
    .lb-head-icon {{ font-size:17px; }}
    .lb-head-title {{ font-size:13.5px; font-weight:800; color:#F1F4FF; flex:1; letter-spacing:-0.1px; }}
    .lb-head-badge {{ font-size:9px; font-weight:800; text-transform:uppercase; letter-spacing:0.07em; }}
    .lb-row {{
        display: flex; align-items: center; gap: 14px;
        padding: 11px 2px;
        border-bottom: 1px solid rgba(255,255,255,0.055);
    }}
    .lb-row:last-child {{ border-bottom: none; padding-bottom: 2px; }}
    .lb-rank {{
        width: 24px; height: 24px; border-radius: 7px;
        display: flex; align-items: center; justify-content: center;
        font-size: 10px; font-weight: 800; color: white; flex-shrink: 0;
        background: var(--lc, #64748B);
    }}
    .lb-info {{ flex: 1; min-width: 0; }}
    .lb-name {{ font-size: 13px; font-weight: 700; color: #F1F4FF; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .lb-sup {{ font-size: 10.5px; color: rgba(255,255,255,0.42); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }}
    .lb-pct {{ font-size: 14.5px; font-weight: 800; flex-shrink: 0; font-family:'Space Grotesk',sans-serif!important; }}

    /* ── Leyenda custom bajo el donut (evita el recorte de la leyenda nativa de Plotly) ── */
    .donut-legend {{ display:flex; justify-content:center; gap:22px; margin-top:2px; }}
    .dl-item {{ font-size:11.5px; color:rgba(255,255,255,0.60); display:flex; align-items:center; gap:7px; }}
    .dl-item b {{ color:#F1F4FF; font-weight:800; margin-left:3px; }}
    .dl-dot {{ width:9px; height:9px; border-radius:50%; display:inline-block; flex-shrink:0; }}

    /* ── Tarjeta del donut de cumplimiento (mismo look que .lb-card, vía container key) ── */
    .st-key-donut_card {{
        background: linear-gradient(160deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.015) 100%);
        border-radius: 18px;
        padding: 20px 22px 18px;
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 16px 34px -16px rgba(0,0,0,0.6);
        height: 328px;
        box-sizing: border-box;
        overflow: hidden;
    }}
    .st-key-donut_card div[data-testid="stPlotlyChart"] {{
        background: transparent !important; border: none !important;
        box-shadow: none !important; padding: 0 !important;
    }}
    .st-key-donut_card [data-testid="stVerticalBlock"] {{ gap: 0.25rem !important; }}

    /* ── Plotly chart: tarjeta de vidrio oscuro ── */
    div[data-testid="stPlotlyChart"] {{
        background: linear-gradient(160deg, rgba(255,255,255,0.05), rgba(255,255,255,0.015)) !important;
        border-radius: 18px !important;
        box-shadow: 0 16px 38px -16px rgba(0,0,0,0.65) !important;
        border: 1px solid rgba(255,255,255,0.09) !important;
        overflow: hidden !important;
        padding: 10px !important;
    }}

    /* ── Tablas: contenedor de vidrio oscuro + encabezado degradado ── */
    div[data-testid="stDataFrame"] {{
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 16px 38px -16px rgba(0,0,0,0.65) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
    }}
    div[data-testid="stDataFrame"] div[role="columnheader"] {{
        background: linear-gradient(135deg, #1b1240 0%, #0EA5E9 100%) !important;
        color: white !important; font-weight: 700 !important;
    }}
    div[data-testid="stDataFrame"] div[role="columnheader"] span {{
        color: white !important;
    }}
    div[data-testid="stDataFrame"] .ag-root-wrapper {{
        background: rgba(16, 13, 36, 0.90) !important;
        border: none !important;
    }}
    div[data-testid="stDataFrame"] .ag-body-viewport,
    div[data-testid="stDataFrame"] .ag-center-cols-viewport {{
        background: transparent !important;
    }}
    div[data-testid="stDataFrame"] .ag-row {{
        background: rgba(16, 13, 36, 0.85) !important;
        border-color: rgba(255,255,255,0.045) !important;
    }}
    div[data-testid="stDataFrame"] .ag-row-odd {{
        background: rgba(22, 18, 48, 0.80) !important;
    }}
    div[data-testid="stDataFrame"] .ag-row:hover,
    div[data-testid="stDataFrame"] .ag-row-hover {{
        background: rgba(14, 165, 233, 0.10) !important;
    }}
    div[data-testid="stDataFrame"] .ag-cell {{
        color: rgba(225, 232, 250, 0.90) !important;
        border-color: rgba(255,255,255,0.04) !important;
    }}
    div[data-testid="stDataFrame"] .ag-header {{
        background: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.10) !important;
    }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar {{
        width: 6px; height: 6px;
    }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar-track {{
        background: rgba(255,255,255,0.04);
    }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {{
        background: rgba(56,189,248,0.35); border-radius: 99px;
    }}

    /* ══ SIDEBAR BASE · mismo fondo de diseño que el hero (sin grid) ══ */
    section[data-testid="stSidebar"] > div:first-child {{
        background:
            radial-gradient(ellipse 95% 42% at 8% 0%,    rgba(14,165,233,0.30) 0%, transparent 55%),
            radial-gradient(ellipse 90% 42% at 100% 26%, rgba(129,140,248,0.28) 0%, transparent 55%),
            radial-gradient(ellipse 85% 42% at 50% 102%, rgba(52,211,153,0.15) 0%, transparent 55%),
            linear-gradient(160deg, #0B0518 0%, #14082b 45%, #0A0414 100%);
        border-right: 1px solid rgba(255,255,255,0.07);
    }}
    div[data-testid="stSidebarContent"] * {{ color: white !important; }}

    /* ══ Scala arriba + footer anclado al fondo del sidebar ══ */
    [data-testid="stSidebarHeader"] {{ padding-top:0.6rem!important; padding-bottom:0!important; }}
    [data-testid="stSidebarUserContent"] {{ padding-top:0!important; }}
    section[data-testid="stSidebar"] > div:first-child {{
        display:flex!important; flex-direction:column!important; min-height:100vh!important; }}
    [data-testid="stSidebarUserContent"] {{
        flex:1 1 auto!important; display:flex!important; flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] > div {{ flex:1 1 auto!important; display:flex!important; flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:last-of-type {{
        margin-top:auto!important; }}
    div[data-testid="stSidebarContent"] hr {{
        border-color: rgba(255,255,255,0.08);
        margin-top: 4px !important; margin-bottom: 4px !important;
    }}
    div[data-testid="stSidebarContent"] [data-testid="stImage"] img {{
        filter: drop-shadow(0 4px 18px rgba(56,189,248,0.30));
        padding: 0 6px;
    }}
    div[data-testid="collapsedControl"] {{ background:transparent!important; border:none!important; box-shadow:none!important; }}
    div[data-testid="collapsedControl"] * {{ color:transparent!important; background:transparent!important; border:none!important; }}
    div[data-testid="stSidebarContent"] {{ width:100%!important; box-sizing:border-box!important; padding-right:0.75rem!important; }}
    div[data-testid="stSidebarContent"] > div {{ width:100%!important; }}

    /* ══ BRAND CARD ══ */
    @keyframes sbcBar {{
        0%   {{ background-position: 0% 0%;   }}
        100% {{ background-position: 200% 0%; }}
    }}
    @keyframes sbcPulse {{
        0%,100% {{ opacity:1; transform:scale(1);   }}
        50%     {{ opacity:.3; transform:scale(.6); }}
    }}
    .sbc {{
        position: relative;
        border-radius: 20px;
        overflow: hidden;
        margin: 0 0 20px;
        padding: 20px 18px 18px;
        background:
            linear-gradient(145deg,
                rgba(56,189,248,0.12)  0%,
                rgba(129,140,248,0.09) 55%,
                rgba(52,211,153,0.07)  100%),
            rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.12);
    }}
    .sbc-orb {{
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
    }}
    .sbc-orb-1 {{
        width: 140px; height: 140px;
        background: radial-gradient(circle, rgba(56,189,248,0.18) 0%, transparent 70%);
        top: -50px; right: -40px;
    }}
    .sbc-orb-2 {{
        width: 90px; height: 90px;
        background: radial-gradient(circle, rgba(129,140,248,0.16) 0%, transparent 70%);
        bottom: -30px; left: -25px;
    }}
    .sbc-orb-3 {{
        width: 60px; height: 60px;
        background: radial-gradient(circle, rgba(52,211,153,0.14) 0%, transparent 70%);
        top: 50%; right: 12px;
    }}
    .sbc-live {{
        position: absolute;
        top: 14px; right: 14px;
        display: flex; align-items: center; gap: 5px;
        font-size: 8px !important; font-weight: 800 !important;
        color: #34D399 !important;
        background: rgba(52,211,153,0.13);
        border: 1px solid rgba(52,211,153,0.30);
        padding: 3px 9px 3px 7px;
        border-radius: 99px;
        letter-spacing: 0.10em;
        z-index: 2;
    }}
    .sbc-pulse {{
        width: 5px; height: 5px;
        background: #34D399;
        border-radius: 50%;
        display: inline-block;
        animation: sbcPulse 1.8s ease-in-out infinite;
    }}
    .sbc-body {{ position: relative; z-index: 1; text-align: center; }}
    .sbc-logo-wrap {{
        margin-bottom: 10px;
        display: flex; justify-content: center; align-items: center;
    }}
    .sbc-logo-img {{
        max-width: 150px !important;
        height: auto !important;
        filter: drop-shadow(0 4px 14px rgba(56,189,248,0.45)) brightness(1.05);
        display: block;
    }}
    .sbc-name {{
        font-size: 13px !important; font-weight: 700 !important;
        color: rgba(255,255,255,0.88) !important;
        letter-spacing: 0 !important; margin-bottom: 4px !important;
    }}
    .sbc-org {{
        font-size: 10px !important;
        color: rgba(255,255,255,0.35) !important;
        margin-bottom: 16px !important;
    }}
    .sbc-stats {{
        display: flex; align-items: center; justify-content: center;
        background: rgba(0,0,0,0.22);
        border-radius: 12px;
        padding: 10px 8px;
        border: 1px solid rgba(255,255,255,0.07);
    }}
    .sbc-stat {{ flex: 1; text-align: center; }}
    .sbc-sv {{
        display: block;
        font-size: 14px !important; font-weight: 900 !important;
        color: white !important; line-height: 1; margin-bottom: 3px;
    }}
    .sbc-sl {{
        display: block;
        font-size: 8px !important; font-weight: 700 !important;
        color: rgba(255,255,255,0.28) !important;
        letter-spacing: 0.10em; text-transform: uppercase;
    }}
    .sbc-sep {{
        width: 1px; height: 28px;
        background: rgba(255,255,255,0.09);
        flex-shrink: 0;
    }}
    .sbc-bar {{
        position: absolute;
        bottom: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #38BDF8, #818CF8, #34D399, #F59E0B, #38BDF8);
        background-size: 300% 100%;
        animation: sbcBar 4s linear infinite;
    }}

    /* ══ SECTION HEADERS ══ */
    .sbh {{
        display: flex; align-items: center; gap: 10px;
        margin: 24px 0 12px;
    }}
    .sbh-num {{
        font-size: 10px !important; font-weight: 900 !important;
        width: 28px; height: 22px;
        border-radius: 7px;
        border: 1px solid;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0; letter-spacing: 0.04em;
    }}
    .sbh-lbl {{
        font-size: 10px !important; font-weight: 800 !important;
        color: rgba(255,255,255,0.60) !important;
        letter-spacing: 0.14em !important; text-transform: uppercase !important;
        white-space: nowrap !important;
    }}
    .sbh-rule {{
        flex: 1; height: 1px;
        background: rgba(255,255,255,0.08);
    }}

    /* ══ DROPDOWNS ══ */
    div[data-baseweb="popover"] *, div[data-baseweb="menu"] *,
    ul[role="listbox"] *, li[role="option"], li[role="option"] * {{
        color: #1E293B !important;
    }}
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {{ background: #F1F5F9 !important; }}

    /* ══ SELECTBOX ══ */
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] span,
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] div[class*="ValueContainer"] *,
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] input {{ color: white !important; }}
    div[data-testid="stSidebarContent"] input[type="text"] {{ color: white !important; }}

    div[data-testid="stSidebarContent"] label,
    div[data-testid="stSidebarContent"] .stSelectbox label,
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"],
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"] p,
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"] span {{
        font-size: 11px !important; font-weight: 500 !important;
        color: rgba(255,255,255,0.50) !important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput label,
    div[data-testid="stSidebarContent"] .stDateInput [data-testid="stWidgetLabel"],
    div[data-testid="stSidebarContent"] .stDateInput [data-testid="stWidgetLabel"] p {{
        font-size: 11px !important; font-weight: 600 !important;
        color: #38BDF8 !important;
    }}
    div[data-testid="stSidebarContent"] .stSelectbox > div > div,
    div[data-testid="stSidebarContent"] .stSelectbox > label + div > div {{
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 9px !important;
        transition: border-color .18s, box-shadow .18s !important;
    }}
    div[data-testid="stSidebarContent"] .stSelectbox > div > div:hover {{
        border-color: rgba(56,189,248,0.50) !important;
        box-shadow: 0 0 0 3px rgba(56,189,248,0.10) !important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput > div > div > input {{
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 9px !important; color: white !important;
        font-size: 11px !important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput > div > div > input:focus {{
        border-color: rgba(56,189,248,0.50) !important;
        box-shadow: 0 0 0 3px rgba(56,189,248,0.10) !important;
    }}

    /* ══ FOOTER ══ */
    .sbf {{ margin-top: 26px; padding: 0; }}
    .sbf-card {{ position:relative;overflow:hidden;border-radius:16px;padding:14px 14px;
        background:linear-gradient(150deg,rgba(56,189,248,0.10),rgba(129,140,248,0.06));
        border:1px solid rgba(255,255,255,0.10);
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.08); }}
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
    .sbf-name {{ font-size:12px!important;font-weight:700!important;color:rgba(255,255,255,0.92)!important;margin-bottom:3px!important; }}
    .sbf-role {{ font-size:10px!important;color:rgba(255,255,255,0.42)!important;line-height:1.3; }}
    .sbf-credit {{ display:flex;align-items:center;justify-content:center;gap:5px;
        margin-top:12px;font-size:9px!important;font-weight:600!important;
        color:rgba(255,255,255,0.30)!important;text-align:center;letter-spacing:0.06em; }}
    .sbf-spark {{ font-size:10px; }}
</style>
""", unsafe_allow_html=True)

_ui.inject_css()

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

# Orden cronológico real de períodos (evita mezcla de meses en modo Día)
_periodo_sorted = (
    dff.groupby("_periodo")["Fecha"].min()
    .sort_values()
    .index.tolist()
)
_periodo_rank = {p: i for i, p in enumerate(_periodo_sorted)}

# Columna de período por granularidad, para que cada gráfica pueda ofrecer su
# propio selector "Granularidad" (filtro interno) sin depender solo del filtro
# global "Agrupar por" de la barra lateral.
_PERIODO_COLS = {"Día": "FechaStr", "Semana": "Semana", "Mes": "Mes"}
_GRANULARIDADES = list(_PERIODO_COLS)

def _periodo_rank_de(col: str):
    orden = dff.groupby(col)["Fecha"].min().sort_values().index.tolist()
    return orden, {p: i for i, p in enumerate(orden)}

_VENTANAS = {"Todo el período": None, "Últimos 15": 15, "Últimos 30": 30, "Últimos 60": 60}

# ─────────────────────────────────────────────
# MÉTRICAS GLOBALES
# ─────────────────────────────────────────────
dff_validos = dff[dff["prog_s"] > 0]
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
filtro_txt = (f"{'Detalle por supervisor y experto.' if camp_sel == 'Todas' else camp_sel}")
_home_pg = st.Page("home.py", title="Inicio", icon="🏠", default=True)
_ocu_pg  = st.Page("pages/2_Ocupacion.py", title="Ocupación", icon="📊")
_tip_pg  = st.Page("pages/4_Tipificacion.py", title="Tipificación", icon="🏷️")
_nov_pg  = st.Page("pages/3_Novedades.py", title="Novedades", icon="📢")

_ui.top_banner(
    "ADHERENCIA", "Centro de Control",
    "Cumplimiento de horario, novedades y riesgo por equipo.",
    "PERÍODO ANALIZADO", rango,
)
_ui.module_nav("adh", [
    ("home", "⌂  Inicio", _home_pg),
    ("adh", "▤  Adherencia", None),
    ("ocu", "◆  Ocupación", _ocu_pg),
    ("tip", "◇  Tipificación", _tip_pg),
    ("nov", "●  Novedades", _nov_pg),
])

# ─────────────────────────────────────────────
# KPIs GLOBALES
# ─────────────────────────────────────────────
_progress_track = f"<div class='ebi-overview-track'><i style='width:{min(max(adh_global * 100, 0), 100):.1f}%'></i></div>"
_ui.overview_kpis([
    ("🎯", "Adherencia", f"{adh_global:.1%}", "Meta: 90%", adh_color, _progress_track),
    ("👥", "Expertos", _ui.number_es(total_agentes), f"{_ui.number_es(total_registros)} registros", COLOR_ACCENT, ""),
    ("✅", "Llegada a tiempo", f"{pct_tiempo:.1f}%".replace(".", ","), f'{_ui.number_es(llegada_counts.get("Llegada a tiempo", 0))} registros', COLOR_SUCCESS, ""),
    ("⏰", "Llegadas tarde", f"{pct_tarde:.1f}%".replace(".", ","), f'{_ui.number_es(llegada_counts.get("Llegada tarde", 0))} registros', COLOR_WARNING, ""),
    ("🚨", "Ausentes", f"{pct_ausentes:.1f}%".replace(".", ","), f'{_ui.number_es(llegada_counts.get("Ausente", 0))} registros', COLOR_DANGER, ""),
])

# ─────────────────────────────────────────────
# GRÁFICAS POR SUPERVISOR (TENDENCIA)
# ─────────────────────────────────────────────
_ui.section("A", "MONITOREO")

sup_lista = sorted(dff_validos["Supervisor"].dropna().unique())
colores_sup = {s: SUPERVISOR_COLORS[i % len(SUPERVISOR_COLORS)] for i, s in enumerate(sup_lista)}

_ui.panel_title("📉", "Tendencia por Supervisor", "Comparación de la evolución de adherencia de cada supervisor a lo largo del período.", "EVOLUCIÓN")
_c_tsup1, _c_tsup2, _c_tsup3 = st.columns([2.2, .9, .9])
with _c_tsup1:
    _sup_filtro = _ui.multiselect_all("Supervisor", sup_lista, "wfm_v1_tend_sup")
with _c_tsup2:
    _gran_tsup = st.selectbox("Granularidad", _GRANULARIDADES, index=_GRANULARIDADES.index(tipo_periodo), key="wfm_v1_tend_sup_gran")
with _c_tsup3:
    _ventana_tsup = st.selectbox("Mostrar", list(_VENTANAS), key="wfm_v1_tend_sup_ventana")
_ui.selected_chips(_sup_filtro)

_col_tsup = _PERIODO_COLS[_gran_tsup]
_orden_tsup, _rank_tsup = _periodo_rank_de(_col_tsup)
tend_sup = (
    dff_validos
    .groupby([_col_tsup, "Supervisor"])[["adh_s","prog_s"]]
    .sum()
    .reset_index()
    .rename(columns={_col_tsup: "_periodo"})
)
tend_sup["ADH"] = (tend_sup["adh_s"] / tend_sup["prog_s"]).where(tend_sup["prog_s"] > 0, 0)
tend_sup = tend_sup.drop(columns=["adh_s","prog_s"])
tend_sup["_ord"] = tend_sup["_periodo"].map(_rank_tsup)
tend_sup = tend_sup.sort_values(["Supervisor","_ord"]).drop(columns="_ord")

fig_sup = go.Figure()
fig_sup.add_hrect(y0=0.60, y1=0.80, fillcolor="rgba(239,68,68,0.03)",  layer="below", line_width=0)
fig_sup.add_hrect(y0=0.80, y1=0.90, fillcolor="rgba(245,158,11,0.04)", layer="below", line_width=0)
fig_sup.add_hrect(y0=0.90, y1=1.05, fillcolor="rgba(16,185,129,0.04)", layer="below", line_width=0)

for sup in _sup_filtro:
    sub = tend_sup[tend_sup["Supervisor"] == sup]
    nombre_corto = " ".join(sup.split()[:2])
    fig_sup.add_trace(go.Scatter(
        x=sub["_periodo"], y=sub["ADH"],
        name=nombre_corto,
        mode="lines+markers",
        line=dict(color=colores_sup[sup], width=2, shape="spline"),
        marker=dict(size=6, color="white", line=dict(color=colores_sup[sup], width=2)),
        hovertemplate=f"<b>{nombre_corto}</b><br>%{{x}}: %{{y:.1%}}<extra></extra>"
    ))
fig_sup.add_hline(y=0.90, line_dash="dot", line_color="rgba(100,116,139,0.6)", line_width=1.5,
                  annotation_text="Meta 90%", annotation_position="top right",
                  annotation_font=dict(color="rgba(255,255,255,0.6)", size=10, family="Inter"))

_periodos_sup   = _orden_tsup
_n_sup_per      = len(_periodos_sup)
_ventana_n_sup  = _VENTANAS[_ventana_tsup]
_ini_sup        = max(-0.5, _n_sup_per - _ventana_n_sup - 0.5) if _ventana_n_sup else -0.5
fig_sup.update_layout(
    height=390, margin=dict(l=0, r=0, t=10, b=40),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(
        tickformat=".0%", gridcolor="rgba(255,255,255,0.08)",
        range=[0.60, 1.05], dtick=0.05,
        tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"),
        zeroline=False
    ),
    xaxis=dict(
        gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"),
        range=[_ini_sup, _n_sup_per - 0.5],
        rangeslider=dict(visible=True, thickness=0.08, bgcolor="rgba(255,255,255,0.05)"),
        tickangle=-30, showgrid=False
    ),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
        font=dict(size=10, family="Inter"),
        itemsizing="constant", bgcolor="rgba(0,0,0,0)"
    ),
    font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)"), showlegend=False
)
st.plotly_chart(fig_sup, use_container_width=True)

# ─────────────────────────────────────────────
# COMPARATIVO POR SUPERVISOR
# ─────────────────────────────────────────────
_ui.panel_title("👥", "Comparativo por Supervisor", "Adherencia consolidada por equipo: verde ≥ 90%, amarillo ≥ 80%, rojo < 80%.", "REAL vs META")
_sup_filtro_b = _ui.multiselect_all("Supervisor", sup_lista, "wfm_v1_cmp_sup")
_ui.selected_chips(_sup_filtro_b)

sup_stats = (
    dff_validos[dff_validos["Supervisor"].isin(_sup_filtro_b)].groupby("Supervisor")
    .agg(adh_s=("adh_s", "sum"), prog_s=("prog_s", "sum"), Agentes=("Nombre", "nunique"))
    .reset_index()
)
sup_stats["ADH"] = (sup_stats["adh_s"] / sup_stats["prog_s"]).where(sup_stats["prog_s"] > 0, 0)
sup_stats = sup_stats.drop(columns=["adh_s", "prog_s"]).sort_values("ADH", ascending=True)
sup_stats["Supervisor"] = sup_stats["Supervisor"].apply(lambda n: " ".join(n.split()[:2]))
_sup_stats_idx = sup_stats.set_index("Supervisor")
_ui.comparison_bar(_sup_stats_idx["ADH"], "Adherencia", lambda v: f"{v:.1%}", meta=0.90, color_fn=_adh_color,
                   extra=_sup_stats_idx["Agentes"], extra_label="Agentes", tickformat=".0%",
                   height=max(280, len(sup_stats) * 36 + 60))

# ─────────────────────────────────────────────
# SEMANA VS. SEMANA
# ─────────────────────────────────────────────
_semanas_orden = dff_validos.groupby("Semana")["Fecha"].min().sort_values().index.tolist()
if len(_semanas_orden) >= 2:
    _sem_actual, _sem_previa = _semanas_orden[-1], _semanas_orden[-2]
    _wow = (
        dff_validos[dff_validos["Semana"].isin([_sem_actual, _sem_previa])]
        .groupby(["Semana", "Supervisor"])[["adh_s", "prog_s"]].sum().reset_index()
    )
    _wow["ADH"] = (_wow["adh_s"] / _wow["prog_s"]).where(_wow["prog_s"] > 0, 0)
    _piv_wow = _wow.pivot(index="Supervisor", columns="Semana", values="ADH").dropna(subset=[_sem_actual, _sem_previa])

    if not _piv_wow.empty:
        _piv_wow["Delta"] = _piv_wow[_sem_actual] - _piv_wow[_sem_previa]
        _piv_wow = _piv_wow.sort_values("Delta", ascending=True)

        _ui.panel_title("📆", "Semana vs. Semana", f"Variación de adherencia por supervisor: {_sem_previa} → {_sem_actual}.", "TENDENCIA")
        _wow_colors = [COLOR_SUCCESS if v >= 0 else COLOR_DANGER for v in _piv_wow["Delta"]]
        _wow_names = [" ".join(s.split()[:2]) for s in _piv_wow.index]
        fig_wow = go.Figure(go.Bar(
            x=_piv_wow["Delta"], y=_wow_names, orientation="h",
            marker=dict(color=_wow_colors, opacity=0.92, line=dict(width=0), cornerradius=6),
            width=0.55,
            text=[f"{v:+.1%}" for v in _piv_wow["Delta"]], textposition="outside", cliponaxis=False,
            textfont=dict(size=11, color="rgba(255,255,255,0.78)", family="Space Grotesk, sans-serif"),
            customdata=np.column_stack([_piv_wow[_sem_previa], _piv_wow[_sem_actual]]),
            hovertemplate=(f"<b>%{{y}}</b><br>{_sem_previa}: %{{customdata[0]:.1%}}<br>"
                           f"{_sem_actual}: %{{customdata[1]:.1%}}<br>Variación: %{{x:+.1%}}<extra></extra>"),
        ))
        fig_wow.add_vline(x=0, line_color="rgba(255,255,255,0.25)", line_width=1)
        _wow_max = max(float(_piv_wow["Delta"].abs().max()), 0.02) * 1.35
        fig_wow.update_layout(
            height=max(260, len(_piv_wow) * 34 + 60), margin=dict(l=0, r=60, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[-_wow_max, _wow_max], tickformat="+.0%", gridcolor="rgba(255,255,255,0.045)",
                       tickfont=dict(size=9, family="Inter", color="rgba(255,255,255,0.32)"), zeroline=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=10.5, family="Inter", color="rgba(255,255,255,0.72)")),
            showlegend=False, font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)"),
        )
        st.plotly_chart(fig_wow, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────
# COMPARATIVO POR SUPERVISOR
# ─────────────────────────────────────────────
_ui.section("B", "PRODUCCIÓN")

# ─────────────────────────────────────────────
# COMPARATIVO POR EXPERTO
# ─────────────────────────────────────────────
exp_stats = (
    dff_validos.groupby("Nombre")
    .agg(adh_s=("adh_s", "sum"), prog_s=("prog_s", "sum"), Registros=("adh_s", "size"))
    .reset_index()
)
exp_stats["ADH"] = (exp_stats["adh_s"] / exp_stats["prog_s"]).where(exp_stats["prog_s"] > 0, 0)
_sup_counts = dff_validos.groupby(["Nombre", "Supervisor"]).size().reset_index(name="_n")
_sup_moda = _sup_counts.sort_values("_n", ascending=False).drop_duplicates("Nombre")[["Nombre", "Supervisor"]]
exp_stats = exp_stats.merge(_sup_moda, on="Nombre", how="left")
exp_stats["Supervisor"] = exp_stats["Supervisor"].fillna("-")
exp_stats = exp_stats.drop(columns=["adh_s", "prog_s"]).sort_values("ADH", ascending=True)
n_exp = len(exp_stats)
_exp_tag = sup_sel if sup_sel != "Todos" else "Todos los equipos"

_ui.panel_title("🧑‍💻", "Comparativo por Experto", f"Adherencia individual de cada experto: verde ≥ 90%, amarillo ≥ 80%, rojo < 80% · {n_exp} expertos · {_exp_tag}", "BARRAS")
_c_exp1, _c_exp2 = st.columns([2.4, 1])
with _c_exp1:
    _sup_filtro_exp = _ui.multiselect_all("Supervisor", sorted(exp_stats["Supervisor"].unique()), "wfm_v1_exp_sup")
with _c_exp2:
    _orden_exp = st.selectbox("Ordenar", ["Mejores arriba", "En riesgo arriba"], key="wfm_v1_exp_orden")

_exp_idx = exp_stats.set_index("Nombre")
_exp_idx = _exp_idx[_exp_idx["Supervisor"].isin(_sup_filtro_exp)].sort_values("ADH", ascending=(_orden_exp == "Mejores arriba"))
with st.container(height=520, border=False):
    _ui.comparison_bar(_exp_idx["ADH"], "Adherencia", lambda v: f"{v:.1%}", meta=0.90, color_fn=_adh_color,
                        extra=_exp_idx["Supervisor"], extra_label="Supervisor", tickformat=".0%")

# ─────────────────────────────────────────────
# TENDENCIA + DISTRIBUCIÓN LLEGADAS
# ─────────────────────────────────────────────
_ui.section("C", "ANÁLISIS")
_ui.panel_title("📈", "Tendencia de Adherencia", "Evolución de la adherencia del equipo y distribución de tipos de llegada en el período.", f"{adh_global:.1%} global")
_c_tend1, _c_tend2 = st.columns([1, 1])
with _c_tend1:
    _gran_tend = st.selectbox("Granularidad", _GRANULARIDADES, index=_GRANULARIDADES.index(tipo_periodo), key="wfm_v1_tend_gran")
with _c_tend2:
    _ventana_tend = st.selectbox("Mostrar", list(_VENTANAS), key="wfm_v1_tend_ventana")

_col_tend = _PERIODO_COLS[_gran_tend]
_orden_tend, _rank_tend = _periodo_rank_de(_col_tend)
tend = (
    dff_validos
    .groupby(_col_tend)[["adh_s","prog_s"]]
    .sum()
    .reset_index()
    .rename(columns={_col_tend: "_periodo"})
)
tend["ADH"] = (tend["adh_s"] / tend["prog_s"]).where(tend["prog_s"] > 0, 0)
tend = tend.drop(columns=["adh_s","prog_s"])
tend["_ord"] = tend["_periodo"].map(_rank_tend)
tend = tend.sort_values("_ord").drop(columns="_ord")

# Las visualizaciones se leen a ancho completo; no quedan gráficos a media página.
c1, c2 = st.container(), st.container()
with c1:
    fig_tend = go.Figure()
    fig_tend.add_hrect(y0=0.60, y1=0.80, fillcolor="rgba(239,68,68,0.04)",   layer="below", line_width=0)
    fig_tend.add_hrect(y0=0.80, y1=0.90, fillcolor="rgba(245,158,11,0.05)",  layer="below", line_width=0)
    fig_tend.add_hrect(y0=0.90, y1=1.01, fillcolor="rgba(16,185,129,0.05)",  layer="below", line_width=0)
    fig_tend.add_trace(go.Scatter(
        x=tend["_periodo"], y=tend["ADH"],
        mode="lines",
        line=dict(color="rgba(14,165,233,0.20)", width=10, shape="spline"),
        showlegend=False, hoverinfo="skip"
    ))
    fig_tend.add_trace(go.Scatter(
        x=tend["_periodo"], y=tend["ADH"],
        mode="lines+markers+text",
        line=dict(color=COLOR_ACCENT, width=2.5, shape="spline"),
        marker=dict(size=10, color="white", line=dict(color=COLOR_ACCENT, width=2.5)),
        text=tend["ADH"].apply(lambda x: f"{x:.0%}"),
        textposition="top center",
        textfont=dict(size=9, color="#CBD3F2", family="Inter", weight=700),
        hovertemplate="%{x}<br><b>ADH: %{y:.1%}</b><extra></extra>"
    ))
    fig_tend.add_hline(y=0.90, line_dash="dot", line_color=COLOR_SUCCESS, line_width=1.5,
                       annotation_text="Meta 90%", annotation_position="top right",
                       annotation_font=dict(color=COLOR_SUCCESS, size=10, family="Inter"))
    _n_tend = len(tend)
    _ventana_n_tend = _VENTANAS[_ventana_tend]
    _ini_tend = max(-0.5, _n_tend - _ventana_n_tend - 0.5) if _ventana_n_tend else -0.5
    fig_tend.update_layout(
        height=370, margin=dict(l=0, r=10, t=24, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            tickformat=".0%", gridcolor="rgba(255,255,255,0.08)",
            range=[0.60, 1.01], dtick=0.04,
            tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"),
            zeroline=False, showgrid=True
        ),
        xaxis=dict(
            gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.62)"),
            range=[_ini_tend, _n_tend - 0.5],
            rangeslider=dict(visible=True, thickness=0.08, bgcolor="rgba(255,255,255,0.05)"),
            tickangle=-30, showgrid=False
        ),
        font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)"), showlegend=False
    )
    st.plotly_chart(fig_tend, use_container_width=True)

with c2:
    color_map = {
        "Llegada a tiempo": COLOR_SUCCESS,
        "Llegada antes":    COLOR_ACCENT,
        "Llegada tarde":    COLOR_WARNING,
        "Ausente":          COLOR_DANGER
    }
    llegadas_plot = dff["Validador Llegada"].value_counts().reset_index()
    llegadas_plot.columns = ["Estado","Cantidad"]
    # Solo los 4 tipos de llegada del título; otros valores de esta columna
    # (novedades como incapacidad o licencia) no son "tipos de llegada" y con
    # etiqueta afuera del donut se veían como texto amontonado sin aportar nada.
    llegadas_plot = llegadas_plot[llegadas_plot["Estado"].isin(color_map)]
    lp_labels = llegadas_plot["Estado"].tolist()
    lp_values = llegadas_plot["Cantidad"].tolist()
    lp_colors = [color_map[l] for l in lp_labels]

    _ui.donut(lp_labels, lp_values, lp_colors, f"{pct_tiempo:.1f}%", "a tiempo", height=370)

# ─────────────────────────────────────────────
# DETALLE POR AGENTE
# ─────────────────────────────────────────────
_ui.section("D", "SEGUIMIENTO OPERATIVO")
_ui.panel_title("🔍", "Detalle por Agente", "Adherencia, planificación y excesos por experto. Filtra por agente desde la barra lateral.", "TABLAS")

# Matrices operativas: la primera capa es visual y el detalle queda bajo demanda.
_matrix_adh = dff_validos[["Fecha", "Supervisor", "Nombre", "adh_s", "prog_s", "Validador Llegada"]].copy()
_matrix_adh["Adherencia"] = (_matrix_adh["adh_s"] / _matrix_adh["prog_s"]).clip(0, 1)
_matrix_adh["Llegada a tiempo"] = _matrix_adh["Validador Llegada"].eq("Llegada a tiempo").astype(float)
_matrix_adh["Asistió a turno"] = _matrix_adh["Validador Llegada"].ne("Ausente").astype(float)
_MATRIX_METRICS = {"Adherencia": "Adherencia", "Llegada a tiempo": "Llegada a tiempo", "Asistió a turno": "Asistió a turno"}
_MATRIX_BINARIOS = {"Llegada a tiempo", "Asistió a turno"}
_ui.panel_title("▦", "Matriz diaria por Supervisor", "Porcentaje diario con alerta <90 % y criticidad <70 %.", "HEATMAP")
_ui.percentage_matrix(_matrix_adh, "Supervisor", "Fecha", _MATRIX_METRICS, "adh_matrix_sup", "Supervisor", binary_metrics=_MATRIX_BINARIOS)
_ui.panel_title("👤", "Matriz diaria por Experto", "Selecciona un supervisor para analizar el riesgo individual.", "SEGUIMIENTO")
_SIN_SUPERVISOR = "— Selecciona un supervisor —"
_matrix_supervisor = st.selectbox(
    "Supervisor para matriz de expertos",
    [_SIN_SUPERVISOR] + sorted(_matrix_adh["Supervisor"].dropna().unique()),
    key="adh_matrix_agent_supervisor",
)
if _matrix_supervisor == _SIN_SUPERVISOR:
    st.info("Selecciona un supervisor para ver la matriz diaria de sus expertos.")
else:
    _matrix_agents = _matrix_adh[_matrix_adh["Supervisor"] == _matrix_supervisor]
    _ui.percentage_matrix(_matrix_agents, "Nombre", "Fecha", _MATRIX_METRICS, "adh_matrix_agent", "Experto", binary_metrics=_MATRIX_BINARIOS)

def seg_a_hhmmss(s):
    if pd.isna(s) or s <= 0:
        return "-"
    s = int(s)
    h, r = divmod(s, 3600)
    m, sec = divmod(r, 60)
    return f"{h}:{m:02d}:{sec:02d}"

def seg_a_hhmmss_vec(seconds):
    """Versión vectorizada de seg_a_hhmmss para columnas completas (evita apply() celda por celda)."""
    s = pd.to_numeric(seconds, errors="coerce")
    valido = s.notna() & (s > 0)
    out = pd.Series("-", index=s.index, dtype=object)
    si = s[valido].astype(int)
    h = si // 3600
    m = (si % 3600) // 60
    sec = si % 60
    out.loc[valido] = h.astype(str) + ":" + m.astype(str).str.zfill(2) + ":" + sec.astype(str).str.zfill(2)
    return out

def fmt_td_vec(series):
    """Formatea una columna de timedelta a h:mm:ss, vectorizado (equivalente a .apply(_fmt_td))."""
    secs = pd.to_timedelta(series, errors="coerce").dt.total_seconds()
    return seg_a_hhmmss_vec(secs)

def fmt_plan(v):
    if pd.isna(v):
        return "-"
    s = str(v).strip()
    if hasattr(v, "total_seconds"):
        return seg_a_hhmmss(v.total_seconds())
    return s

def fmt_plan_vec(series):
    """Vectoriza fmt_plan cuando la columna completa es timedelta (caso común de
    Turno/Break/Lunch); si no, cae exactamente al mismo .apply(fmt_plan) de siempre."""
    if pd.api.types.is_timedelta64_dtype(series):
        return fmt_td_vec(series)
    return series.apply(fmt_plan)

# ── Panel de incidencias: casos puntuales, no promedios ──
_ui.section("E", "RESUMEN")
_inc_worst = dff_validos.dropna(subset=["ADH_pct"]).sort_values("ADH_pct", ascending=True).head(8)
_inc_items = [
    {
        "name": r["Nombre"], "sup": r["Supervisor"], "date": r["Fecha"].strftime("%d/%m/%Y"),
        "value": f"{float(r['ADH_pct']):.0%}", "label": "Adherencia",
        "severity": "critical" if float(r["ADH_pct"]) < 0.70 else "warning",
        "foot": [("Llegada", r["Validador Llegada"]), ("Campaña", r["Campana"])],
    }
    for _, r in _inc_worst.iterrows()
]
_ui.panel_title("🚨", "Panel de Incidencias", "Los casos puntuales de menor adherencia en el período filtrado — el detalle exacto que revisar, no solo el promedio.", f"{len(_inc_items)} casos")
_ui.incident_list(_inc_items, scroll_height=420)

# ── Tabla 1: Resumen General ──────────────────
st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)
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
t1["Retardo"]           = np.where(t1["Validador Llegada"] == "Llegada tarde", "Sí", "No")
t1["Ausencia"]          = np.where(t1["Validador Llegada"] == "Ausente", "Sí", "No")
t1["Tiempo de retardo"] = seg_a_hhmmss_vec(t1["tard_s"]).where(t1["Retardo"] == "Sí", "-")
t1["T. Programado"]     = seg_a_hhmmss_vec(t1["prog_s"])
t1["Fuera de ADH"]      = seg_a_hhmmss_vec((t1["prog_s"] - t1["adh_s"]).clip(lower=0))
t1["ADH Aplicada"]      = seg_a_hhmmss_vec(t1["adh_s"])
t1["Adherencia %"]      = t1["ADH_pct"].fillna(0) * 100

t1_show = (
    t1.rename(columns={"Nombre": "Agente", "Campana": "Campaña"})[
        ["Fecha", "Agente", "Supervisor", "Campaña", "Adherencia %",
         "Retardo", "Tiempo de retardo", "Ausencia",
         "T. Programado", "Fuera de ADH", "ADH Aplicada"]
    ].sort_values(["Fecha", "Agente"]).reset_index(drop=True)
)
df_descarga(
    t1_show,
    "detalle_adherencia.xlsx",
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

# ── Distribución y patrones de adherencia ──
_ui.section("F", "PATRONES")
_ui.panel_title("📶", "Distribución y Patrones de Adherencia", "Cómo se reparten los expertos por rango de adherencia y qué días de la semana concentran el mayor riesgo.", f"{n_exp} expertos")

c_hist, c_dia = st.container(), st.container()
with c_hist:
    _sup_filtro_hist = _ui.multiselect_all("Supervisor", sorted(exp_stats["Supervisor"].unique()), "wfm_v1_hist_sup")
    _bins = [-0.01, 0.70, 0.80, 0.90, 0.95, 10]
    _labels = ["<70%", "70-79%", "80-89%", "90-94%", "≥95%"]
    _bucket_colors = [COLOR_DANGER, COLOR_DANGER, COLOR_WARNING, COLOR_SUCCESS, COLOR_SUCCESS]
    _exp_stats_hist = exp_stats[exp_stats["Supervisor"].isin(_sup_filtro_hist)]
    hist_counts = pd.cut(_exp_stats_hist["ADH"], bins=_bins, labels=_labels).value_counts().reindex(_labels).fillna(0).astype(int)
    fig_hist = go.Figure(go.Bar(
        x=_labels, y=hist_counts.values,
        marker=dict(color=_bucket_colors, opacity=0.92, line=dict(width=0), cornerradius=6),
        width=0.55,
        text=hist_counts.values, textposition="outside", cliponaxis=False,
        textfont=dict(size=11, color="rgba(255,255,255,0.78)", family="Space Grotesk, sans-serif"),
        hovertemplate="<b>%{x}</b><br>%{y} expertos<extra></extra>"
    ))
    fig_hist.update_layout(
        height=330, margin=dict(l=0, r=0, t=26, b=0), bargap=0.42,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.55)"), fixedrange=True),
        yaxis=dict(gridcolor="rgba(255,255,255,0.045)", tickfont=dict(size=9, family="Inter", color="rgba(255,255,255,0.32)"), fixedrange=True),
        showlegend=False, font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)")
    )
    st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

with c_dia:
    _comparar_dia = st.selectbox("Comparar", ["General", "Por Supervisor"], key="wfm_v1_dia_comparar")
    _dia_map = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
                "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
    _dia_order = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    _base_dia = dff_validos.assign(DiaEs=dff_validos["DiaSemana"].map(_dia_map))

    if _comparar_dia == "General":
        _dia_sum = _base_dia.groupby("DiaEs")[["adh_s","prog_s"]].sum()
        dia_stats = (
            (_dia_sum["adh_s"] / _dia_sum["prog_s"]).where(_dia_sum["prog_s"] > 0, 0)
            .reindex(_dia_order)
            .dropna()
        )
        dia_colors = [COLOR_SUCCESS if v >= 0.90 else (COLOR_WARNING if v >= 0.80 else COLOR_DANGER) for v in dia_stats.values]
        fig_dia = go.Figure(go.Bar(
            x=dia_stats.index, y=dia_stats.values,
            marker=dict(color=dia_colors, opacity=0.92, line=dict(width=0), cornerradius=6),
            width=0.55,
            text=[f"{v:.1%}" for v in dia_stats.values], textposition="outside", cliponaxis=False,
            textfont=dict(size=11, color="rgba(255,255,255,0.78)", family="Space Grotesk, sans-serif"),
            hovertemplate="<b>%{x}</b><br>Adherencia: %{y:.1%}<extra></extra>"
        ))
        fig_dia.add_hline(y=0.90, line_dash="dot", line_color="rgba(125,211,252,0.75)", line_width=1.5,
                          annotation_text="Meta 90%",
                          annotation_font=dict(size=10, color="#7DD3FC"),
                          annotation_position="top left")
        fig_dia.update_layout(
            height=330, margin=dict(l=0, r=0, t=26, b=0), bargap=0.42,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.55)"), fixedrange=True),
            yaxis=dict(tickformat=".0%", range=[0, 1.10], gridcolor="rgba(255,255,255,0.045)",
                       tickfont=dict(size=9, family="Inter", color="rgba(255,255,255,0.32)"), fixedrange=True),
            showlegend=False, font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)")
        )
        st.plotly_chart(fig_dia, use_container_width=True, config={"displayModeBar": False})
    else:
        _dia_sup = _base_dia.groupby(["Supervisor", "DiaEs"])[["adh_s","prog_s"]].sum().reset_index()
        _dia_sup["ADH"] = (_dia_sup["adh_s"] / _dia_sup["prog_s"]).where(_dia_sup["prog_s"] > 0, 0)
        _piv_dia = _dia_sup.pivot(index="Supervisor", columns="DiaEs", values="ADH").reindex(columns=_dia_order)
        _z_dia = _piv_dia.to_numpy(dtype=float)
        fig_dia = go.Figure(go.Heatmap(
            z=_z_dia, x=_piv_dia.columns, y=_piv_dia.index, zmin=0, zmax=1,
            colorscale=[[0, "#F43F5E"], [.7999, "#F43F5E"], [.80, "#F59E0B"], [.8999, "#F59E0B"], [.90, "#10B981"], [1, "#10B981"]],
            text=np.where(np.isnan(_z_dia), "—", np.vectorize(lambda v: f"{v:.0%}")(np.nan_to_num(_z_dia))),
            texttemplate="%{text}", textfont=dict(size=9.5, family="Inter", color="rgba(255,255,255,.94)"),
            xgap=3, ygap=3, showscale=False,
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1%}<extra></extra>",
        ))
        fig_dia.update_layout(
            height=max(280, len(_piv_dia) * 30 + 90), margin=dict(l=150, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
            font=dict(family="Inter"),
            xaxis=dict(showgrid=False, side="top", tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.55)")),
            yaxis=dict(showgrid=False, tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,0.70)")),
        )
        st.caption("Verde ≥ 90 % · amarillo 80–89,9 % · rojo < 80 %")
        st.plotly_chart(fig_dia, use_container_width=True, config={"displayModeBar": False})

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
    t2[c] = fmt_plan_vec(t2[c])

df_descarga(
    t2.sort_values(["Fecha", "Agente"]).reset_index(drop=True),
    "planificacion.xlsx",
    use_container_width=True, hide_index=True, height=350
)

# ── Comparativo por campaña y excesos ──
_ui.section("G", "CAMPAÑAS")
_ui.panel_title("🗂️", "Campañas y Excesos", "Adherencia consolidada por campaña y dónde se concentra el tiempo fuera de programación.", f'{dff_validos["Campana"].nunique()} campañas')

c_camp, c_exc = st.container(), st.container()
with c_camp:
    _orden_camp = st.selectbox("Ordenar", ["Mejores arriba", "En riesgo arriba"], key="wfm_v1_camp_orden")
    camp_stats = (
        dff_validos.groupby("Campana")
        .agg(adh_s=("adh_s", "sum"), prog_s=("prog_s", "sum"), Agentes=("Nombre", "nunique"))
        .reset_index()
    )
    camp_stats["ADH"] = (camp_stats["adh_s"] / camp_stats["prog_s"]).where(camp_stats["prog_s"] > 0, 0)
    camp_stats = camp_stats.drop(columns=["adh_s", "prog_s"]).sort_values("ADH", ascending=(_orden_camp == "Mejores arriba"))
    _camp_idx = camp_stats.set_index("Campana")
    _ui.comparison_bar(_camp_idx["ADH"], "Adherencia", lambda v: f"{v:.1%}", meta=0.90, color_fn=_adh_color,
                        extra=_camp_idx["Agentes"], extra_label="Agentes", tickformat=".0%")

with c_exc:
    _camp_filtro_exc = _ui.multiselect_all("Campaña", sorted(dff["Campana"].dropna().unique()), "wfm_v1_exc_camp")
    exc_tipo_cols = ["Exceso Almuerzo", "Exceso Descanso", "Exceso Seguimiento",
                     "Exceso Toilette", "Exceso Entrenamiento", "Exceso Feedback", "Exceso Calidad"]
    exc_tipo_min  = [c + "_min" for c in exc_tipo_cols]
    exc_tipo_disp = [c for c in exc_tipo_min if c in dff.columns]
    _dff_exc      = dff[dff["Campana"].isin(_camp_filtro_exc)]
    exc_totales   = _dff_exc[exc_tipo_disp].sum().sort_values(ascending=True)
    exc_labels    = [c.replace("_min", "").replace("Exceso ", "") for c in exc_totales.index]
    _serie_exc    = pd.Series((exc_totales.values / 60), index=exc_labels)
    _ui.comparison_bar(_serie_exc, "Horas", lambda v: seg_a_hhmmss(v * 3600), color_fija="#FB7185")

# ── Pareto de excesos por experto (80/20) ──
_ui.panel_title("📐", "Pareto de Excesos por Experto", "Qué expertos concentran la mayor parte del tiempo fuera de programación.", "80/20")
_exc_por_agente = _dff_exc.groupby("Nombre")[exc_tipo_disp].sum().sum(axis=1).sort_values(ascending=False)
_exc_por_agente = _exc_por_agente[_exc_por_agente > 0]
if _exc_por_agente.empty:
    st.info("Sin tiempo de exceso registrado para la selección actual.")
else:
    _PARETO_TOP_N = 20
    _top = _exc_por_agente.head(_PARETO_TOP_N)
    _resto = float(_exc_por_agente.iloc[_PARETO_TOP_N:].sum())
    if _resto > 0:
        _top = pd.concat([_top, pd.Series({"Otros expertos": _resto})])
    _horas    = _top / 60
    _cum_pct  = _top.cumsum() / _exc_por_agente.sum() * 100
    _nombres_cortos = [" ".join(str(n).split()[:2]) if n != "Otros expertos" else n for n in _top.index]

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        x=_nombres_cortos, y=_horas.values, name="Horas de exceso",
        marker=dict(color="#FB7185", opacity=0.88, cornerradius=4),
        text=[seg_a_hhmmss(v * 3600) for v in _horas.values], textposition="outside", cliponaxis=False,
        textfont=dict(size=9, color="rgba(255,255,255,0.7)", family="Inter"),
        hovertemplate="<b>%{x}</b><br>Exceso: %{text}<extra></extra>",
    ))
    fig_pareto.add_trace(go.Scatter(
        x=_nombres_cortos, y=_cum_pct.values, mode="lines+markers", name="% acumulado", yaxis="y2",
        line=dict(color="#38BDF8", width=2.5, shape="spline"),
        marker=dict(size=5, color="white", line=dict(color="#38BDF8", width=2)),
        hovertemplate="<b>%{x}</b><br>Acumulado: %{y:.1f}%<extra></extra>",
    ))
    fig_pareto.add_hline(y=80, yref="y2", line_dash="dot", line_color="rgba(56,189,248,0.55)", line_width=1.5,
                          annotation_text="80%", annotation_font=dict(size=10, color="#7DD3FC"), annotation_position="right")
    fig_pareto.update_layout(
        height=380, margin=dict(l=0, r=45, t=20, b=90),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(size=9, family="Inter", color="rgba(255,255,255,0.55)"), tickangle=-45, showgrid=False),
        yaxis=dict(title=dict(text="Horas", font=dict(size=10, color="rgba(255,255,255,0.4)")),
                   gridcolor="rgba(255,255,255,0.045)", tickfont=dict(size=9, family="Inter", color="rgba(255,255,255,0.32)")),
        yaxis2=dict(title=dict(text="% acumulado", font=dict(size=10, color="rgba(56,189,248,0.6)")),
                    overlaying="y", side="right", range=[0, 105], showgrid=False,
                    tickfont=dict(size=9, family="Inter", color="rgba(56,189,248,0.55)")),
        legend=dict(orientation="h", yanchor="bottom", y=1.10, xanchor="left", x=0,
                    font=dict(size=10, family="Inter"), bgcolor="rgba(0,0,0,0)"),
        showlegend=True, font=dict(family="Inter", size=11, color="rgba(255,255,255,0.72)"),
    )
    st.caption(
        f"{len(_exc_por_agente)} expertos con exceso registrado · se muestran los "
        f"{min(_PARETO_TOP_N, len(_exc_por_agente))} con más horas" + (" + Otros expertos" if _resto > 0 else "") + "."
    )
    st.plotly_chart(fig_pareto, use_container_width=True, config={"displayModeBar": False})

# ── Tabla 3: Estados y Excesos ────────────────
st.markdown(f"""<div class='tbl-hdr' style='background:linear-gradient(135deg,{COLOR_DANGER} 0%,#DC2626 100%);margin-top:20px'>
    <span class='tbl-hdr-icon'>⚠️</span>
    <div class='tbl-hdr-body'>
        <div class='tbl-hdr-title'>Estados y Excesos</div>
        <div class='tbl-hdr-desc'>Login · Tiempos por estado · Excesos por actividad en h:mm:ss</div>
    </div>
    <span class='tbl-hdr-badge'>Excesos</span>
</div>""", unsafe_allow_html=True)

exc_cols     = ["Exceso Almuerzo", "Exceso Descanso", "Exceso Seguimiento",
                "Exceso Toilette", "Exceso Entrenamiento", "Exceso Feedback", "Exceso Calidad"]
exc_min_cols = [c + "_min" for c in exc_cols]
exc_min_disp = [c for c in exc_min_cols if c in dff.columns]

_estado_cols = [
    "Alertas tempranas", "Almuerzo", "Ausente", "Break", "Calidad",
    "Disponible", "En Línea No ACD", "Entrenamiento", "Niveles de riesgo",
    "Recorrido de Aula", "Retroalimentación", "Seguimiento", "Seguimiento Aulas",
    "Toilette", "WhatsApp", "webchat",
]

def _fmt_hora(v):
    if v is None or (not isinstance(v, object)) or str(v) in ("nan", "NaT", "None"):
        return "-"
    try:
        import datetime
        if isinstance(v, (datetime.time, datetime.datetime)):
            return v.strftime("%H:%M")
        s = str(v)
        return s[:5] if len(s) >= 5 else s
    except Exception:
        return "-"

t3 = dff.rename(columns={"Nombre": "Agente", "Campana": "Campaña"}).copy()
t3["Fecha"] = t3["Fecha"].dt.strftime("%d/%m/%Y")

login_cols = []
for col in ["Hora Login", "Hora Deslogueo"]:
    if col in t3.columns:
        t3[col] = t3[col].apply(_fmt_hora)
        login_cols.append(col)

estado_disp = []
for col in _estado_cols:
    if col in t3.columns:
        t3[col] = fmt_td_vec(t3[col])
        estado_disp.append(col)

exc_fmt_cols = []
for orig, min_col in zip(exc_cols, exc_min_cols):
    if min_col in t3.columns:
        t3[orig] = seg_a_hhmmss_vec(t3[min_col] * 60)
        exc_fmt_cols.append(orig)

if exc_min_disp:
    total_s = t3[exc_min_disp].sum(axis=1) * 60
    t3["Total excesos"] = seg_a_hhmmss_vec(total_s)

cols_t3 = (
    ["Fecha", "Agente", "Supervisor", "Campaña"]
    + login_cols
    + estado_disp
    + exc_fmt_cols
    + (["Total excesos"] if exc_min_disp else [])
)
t3_show = t3[cols_t3].sort_values(["Fecha", "Agente"]).reset_index(drop=True)
df_descarga(t3_show, "estados_excesos.xlsx", use_container_width=True, hide_index=True, height=350)

# ── Semana vs. semana: quién se movió más ──
_ui.section("H", "EVOLUCIÓN SEMANAL")
_ui.panel_title("🔁", "Semana vs. Semana", "Adherencia promedio por experto frente a la semana anterior — solo expertos con datos en ambas semanas.", "COMPARATIVO")

def _wow_bar(delta_pp, height=None):
    """delta_pp: Series índice=categoría, valores=delta en puntos porcentuales,
    ya ordenada de forma que el último elemento es el que debe quedar arriba."""
    cats = delta_pp.index.tolist()
    vals = delta_pp.tolist()
    colors = [COLOR_SUCCESS if v >= 0 else COLOR_DANGER for v in vals]
    fig = go.Figure(go.Bar(
        x=vals, y=cats, orientation="h",
        marker=dict(color=colors, line=dict(width=0), cornerradius=4), width=0.6,
        text=[f"{v:+.1f} pp" for v in vals], textposition="outside", cliponaxis=False,
        textfont=dict(size=10, color="rgba(255,255,255,0.78)", family="Inter"),
        hovertemplate="<b>%{y}</b><br>%{x:+.1f} pp<extra></extra>",
    ))
    fig.add_vline(x=0, line_color="rgba(255,255,255,0.25)", line_width=1)
    _lo = min(vals + [0]) * 1.25
    _hi = max(vals + [0]) * 1.25
    if _lo == _hi:
        _lo, _hi = -1, 1
    fig.update_layout(
        height=height or max(240, len(cats) * 36 + 40), margin=dict(l=0, r=45, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[_lo, _hi], showgrid=True, gridcolor="rgba(255,255,255,.06)", zeroline=False,
                   tickfont=dict(size=9.5, family="Inter", color="rgba(255,255,255,.5)")),
        yaxis=dict(showgrid=False, tickfont=dict(size=10.5, family="Inter", color="rgba(255,255,255,.75)")),
        showlegend=False, font=dict(family="Inter"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

_sem_orden = dff_validos.groupby("Semana")["Fecha"].min().sort_values().index.tolist()
if len(_sem_orden) < 2:
    st.info("Se necesitan al menos dos semanas en el período filtrado para comparar.")
else:
    _sem_actual, _sem_previa = _sem_orden[-1], _sem_orden[-2]
    _wow = (
        dff_validos[dff_validos["Semana"].isin([_sem_actual, _sem_previa])]
        .groupby(["Nombre", "Semana"])
        .agg(adh_s=("adh_s", "sum"), prog_s=("prog_s", "sum"))
        .reset_index()
    )
    _wow["ADH"] = (_wow["adh_s"] / _wow["prog_s"]).where(_wow["prog_s"] > 0, np.nan)
    _piv_wow = _wow.pivot(index="Nombre", columns="Semana", values="ADH").dropna(subset=[_sem_actual, _sem_previa])
    _piv_wow["Delta"] = (_piv_wow[_sem_actual] - _piv_wow[_sem_previa]) * 100
    _piv_wow.index = [" ".join(str(n).split()[:2]) for n in _piv_wow.index]

    if _piv_wow.empty:
        st.info("Ningún experto tiene registros en ambas semanas para comparar.")
    else:
        _c_mej, _c_emp = st.columns(2)
        with _c_mej:
            st.caption(f"📈 Mejoraron más · {_sem_previa} → {_sem_actual}")
            _top_mej = _piv_wow.nlargest(8, "Delta")["Delta"].sort_values(ascending=True)
            _wow_bar(_top_mej)
        with _c_emp:
            st.caption(f"📉 Empeoraron más · {_sem_previa} → {_sem_actual}")
            _top_emp = _piv_wow.nsmallest(8, "Delta")["Delta"].sort_values(ascending=False)
            _wow_bar(_top_emp)

st.caption(f"📋 {dff['Nombre'].nunique()} agentes · {len(dff)} registros en el período seleccionado")
