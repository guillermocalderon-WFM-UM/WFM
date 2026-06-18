import streamlit as st
import base64

st.set_page_config(
    page_title="WFM Dashboard – Uniminuto",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

COLOR_PRIMARY = "#28053F"
COLOR_ACCENT  = "#0EA5E9"
COLOR_BG      = "#F0F4F8"

_LOGO_PATH = "logo-scala-learning-transformacion-digital-universidades.webp"
try:
    with open(_LOGO_PATH, "rb") as _f:
        _logo_b64 = base64.b64encode(_f.read()).decode()
    _logo_src = f"data:image/webp;base64,{_logo_b64}"
except FileNotFoundError:
    _logo_src = ""

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
        <div class='sbf-rule'></div>
        <div class='sbf-row'>
            <div class='sbf-avatar'>GC</div>
            <div class='sbf-info'>
                <div class='sbf-name'>Guillermo Calderón</div>
                <div class='sbf-role'>Analista WFM · Scala Learning</div>
            </div>
        </div>
        <div class='sbf-credit'>Desarrollado por Workforce Management</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    * {{ font-family: 'Inter', sans-serif !important; }}

    .main {{
        background-color: {COLOR_BG};
        background-image: radial-gradient(circle, #C8D6E3 1px, transparent 1px);
        background-size: 28px 28px;
    }}
    .block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}

    div[data-testid="collapsedControl"] {{ background:transparent!important;border:none!important;box-shadow:none!important; }}
    div[data-testid="collapsedControl"] * {{ color:transparent!important;background:transparent!important;border:none!important; }}
    div[data-testid="stSidebarContent"] {{ width:100%!important;box-sizing:border-box!important;padding-right:0.75rem!important; }}
    div[data-testid="stSidebarContent"] > div {{ width:100%!important; }}

    /* ══ SIDEBAR ══ */
    section[data-testid="stSidebar"] > div:first-child {{
        background:
            url("data:image/svg+xml,%3Csvg width='52' height='52' viewBox='0 0 52 52' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M26 0 L52 26 L26 52 L0 26 Z' fill='none' stroke='rgba(255,255,255,0.028)' stroke-width='1'/%3E%3C/svg%3E"),
            repeating-linear-gradient(-60deg, rgba(255,255,255,0.018) 0px, rgba(255,255,255,0.018) 1px, transparent 1px, transparent 14px),
            radial-gradient(ellipse at 0% 0%,    rgba(56,189,248,0.16) 0%,  transparent 42%),
            radial-gradient(ellipse at 100% 100%, rgba(129,140,248,0.18) 0%, transparent 42%),
            radial-gradient(ellipse at 50% 55%,   rgba(52,211,153,0.08) 0%,  transparent 38%),
            linear-gradient(170deg, #1c0636 0%, #28053F 50%, #18022b 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }}
    div[data-testid="stSidebarContent"] * {{ color: white !important; }}

    /* ══ ANIMATIONS ══ */
    @keyframes sbcBar {{
        0%   {{ background-position: 0% 0%;   }}
        100% {{ background-position: 200% 0%; }}
    }}
    @keyframes sbcPulse {{
        0%,100% {{ opacity:1; transform:scale(1);   }}
        50%     {{ opacity:.3; transform:scale(.6); }}
    }}
    @keyframes float {{
        0%,100% {{ transform: translateY(0px);  }}
        50%     {{ transform: translateY(-8px); }}
    }}
    @keyframes fadeUp {{
        from {{ opacity:0; transform:translateY(24px); }}
        to   {{ opacity:1; transform:translateY(0);    }}
    }}
    @keyframes shimmer {{
        0%   {{ background-position: -200% 0; }}
        100% {{ background-position:  200% 0; }}
    }}

    /* ══ BRAND CARD ══ */
    .sbc {{
        position:relative;border-radius:20px;overflow:hidden;
        margin:6px 0 26px;padding:20px 18px 18px;
        background:linear-gradient(145deg,rgba(56,189,248,0.12) 0%,rgba(129,140,248,0.09) 55%,rgba(52,211,153,0.07) 100%),rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.12);
    }}
    .sbc-orb {{ position:absolute;border-radius:50%;pointer-events:none; }}
    .sbc-orb-1 {{ width:140px;height:140px;background:radial-gradient(circle,rgba(56,189,248,0.18) 0%,transparent 70%);top:-50px;right:-40px; }}
    .sbc-orb-2 {{ width:90px;height:90px;background:radial-gradient(circle,rgba(129,140,248,0.16) 0%,transparent 70%);bottom:-30px;left:-25px; }}
    .sbc-orb-3 {{ width:60px;height:60px;background:radial-gradient(circle,rgba(52,211,153,0.14) 0%,transparent 70%);top:50%;right:12px; }}
    .sbc-live {{
        position:absolute;top:14px;right:14px;display:flex;align-items:center;gap:5px;
        font-size:8px!important;font-weight:800!important;color:#34D399!important;
        background:rgba(52,211,153,0.13);border:1px solid rgba(52,211,153,0.30);
        padding:3px 9px 3px 7px;border-radius:99px;letter-spacing:0.10em;z-index:2;
    }}
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
    .sbc-bar {{
        position:absolute;bottom:0;left:0;right:0;height:3px;
        background:linear-gradient(90deg,#38BDF8,#818CF8,#34D399,#F59E0B,#38BDF8);
        background-size:300% 100%;animation:sbcBar 4s linear infinite;
    }}

    /* ══ FOOTER ══ */
    .sbf {{ margin-top:28px;padding:0; }}
    .sbf-rule {{ height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.12),transparent);margin-bottom:14px; }}
    .sbf-row {{ display:flex;align-items:center;gap:10px;margin-bottom:10px; }}
    .sbf-avatar {{
        width:38px;height:38px;border-radius:11px;
        background:linear-gradient(135deg,#38BDF8 0%,#818CF8 100%);
        display:flex;align-items:center;justify-content:center;
        font-size:13px!important;font-weight:900!important;color:white!important;
        flex-shrink:0;letter-spacing:0.5px;box-shadow:0 4px 14px rgba(56,189,248,0.35);
    }}
    .sbf-name {{ font-size:11px!important;font-weight:700!important;color:rgba(255,255,255,0.68)!important;margin-bottom:2px!important; }}
    .sbf-role {{ font-size:10px!important;color:rgba(255,255,255,0.28)!important; }}
    .sbf-credit {{ font-size:9px!important;font-weight:600!important;color:rgba(255,255,255,0.18)!important;text-align:center;letter-spacing:0.06em; }}

    /* ══ HOME PAGE ══ */

    /* Hero */
    .home-hero {{
        background:
            repeating-linear-gradient(-45deg,
                rgba(255,255,255,0) 0px, rgba(255,255,255,0) 12px,
                rgba(255,255,255,0.018) 12px, rgba(255,255,255,0.018) 13px),
            radial-gradient(ellipse at 10% 30%, rgba(56,189,248,0.22) 0%, transparent 50%),
            radial-gradient(ellipse at 90% 80%, rgba(129,140,248,0.24) 0%, transparent 50%),
            radial-gradient(ellipse at 55% 10%, rgba(52,211,153,0.10) 0%, transparent 40%),
            linear-gradient(145deg, {COLOR_PRIMARY} 0%, #3B0764 45%, #1E1B4B 100%);
        border-radius: 24px;
        padding: 72px 60px 68px;
        text-align: center;
        box-shadow: 0 12px 56px rgba(40,5,63,0.40);
        position: relative;
        overflow: hidden;
        margin-bottom: 40px;
        animation: fadeUp 0.6s ease both;
    }}
    .home-hero-eyebrow {{
        display: inline-flex; align-items: center; gap: 8px;
        background: rgba(255,255,255,0.09);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 99px;
        padding: 5px 16px;
        font-size: 11px; font-weight: 700; color: rgba(255,255,255,0.75);
        letter-spacing: 0.10em; text-transform: uppercase;
        margin-bottom: 28px;
    }}
    .home-hero-dot {{
        width: 6px; height: 6px;
        background: #34D399; border-radius: 50%;
        animation: sbcPulse 1.8s ease-in-out infinite;
    }}
    .home-hero-title {{
        font-size: 48px; font-weight: 900;
        color: white; margin: 0 0 16px;
        letter-spacing: -1.5px; line-height: 1.1;
    }}
    .home-hero-title span {{
        background: linear-gradient(90deg, #38BDF8, #818CF8, #34D399);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 3s linear infinite;
    }}
    .home-hero-sub {{
        font-size: 17px; color: rgba(255,255,255,0.58);
        max-width: 560px; margin: 0 auto 36px;
        line-height: 1.65;
    }}
    .home-hero-pills {{
        display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;
    }}
    .home-pill {{
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.20);
        border-radius: 99px;
        padding: 6px 18px;
        font-size: 12px; font-weight: 600;
        color: rgba(255,255,255,0.75);
        letter-spacing: 0.02em;
    }}
    /* Decorative orbs in hero */
    .hero-orb {{
        position: absolute; border-radius: 50%; pointer-events: none;
    }}
    .hero-orb-1 {{
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(56,189,248,0.10) 0%, transparent 70%);
        top: -80px; left: -80px;
    }}
    .hero-orb-2 {{
        width: 200px; height: 200px;
        background: radial-gradient(circle, rgba(129,140,248,0.12) 0%, transparent 70%);
        bottom: -60px; right: -60px;
    }}

    /* Section label */
    .home-section-lbl {{
        font-size: 10px; font-weight: 800;
        color: #64748B;
        letter-spacing: 0.14em; text-transform: uppercase;
        margin-bottom: 14px;
        display: flex; align-items: center; gap: 8px;
    }}
    .home-section-lbl::after {{
        content: '';
        flex: 1; height: 1px;
        background: linear-gradient(90deg, #CBD5E1, transparent);
    }}

    /* Module cards */
    .mod-card {{
        background: white;
        border-radius: 22px;
        padding: 36px 28px 28px;
        box-shadow: 0 6px 32px rgba(0,0,0,0.09);
        border: 1px solid rgba(0,0,0,0.04);
        position: relative;
        overflow: hidden;
        height: 100%;
        display: flex; flex-direction: column;
        transition: transform 0.28s ease, box-shadow 0.28s ease;
        animation: fadeUp 0.7s ease both;
    }}
    .mod-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 18px 56px rgba(0,0,0,0.14);
    }}
    .mod-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 5px;
        background: var(--mc, {COLOR_PRIMARY});
        border-radius: 22px 22px 0 0;
    }}
    /* top-right glow circle */
    .mod-card::after {{
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 130px; height: 130px;
        background: radial-gradient(circle, var(--mc, {COLOR_PRIMARY}), transparent 70%);
        opacity: 0.10;
        border-radius: 50%;
    }}
    .mod-card-wash {{
        position: absolute;
        bottom: 0; left: 0; right: 0; height: 100px;
        background: linear-gradient(0deg, rgba(0,0,0,0.016), transparent);
        pointer-events: none;
    }}
    .mod-icon-wrap {{
        width: 68px; height: 68px;
        border-radius: 20px;
        display: flex; align-items: center; justify-content: center;
        font-size: 34px; margin-bottom: 20px;
        flex-shrink: 0;
        position: relative; z-index: 1;
        animation: float 3.5s ease-in-out infinite;
    }}
    .mod-status {{
        display: inline-flex; align-items: center; gap: 5px;
        font-size: 9px; font-weight: 700;
        padding: 3px 10px; border-radius: 99px;
        letter-spacing: 0.08em; text-transform: uppercase;
        margin-bottom: 12px; position: relative; z-index: 1;
    }}
    .mod-title {{
        font-size: 22px; font-weight: 900;
        color: #1E293B; margin: 0 0 10px;
        letter-spacing: -0.5px;
        position: relative; z-index: 1;
    }}
    .mod-desc {{
        font-size: 13px; color: #64748B;
        line-height: 1.7; margin: 0 0 22px;
        flex: 1; position: relative; z-index: 1;
    }}
    .mod-features {{
        display: flex; flex-direction: column; gap: 8px;
        margin-bottom: 26px; position: relative; z-index: 1;
    }}
    .mod-feat {{
        display: flex; align-items: center; gap: 8px;
        font-size: 12px; color: #475569;
    }}
    .mod-feat-dot {{
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--mc, {COLOR_PRIMARY}); flex-shrink: 0;
    }}
    /* Streamlit buttons in module cards */
    div[data-testid="stButton"] > button {{
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 0.01em !important;
        height: 44px !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    }}
    div[data-testid="stButton"] > button[kind="primary"] {{
        background: linear-gradient(135deg, {COLOR_PRIMARY}, {COLOR_ACCENT}) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(14,165,233,0.30) !important;
    }}
    div[data-testid="stButton"] > button[kind="primary"]:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(14,165,233,0.40) !important;
    }}
    div[data-testid="stButton"] > button[kind="secondary"] {{
        background: white !important;
        border: 2px solid #E2E8F0 !important;
        color: #64748B !important;
    }}
    div[data-testid="stButton"] > button[kind="secondary"]:hover {{
        border-color: #8B5CF6 !important;
        color: #8B5CF6 !important;
        transform: translateY(-2px) !important;
    }}

    /* Stats row at bottom of page */
    .home-stats {{
        display: flex; gap: 16px; margin-top: 36px;
        animation: fadeUp 0.9s ease both;
    }}
    .home-stat {{
        flex: 1; background: white;
        border-radius: 16px; padding: 22px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.07);
        border: 1px solid rgba(0,0,0,0.04);
        text-align: center; position: relative; overflow: hidden;
    }}
    .home-stat::before {{
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: var(--sc, #94A3B8);
        border-radius: 16px 16px 0 0;
    }}
    .home-stat-val {{
        font-size: 28px; font-weight: 900; color: #1E293B;
        line-height: 1; margin-bottom: 4px;
    }}
    .home-stat-lbl {{
        font-size: 10px; font-weight: 700; color: #94A3B8;
        text-transform: uppercase; letter-spacing: 0.09em;
    }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class='home-hero'>
    <div class='hero-orb hero-orb-1'></div>
    <div class='hero-orb hero-orb-2'></div>
    <div class='home-hero-eyebrow'>
        <span class='home-hero-dot'></span>
        Uniminuto · Scala Learning · 2026
    </div>
    <div class='home-hero-title'>
        Workforce<br><span>Management</span>
    </div>
    <div class='home-hero-sub'>
        Plataforma de análisis y seguimiento del equipo de expertos.
        Monitorea adherencia, ocupación y desempeño en tiempo real.
    </div>
    <div class='home-hero-pills'>
        <span class='home-pill'>📊 Análisis en tiempo real</span>
        <span class='home-pill'>🎯 Meta de adherencia 90%</span>
        <span class='home-pill'>👥 Seguimiento por equipo</span>
        <span class='home-pill'>📈 Tendencias históricas</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MODULE CARDS
# ─────────────────────────────────────────────
st.markdown("""<div class='home-section-lbl'>Módulos disponibles</div>""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class='mod-card' style='--mc:#0EA5E9; animation-delay:0.1s'>
        <div class='mod-card-wash'></div>
        <div class='mod-icon-wrap' style='background:linear-gradient(135deg,rgba(14,165,233,0.18),rgba(14,165,233,0.06))'>🎯</div>
        <span class='mod-status' style='background:rgba(16,185,129,0.12);color:#10B981;border:1px solid rgba(16,185,129,0.25)'>
            <span style='width:5px;height:5px;border-radius:50%;background:#10B981;display:inline-block'></span>
            Disponible
        </span>
        <div class='mod-title'>Adherencia</div>
        <div class='mod-desc'>
            Seguimiento de la adherencia de cada experto respecto a su tiempo programado.
            Visualiza tendencias, distribución de llegadas y comparativos por supervisor.
        </div>
        <div class='mod-features'>
            <div class='mod-feat'><span class='mod-feat-dot' style='--mc:#0EA5E9'></span>Tendencia diaria, semanal y mensual</div>
            <div class='mod-feat'><span class='mod-feat-dot' style='--mc:#0EA5E9'></span>Distribución de tipos de llegada</div>
            <div class='mod-feat'><span class='mod-feat-dot' style='--mc:#0EA5E9'></span>Ranking y comparativo por supervisor</div>
            <div class='mod-feat'><span class='mod-feat-dot' style='--mc:#0EA5E9'></span>Tablas de planificación y excesos</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎯  Abrir módulo de Adherencia →", use_container_width=True, key="btn_adh", type="primary"):
        st.switch_page("pages/1_Adherencia.py")

with col2:
    st.markdown("""
    <div class='mod-card' style='--mc:#8B5CF6; animation-delay:0.2s'>
        <div class='mod-card-wash'></div>
        <div class='mod-icon-wrap' style='background:linear-gradient(135deg,rgba(139,92,246,0.18),rgba(139,92,246,0.06))'>📊</div>
        <span class='mod-status' style='background:rgba(245,158,11,0.12);color:#F59E0B;border:1px solid rgba(245,158,11,0.25)'>
            <span style='width:5px;height:5px;border-radius:50%;background:#F59E0B;display:inline-block'></span>
            En Desarrollo
        </span>
        <div class='mod-title'>Ocupación</div>
        <div class='mod-desc'>
            Análisis de ocupación, shrinkage, capacidad y nivel de servicio del equipo.
            Correlaciona la disponibilidad real con los requerimientos operativos por franja horaria.
        </div>
        <div class='mod-features'>
            <div class='mod-feat'><span class='mod-feat-dot' style='--mc:#8B5CF6'></span>Ocupación por hora y campaña</div>
            <div class='mod-feat'><span class='mod-feat-dot' style='--mc:#8B5CF6'></span>Cálculo de shrinkage planificado vs real</div>
            <div class='mod-feat'><span class='mod-feat-dot' style='--mc:#8B5CF6'></span>Cobertura y nivel de servicio</div>
            <div class='mod-feat'><span class='mod-feat-dot' style='--mc:#8B5CF6'></span>Próximamente disponible</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📊  Ver módulo de Ocupación →", use_container_width=True, key="btn_ocu"):
        st.switch_page("pages/2_Ocupacion.py")

# ─────────────────────────────────────────────
# STATS ROW
# ─────────────────────────────────────────────
st.markdown("""
<div class='home-stats'>
    <div class='home-stat' style='--sc:#0EA5E9'>
        <div class='home-stat-val'>90%</div>
        <div class='home-stat-lbl'>Meta Adherencia</div>
    </div>
    <div class='home-stat' style='--sc:#10B981'>
        <div class='home-stat-val'>2026</div>
        <div class='home-stat-lbl'>Año en Curso</div>
    </div>
    <div class='home-stat' style='--sc:#8B5CF6'>
        <div class='home-stat-val'>2</div>
        <div class='home-stat-lbl'>Módulos</div>
    </div>
    <div class='home-stat' style='--sc:#F59E0B'>
        <div class='home-stat-val'>COL</div>
        <div class='home-stat-lbl'>País</div>
    </div>
</div>
""", unsafe_allow_html=True)
