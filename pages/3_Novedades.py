# v5
import streamlit as st
import pandas as pd
import base64
import urllib.parse
from datetime import date

COLOR_PRIMARY = "#28053F"
COLOR_ACCENT  = "#0EA5E9"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER  = "#EF4444"

_LOGO_PATH = "logo-scala-learning-transformacion-digital-universidades.webp"

@st.cache_data(show_spinner=False)
def _cargar_logo():
    try:
        with open(_LOGO_PATH, "rb") as _f:
            return f"data:image/webp;base64,{base64.b64encode(_f.read()).decode()}"
    except FileNotFoundError:
        return ""

_logo_src = _cargar_logo()

# ─────────────────────────────────────────────
# CONEXIÓN GOOGLE SHEETS
# ─────────────────────────────────────────────
_SHEET_ID = "1-Ld6qxNvCl2g3u7_qmqnvljPoRYr_sgGyovGiOJ_Riw"

@st.cache_data(ttl=300, show_spinner=False)
def _cargar_hoja(nombre_hoja: str) -> pd.DataFrame:
    url = (
        f"https://docs.google.com/spreadsheets/d/{_SHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(nombre_hoja)}"
    )
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return pd.DataFrame({"_error": [str(e)]})

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _fmt_fecha(v):
    try:
        return pd.to_datetime(v).strftime("%d/%m/%Y")
    except Exception:
        return str(v) if pd.notna(v) else "-"

def _kpi_bar(pct, color, max_val=100):
    fill = min(pct / max_val * 100, 100) if max_val else 0
    return (f"<div class='kpi-bar-wrap'>"
            f"<div class='kpi-bar-fill' style='width:{fill:.0f}%;background:{color};'></div>"
            f"</div>")

