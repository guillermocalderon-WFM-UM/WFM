# v2
import streamlit as st
import pandas as pd
import base64
import urllib.parse

COLOR_PRIMARY = "#28053F"
COLOR_ACCENT  = "#0EA5E9"

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
# CONEXIÓN GOOGLE SHEETS (CSV export)
# ─────────────────────────────────────────────
_SHEET_ID = "1-Ld6qxNvCl2g3u7_qmqnvljPoRYr_sgGyovGiOJ_Riw"

@st.cache_data(ttl=60, show_spinner=False)
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


def _kpi_card(label, valor, color, icon):
    return (
        f"<div style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.09);"
        f"border-top:2.5px solid {color};border-radius:14px;padding:16px 18px;text-align:center;"
        f"box-shadow:0 6px 22px rgba(0,0,0,0.20),0 0 0 0 {color}'>"
        f"<div style='font-size:24px;margin-bottom:5px'>{icon}</div>"
        f"<div style='font-size:26px;font-weight:800;color:white;line-height:1'>{valor}</div>"
        f"<div style='font-size:9.5px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;"
        f"color:{color};margin-top:6px;opacity:0.90'>{label}</div>"
        f"</div>"
    )

def _fmt_fecha(v):
    try:
        return pd.to_datetime(v).strftime("%d/%m/%Y")
    except Exception:
        return str(v) if pd.notna(v) else "-"

_DEMO = pd.DataFrame([
    {"ID Novedad":"NOV-001","Estado":"Pendiente",  "Nombre":"Laura Sofía Ramírez",    "Cédula":"1012345678","Supervisor":"Ana Milena Carvajal",   "Tipo de novedad":"Tiempo real",  "Novedad específica":"Falla de sistema","Fecha inicio":"01/07/2026","Hora inicio":"08:15","Fecha fin":"01/07/2026","Hora fin":"09:00","Horas":"0:45","Comentarios":"Equipo sin conectividad"},
    {"ID Novedad":"NOV-002","Estado":"Aprobado",   "Nombre":"Carlos Andrés Moreno",   "Cédula":"1098765432","Supervisor":"Johan Sebastian López",   "Tipo de novedad":"Planificación","Novedad específica":"Cambio de turno","Fecha inicio":"02/07/2026","Hora inicio":"07:00","Fecha fin":"02/07/2026","Hora fin":"15:00","Horas":"8:00","Comentarios":"Aprobado por coordinación"},
    {"ID Novedad":"NOV-003","Estado":"Rechazado",  "Nombre":"María Camila Torres",    "Cédula":"1023456789","Supervisor":"Zully Paola Rodríguez",  "Tipo de novedad":"Históricas",  "Novedad específica":"Permiso médico", "Fecha inicio":"28/06/2026","Hora inicio":"10:00","Fecha fin":"28/06/2026","Hora fin":"14:00","Horas":"4:00","Comentarios":"Sin soporte adjunto"},
    {"ID Novedad":"NOV-004","Estado":"Aprobado",   "Nombre":"Andrés Felipe Gómez",    "Cédula":"1034567890","Supervisor":"Karen Julieth Barreto",   "Tipo de novedad":"Planificación","Novedad específica":"Licencia",       "Fecha inicio":"03/07/2026","Hora inicio":"06:00","Fecha fin":"05/07/2026","Hora fin":"15:00","Horas":"24:00","Comentarios":"Licencia por calamidad"},
    {"ID Novedad":"NOV-005","Estado":"Pendiente",  "Nombre":"Valentina Herrera Cruz",  "Cédula":"1045678901","Supervisor":"Camila Maldonado",        "Tipo de novedad":"Tiempo real",  "Novedad específica":"Ausente",        "Fecha inicio":"01/07/2026","Hora inicio":"06:55","Fecha fin":"01/07/2026","Hora fin":"15:00","Horas":"8:05","Comentarios":"No se reportó"},
    {"ID Novedad":"NOV-006","Estado":"Aprobado",   "Nombre":"Diego Fernando Ruiz",    "Cédula":"1056789012","Supervisor":"Ana Milena Carvajal",   "Tipo de novedad":"Históricas",  "Novedad específica":"Retiro",         "Fecha inicio":"25/06/2026","Hora inicio":"06:00","Fecha fin":"25/06/2026","Hora fin":"15:00","Horas":"9:00","Comentarios":"Procesado en nómina"},
])

