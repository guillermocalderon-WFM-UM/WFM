import streamlit as st
import pandas as pd
import base64
import glob
import os

COLOR_PRIMARY = "#28053F"
COLOR_ACCENT  = "#0EA5E9"

# objetos de página (mismos parámetros que en Dashboard.py → switch_page funciona)
adh_pg = st.Page("pages/1_Adherencia.py", title="Adherencia", icon="🎯")
ocu_pg = st.Page("pages/2_Ocupacion.py",  title="Ocupación",  icon="📊")
nov_pg = st.Page("pages/3_Novedades.py",  title="Novedades",  icon="📢")

_MESES_ABR = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
              7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}


@st.cache_data(ttl=86400, show_spinner=False)
def _datos_adherencia_dia():
    """Estadísticas del último día con datos cargados en los Consolidado_*.xlsx.

    Se recalcula una vez al día (ttl=86400): misma fuente y fórmula que usa el módulo de Adherencia
    (ADH = suma de tiempo adherido / suma de tiempo programado), pero acotada al día más reciente
    en lugar del rango completo, para reflejar el desempeño más actual. Los Excel son pesados, así
    que se leen una sola vez y de aquí se derivan tanto el top de supervisores como el de asesores.
    """
    archivos = [f for f in glob.glob("Consolidado_*.xlsx") if "_O_" not in os.path.basename(f)]
    if not archivos:
        return None

    partes = []
    for archivo in archivos:
        try:
            partes.append(pd.read_excel(archivo, sheet_name="Detalle", engine="openpyxl"))
        except Exception:
            continue
    if not partes:
        return None

    df = pd.concat(partes, ignore_index=True)
    if "Fecha" not in df.columns or "Supervisor" not in df.columns or "Nombre" not in df.columns:
        return None
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])
    if df.empty:
        return None

    df["adh_s"]  = pd.to_timedelta(df["ADH aplicada"], errors="coerce").dt.total_seconds()
    df["prog_s"] = pd.to_timedelta(df["Tiempo programado"], errors="coerce").dt.total_seconds()

    ultimo_dia = df["Fecha"].max().normalize()
    dia = df[
        (df["Fecha"].dt.normalize() == ultimo_dia)
        & (df["prog_s"] > 0)
        & (df["Validador Llegada"] != "Ausente")
    ]
    if dia.empty:
        return None

    sup_sums = dia.groupby("Supervisor")[["adh_s", "prog_s"]].sum()
    top_sup = (
        (sup_sums["adh_s"] / sup_sums["prog_s"].where(sup_sums["prog_s"] > 0))
        .fillna(0)
        .reset_index(name="ADH")
        .sort_values("ADH", ascending=False)
    )
    if top_sup.empty:
        return None

    # Bottom 5 asesores con menor adherencia, excluyendo 0% (sin datos reales ese día, no bajo desempeño)
    ases_sums = dia.groupby(["Nombre", "Supervisor"])[["adh_s", "prog_s"]].sum()
    bottom_ases = (
        (ases_sums["adh_s"] / ases_sums["prog_s"].where(ases_sums["prog_s"] > 0))
        .fillna(0)
        .reset_index(name="ADH")
    )
    bottom_ases = bottom_ases[bottom_ases["ADH"] > 0].sort_values("ADH", ascending=True)

    total_prog = dia["prog_s"].sum()
    promedio_general = (dia["adh_s"].sum() / total_prog) if total_prog > 0 else 0

    return {
        "fecha": ultimo_dia,
        "top3_supervisores": top_sup.head(3).to_dict("records"),
        "bottom5_asesores": bottom_ases.head(5).to_dict("records"),
        "promedio_general": promedio_general,
    }

# ── Logo base64 ──────────────────────────
_LOGO_PATH = "logo-scala-learning-transformacion-digital-universidades.webp"
try:
    with open(_LOGO_PATH, "rb") as _f:
        _logo_b64 = base64.b64encode(_f.read()).decode()
    _logo_src = f"data:image/webp;base64,{_logo_b64}"
except FileNotFoundError:
    _logo_src = ""

# ── Sidebar ──────────────────────────────
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