_MESES_ES = ["Todos","Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

_DEMO = pd.DataFrame([
    {"ID Novedad":"WFM-ID-611977","Estado":"Aprobado supervisor","Nombre":"Laura Camila Sanchez Toro",  "Cédula":"1125230546","Supervisor":"Claudia Daniela Arevalo Martinez","Tipo de novedad":"Tiempo real",  "Novedad específica":"Falla de sistema",  "Fecha inicio":"01/07/2026","Hora inicio":"08:15","Fecha fin":"01/07/2026","Hora fin":"09:00","Horas":"0:45","Comentarios":"Equipo sin conectividad"},
    {"ID Novedad":"NOV-002",      "Estado":"Aprobado",           "Nombre":"Carlos Andrés Moreno",        "Cédula":"1098765432","Supervisor":"Johan Sebastian López",           "Tipo de novedad":"Planificación","Novedad específica":"Cambio de turno",    "Fecha inicio":"02/07/2026","Hora inicio":"07:00","Fecha fin":"02/07/2026","Hora fin":"15:00","Horas":"8:00","Comentarios":"Aprobado por coordinación"},
    {"ID Novedad":"NOV-003",      "Estado":"Rechazado",           "Nombre":"María Camila Torres",         "Cédula":"1023456789","Supervisor":"Zully Paola Rodríguez",          "Tipo de novedad":"Históricas",  "Novedad específica":"Permiso médico",     "Fecha inicio":"28/06/2026","Hora inicio":"10:00","Fecha fin":"28/06/2026","Hora fin":"14:00","Horas":"4:00","Comentarios":"Sin soporte adjunto"},
    {"ID Novedad":"NOV-004",      "Estado":"Aprobado",           "Nombre":"Andrés Felipe Gómez",         "Cédula":"1034567890","Supervisor":"Karen Julieth Barreto",           "Tipo de novedad":"Planificación","Novedad específica":"Licencia",           "Fecha inicio":"03/07/2026","Hora inicio":"06:00","Fecha fin":"05/07/2026","Hora fin":"15:00","Horas":"24:00","Comentarios":"Licencia por calamidad"},
    {"ID Novedad":"NOV-005",      "Estado":"Pendiente",           "Nombre":"Valentina Herrera Cruz",      "Cédula":"1045678901","Supervisor":"Camila Maldonado",               "Tipo de novedad":"Tiempo real",  "Novedad específica":"Ausente",            "Fecha inicio":"01/07/2026","Hora inicio":"06:55","Fecha fin":"01/07/2026","Hora fin":"15:00","Horas":"8:05","Comentarios":"No se reportó"},
    {"ID Novedad":"NOV-006",      "Estado":"Aprobado",           "Nombre":"Diego Fernando Ruiz",         "Cédula":"1056789012","Supervisor":"Ana Milena Carvajal",             "Tipo de novedad":"Históricas",  "Novedad específica":"Retiro",             "Fecha inicio":"25/06/2026","Hora inicio":"06:00","Fecha fin":"25/06/2026","Hora fin":"15:00","Horas":"9:00","Comentarios":"Procesado en nómina"},
])

# ─────────────────────────────────────────────
# RENDER TAB
# ─────────────────────────────────────────────
def _render_tab(df: pd.DataFrame, sup_sel, tipo_sel, buscar, fecha_desde, fecha_hasta, agrupar, periodo_sel):
    if "_error" in df.columns:
        st.error(f"No se pudo cargar la hoja: {df['_error'].iloc[0]}")
        return

    es_demo = df.empty
    if es_demo:
        df = _DEMO.copy()
        st.markdown(
            "<div style='background:rgba(245,158,11,0.10);border:1px solid rgba(245,158,11,0.30);"
            "border-radius:12px;padding:10px 16px;margin-bottom:16px;font-size:12px;"
            "color:rgba(255,255,255,0.70);display:flex;align-items:center;gap:8px'>"
            "<span style='font-size:16px'>👁️</span>"
            "<span><b style='color:#F59E0B'>Vista previa</b> — datos de muestra. "
            "Cuando registres novedades en el Sheet aparecerán aquí automáticamente.</span>"
            "</div>",
            unsafe_allow_html=True
        )

    df = df.copy()
    if "Fecha inicio" in df.columns:
        df["_fecha_dt"] = pd.to_datetime(df["Fecha inicio"], dayfirst=True, errors="coerce")
    else:
        df["_fecha_dt"] = pd.NaT

    if fecha_desde:
        df = df[df["_fecha_dt"].isna() | (df["_fecha_dt"].dt.date >= fecha_desde)]
    if fecha_hasta:
        df = df[df["_fecha_dt"].isna() | (df["_fecha_dt"].dt.date <= fecha_hasta)]

    if agrupar == "Mes" and periodo_sel and periodo_sel != "Todos":
        mes_num = _MESES_ES.index(periodo_sel)
        df = df[df["_fecha_dt"].isna() | (df["_fecha_dt"].dt.month == mes_num)]
    elif agrupar == "Semana" and periodo_sel and periodo_sel != "Todas":
        try:
            sem_n = int(periodo_sel.split()[-1])
            df = df[df["_fecha_dt"].isna() | (df["_fecha_dt"].dt.isocalendar().week == sem_n)]
        except Exception:
            pass
    elif agrupar == "Trimestre" and periodo_sel and periodo_sel != "Todos":
        _tri_map = {"T1 (Ene–Mar)": [1,2,3], "T2 (Abr–Jun)": [4,5,6],
                    "T3 (Jul–Sep)": [7,8,9],  "T4 (Oct–Dic)": [10,11,12]}
        meses_tri = _tri_map.get(periodo_sel, [])
        if meses_tri:
            df = df[df["_fecha_dt"].isna() | (df["_fecha_dt"].dt.month.isin(meses_tri))]
    elif agrupar == "Semestre" and periodo_sel and periodo_sel != "Todos":
        meses_sem = [1,2,3,4,5,6] if "S1" in periodo_sel else [7,8,9,10,11,12]
        df = df[df["_fecha_dt"].isna() | (df["_fecha_dt"].dt.month.isin(meses_sem))]

    if sup_sel != "Todos" and "Supervisor" in df.columns:
        df = df[df["Supervisor"] == sup_sel]
    if tipo_sel != "Todos" and "Tipo de novedad" in df.columns:
        df = df[df["Tipo de novedad"] == tipo_sel]
    if buscar:
        mask = pd.Series(False, index=df.index)
        for c in ["Nombre", "Cédula", "Novedad específica"]:
            if c in df.columns:
                mask |= df[c].astype(str).str.contains(buscar, case=False, na=False)
        df = df[mask]

    for c in ["Fecha inicio", "Fecha fin", "Fecha procesamiento"]:
        if c in df.columns:
            df[c] = df[c].apply(_fmt_fecha)
    df = df.drop(columns=["_fecha_dt"], errors="ignore")

    # ── KPIs ─────────────────────────────────────────
    total = len(df)
    if "Estado" in df.columns:
        estados = df["Estado"].astype(str).str.strip()
        pend = estados.str.contains("Pendiente", case=False).sum()
        apro = estados.str.contains("Aprobado", case=False).sum()
        rech = estados.str.contains("Rechazado", case=False).sum()
    else:
        pend = apro = rech = 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_ACCENT}'>
            <div class='kpi-bg-icon'>📋</div>
            <div>
                <div class='kpi-label'>Total</div>
                <div class='kpi-value' style='color:#7DD3FC'>{total}</div>
                <div class='kpi-sub'>Novedades registradas</div>
            </div>
            {_kpi_bar(total, COLOR_ACCENT, max(total, 1))}
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_WARNING}'>
            <div class='kpi-bg-icon'>⏳</div>
            <div>
                <div class='kpi-label'>Pendientes</div>
                <div class='kpi-value' style='color:{COLOR_WARNING}'>{pend}</div>
                <div class='kpi-sub'>Sin gestionar</div>
            </div>
            {_kpi_bar(pend, COLOR_WARNING, max(total, 1))}
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_SUCCESS}'>
            <div class='kpi-bg-icon'>✅</div>
            <div>
                <div class='kpi-label'>Aprobados</div>
                <div class='kpi-value' style='color:{COLOR_SUCCESS}'>{apro}</div>
                <div class='kpi-sub'>Novedad aprobada</div>
            </div>
            {_kpi_bar(apro, COLOR_SUCCESS, max(total, 1))}
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class='kpi-card' style='--kc:{COLOR_DANGER}'>
            <div class='kpi-bg-icon'>❌</div>
            <div>
                <div class='kpi-label'>Rechazados</div>
                <div class='kpi-value' style='color:{COLOR_DANGER}'>{rech}</div>
                <div class='kpi-sub'>Novedad rechazada</div>
            </div>
            {_kpi_bar(rech, COLOR_DANGER, max(total, 1))}
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    # ── Tabla ─────────────────────────────────────────
    _COLS = [c for c in [
        "ID Novedad", "Estado", "Nombre", "Cédula", "Supervisor",
        "Tipo de novedad", "Novedad específica",
        "Fecha inicio", "Hora inicio", "Fecha fin", "Hora fin",
        "Horas", "Comentarios",
    ] if c in df.columns]

    st.markdown(f"""<div class='tbl-hdr' style='background:linear-gradient(135deg,{COLOR_PRIMARY} 0%,{COLOR_ACCENT} 100%)'>
        <span class='tbl-hdr-icon'>📋</span>
        <div class='tbl-hdr-body'>
            <div class='tbl-hdr-title'>Registro de Novedades</div>
            <div class='tbl-hdr-desc'>Detalle completo · filtros aplicados desde el panel lateral</div>
        </div>
        <span class='tbl-hdr-badge'>{total} registros</span>
    </div>""", unsafe_allow_html=True)

    st.dataframe(
        df[_COLS].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        height=min(80 + len(df) * 35, 500),
    )
    if es_demo:
        st.caption("👁️ Vista previa con datos de muestra — conectado a Google Sheets")
    else:
        st.caption(f"📋 {len(df)} registros · Google Sheets · recarga la página para actualizar")