def _render_tab(df: pd.DataFrame, acento: str):
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
    for c in ["Fecha inicio", "Fecha fin", "Fecha procesamiento"]:
        if c in df.columns:
            df[c] = df[c].apply(_fmt_fecha)

    # ── Filtros ──────────────────────────────────────
    fc1, fc2, fc3 = st.columns([2, 2, 3])
    with fc1:
        sups = ["Todos"] + sorted(df["Supervisor"].dropna().unique().tolist()) if "Supervisor" in df.columns else ["Todos"]
        sup_sel = st.selectbox("Supervisor", sups, key=f"sup_{acento}")
    with fc2:
        if "Tipo de novedad" in df.columns:
            tipos = ["Todos"] + sorted(df["Tipo de novedad"].dropna().unique().tolist())
            tipo_sel = st.selectbox("Tipo", tipos, key=f"tipo_{acento}")
        else:
            tipo_sel = "Todos"
    with fc3:
        buscar = st.text_input("Buscar", key=f"bus_{acento}",
                               placeholder="Nombre, cédula o novedad...")

    dff = df.copy()
    if sup_sel != "Todos" and "Supervisor" in dff.columns:
        dff = dff[dff["Supervisor"] == sup_sel]
    if tipo_sel != "Todos" and "Tipo de novedad" in dff.columns:
        dff = dff[dff["Tipo de novedad"] == tipo_sel]
    if buscar:
        mask = pd.Series(False, index=dff.index)
        for c in ["Nombre", "Cédula", "Novedad específica"]:
            if c in dff.columns:
                mask |= dff[c].astype(str).str.contains(buscar, case=False, na=False)
        dff = dff[mask]

    # ── KPIs ─────────────────────────────────────────
    total = len(dff)
    if "Estado" in dff.columns:
        estados = dff["Estado"].astype(str).str.strip()
        pend = (estados == "Pendiente").sum()
        apro = (estados == "Aprobado").sum()
        rech = (estados == "Rechazado").sum()
    else:
        pend = apro = rech = 0

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(_kpi_card("Total",       total, "#38BDF8", "📋"), unsafe_allow_html=True)
    k2.markdown(_kpi_card("Pendientes",  pend,  "#F59E0B", "⏳"), unsafe_allow_html=True)
    k3.markdown(_kpi_card("Aprobados",   apro,  "#34D399", "✅"), unsafe_allow_html=True)
    k4.markdown(_kpi_card("Rechazados",  rech,  "#EF4444", "❌"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    # ── Tabla ─────────────────────────────────────────
    _COLS = [c for c in [
        "ID Novedad", "Estado", "Nombre", "Cédula", "Supervisor",
        "Tipo de novedad", "Novedad específica",
        "Fecha inicio", "Hora inicio", "Fecha fin", "Hora fin",
        "Horas", "Comentarios",
    ] if c in dff.columns]

    st.dataframe(
        dff[_COLS].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        height=min(80 + len(dff) * 35, 500),
    )
    if es_demo:
        st.caption("👁️ Vista previa con datos de muestra — conectado a Google Sheets")
    else:
        st.caption(f"📋 {len(dff)} registros · Google Sheets en vivo · actualización cada 60 s")

# ─────────────────────────────────────────────
# AUTO-REFRESH
# ── Auto-refresh cada 60 s (sin dependencias externas) ───────────
st.markdown('<meta http-equiv="refresh" content="60">', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class='sbc'>
        <div class='sbc-orb sbc-orb-1'></div><div class='sbc-orb sbc-orb-2'></div><div class='sbc-orb sbc-orb-3'></div>
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
    * {{ font-family:'Inter',sans-serif !important; }}
    span[data-testid="stIconMaterial"],.material-symbols-rounded,.material-symbols-outlined,.material-icons {{
        font-family:'Material Symbols Rounded','Material Symbols Outlined','Material Icons' !important; }}
    [data-testid="stSidebarNav"] {{ display:none !important; }}

    .main {{
        background:
            radial-gradient(ellipse 55% 45% at 0% 0%,   rgba(14,165,233,0.07) 0%,transparent 55%),
            radial-gradient(ellipse 55% 45% at 100% 6%, rgba(139,92,246,0.07) 0%,transparent 55%),
            radial-gradient(ellipse 60% 50% at 90% 100%,rgba(52,211,153,0.05) 0%,transparent 55%),
            #0B0518;
        background-attachment:fixed;
    }}
    .block-container {{ padding-top:2rem;padding-bottom:1rem; }}

    [data-testid="stSidebarCollapseButton"] button,
    div[data-testid="collapsedControl"] button {{
        background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.10)!important;
        border-radius:10px!important;transition:all .2s ease!important; }}
    div[data-testid="collapsedControl"] button {{
        background:rgba(40,5,63,0.06)!important;border:1px solid rgba(40,5,63,0.15)!important; }}
    [data-testid="stSidebarCollapseButton"] button:hover,
    div[data-testid="collapsedControl"] button:hover {{ border-color:rgba(14,165,233,0.45)!important; }}
    [data-testid="stSidebarCollapseButton"] span {{ color:rgba(255,255,255,0.80)!important;font-size:20px!important; }}
    div[data-testid="collapsedControl"] span {{ color:{COLOR_PRIMARY}!important;font-size:20px!important; }}
    div[data-testid="stSidebarContent"] {{ width:100%!important;box-sizing:border-box!important;padding-right:0.75rem!important; }}
    div[data-testid="stSidebarContent"] > div {{ width:100%!important; }}

    section[data-testid="stSidebar"] > div:first-child {{
        background:
            radial-gradient(ellipse 95% 42% at 8% 0%,    rgba(14,165,233,0.30) 0%,transparent 55%),
            radial-gradient(ellipse 90% 42% at 100% 26%, rgba(129,140,248,0.28) 0%,transparent 55%),
            radial-gradient(ellipse 85% 42% at 50% 102%, rgba(52,211,153,0.15) 0%,transparent 55%),
            linear-gradient(160deg,#0B0518 0%,#14082b 45%,#0A0414 100%);
        border-right:1px solid rgba(255,255,255,0.07);
        display:flex!important;flex-direction:column!important;min-height:100vh!important;
    }}
    div[data-testid="stSidebarContent"] * {{ color:white !important; }}
    [data-testid="stSidebarHeader"] {{ padding-top:0.1rem!important;padding-bottom:0!important;min-height:0!important; }}
    [data-testid="stSidebarUserContent"] {{ padding-top:0!important;flex:1 1 auto!important;display:flex!important;flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] > div {{ flex:1 1 auto!important;display:flex!important;flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:last-of-type {{ margin-top:auto!important; }}
    section[data-testid="stSidebar"] .block-container {{ padding-top:0.5rem!important; }}

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

    /* ── Banner header ── */
    .st-key-hdrbanner {{
        position:relative;overflow:hidden;border-radius:20px;padding:18px 30px;margin-bottom:18px;
        background:
            radial-gradient(ellipse 70% 130% at 2% -15%,   rgba(14,165,233,0.34) 0%,transparent 60%),
            radial-gradient(ellipse 65% 130% at 100% 120%, rgba(129,140,248,0.34) 0%,transparent 60%),
            radial-gradient(ellipse 55% 110% at 72% 130%,  rgba(245,158,11,0.16) 0%,transparent 60%),
            linear-gradient(155deg,#0B0518 0%,#14082b 50%,#0A0414 100%);
        border:1px solid rgba(255,255,255,0.10);
        box-shadow:0 18px 46px -18px rgba(0,0,0,0.45),inset 0 1px 0 rgba(255,255,255,0.08);
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
        position:relative;z-index:2;white-space:nowrap!important;color:#CBD3F2!important;
        border-radius:9px!important;font-size:10px!important;font-weight:700!important;
        height:32px!important;min-height:32px!important;padding:0 11px!important;
        border:1px solid rgba(255,255,255,0.12)!important;
        background:linear-gradient(180deg,rgba(255,255,255,0.085),rgba(255,255,255,0.025))!important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.10),0 4px 12px -8px rgba(8,3,24,0.60)!important;
        transition:all .16s ease!important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button p {{ white-space:nowrap!important;margin:0!important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button:hover {{
        color:#FFF4E6!important;transform:translateY(-1px)!important;
        border-color:rgba(251,191,36,0.45)!important;
        background:linear-gradient(180deg,rgba(251,191,36,0.16),rgba(255,255,255,0.04))!important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"] {{
        color:#FFF8EE!important;padding-left:20px!important;
        border:1px solid rgba(245,158,11,0.55)!important;
        background:linear-gradient(180deg,rgba(245,158,11,0.32),rgba(251,146,60,0.18))!important;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.22),0 8px 22px -10px rgba(245,158,11,0.55)!important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"]::before {{
        content:"";position:absolute;left:8px;top:50%;transform:translateY(-50%);
        width:5px;height:5px;border-radius:50%;background:#FBBF24;box-shadow:0 0 8px rgba(251,191,36,0.9); }}

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

    /* ── Inputs ── */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stTextInput"] > div > div > input {{
        background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.12)!important;
        border-radius:10px!important;color:white!important; }}
    [data-testid="stSelectbox"] label,[data-testid="stTextInput"] label {{
        color:rgba(255,255,255,0.50)!important;font-size:12px!important;font-weight:600!important; }}
    [data-testid="stDataFrame"] {{ border-radius:14px;overflow:hidden; }}
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
        <span class='hb-chip'>🔄 Actualización automática · 60 s</span>
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

tab_rt, tab_plan, tab_hist = st.tabs([
    "🚨  Tiempo real",
    "🗓️  Planificación",
    "📁  Históricas",
])

with tab_rt:
    st.markdown(_sec_label("Novedades activas · turno en curso", "#EF4444"), unsafe_allow_html=True)
    with st.spinner("Conectando con Google Sheets..."):
        df_rt = _cargar_hoja("Tiempo real")
    _render_tab(df_rt, acento="rt")

with tab_plan:
    st.markdown(_sec_label("Novedades planificadas · próximos días", "#38BDF8"), unsafe_allow_html=True)
    with st.spinner("Conectando con Google Sheets..."):
        df_plan = _cargar_hoja("Planificación")
    _render_tab(df_plan, acento="plan")

with tab_hist:
    st.markdown(_sec_label("Registro histórico · novedades cerradas", "#34D399"), unsafe_allow_html=True)
    with st.spinner("Conectando con Google Sheets..."):
        df_hist = _cargar_hoja("Históricas")
    _render_tab(df_hist, acento="hist")