# ── CSS ──────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');
    * {{ font-family: 'Inter', sans-serif !important; }}
    /* restaurar la fuente de íconos Material (si no, sale el texto "keyboard_double_arrow_left") */
    span[data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="collapsedControl"] span,
    .material-symbols-rounded, .material-symbols-outlined, .material-icons {{
        font-family: 'Material Symbols Rounded','Material Symbols Outlined','Material Icons' !important;
    }}

    /* ══ FONDO GENERAL OSCURO + AURORA ══ */
    [data-testid="stAppViewContainer"] {{
        background:
            radial-gradient(ellipse 110% 70% at 8% -10%,  rgba(14,165,233,0.15) 0%, transparent 60%),
            radial-gradient(ellipse 100% 65% at 100% 0%,  rgba(99,102,241,0.15) 0%, transparent 60%),
            radial-gradient(ellipse 90% 70% at 85% 105%,  rgba(52,211,153,0.08) 0%, transparent 60%),
            radial-gradient(ellipse 80% 60% at 0% 100%,   rgba(99,102,241,0.07) 0%, transparent 60%),
            linear-gradient(160deg, #0A0813 0%, #0F0B20 45%, #08060F 100%);
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    .block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1180px; }}

    /* malla de puntos sutil sobre el fondo */
    [data-testid="stAppViewContainer"]::before {{
        content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
        background-image: radial-gradient(circle, rgba(255,255,255,0.035) 1px, transparent 1px);
        background-size: 34px 34px;
        mask-image: radial-gradient(ellipse 80% 80% at 50% 30%, black 0%, transparent 75%);
        -webkit-mask-image: radial-gradient(ellipse 80% 80% at 50% 30%, black 0%, transparent 75%);
    }}
    [data-testid="stAppViewContainer"] > .main {{ position: relative; z-index: 1; }}

    /* botón para colapsar el sidebar: ícono limpio, sin texto crudo */
    [data-testid="stSidebarCollapseButton"] button,
    div[data-testid="collapsedControl"] button {{
        background:rgba(255,255,255,0.06)!important;border:1px solid rgba(255,255,255,0.10)!important;
        border-radius:10px!important;transition:all .2s ease!important; }}
    [data-testid="stSidebarCollapseButton"] button:hover,
    div[data-testid="collapsedControl"] button:hover {{
        background:rgba(255,255,255,0.14)!important;border-color:rgba(56,189,248,0.4)!important; }}
    [data-testid="stSidebarCollapseButton"] span,
    div[data-testid="collapsedControl"] span {{ color:rgba(255,255,255,0.75)!important;font-size:20px!important; }}
    div[data-testid="stSidebarContent"] {{ width:100%!important;box-sizing:border-box!important;padding-right:0.75rem!important; }}
    div[data-testid="stSidebarContent"] > div {{ width:100%!important; }}

    /* ══ SIDEBAR · mismo fondo de diseño que el hero (sin grid) ══ */
    section[data-testid="stSidebar"] > div:first-child {{
        background:
            radial-gradient(ellipse 95% 42% at 8% 0%,    rgba(14,165,233,0.30) 0%, transparent 55%),
            radial-gradient(ellipse 90% 42% at 100% 26%, rgba(129,140,248,0.28) 0%, transparent 55%),
            radial-gradient(ellipse 85% 42% at 50% 102%, rgba(52,211,153,0.15) 0%, transparent 55%),
            linear-gradient(160deg, #0B0518 0%, #14082b 45%, #0A0414 100%);
        border-right: 1px solid rgba(255,255,255,0.07);
    }}
    div[data-testid="stSidebarContent"] * {{ color: white !important; }}

    /* ══ Scala bien arriba + footer pegado al fondo del sidebar ══ */
    [data-testid="stSidebarHeader"] {{ padding-top:0.1rem!important; padding-bottom:0!important; min-height:0!important; }}
    section[data-testid="stSidebar"] .block-container {{ padding-top:0.5rem!important; padding-bottom:0.8rem!important; }}
    /* toda la cadena del sidebar a altura completa para poder anclar abajo */
    section[data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarContent"] {{
        display:flex!important; flex-direction:column!important; min-height:100vh!important; }}
    [data-testid="stSidebarUserContent"] {{
        flex:1 1 auto!important; display:flex!important; flex-direction:column!important;
        padding-top:0!important; padding-bottom:0!important; }}
    [data-testid="stSidebarUserContent"] > div,
    [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {{
        flex:1 1 auto!important; display:flex!important; flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:last-of-type {{
        margin-top:auto!important; margin-bottom:32px!important; }}

    /* ══ ANIMATIONS ══ */
    @keyframes sbcBar {{ 0% {{ background-position:0% 0%; }} 100% {{ background-position:200% 0%; }} }}
    @keyframes sbcPulse {{ 0%,100% {{ opacity:1; transform:scale(1); }} 50% {{ opacity:.3; transform:scale(.6); }} }}
    @keyframes float {{ 0%,100% {{ transform:translateY(0px); }} 50% {{ transform:translateY(-9px); }} }}
    @keyframes fadeUp {{ from {{ opacity:0; transform:translateY(28px); }} to {{ opacity:1; transform:translateY(0); }} }}
    @keyframes shimmer {{ 0% {{ background-position:-200% 0; }} 100% {{ background-position:200% 0; }} }}
    @keyframes auroraMove {{
        0%   {{ transform:translate(0,0) scale(1);        }}
        33%  {{ transform:translate(40px,-30px) scale(1.15); }}
        66%  {{ transform:translate(-30px,25px) scale(0.92); }}
        100% {{ transform:translate(0,0) scale(1);        }}
    }}
    @keyframes ring {{ 0% {{ transform:scale(.85); opacity:.55; }} 100% {{ transform:scale(1.7); opacity:0; }} }}

    /* ══ BRAND CARD (sidebar) ══ */
    .sbc {{ position:relative;border-radius:20px;overflow:hidden;margin:-18px 0 20px;padding:20px 18px 18px;
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
    .sbc-body {{ position:relative;z-index:1;text-align:center; }}
    .sbc-logo-wrap {{ margin-bottom:10px;display:flex;justify-content:center;align-items:center; }}
    .sbc-logo-img {{ max-width:150px!important;height:auto!important;filter:drop-shadow(0 4px 14px rgba(56,189,248,0.45)) brightness(1.05);display:block; }}
    .sbc-name {{ font-size:13px!important;font-weight:700!important;color:rgba(255,255,255,0.88)!important;letter-spacing:0!important;margin-bottom:4px!important; }}
    .sbc-org  {{ font-size:10px!important;color:rgba(255,255,255,0.35)!important;margin-bottom:16px!important; }}
    .sbc-stats {{ display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.22);border-radius:12px;padding:10px 8px;border:1px solid rgba(255,255,255,0.07); }}
    .sbc-stat {{ flex:1;text-align:center; }}
    .sbc-sv {{ display:block;font-size:14px!important;font-weight:900!important;color:white!important;line-height:1;margin-bottom:3px; }}
    .sbc-sl  {{ display:block;font-size:8px!important;font-weight:700!important;color:rgba(255,255,255,0.28)!important;letter-spacing:0.10em;text-transform:uppercase; }}
    .sbc-sep {{ width:1px;height:28px;background:rgba(255,255,255,0.09);flex-shrink:0; }}
    .sbc-bar {{ position:absolute;bottom:0;left:0;right:0;height:3px;
                background:linear-gradient(90deg,#38BDF8,#818CF8,#34D399,#F59E0B,#38BDF8);
                background-size:300% 100%;animation:sbcBar 4s linear infinite; }}
    .sbf {{ margin-top:26px;padding:0; }}
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

    /* ══════════ HERO ══════════ */
    .hero {{
        position:relative; border-radius:28px; overflow:hidden;
        padding:34px 50px 30px; text-align:center; margin-bottom:20px;
        background:
            linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%);
        border:1px solid rgba(255,255,255,0.11);
        box-shadow:0 32px 90px rgba(0,0,0,0.50), inset 0 1px 0 rgba(255,255,255,0.12);
        backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
        animation:fadeUp 0.7s ease both;
    }}
    .hero-aurora {{ position:absolute; border-radius:50%; filter:blur(52px); pointer-events:none; z-index:0; }}
    .ha1 {{ width:420px;height:420px;background:radial-gradient(circle,rgba(14,165,233,0.52),transparent 65%);top:-160px;left:-110px;animation:auroraMove 14s ease-in-out infinite; }}
    .ha2 {{ width:380px;height:380px;background:radial-gradient(circle,rgba(129,140,248,0.48),transparent 65%);bottom:-170px;right:-80px;animation:auroraMove 18s ease-in-out infinite reverse; }}
    .ha3 {{ width:280px;height:280px;background:radial-gradient(circle,rgba(52,211,153,0.35),transparent 65%);top:25%;right:15%;animation:auroraMove 22s ease-in-out infinite; }}
    .ha4 {{ width:220px;height:220px;background:radial-gradient(circle,rgba(245,158,11,0.28),transparent 65%);bottom:-80px;left:10%;animation:auroraMove 26s ease-in-out infinite reverse; }}
    .hero::before {{
        content:''; position:absolute; inset:0; z-index:0;
        background-image:linear-gradient(rgba(255,255,255,0.045) 1px,transparent 1px),
                         linear-gradient(90deg,rgba(255,255,255,0.045) 1px,transparent 1px);
        background-size:44px 44px;
        mask-image:radial-gradient(ellipse 75% 75% at 50% 40%,black,transparent 82%);
        -webkit-mask-image:radial-gradient(ellipse 75% 75% at 50% 40%,black,transparent 82%);
    }}
    .hero-inner {{ position:relative; z-index:1; }}
    .hero-badge {{ display:inline-flex;align-items:center;gap:9px;
        background:rgba(52,211,153,0.08);
        border:1px solid rgba(52,211,153,0.28);
        border-radius:99px;padding:7px 20px;margin-bottom:28px;
        font-size:10.5px;font-weight:700;color:rgba(255,255,255,0.82);
        letter-spacing:0.14em;text-transform:uppercase;
        box-shadow:0 4px 22px rgba(0,0,0,0.28), 0 0 18px -6px rgba(52,211,153,0.30); }}
    .hero-badge-dot {{ position:relative;width:8px;height:8px; }}
    .hero-badge-dot::after {{ content:'';position:absolute;inset:0;border-radius:50%;background:#34D399; }}
    .hero-badge-dot::before {{ content:'';position:absolute;inset:0;border-radius:50%;border:2px solid #34D399;animation:ring 1.8s ease-out infinite; }}
    .hero-title {{ font-family:'Space Grotesk',sans-serif!important;
        font-size:44px;font-weight:800;color:white;margin:0 0 12px;
        letter-spacing:-1.8px;line-height:1.04;text-shadow:0 4px 44px rgba(0,0,0,0.45); }}
    .hero-title .grad {{ background:linear-gradient(90deg,#38BDF8 0%,#818CF8 35%,#34D399 70%,#38BDF8 100%);
        background-size:220% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;animation:shimmer 4s linear infinite; }}
    .hero-sub {{ font-size:15px;color:rgba(255,255,255,0.62);max-width:580px;
        margin:0 auto 0;line-height:1.68;font-weight:400; }}

    /* ══ SECTION LABEL ══ */
    .sec-lbl {{ display:flex;align-items:center;gap:12px;margin:38px 0 20px;
        font-size:11px;font-weight:800;letter-spacing:0.16em;text-transform:uppercase;
        color:rgba(255,255,255,0.45); }}
    .sec-lbl::before {{ content:'';width:26px;height:2px;border-radius:2px;
        background:linear-gradient(90deg,#38BDF8,#818CF8); }}
    .sec-lbl::after {{ content:'';flex:1;height:1px;
        background:linear-gradient(90deg,rgba(255,255,255,0.14),transparent); }}

    /* ══ MODULE CARDS ══ */
    .mod {{ position:relative;border-radius:24px;overflow:hidden;
        padding:34px 30px 26px;display:flex;flex-direction:column;height:100%;
        background:linear-gradient(160deg,rgba(255,255,255,0.075) 0%,rgba(255,255,255,0.02) 100%);
        border:1px solid rgba(255,255,255,0.10);
        box-shadow:0 20px 50px rgba(0,0,0,0.35),inset 0 1px 0 rgba(255,255,255,0.08);
        backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
        transition:transform .3s cubic-bezier(.2,.8,.2,1),box-shadow .3s ease,border-color .3s ease;
        animation:fadeUp .8s ease both; }}
    .mod:hover {{ transform:translateY(-8px);
        border-color:var(--glow,rgba(255,255,255,0.25));
        box-shadow:0 32px 70px rgba(0,0,0,0.5),0 0 0 1px var(--glow,transparent),
                   0 0 50px -8px var(--glow,transparent); }}
    .mod-glow {{ position:absolute;top:-60px;right:-60px;width:200px;height:200px;border-radius:50%;
        background:radial-gradient(circle,var(--accent),transparent 70%);opacity:.16;pointer-events:none; }}
    .mod-head {{ display:flex;align-items:flex-start;justify-content:space-between;
        position:relative;z-index:1;margin-bottom:18px; }}
    .mod-ico {{ position:relative;width:64px;height:64px;border-radius:18px;
        display:flex;align-items:center;justify-content:center;font-size:30px;flex-shrink:0;
        background:var(--icobg);border:1px solid var(--glow,rgba(255,255,255,0.12));
        animation:float 3.8s ease-in-out infinite;
        box-shadow:0 10px 30px -6px var(--glow,transparent); }}
    .mod-badge {{ display:inline-flex;align-items:center;gap:6px;
        font-size:9.5px;font-weight:800;padding:5px 11px;border-radius:99px;
        letter-spacing:0.08em;text-transform:uppercase; }}
    .mod-badge-dot {{ width:6px;height:6px;border-radius:50%; }}
    .mod-title {{ font-family:'Space Grotesk',sans-serif!important;
        font-size:25px;font-weight:700;color:white;margin:0 0 9px;
        letter-spacing:-0.5px;position:relative;z-index:1; }}
    .mod-desc {{ font-size:13.5px;color:rgba(255,255,255,0.55);line-height:1.7;
        margin:0 0 22px;position:relative;z-index:1; }}
    .mod-feats {{ display:flex;flex-direction:column;gap:11px;margin-bottom:26px;
        position:relative;z-index:1; }}
    .mfeat {{ display:flex;align-items:center;gap:11px;font-size:12.5px;
        color:rgba(255,255,255,0.72);font-weight:500; }}
    .mfeat-ck {{ width:19px;height:19px;border-radius:6px;flex-shrink:0;
        display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:900;
        background:var(--icobg);color:var(--accent-solid);border:1px solid var(--glow,rgba(255,255,255,0.12)); }}
    .mod-div {{ height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.12),transparent);
        margin:0 0 16px;position:relative;z-index:1; }}
    .mod-foot {{ display:flex;align-items:flex-end;justify-content:space-between;gap:14px;
        margin-bottom:22px;position:relative;z-index:1; }}
    .mod-chips {{ display:flex;flex-direction:column;gap:7px; }}
    .mchip {{ display:inline-flex;align-items:center;gap:6px;align-self:flex-start;
        font-size:10.5px;font-weight:700;padding:5px 10px;border-radius:8px;
        background:var(--icobg);color:rgba(255,255,255,0.82);
        border:1px solid var(--glow,rgba(255,255,255,0.12)); }}
    .mchip b {{ color:var(--accent-solid);font-weight:800; }}
    .mspark {{ display:flex;align-items:flex-end;gap:4px;height:46px;padding:0 2px; }}
    .mspark span {{ width:7px;border-radius:4px;background:var(--accent);
        opacity:.55;transform-origin:bottom;transition:transform .4s cubic-bezier(.2,.8,.2,1),opacity .3s ease; }}
    .mod:hover .mspark span {{ opacity:.95;transform:scaleY(1.18); }}

    /* ══ BUTTONS ══ */
    div[data-testid="stButton"] > button {{
        border-radius:14px!important;font-weight:700!important;font-size:14px!important;
        height:50px!important;letter-spacing:0.01em!important;
        transition:transform .2s ease,box-shadow .2s ease,filter .2s ease!important; }}
    div[data-testid="stButton"] > button[kind="primary"] {{
        background:linear-gradient(120deg,#0EA5E9 0%,#6366F1 55%,#8B5CF6 100%)!important;
        background-size:160% auto!important;color:white!important;border:none!important;
        box-shadow:0 10px 30px -6px rgba(99,102,241,0.6)!important; }}
    div[data-testid="stButton"] > button[kind="primary"]:hover {{
        transform:translateY(-3px)!important;filter:brightness(1.08)!important;
        box-shadow:0 16px 40px -8px rgba(99,102,241,0.75)!important; }}
    div[data-testid="stButton"] > button[kind="secondary"] {{
        background:rgba(255,255,255,0.05)!important;color:rgba(255,255,255,0.80)!important;
        border:1px solid rgba(255,255,255,0.18)!important; }}
    div[data-testid="stButton"] > button[kind="secondary"]:hover {{
        background:rgba(139,92,246,0.16)!important;border-color:rgba(167,139,250,0.6)!important;
        color:white!important;transform:translateY(-3px)!important;
        box-shadow:0 14px 34px -10px rgba(139,92,246,0.6)!important; }}

    /* ══ STATS STRIP ══ */
    .stats {{ display:flex;gap:16px;margin-top:34px;animation:fadeUp 1s ease both; }}
    .stat {{ flex:1;position:relative;overflow:hidden;border-radius:18px;padding:24px 18px;
        text-align:center;background:linear-gradient(160deg,rgba(255,255,255,0.06),rgba(255,255,255,0.015));
        border:1px solid rgba(255,255,255,0.09);
        box-shadow:0 12px 30px rgba(0,0,0,0.3),inset 0 1px 0 rgba(255,255,255,0.06);
        transition:transform .25s ease,border-color .25s ease; }}
    .stat:hover {{ transform:translateY(-4px);border-color:var(--sc); }}
    .stat::after {{ content:'';position:absolute;bottom:0;left:50%;transform:translateX(-50%);
        width:60%;height:2px;background:var(--sc);border-radius:2px;opacity:.7; }}
    .stat-ico {{ font-size:18px;margin-bottom:8px;opacity:.9; }}
    .stat-val {{ font-family:'Space Grotesk',sans-serif!important;
        font-size:30px;font-weight:700;color:white;line-height:1;margin-bottom:6px; }}
    .stat-lbl {{ font-size:10px;font-weight:700;color:rgba(255,255,255,0.42);
        text-transform:uppercase;letter-spacing:0.10em; }}

    /* ══ Ocultar el menú automático del sidebar ══ */
    [data-testid="stSidebarNav"] {{ display:none !important; }}

    /* ══ HERO · separador y tarjetas de estado ══ */
    .hero-divider {{ width:56px;height:1.5px;margin:22px auto 20px;border-radius:2px;
        background:linear-gradient(90deg,transparent,rgba(56,189,248,0.55),rgba(129,140,248,0.55),transparent); }}
    .hero-cards {{ display:flex;justify-content:center;gap:10px;flex-wrap:wrap; }}
    .hcard {{ display:flex;align-items:center;gap:13px;min-width:148px;
        background:rgba(255,255,255,0.05);
        border:1px solid rgba(255,255,255,0.09);
        border-top:2px solid var(--hc,rgba(56,189,248,0.50));
        border-radius:16px;padding:14px 20px;
        backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
        box-shadow:0 8px 28px rgba(0,0,0,0.22),inset 0 1px 0 rgba(255,255,255,0.07);
        transition:transform .24s cubic-bezier(.2,.8,.2,1),box-shadow .24s ease,background .24s ease; }}
    .hcard:hover {{ transform:translateY(-5px);background:rgba(255,255,255,0.09);
        box-shadow:0 18px 44px rgba(0,0,0,0.32),0 0 0 1px var(--hc,rgba(56,189,248,0.28)),
                   0 0 24px -8px var(--hc,rgba(56,189,248,0.28)); }}
    .hcard-ico {{ width:44px;height:44px;border-radius:13px;flex-shrink:0;
        display:flex;align-items:center;justify-content:center;font-size:20px;
        background:var(--hc-bg,rgba(56,189,248,0.12));
        border:1px solid var(--hc,rgba(56,189,248,0.22));
        box-shadow:0 4px 16px -4px var(--hc,rgba(56,189,248,0.30)); }}
    .hcard-txt {{ text-align:left; }}
    .hcard-lbl {{ font-size:8.5px;font-weight:700;letter-spacing:0.13em;text-transform:uppercase;
        color:var(--hc,rgba(56,189,248,0.80));margin-bottom:4px;display:block; }}
    .hcard-val {{ font-size:15px;font-weight:800;color:white;line-height:1;display:block; }}
    .hcard-val .dot {{ display:inline-block;width:7px;height:7px;border-radius:50%;background:#34D399;
        box-shadow:0 0 10px #34D399;margin-right:6px;animation:sbcPulse 1.8s ease-in-out infinite; }}

    /* ══ TICKER EN VIVO ══ */
    @keyframes nticker {{ 0% {{ transform:translateX(0); }} 100% {{ transform:translateX(-50%); }} }}
    .nticker-shell {{ display:flex;align-items:stretch;overflow:hidden;border-radius:14px;
        background:rgba(245,158,11,0.04);
        border:1px solid rgba(245,158,11,0.22);
        box-shadow:0 0 30px -8px rgba(245,158,11,0.12),inset 0 1px 0 rgba(255,255,255,0.06);
        margin:24px 0 0; }}
    .nticker-label {{ flex-shrink:0;display:flex;align-items:center;gap:8px;
        padding:12px 18px;font-size:8.5px;font-weight:800;letter-spacing:0.18em;
        text-transform:uppercase;color:#F59E0B;
        background:linear-gradient(135deg,rgba(245,158,11,0.18),rgba(245,158,11,0.08));
        border-right:1px solid rgba(245,158,11,0.22); }}
    .nticker-dot {{ width:7px;height:7px;border-radius:50%;background:#F59E0B;
        box-shadow:0 0 8px #F59E0B;
        animation:sbcPulse 1.8s ease-in-out infinite;flex-shrink:0; }}
    .nticker-track {{ overflow:hidden;flex:1;
        mask-image:linear-gradient(90deg,transparent 0%,black 5%,black 95%,transparent 100%);
        -webkit-mask-image:linear-gradient(90deg,transparent 0%,black 5%,black 95%,transparent 100%); }}
    .nticker-inner {{ display:flex;width:max-content;
        animation:nticker 38s linear infinite;padding:12px 0; }}
    .nticker-inner:hover {{ animation-play-state:paused; }}
    .nticker-item {{ display:flex;align-items:center;gap:10px;
        padding:0 48px;white-space:nowrap;
        font-size:13px;color:rgba(255,255,255,0.68);font-weight:500; }}
    .nticker-sep {{ color:rgba(245,158,11,0.35);font-size:18px;margin-left:6px; }}
    .ntag {{ font-size:8px;font-weight:800;padding:3px 8px;border-radius:5px;
        text-transform:uppercase;letter-spacing:0.09em;flex-shrink:0; }}
    .ntag-a {{ background:rgba(244,63,94,0.18);color:#FB7185;border:1px solid rgba(244,63,94,0.28); }}
    .ntag-u {{ background:rgba(14,165,233,0.18);color:#38BDF8;border:1px solid rgba(14,165,233,0.28); }}
    .ntag-n {{ background:rgba(52,211,153,0.18);color:#34D399;border:1px solid rgba(52,211,153,0.28); }}
    .ntag-p {{ background:rgba(245,158,11,0.18);color:#FCD34D;border:1px solid rgba(245,158,11,0.28); }}

    /* ══ NEWS GRID ══ */
    .nws-grid {{ display:grid;grid-template-columns:1.6fr 1fr;
        grid-template-rows:1fr 1fr;gap:14px;
        margin:20px 0 34px;animation:fadeUp 1.05s ease both; }}

    /* BASE CARD */
    .ncard {{ position:relative;overflow:hidden;border-radius:22px;
        padding:24px 26px;display:flex;flex-direction:column;
        border:1px solid rgba(255,255,255,0.08);
        box-shadow:0 14px 36px rgba(0,0,0,0.30),inset 0 1px 0 rgba(255,255,255,0.06);
        backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
        transition:transform .30s cubic-bezier(.2,.8,.2,1),box-shadow .30s ease,border-color .30s ease; }}

    /* Color-coded small cards */
    .ncard-nuevo {{ background:linear-gradient(145deg,rgba(14,165,233,0.09) 0%,rgba(14,165,233,0.02) 60%,rgba(255,255,255,0.01) 100%);
        border-left:3px solid rgba(14,165,233,0.60); }}
    .ncard-nuevo:hover {{ transform:translateY(-5px);border-color:rgba(14,165,233,0.55);
        box-shadow:0 22px 52px rgba(0,0,0,0.38),-4px 0 28px -6px rgba(14,165,233,0.22),inset 0 1px 0 rgba(255,255,255,0.08); }}
    .ncard-logro {{ background:linear-gradient(145deg,rgba(52,211,153,0.09) 0%,rgba(52,211,153,0.02) 60%,rgba(255,255,255,0.01) 100%);
        border-left:3px solid rgba(52,211,153,0.60); }}
    .ncard-logro:hover {{ transform:translateY(-5px);border-color:rgba(52,211,153,0.55);
        box-shadow:0 22px 52px rgba(0,0,0,0.38),-4px 0 28px -6px rgba(52,211,153,0.22),inset 0 1px 0 rgba(255,255,255,0.08); }}
    .ncard-potenciar {{ background:linear-gradient(145deg,rgba(245,158,11,0.09) 0%,rgba(245,158,11,0.02) 60%,rgba(255,255,255,0.01) 100%);
        border-left:3px solid rgba(245,158,11,0.55); }}
    .ncard-potenciar:hover {{ transform:translateY(-5px);border-color:rgba(245,158,11,0.55);
        box-shadow:0 22px 52px rgba(0,0,0,0.38),-4px 0 28px -6px rgba(245,158,11,0.22),inset 0 1px 0 rgba(255,255,255,0.08); }}

    /* FEATURED CARD (Logro del día) */
    .ncard-feat {{ grid-row:1/3;padding:0;
        background:linear-gradient(160deg,rgba(52,211,153,0.13) 0%,rgba(52,211,153,0.04) 45%,rgba(14,165,233,0.07) 100%);
        border-color:rgba(52,211,153,0.26);
        box-shadow:0 20px 60px rgba(0,0,0,0.40),0 0 0 1px rgba(52,211,153,0.10),inset 0 1px 0 rgba(255,255,255,0.08); }}
    .ncard-feat::before {{ content:'';position:absolute;top:0;left:15%;right:15%;height:1px;
        background:linear-gradient(90deg,transparent,rgba(52,211,153,0.75),transparent);z-index:2; }}
    .ncard-feat:hover {{ transform:translateY(-6px);border-color:rgba(52,211,153,0.52);
        box-shadow:0 32px 80px rgba(0,0,0,0.50),0 0 50px -10px rgba(52,211,153,0.22),inset 0 1px 0 rgba(255,255,255,0.10); }}

    /* Abstract viz header inside featured */
    .ncard-vis {{ position:relative;overflow:hidden;height:88px;margin:0;
        background:
            radial-gradient(ellipse 60% 100% at 15% 50%,rgba(14,165,233,0.38) 0%,transparent 65%),
            radial-gradient(ellipse 50% 100% at 82% 30%,rgba(52,211,153,0.32) 0%,transparent 60%),
            radial-gradient(ellipse 45% 100% at 55% 90%,rgba(129,140,248,0.26) 0%,transparent 60%),
            linear-gradient(135deg,rgba(52,211,153,0.06),rgba(14,165,233,0.04));
        flex-shrink:0; }}
    .ncard-vis::before {{ content:'';position:absolute;inset:0;
        background-image:linear-gradient(rgba(255,255,255,0.055) 1px,transparent 1px),
                         linear-gradient(90deg,rgba(255,255,255,0.055) 1px,transparent 1px);
        background-size:20px 20px; }}
    .ncard-vis::after {{ content:'';position:absolute;bottom:0;left:0;right:0;height:40px;
        background:linear-gradient(to bottom,transparent,rgba(10,8,19,0.65)); }}

    .ncard-feat-body {{ padding:28px 30px 26px;display:flex;flex-direction:column;flex:1;position:relative; }}
    .ncard-ghost {{ position:absolute;bottom:-30px;right:-18px;
        font-family:'Space Grotesk',sans-serif;font-size:210px;font-weight:900;
        line-height:1;color:rgba(52,211,153,0.058);pointer-events:none;
        user-select:none;letter-spacing:-12px;z-index:0;transform:rotate(-5deg); }}

    /* Card content elements */
    .ncard-eyebrow {{ display:flex;align-items:center;gap:9px;
        margin-bottom:12px;position:relative;z-index:1; }}
    .ncard-date {{ font-size:10px;font-weight:600;letter-spacing:0.07em;
        color:rgba(255,255,255,0.30);text-transform:uppercase; }}
    .ncard-title-feat {{ font-family:'Space Grotesk',sans-serif;
        font-size:23px;font-weight:700;color:white;
        line-height:1.26;letter-spacing:-0.5px;
        margin-bottom:13px;position:relative;z-index:1; }}
    .ncard-body {{ font-size:13px;color:rgba(255,255,255,0.46);
        line-height:1.68;flex:1;position:relative;z-index:1;margin-bottom:20px; }}
    .ncard-title {{ font-size:14px;font-weight:700;color:rgba(255,255,255,0.88);
        line-height:1.38;letter-spacing:-0.15px;position:relative;z-index:1; }}
    .ncard-body-sm {{ font-size:12.5px;color:rgba(255,255,255,0.44);
        line-height:1.60;position:relative;z-index:1;margin-top:8px;flex:1; }}

    .ncard-footer {{ display:flex;align-items:center;gap:11px;
        padding:16px 0 0;border-top:1px solid rgba(255,255,255,0.08);
        position:relative;z-index:1; }}
    .ncard-avatar {{ width:34px;height:34px;border-radius:10px;flex-shrink:0;
        background:linear-gradient(135deg,#34D399 0%,#10B981 100%);
        display:flex;align-items:center;justify-content:center;font-size:16px;
        box-shadow:0 6px 16px rgba(52,211,153,0.40); }}
    .ncard-byline {{ font-size:10.5px;color:rgba(255,255,255,0.36);line-height:1.35; }}
    .ncard-byline strong {{ font-size:12px;font-weight:700;
        color:rgba(255,255,255,0.75);display:block;margin-bottom:1px; }}
    .ncard-arrow {{ margin-left:auto;width:34px;height:34px;border-radius:10px;
        background:rgba(52,211,153,0.12);border:1px solid rgba(52,211,153,0.25);
        display:flex;align-items:center;justify-content:center;
        font-size:16px;color:#34D399;flex-shrink:0;
        transition:transform .22s ease,background .22s ease,box-shadow .22s ease; }}
    .ncard-feat:hover .ncard-arrow {{ transform:translateX(3px);
        background:rgba(52,211,153,0.22);box-shadow:0 6px 18px -4px rgba(52,211,153,0.40); }}
</style>
""", unsafe_allow_html=True)

# ── HERO ─────────────────────────────────
st.markdown("""
<div class='hero'>
    <div class='hero-aurora ha1'></div>
    <div class='hero-aurora ha2'></div>
    <div class='hero-aurora ha3'></div>
    <div class='hero-aurora ha4'></div>
    <div class='hero-inner'>
        <div class='hero-badge'>
            <span class='hero-badge-dot'></span>
            Centro de Control · Uniminuto · 2026
        </div>
        <div class='hero-title'>
            Workforce<br><span class='grad'>Management</span>
        </div>
        <div class='hero-sub'>
            Plataforma inteligente de análisis y seguimiento del equipo de expertos.
            Monitorea <b style='color:rgba(255,255,255,0.85)'>adherencia</b>,
            <b style='color:rgba(255,255,255,0.85)'>ocupación</b> y desempeño operativo en tiempo real.
        </div>
        <div class='hero-divider'></div>
        <div class='hero-cards'>
            <div class='hcard' style='--hc:rgba(52,211,153,0.70);--hc-bg:rgba(52,211,153,0.13)'>
                <div class='hcard-ico'>⚡</div>
                <div class='hcard-txt'>
                    <span class='hcard-lbl'>Estado del sistema</span>
                    <span class='hcard-val'><span class='dot'></span>En línea</span>
                </div>
            </div>
            <div class='hcard' style='--hc:rgba(56,189,248,0.70);--hc-bg:rgba(56,189,248,0.13)'>
                <div class='hcard-ico'>◈</div>
                <div class='hcard-txt'>
                    <span class='hcard-lbl'>Seguimiento</span>
                    <span class='hcard-val'>Por equipo</span>
                </div>
            </div>
            <div class='hcard' style='--hc:rgba(129,140,248,0.70);--hc-bg:rgba(129,140,248,0.13)'>
                <div class='hcard-ico'>◷</div>
                <div class='hcard-txt'>
                    <span class='hcard-lbl'>Período activo</span>
                    <span class='hcard-val'>2026</span>
                </div>
            </div>
            <div class='hcard' style='--hc:rgba(245,158,11,0.70);--hc-bg:rgba(245,158,11,0.13)'>
                <div class='hcard-ico'>✦</div>
                <div class='hcard-txt'>
                    <span class='hcard-lbl'>Alianza</span>
                    <span class='hcard-val'>Uniminuto</span>
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── NOTICIAS ─────────────────────────────
_datos_dia = _datos_adherencia_dia()
_medallas = ["🥇", "🥈", "🥉"]

if _datos_dia:
    _fecha_dia = _datos_dia["fecha"]
    _fecha_str = f"{_fecha_dia.day:02d} {_MESES_ABR[_fecha_dia.month]} {_fecha_dia.year}"

    _lineas_top3 = "".join(
        f"{_medallas[i]} <b style='color:rgba(255,255,255,0.85)'>{row['Supervisor']}</b> · {row['ADH'] * 100:.1f}%<br>"
        for i, row in enumerate(_datos_dia["top3_supervisores"])
    )
    _promedio_str = f"{_datos_dia['promedio_general'] * 100:.1f}%"
    _top1_nombre = _datos_dia["top3_supervisores"][0]["Supervisor"]
    _top1_pct = f"{_datos_dia['top3_supervisores'][0]['ADH'] * 100:.1f}"
    _ticker_logro = f"{_fecha_str} — {_top1_nombre} lidera adherencia con {_top1_pct}%"

    _bottom5 = _datos_dia["bottom5_asesores"]
    if _bottom5:
        _lineas_bottom5 = "".join(
            f"<b style='color:rgba(255,255,255,0.75)'>{i + 1}.</b> {row['Nombre']} · "
            f"<span style='color:#FCD34D'>{row['ADH'] * 100:.1f}%</span><br>"
            for i, row in enumerate(_bottom5)
        )
        _ticker_potenciar = f"{_fecha_str} — {len(_bottom5)} asesores por debajo de la meta necesitan refuerzo"
    else:
        _lineas_bottom5 = "<span style='color:rgba(255,255,255,0.40)'>Sin suficientes datos para el ranking de hoy.</span>"
        _ticker_potenciar = "Aún no hay suficientes datos para el ranking de refuerzo"
else:
    _fecha_str = "Sin datos"
    _lineas_top3 = "<span style='color:rgba(255,255,255,0.40)'>Aún no hay datos de adherencia cargados para calcular el ranking del día.</span>"
    _promedio_str = "—"
    _ticker_logro = "Aún no hay datos de adherencia cargados"
    _lineas_bottom5 = "<span style='color:rgba(255,255,255,0.40)'>Aún no hay datos de adherencia cargados.</span>"
    _ticker_potenciar = "Aún no hay datos de adherencia cargados"

st.markdown(
"<div class='nticker-shell'>"
"<div class='nticker-label'><span class='nticker-dot'></span>EN VIVO</div>"
"<div class='nticker-track'><div class='nticker-inner'>"
f"<div class='nticker-item'><span class='ntag ntag-n'>Logro</span>{_ticker_logro} <span class='nticker-sep'>·</span></div>"
"<div class='nticker-item'><span class='ntag ntag-u'>Nuevo</span>Módulo de Novedades disponible — registra tus novedades en tiempo real <span class='nticker-sep'>·</span></div>"
f"<div class='nticker-item'><span class='ntag ntag-p'>Potenciar</span>{_ticker_potenciar} <span class='nticker-sep'>·</span></div>"
f"<div class='nticker-item'><span class='ntag ntag-n'>Logro</span>{_ticker_logro} <span class='nticker-sep'>·</span></div>"
"<div class='nticker-item'><span class='ntag ntag-u'>Nuevo</span>Módulo de Novedades disponible — registra tus novedades en tiempo real <span class='nticker-sep'>·</span></div>"
f"<div class='nticker-item'><span class='ntag ntag-p'>Potenciar</span>{_ticker_potenciar} <span class='nticker-sep'>·</span></div>"
"</div></div></div>"
"<div class='sec-lbl' style='margin-top:30px'>Noticias · Pulso WFM</div>"
"<div class='nws-grid'>"
"<div class='ncard ncard-feat'>"
"<div class='ncard-vis'></div>"
"<div class='ncard-feat-body'>"
"<div class='ncard-ghost'>🏆</div>"
f"<div class='ncard-eyebrow'><span class='ntag ntag-n'>Logro</span><span class='ncard-date'>{_fecha_str}</span></div>"
"<div class='ncard-title-feat'>Los mejores del día — Top 3 en adherencia</div>"
f"<div class='ncard-body' style='margin-bottom:14px'>{_lineas_top3}</div>"
f"<div class='ncard-body' style='margin-top:-8px'><span style='color:rgba(255,255,255,0.35);font-size:11px'>Meta equipo: 90% · Promedio general: {_promedio_str}</span></div>"
"<div class='ncard-footer'>"
"<div class='ncard-avatar'>🏆</div>"
"<div class='ncard-byline'><strong>Ranking automático diario</strong>Calculado desde el último día cargado en Adherencia</div>"
"</div></div></div>"
"<div class='ncard ncard-nuevo'>"
"<div class='ncard-eyebrow'><span class='ntag ntag-u'>Nuevo</span><span class='ncard-date'>Jul 2026</span></div>"
"<div class='ncard-title'>El módulo de Novedades ya está disponible</div>"
"<div class='ncard-body-sm'>Cada experto puede registrar sus novedades operativas desde el dashboard. Pasa por aprobación en dos etapas: supervisor y luego Workforce Management.</div>"
"</div>"
"<div class='ncard ncard-potenciar'>"
f"<div class='ncard-eyebrow'><span class='ntag ntag-p'>Potenciar</span><span class='ncard-date'>{_fecha_str}</span></div>"
"<div class='ncard-title'>Asesores a impulsar — menor adherencia del día</div>"
f"<div class='ncard-body-sm'>{_lineas_bottom5}"
"<span style='color:rgba(255,255,255,0.35);font-size:11px'>Se excluyen 0% (sin datos ese día)</span>"
"</div>"
"</div>"
"</div>",
unsafe_allow_html=True)

# ── MÓDULOS ──────────────────────────────
st.markdown("<div class='sec-lbl'>Módulos disponibles</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    <div class='mod' style='
        --accent:linear-gradient(90deg,#0EA5E9,#6366F1);
        --accent-solid:#38BDF8;
        --glow:rgba(56,189,248,0.55);
        --icobg:linear-gradient(135deg,rgba(14,165,233,0.22),rgba(99,102,241,0.10));'>
        <div class='mod-glow'></div>
        <div class='mod-head'>
            <div class='mod-ico'>🎯</div>
            <span class='mod-badge' style='background:rgba(16,185,129,0.14);color:#34D399;border:1px solid rgba(16,185,129,0.30);'>
                <span class='mod-badge-dot' style='background:#34D399'></span>Disponible
            </span>
        </div>
        <div class='mod-title'>Adherencia</div>
        <div class='mod-desc'>
            Seguimiento de la adherencia de cada experto respecto a su tiempo programado.
            Tendencias, distribución de llegadas y comparativos por supervisor.
        </div>
        <div class='mod-feats'>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Tendencia diaria, semanal y mensual</div>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Distribución de tipos de llegada</div>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Ranking y comparativo por supervisor</div>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Tablas de planificación y excesos</div>
        </div>
        <div class='mod-div'></div>
        <div class='mod-foot'>
            <div class='mod-chips'>
                <span class='mchip'>🎯 Meta&nbsp;<b>90%</b></span>
                <span class='mchip'>📊 <b>4</b>&nbsp;vistas</span>
            </div>
            <div class='mspark'>
                <span style='height:38%'></span><span style='height:62%'></span>
                <span style='height:48%'></span><span style='height:78%'></span>
                <span style='height:58%'></span><span style='height:90%'></span>
                <span style='height:70%'></span><span style='height:100%'></span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎯  Abrir módulo de Adherencia →", key="btn_adh",
                 use_container_width=True, type="primary"):
        st.switch_page(adh_pg)

with col2:
    st.markdown("""
    <div class='mod' style='
        --accent:linear-gradient(90deg,#8B5CF6,#EC4899);
        --accent-solid:#A78BFA;
        --glow:rgba(139,92,246,0.55);
        --icobg:linear-gradient(135deg,rgba(139,92,246,0.22),rgba(236,72,153,0.10));'>
        <div class='mod-glow'></div>
        <div class='mod-head'>
            <div class='mod-ico'>📊</div>
            <span class='mod-badge' style='background:rgba(16,185,129,0.14);color:#34D399;border:1px solid rgba(16,185,129,0.30);'>
                <span class='mod-badge-dot' style='background:#34D399'></span>Disponible
            </span>
        </div>
        <div class='mod-title'>Ocupación</div>
        <div class='mod-desc'>
            Seguimiento de ocupación y contacto por experto. Tendencias por supervisor,
            detalle de llamadas y resumen de distribución por equipo.
        </div>
        <div class='mod-feats'>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Ocupación y contacto por período</div>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Tendencia por supervisor y experto</div>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Detalle de llamadas atendidas</div>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Resumen y distribución por supervisor</div>
        </div>
        <div class='mod-div'></div>
        <div class='mod-foot'>
            <div class='mod-chips'>
                <span class='mchip'>📈 Meta&nbsp;<b>90%</b></span>
                <span class='mchip'>📊 <b>3</b>&nbsp;vistas</span>
            </div>
            <div class='mspark'>
                <span style='height:55%'></span><span style='height:35%'></span>
                <span style='height:72%'></span><span style='height:50%'></span>
                <span style='height:85%'></span><span style='height:62%'></span>
                <span style='height:95%'></span><span style='height:74%'></span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📊  Abrir módulo de Ocupación →", key="btn_ocu",
                 use_container_width=True, type="primary"):
        st.switch_page(ocu_pg)

with col3:
    st.markdown("""
    <div class='mod' style='
        --accent:linear-gradient(90deg,#34D399,#059669);
        --accent-solid:#34D399;
        --glow:rgba(52,211,153,0.55);
        --icobg:linear-gradient(135deg,rgba(52,211,153,0.22),rgba(5,150,105,0.10));'>
        <div class='mod-glow'></div>
        <div class='mod-head'>
            <div class='mod-ico'>📢</div>
            <span class='mod-badge' style='background:rgba(52,211,153,0.14);color:#34D399;border:1px solid rgba(52,211,153,0.30);'>
                <span class='mod-badge-dot' style='background:#34D399'></span>Disponible
            </span>
        </div>
        <div class='mod-title'>Novedades</div>
        <div class='mod-desc'>
            Registra y gestiona las novedades operativas del equipo. Cada novedad sigue un flujo
            de aprobación: experto → supervisor → WFM.
        </div>
        <div class='mod-feats'>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Registro de novedades en tiempo real</div>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Vista por estado: pendientes, aprobadas e históricas</div>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Filtros por supervisor, experto y período</div>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Descarga en Excel y sincronización con Google Sheets</div>
        </div>
        <div class='mod-div'></div>
        <div class='mod-foot'>
            <div class='mod-chips'>
                <span class='mchip'>🟢 <b>Live</b></span>
                <span class='mchip'>📊 <b>3</b>&nbsp;vistas</span>
            </div>
            <div class='mspark'>
                <span style='height:45%'></span><span style='height:70%'></span>
                <span style='height:55%'></span><span style='height:82%'></span>
                <span style='height:64%'></span><span style='height:92%'></span>
                <span style='height:76%'></span><span style='height:100%'></span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📢  Abrir módulo de Novedades →", key="btn_nov",
                 use_container_width=True, type="primary"):
        st.switch_page(nov_pg)

# ── STATS ─────────────────────────────────
st.markdown("""
<div class='stats'>
    <div class='stat' style='--sc:#38BDF8'>
        <div class='stat-ico'>🎯</div>
        <div class='stat-val'>90%</div>
        <div class='stat-lbl'>Meta Adherencia</div>
    </div>
    <div class='stat' style='--sc:#34D399'>
        <div class='stat-ico'>📅</div>
        <div class='stat-val'>2026</div>
        <div class='stat-lbl'>Año en Curso</div>
    </div>
    <div class='stat' style='--sc:#A78BFA'>
        <div class='stat-ico'>🧩</div>
        <div class='stat-val'>3</div>
        <div class='stat-lbl'>Módulos</div>
    </div>
    <div class='stat' style='--sc:#FBBF24'>
        <div class='stat-ico'>🤝</div>
        <div class='stat-val' style='font-size:22px'>Alianza</div>
        <div class='stat-lbl'>Uniminuto</div>
    </div>
</div>
""", unsafe_allow_html=True)