# ─────────────────────────────────────────────
# CARGAR DATOS
# ─────────────────────────────────────────────
df_rt   = _cargar_hoja("Tiempo real")
df_plan = _cargar_hoja("Planificación")
df_hist = _cargar_hoja("Históricas")

def _get_opts(col):
    vals = []
    for df in [df_rt, df_plan, df_hist]:
        if not df.empty and "_error" not in df.columns and col in df.columns:
            vals += df[col].dropna().astype(str).unique().tolist()
    return sorted(set(vals)) or (sorted(_DEMO[col].dropna().unique().tolist()) if col in _DEMO.columns else [])

_sups  = _get_opts("Supervisor")
_tipos = _get_opts("Tipo de novedad")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class='sbc'>
        <div class='sbc-orb sbc-orb-1'></div>
        <div class='sbc-orb sbc-orb-2'></div>
        <div class='sbc-orb sbc-orb-3'></div>
        <div class='sbc-live'><span class='sbc-pulse'></span>LIVE</div>
        <div class='sbc-body'>
            <div class='sbc-logo-wrap'><img src='{_logo_src}' class='sbc-logo-img' /></div>
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

    # ── 01 PERÍODO ──────────────────────────────────
    st.markdown("""<div class='sbh'>
        <div class='sbh-num' style='color:#38BDF8!important;background:rgba(56,189,248,0.12);border-color:rgba(56,189,248,0.22)'>01</div>
        <div class='sbh-lbl'>Período</div>
        <div class='sbh-rule'></div>
    </div>""", unsafe_allow_html=True)

    agrupar = st.selectbox("Agrupar por", ["Día", "Semana", "Mes", "Trimestre", "Semestre"], key="sb_agrupar")

    periodo_sel = None
    if agrupar == "Mes":
        periodo_sel = st.selectbox("Mes", _MESES_ES, key="sb_mes")
    elif agrupar == "Semana":
        periodo_sel = st.selectbox("Semana", ["Todas"] + [f"Semana {i}" for i in range(1, 53)], key="sb_sem")
    elif agrupar == "Trimestre":
        periodo_sel = st.selectbox("Trimestre", ["Todos","T1 (Ene–Mar)","T2 (Abr–Jun)","T3 (Jul–Sep)","T4 (Oct–Dic)"], key="sb_tri")
    elif agrupar == "Semestre":
        periodo_sel = st.selectbox("Semestre", ["Todos","S1 (Ene–Jun)","S2 (Jul–Dic)"], key="sb_sem2")

    c1, c2 = st.columns(2)
    with c1:
        fecha_desde = st.date_input("Desde", value=date(2026, 4, 1), key="sb_desde")
    with c2:
        fecha_hasta = st.date_input("Hasta", value=date.today(), key="sb_hasta")

    # ── 02 FILTROS ───────────────────────────────────
    st.markdown("""<div class='sbh'>
        <div class='sbh-num' style='color:#34D399!important;background:rgba(52,211,153,0.12);border-color:rgba(52,211,153,0.22)'>02</div>
        <div class='sbh-lbl'>Filtros</div>
        <div class='sbh-rule'></div>
    </div>""", unsafe_allow_html=True)

    sup_sel  = st.selectbox("Supervisor",      ["Todos"] + _sups,  key="sb_sup")
    tipo_sel = st.selectbox("Tipo de novedad", ["Todos"] + _tipos, key="sb_tipo")
    buscar   = st.text_input("Buscar", placeholder="Nombre, cédula o novedad...", key="sb_bus")

    # ── Usuario ──────────────────────────────────────
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
# CSS  (idéntico a Adherencia / Ocupación)
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

    [data-testid="stAppViewContainer"], .main {{
        background:
            radial-gradient(ellipse 90% 55% at 6% -6%,   rgba(14,165,233,0.16) 0%, transparent 55%),
            radial-gradient(ellipse 80% 55% at 100% 0%,  rgba(99,102,241,0.17) 0%, transparent 55%),
            radial-gradient(ellipse 75% 60% at 92% 100%, rgba(52,211,153,0.08) 0%, transparent 55%),
            radial-gradient(ellipse 60% 50% at 0% 100%,  rgba(99,102,241,0.07) 0%, transparent 55%),
            linear-gradient(160deg, #0A0813 0%, #0F0B20 45%, #08060F 100%);
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    .block-container {{ padding-top: 2rem; padding-bottom: 1rem; }}

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
    [data-testid="stSidebarCollapseButton"] span {{ color: rgba(255,255,255,0.80) !important; font-size:20px !important; }}
    div[data-testid="collapsedControl"] span {{ color: {COLOR_PRIMARY} !important; font-size:20px !important; }}
    div[data-testid="stSidebarContent"] {{ width:100%!important; box-sizing:border-box!important; padding-right:0.75rem!important; }}
    div[data-testid="stSidebarContent"] > div {{ width:100%!important; }}

    /* ── KPI cards ── */
    .kpi-card {{
        background: linear-gradient(160deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.02) 100%);
        border-radius: 20px; padding: 22px 22px 18px;
        box-shadow: 0 20px 44px -18px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.08);
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        position: relative; overflow: hidden;
        min-height: 148px; display: flex; flex-direction: column; justify-content: space-between;
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
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
        background: var(--kc, {COLOR_PRIMARY}); box-shadow: 0 0 18px -2px var(--kc, {COLOR_PRIMARY});
    }}
    .kpi-card::after {{
        content: ''; position: absolute; top: -40px; right: -40px;
        width: 120px; height: 120px;
        background: radial-gradient(circle, var(--kc, {COLOR_PRIMARY}), transparent 70%);
        opacity: 0.22; border-radius: 50%;
    }}
    .kpi-bg-icon {{
        position: absolute; bottom: 12px; right: 16px;
        font-size: 46px; opacity: 0.10; line-height: 1; pointer-events: none; z-index: 0;
    }}
    .kpi-label {{ font-size: 10px; color: rgba(255,255,255,0.50); font-weight: 700; text-transform: uppercase; letter-spacing: 0.10em; position: relative; z-index: 1; }}
    .kpi-value {{ font-family:'Space Grotesk',sans-serif!important; font-size: 34px; font-weight: 700; line-height: 1.1; margin: 10px 0 4px; position: relative; z-index: 1; letter-spacing:-0.5px; text-shadow:0 2px 16px rgba(0,0,0,0.4); }}
    .kpi-sub   {{ font-size: 11px; color: rgba(255,255,255,0.42); position: relative; z-index: 1; }}
    .kpi-bar-wrap {{ background: rgba(255,255,255,0.09); border-radius: 99px; height: 5px; margin-top: 12px; overflow: hidden; position: relative; z-index: 1; }}
    .kpi-bar-fill {{ height: 5px; border-radius: 99px; box-shadow:0 0 10px -1px currentColor; }}

    /* ── Table headers ── */
    .tbl-hdr {{
        padding: 14px 20px; border-radius: 14px;
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 6px; box-shadow: 0 4px 18px rgba(0,0,0,0.15);
        position: relative; overflow: hidden;
    }}
    .tbl-hdr::before {{ content:''; position:absolute; left:-10px; top:-10px; width:60px; height:60px; background:rgba(255,255,255,0.08); border-radius:50%; }}
    .tbl-hdr::after  {{ content:''; position:absolute; right:-20px; bottom:-20px; width:80px; height:80px; background:rgba(255,255,255,0.10); border-radius:50%; }}
    .tbl-hdr-icon  {{ font-size:24px; flex-shrink:0; position:relative; z-index:1; }}
    .tbl-hdr-body  {{ flex:1; position:relative; z-index:1; }}
    .tbl-hdr-title {{ font-size:14px; font-weight:800; color:white; margin:0 0 2px; letter-spacing:-0.2px; }}
    .tbl-hdr-desc  {{ font-size:11px; color:rgba(255,255,255,0.72); margin:0; }}
    .tbl-hdr-badge {{ font-size:10px; font-weight:700; color:white; background:rgba(255,255,255,0.20); border:1px solid rgba(255,255,255,0.35); padding:4px 12px; border-radius:99px; flex-shrink:0; white-space:nowrap; position:relative; z-index:1; }}

    /* ── Plotly chart ── */
    div[data-testid="stPlotlyChart"] {{
        background: linear-gradient(160deg, rgba(255,255,255,0.05), rgba(255,255,255,0.015)) !important;
        border-radius: 18px !important; box-shadow: 0 16px 38px -16px rgba(0,0,0,0.65) !important;
        border: 1px solid rgba(255,255,255,0.09) !important; overflow: hidden !important; padding: 10px !important;
    }}

    /* ── Tabla oscura ── */
    div[data-testid="stDataFrame"] {{
        border-radius: 16px !important; overflow: hidden !important;
        box-shadow: 0 16px 38px -16px rgba(0,0,0,0.65) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
    }}
    div[data-testid="stDataFrame"] div[role="columnheader"] {{
        background: linear-gradient(135deg, #1b1240 0%, #0EA5E9 100%) !important;
        color: white !important; font-weight: 700 !important;
    }}
    div[data-testid="stDataFrame"] div[role="columnheader"] span {{ color: white !important; }}
    div[data-testid="stDataFrame"] .ag-root-wrapper {{ background: rgba(16,13,36,0.90) !important; border: none !important; }}
    div[data-testid="stDataFrame"] .ag-body-viewport,
    div[data-testid="stDataFrame"] .ag-center-cols-viewport {{ background: transparent !important; }}
    div[data-testid="stDataFrame"] .ag-row {{ background: rgba(16,13,36,0.85) !important; border-color: rgba(255,255,255,0.045) !important; }}
    div[data-testid="stDataFrame"] .ag-row-odd {{ background: rgba(22,18,48,0.80) !important; }}
    div[data-testid="stDataFrame"] .ag-row:hover,
    div[data-testid="stDataFrame"] .ag-row-hover {{ background: rgba(14,165,233,0.10) !important; }}
    div[data-testid="stDataFrame"] .ag-cell {{ color: rgba(225,232,250,0.90) !important; border-color: rgba(255,255,255,0.04) !important; }}
    div[data-testid="stDataFrame"] .ag-header {{ background: transparent !important; border-bottom: 1px solid rgba(255,255,255,0.10) !important; }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar {{ width:6px; height:6px; }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.04); }}
    div[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {{ background: rgba(56,189,248,0.35); border-radius:99px; }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] > div:first-child {{
        background:
            radial-gradient(ellipse 95% 42% at 8% 0%,    rgba(14,165,233,0.30) 0%, transparent 55%),
            radial-gradient(ellipse 90% 42% at 100% 26%, rgba(129,140,248,0.28) 0%, transparent 55%),
            radial-gradient(ellipse 85% 42% at 50% 102%, rgba(52,211,153,0.15) 0%, transparent 55%),
            linear-gradient(160deg, #0B0518 0%, #14082b 45%, #0A0414 100%);
        border-right: 1px solid rgba(255,255,255,0.07);
        display:flex!important; flex-direction:column!important; min-height:100vh!important;
    }}
    div[data-testid="stSidebarContent"] * {{ color: white !important; }}
    [data-testid="stSidebarHeader"] {{ padding-top:0.6rem!important; padding-bottom:0!important; }}
    [data-testid="stSidebarUserContent"] {{ padding-top:0!important; flex:1 1 auto!important; display:flex!important; flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] > div {{ flex:1 1 auto!important; display:flex!important; flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:last-of-type {{ margin-top:auto!important; }}
    div[data-testid="stSidebarContent"] hr {{ border-color: rgba(255,255,255,0.08); margin-top:4px!important; margin-bottom:4px!important; }}
    div[data-testid="collapsedControl"] {{ background:transparent!important; border:none!important; box-shadow:none!important; }}
    div[data-testid="collapsedControl"] * {{ color:transparent!important; background:transparent!important; border:none!important; }}

    @keyframes sbcBar   {{ 0%{{background-position:0% 0%;}} 100%{{background-position:200% 0%;}} }}
    @keyframes sbcPulse {{ 0%,100%{{opacity:1;transform:scale(1);}} 50%{{opacity:.3;transform:scale(.6);}} }}

    .sbc {{ position:relative;border-radius:20px;overflow:hidden;margin:0 0 20px;padding:20px 18px 18px;
        background:linear-gradient(145deg,rgba(56,189,248,0.12),rgba(129,140,248,0.09),rgba(52,211,153,0.07)),rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.12); }}
    .sbc-orb {{ position:absolute;border-radius:50%;pointer-events:none; }}
    .sbc-orb-1 {{ width:140px;height:140px;background:radial-gradient(circle,rgba(56,189,248,0.18),transparent 70%);top:-50px;right:-40px; }}
    .sbc-orb-2 {{ width:90px;height:90px;background:radial-gradient(circle,rgba(129,140,248,0.16),transparent 70%);bottom:-30px;left:-25px; }}
    .sbc-orb-3 {{ width:60px;height:60px;background:radial-gradient(circle,rgba(52,211,153,0.14),transparent 70%);top:50%;right:12px; }}
    .sbc-live {{ position:absolute;top:14px;right:14px;display:flex;align-items:center;gap:5px;
        font-size:8px!important;font-weight:800!important;color:#34D399!important;
        background:rgba(52,211,153,0.13);border:1px solid rgba(52,211,153,0.30);
        padding:3px 9px 3px 7px;border-radius:99px;letter-spacing:0.10em;z-index:2; }}
    .sbc-pulse {{ width:5px;height:5px;background:#34D399;border-radius:50%;display:inline-block;animation:sbcPulse 1.8s ease-in-out infinite; }}
    .sbc-body {{ position:relative;z-index:1;text-align:center; }}
    .sbc-logo-wrap {{ margin-bottom:10px;display:flex;justify-content:center; }}
    .sbc-logo-img {{ max-width:150px!important;height:auto!important;filter:drop-shadow(0 4px 14px rgba(56,189,248,0.45)) brightness(1.05); }}
    .sbc-name {{ font-size:13px!important;font-weight:700!important;color:rgba(255,255,255,0.88)!important;margin-bottom:4px!important; }}
    .sbc-org  {{ font-size:10px!important;color:rgba(255,255,255,0.35)!important;margin-bottom:16px!important; }}
    .sbc-stats {{ display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.22);border-radius:12px;padding:10px 8px;border:1px solid rgba(255,255,255,0.07); }}
    .sbc-stat {{ flex:1;text-align:center; }}
    .sbc-sv {{ display:block;font-size:14px!important;font-weight:900!important;color:white!important;line-height:1;margin-bottom:3px; }}
    .sbc-sl {{ display:block;font-size:8px!important;font-weight:700!important;color:rgba(255,255,255,0.28)!important;letter-spacing:0.10em;text-transform:uppercase; }}
    .sbc-sep {{ width:1px;height:28px;background:rgba(255,255,255,0.09);flex-shrink:0; }}
    .sbc-bar {{ position:absolute;bottom:0;left:0;right:0;height:3px;
        background:linear-gradient(90deg,#38BDF8,#818CF8,#34D399,#F59E0B,#38BDF8);
        background-size:300% 100%;animation:sbcBar 4s linear infinite; }}

    .sbh {{ display:flex;align-items:center;gap:10px;margin:24px 0 12px; }}
    .sbh-num {{ font-size:10px!important;font-weight:900!important;width:28px;height:22px;border-radius:7px;border:1px solid;display:flex;align-items:center;justify-content:center;flex-shrink:0;letter-spacing:0.04em; }}
    .sbh-lbl {{ font-size:10px!important;font-weight:800!important;color:rgba(255,255,255,0.60)!important;letter-spacing:0.14em!important;text-transform:uppercase!important;white-space:nowrap!important; }}
    .sbh-rule {{ flex:1;height:1px;background:rgba(255,255,255,0.08); }}

    div[data-baseweb="popover"] *, div[data-baseweb="menu"] *,
    ul[role="listbox"] *, li[role="option"], li[role="option"] * {{ color: #1E293B !important; }}
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {{ background: #F1F5F9 !important; }}

    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] span,
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] div[class*="ValueContainer"] *,
    div[data-testid="stSidebarContent"] .stSelectbox [data-baseweb="select"] input {{ color: white !important; }}
    div[data-testid="stSidebarContent"] input[type="text"] {{ color: white !important; }}
    div[data-testid="stSidebarContent"] label,
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"],
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"] p,
    div[data-testid="stSidebarContent"] [data-testid="stWidgetLabel"] span {{
        font-size:11px!important; font-weight:500!important; color:rgba(255,255,255,0.50)!important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput label,
    div[data-testid="stSidebarContent"] .stDateInput [data-testid="stWidgetLabel"],
    div[data-testid="stSidebarContent"] .stDateInput [data-testid="stWidgetLabel"] p {{
        font-size:11px!important; font-weight:600!important; color:#38BDF8!important;
    }}
    div[data-testid="stSidebarContent"] .stSelectbox > div > div,
    div[data-testid="stSidebarContent"] .stSelectbox > label + div > div {{
        background:rgba(255,255,255,0.05)!important; border:1px solid rgba(255,255,255,0.12)!important;
        border-radius:9px!important; transition:border-color .18s, box-shadow .18s!important;
    }}
    div[data-testid="stSidebarContent"] .stSelectbox > div > div:hover {{
        border-color:rgba(56,189,248,0.50)!important; box-shadow:0 0 0 3px rgba(56,189,248,0.10)!important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput > div > div > input {{
        background:rgba(255,255,255,0.05)!important; border:1px solid rgba(255,255,255,0.12)!important;
        border-radius:9px!important; color:white!important; font-size:11px!important;
    }}
    div[data-testid="stSidebarContent"] .stDateInput > div > div > input:focus {{
        border-color:rgba(56,189,248,0.50)!important; box-shadow:0 0 0 3px rgba(56,189,248,0.10)!important;
    }}
    div[data-testid="stSidebarContent"] .stTextInput > div > div > input {{
        background:rgba(255,255,255,0.05)!important; border:1px solid rgba(255,255,255,0.12)!important;
        border-radius:9px!important; color:white!important; font-size:11px!important;
    }}

    .sbf {{ margin-top:26px; }}
    .sbf-card {{ position:relative;overflow:hidden;border-radius:16px;padding:14px;
        background:linear-gradient(150deg,rgba(56,189,248,0.10),rgba(129,140,248,0.06));
        border:1px solid rgba(255,255,255,0.10);box-shadow:inset 0 1px 0 rgba(255,255,255,0.08); }}
    .sbf-glow {{ position:absolute;width:120px;height:120px;border-radius:50%;top:-50px;right:-40px;
        background:radial-gradient(circle,rgba(56,189,248,0.20),transparent 70%);pointer-events:none; }}
    .sbf-row {{ display:flex;align-items:center;gap:12px;position:relative;z-index:1; }}
    .sbf-avatar {{ position:relative;width:42px;height:42px;border-radius:13px;flex-shrink:0;
        background:linear-gradient(135deg,#38BDF8,#818CF8);
        display:flex;align-items:center;justify-content:center;
        font-size:14px!important;font-weight:900!important;color:white!important;
        box-shadow:0 6px 18px rgba(56,189,248,0.45),inset 0 1px 0 rgba(255,255,255,0.3); }}
    .sbf-online {{ position:absolute;bottom:-2px;right:-2px;width:12px;height:12px;border-radius:50%;
        background:#34D399;border:2.5px solid #130A2B;box-shadow:0 0 8px rgba(52,211,153,0.8);
        animation:sbcPulse 2s ease-in-out infinite; }}
    .sbf-info {{ flex:1; }}
    .sbf-name {{ font-size:12px!important;font-weight:700!important;color:rgba(255,255,255,0.92)!important;margin-bottom:3px!important; }}
    .sbf-role {{ font-size:10px!important;color:rgba(255,255,255,0.42)!important;line-height:1.3; }}
    .sbf-credit {{ display:flex;align-items:center;justify-content:center;gap:5px;margin-top:12px;
        font-size:9px!important;font-weight:600!important;color:rgba(255,255,255,0.30)!important;letter-spacing:0.06em; }}
    .sbf-spark {{ font-size:10px; }}

    /* ── Header banner (idéntico a los otros módulos) ── */
    .st-key-hdrbanner {{
        position:relative; overflow:hidden; border-radius:20px; padding:18px 30px; margin-bottom:18px;
        background:
            radial-gradient(ellipse 70% 130% at 2% -15%,   rgba(14,165,233,0.34) 0%, transparent 60%),
            radial-gradient(ellipse 65% 130% at 100% 120%, rgba(129,140,248,0.34) 0%, transparent 60%),
            radial-gradient(ellipse 55% 110% at 72% 130%,  rgba(52,211,153,0.16) 0%, transparent 60%),
            linear-gradient(155deg, #0B0518 0%, #14082b 50%, #0A0414 100%);
        border:1px solid rgba(255,255,255,0.10);
        box-shadow:0 18px 46px -18px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.08);
    }}
    .hb-eyebrow {{ display:inline-flex;align-items:center;gap:8px;
        background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.16);
        border-radius:99px;padding:5px 13px;margin-bottom:11px;
        font-size:10px;font-weight:700;color:rgba(255,255,255,0.78);letter-spacing:0.12em;text-transform:uppercase; }}
    .hb-dot {{ width:7px;height:7px;border-radius:50%;background:#34D399;
        box-shadow:0 0 9px #34D399;animation:sbcPulse 1.8s ease-in-out infinite; }}
    .hb-title {{ font-family:'Space Grotesk',sans-serif!important;
        font-size:29px;font-weight:700;color:white;margin:0 0 9px;letter-spacing:-0.8px; }}
    .hb-meta {{ display:flex;flex-wrap:wrap;gap:8px;margin:0 0 2px; }}
    .hb-chip {{ display:inline-flex;align-items:center;gap:6px;
        background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.13);
        border-radius:9px;padding:5px 11px;font-size:11px;font-weight:600;color:rgba(255,255,255,0.74); }}
    .hb-chip b {{ color:#fff;font-weight:700; }}
    .nav-lbl {{ font-size:9px;font-weight:800;letter-spacing:0.16em;text-transform:uppercase;
        color:rgba(255,255,255,0.40);margin:3px 0 7px; }}
    .st-key-hdrbanner [data-testid="stVerticalBlock"] {{ gap:0.5rem!important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button {{
        position:relative; z-index:2; white-space:nowrap!important; color:#CBD3F2!important;
        border-radius:9px!important; font-size:10px!important; font-weight:700!important;
        height:32px!important; min-height:32px!important; padding:0 11px!important;
        border:1px solid rgba(255,255,255,0.12)!important; border-top-color:rgba(255,255,255,0.18)!important;
        background:linear-gradient(180deg, rgba(255,255,255,0.085), rgba(255,255,255,0.025))!important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.10), 0 4px 12px -8px rgba(8,3,24,0.60)!important;
        transition:all .16s ease!important;
    }}
    .st-key-hdrbanner [data-testid="stButton"] > button p {{ white-space:nowrap!important; margin:0!important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button:hover {{
        color:#EAF2FF!important; transform:translateY(-1px)!important;
        border-color:rgba(125,211,252,0.42)!important;
        background:linear-gradient(180deg, rgba(125,211,252,0.15), rgba(255,255,255,0.04))!important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.16), 0 8px 20px -10px rgba(56,189,248,0.38)!important;
    }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"] {{
        color:#F4F9FF!important; padding-left:20px!important;
        border:1px solid rgba(56,189,248,0.55)!important; border-top-color:rgba(186,225,255,0.62)!important;
        background:linear-gradient(180deg, rgba(56,189,248,0.30), rgba(59,130,246,0.16))!important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.22), 0 8px 22px -10px rgba(56,189,248,0.50)!important;
    }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"]::before {{
        content:""; position:absolute; left:8px; top:50%; transform:translateY(-50%);
        width:5px; height:5px; border-radius:50%; background:#7DD3FC; box-shadow:0 0 8px rgba(125,211,252,0.9);
    }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"]:hover {{
        transform:translateY(-1px)!important;
        background:linear-gradient(180deg, rgba(56,189,248,0.36), rgba(59,130,246,0.20))!important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.24), 0 10px 26px -10px rgba(56,189,248,0.58)!important;
    }}

    /* ── Tabs ── */
    [data-testid="stTabs"] [role="tablist"] {{
        background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
        border-radius:14px;padding:4px;gap:4px; }}
    [data-testid="stTabs"] [role="tab"] {{
        border-radius:10px!important;font-weight:700!important;font-size:13px!important;
        color:rgba(255,255,255,0.45)!important;padding:9px 22px!important;
        transition:all .2s ease!important;border:none!important; }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
        background:rgba(255,255,255,0.10)!important;color:white!important;
        box-shadow:0 2px 14px rgba(0,0,0,0.28)!important; }}
    [data-testid="stTabs"] [role="tab"]:hover {{ color:rgba(255,255,255,0.80)!important; }}
    [data-testid="stTabPanel"] {{ padding-top:22px!important; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
_home_pg = st.Page("home.py",               title="Inicio",     icon="🏠", default=True)
_adh_pg  = st.Page("pages/1_Adherencia.py", title="Adherencia", icon="🎯")
_ocu_pg  = st.Page("pages/2_Ocupacion.py",  title="Ocupación",  icon="📊")

with st.container(key="hdrbanner"):
    st.markdown("""
    <div class='hb-eyebrow'><span class='hb-dot'></span>Centro de Control · Uniminuto 2026</div>
    <div class='hb-title'>Novedades Operativas</div>
    <div class='hb-meta'>
        <span class='hb-chip'>📢 <b>Google Sheets en vivo</b></span>
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
        if st.button("📊 Ocupación",  key="hdr_ocu",  use_container_width=True):
            st.switch_page(_ocu_pg)
    with nb4:
        st.button("📢 Novedades", key="hdr_nov", use_container_width=True, type="primary")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
def _sec_label(texto, color):
    return (
        f"<div style='font-size:11px;font-weight:800;letter-spacing:0.14em;text-transform:uppercase;"
        f"color:rgba(255,255,255,0.38);display:flex;align-items:center;gap:10px;margin-bottom:18px'>"
        f"<span style='width:22px;height:2px;background:{color};border-radius:2px;display:inline-block'></span>"
        f"{texto}</div>"
    )

_filter_args = dict(
    sup_sel=sup_sel, tipo_sel=tipo_sel, buscar=buscar,
    fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
    agrupar=agrupar, periodo_sel=periodo_sel,
)

tab_rt, tab_plan, tab_hist = st.tabs([
    "🚨  Tiempo real",
    "🗓️  Planificación",
    "📁  Históricas",
])

with tab_rt:
    st.markdown(_sec_label("Novedades activas · turno en curso", "#EF4444"), unsafe_allow_html=True)
    _render_tab(df_rt, **_filter_args)

with tab_plan:
    st.markdown(_sec_label("Novedades planificadas · próximos días", "#38BDF8"), unsafe_allow_html=True)
    _render_tab(df_plan, **_filter_args)

with tab_hist:
    st.markdown(_sec_label("Registro histórico · novedades cerradas", "#34D399"), unsafe_allow_html=True)
    _render_tab(df_hist, **_filter_args)
