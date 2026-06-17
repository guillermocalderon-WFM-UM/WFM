import streamlit as st
import base64
import os

st.set_page_config(
    page_title="Ocupación – WFM Uniminuto",
    page_icon="📊",
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

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    * {{ font-family: 'Inter', sans-serif !important; }}

    .main {{
        background-color: {COLOR_BG};
        background-image: radial-gradient(circle, #C8D6E3 1px, transparent 1px);
        background-size: 28px 28px;
    }}
    .block-container {{ padding-top: 2rem; padding-bottom: 1rem; }}

    div[data-testid="collapsedControl"] {{ background:transparent!important; border:none!important; box-shadow:none!important; }}
    div[data-testid="collapsedControl"] * {{ color:transparent!important; background:transparent!important; border:none!important; }}
    div[data-testid="stSidebarContent"] {{ width:100%!important; box-sizing:border-box!important; padding-right:0.75rem!important; }}
    div[data-testid="stSidebarContent"] > div {{ width:100%!important; }}

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

    @keyframes sbcBar {{
        0%   {{ background-position: 0% 0%;   }}
        100% {{ background-position: 200% 0%; }}
    }}
    @keyframes sbcPulse {{
        0%,100% {{ opacity:1; transform:scale(1);   }}
        50%     {{ opacity:.3; transform:scale(.6); }}
    }}
    @keyframes float {{
        0%,100% {{ transform: translateY(0px);   }}
        50%     {{ transform: translateY(-12px); }}
    }}
    @keyframes spin-slow {{
        from {{ transform: rotate(0deg);   }}
        to   {{ transform: rotate(360deg); }}
    }}
    @keyframes pulse-ring {{
        0%   {{ transform: scale(1);   opacity: 0.6; }}
        100% {{ transform: scale(1.8); opacity: 0;   }}
    }}

    .sbc {{
        position: relative; border-radius: 20px; overflow: hidden;
        margin: 6px 0 26px; padding: 20px 18px 18px;
        background:
            linear-gradient(145deg,
                rgba(56,189,248,0.12)  0%,
                rgba(129,140,248,0.09) 55%,
                rgba(52,211,153,0.07)  100%),
            rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.12);
    }}
    .sbc-orb {{ position: absolute; border-radius: 50%; pointer-events: none; }}
    .sbc-orb-1 {{ width:140px;height:140px;background:radial-gradient(circle,rgba(56,189,248,0.18) 0%,transparent 70%);top:-50px;right:-40px; }}
    .sbc-orb-2 {{ width:90px;height:90px;background:radial-gradient(circle,rgba(129,140,248,0.16) 0%,transparent 70%);bottom:-30px;left:-25px; }}
    .sbc-orb-3 {{ width:60px;height:60px;background:radial-gradient(circle,rgba(52,211,153,0.14) 0%,transparent 70%);top:50%;right:12px; }}
    .sbc-live {{
        position:absolute;top:14px;right:14px;
        display:flex;align-items:center;gap:5px;
        font-size:8px!important;font-weight:800!important;
        color:#34D399!important;background:rgba(52,211,153,0.13);
        border:1px solid rgba(52,211,153,0.30);
        padding:3px 9px 3px 7px;border-radius:99px;
        letter-spacing:0.10em;z-index:2;
    }}
    .sbc-pulse {{
        width:5px;height:5px;background:#34D399;border-radius:50%;
        display:inline-block;animation:sbcPulse 1.8s ease-in-out infinite;
    }}
    .sbc-body {{ position:relative;z-index:1;text-align:center; }}
    .sbc-logo-wrap {{ margin-bottom:10px;display:flex;justify-content:center;align-items:center; }}
    .sbc-logo-img {{ max-width:150px!important;height:auto!important;filter:drop-shadow(0 4px 14px rgba(56,189,248,0.45)) brightness(1.05);display:block; }}
    .sbc-name {{ font-size:13px!important;font-weight:700!important;color:rgba(255,255,255,0.88)!important;letter-spacing:0!important;margin-bottom:4px!important; }}
    .sbc-org  {{ font-size:10px!important;color:rgba(255,255,255,0.35)!important;margin-bottom:16px!important; }}
    .sbc-stats {{ display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.22);border-radius:12px;padding:10px 8px;border:1px solid rgba(255,255,255,0.07); }}
    .sbc-stat {{ flex:1;text-align:center; }}
    .sbc-sv {{ display:block;font-size:14px!important;font-weight:900!important;color:white!important;line-height:1;margin-bottom:3px; }}
    .sbc-sl {{ display:block;font-size:8px!important;font-weight:700!important;color:rgba(255,255,255,0.28)!important;letter-spacing:0.10em;text-transform:uppercase; }}
    .sbc-sep {{ width:1px;height:28px;background:rgba(255,255,255,0.09);flex-shrink:0; }}
    .sbc-bar {{
        position:absolute;bottom:0;left:0;right:0;height:3px;
        background:linear-gradient(90deg,#38BDF8,#818CF8,#34D399,#F59E0B,#38BDF8);
        background-size:300% 100%;animation:sbcBar 4s linear infinite;
    }}
    .sbf {{ margin-top:28px;padding:0; }}
    .sbf-rule {{ height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.12),transparent);margin-bottom:14px; }}
    .sbf-row {{ display:flex;align-items:center;gap:10px;margin-bottom:10px; }}
    .sbf-avatar {{
        width:38px;height:38px;border-radius:11px;
        background:linear-gradient(135deg,#38BDF8 0%,#818CF8 100%);
        display:flex;align-items:center;justify-content:center;
        font-size:13px!important;font-weight:900!important;
        color:white!important;flex-shrink:0;letter-spacing:0.5px;
        box-shadow:0 4px 14px rgba(56,189,248,0.35);
    }}
    .sbf-name {{ font-size:11px!important;font-weight:700!important;color:rgba(255,255,255,0.68)!important;margin-bottom:2px!important; }}
    .sbf-role {{ font-size:10px!important;color:rgba(255,255,255,0.28)!important; }}
    .sbf-credit {{ font-size:9px!important;font-weight:600!important;color:rgba(255,255,255,0.18)!important;text-align:center;letter-spacing:0.06em; }}

    /* ── Placeholder styles ── */
    .ocu-hero {{
        background:
            repeating-linear-gradient(-45deg,
                rgba(255,255,255,0) 0px, rgba(255,255,255,0) 12px,
                rgba(255,255,255,0.02) 12px, rgba(255,255,255,0.02) 13px),
            radial-gradient(ellipse at 20% 40%, rgba(56,189,248,0.20) 0%, transparent 55%),
            radial-gradient(ellipse at 80% 70%, rgba(129,140,248,0.22) 0%, transparent 55%),
            linear-gradient(135deg, {COLOR_PRIMARY} 0%, #4C1D95 60%, #0F172A 100%);
        border-radius: 20px;
        padding: 64px 40px;
        text-align: center;
        box-shadow: 0 8px 40px rgba(40,5,63,0.35);
        position: relative;
        overflow: hidden;
        margin-bottom: 32px;
    }}
    .ocu-hero-icon {{
        font-size: 72px;
        display: block;
        margin-bottom: 20px;
        animation: float 3.5s ease-in-out infinite;
        line-height: 1;
    }}
    .ocu-hero-title {{
        font-size: 32px; font-weight: 900;
        color: white; margin: 0 0 10px;
        letter-spacing: -0.8px;
    }}
    .ocu-hero-sub {{
        font-size: 15px; color: rgba(255,255,255,0.60);
        margin: 0 auto; max-width: 520px; line-height: 1.6;
    }}
    .ocu-badge {{
        display: inline-block;
        margin-top: 24px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.22);
        color: rgba(255,255,255,0.80);
        font-size: 12px; font-weight: 700;
        padding: 8px 22px; border-radius: 99px;
        letter-spacing: 0.06em; text-transform: uppercase;
    }}
    /* Ring animation behind icon */
    .ocu-ring {{
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: 180px; height: 180px;
        border-radius: 50%;
        border: 2px solid rgba(56,189,248,0.15);
        animation: pulse-ring 2.8s ease-out infinite;
        pointer-events: none;
    }}
    .ocu-ring-2 {{
        animation-delay: 1.4s;
    }}

    .ocu-features {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 18px;
        margin-bottom: 28px;
    }}
    .ocu-feat {{
        background: white;
        border-radius: 16px;
        padding: 28px 22px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.07);
        border: 1px solid rgba(0,0,0,0.04);
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: transform 0.22s ease, box-shadow 0.22s ease;
    }}
    .ocu-feat:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 36px rgba(0,0,0,0.12);
    }}
    .ocu-feat::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 4px;
        background: var(--fc, {COLOR_PRIMARY});
        border-radius: 16px 16px 0 0;
    }}
    .ocu-feat-icon {{ font-size: 36px; display: block; margin-bottom: 12px; line-height: 1; }}
    .ocu-feat-title {{
        font-size: 14px; font-weight: 800;
        color: #1E293B; margin: 0 0 6px;
        letter-spacing: -0.2px;
    }}
    .ocu-feat-desc {{ font-size: 12px; color: #94A3B8; line-height: 1.6; margin: 0; }}

    .ocu-soon {{
        background: white;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.07);
        border: 1px solid rgba(0,0,0,0.04);
        display: flex; align-items: center; gap: 24px;
    }}
    .ocu-soon-icon {{
        width: 64px; height: 64px;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(14,165,233,0.15), rgba(14,165,233,0.05));
        display: flex; align-items: center; justify-content: center;
        font-size: 32px; flex-shrink: 0;
    }}
    .ocu-soon-title {{ font-size: 18px; font-weight: 800; color: #1E293B; margin: 0 0 6px; letter-spacing: -0.3px; }}
    .ocu-soon-desc  {{ font-size: 13px; color: #64748B; margin: 0; line-height: 1.6; }}
    .ocu-soon-tag {{
        margin-left: auto; flex-shrink: 0;
        background: linear-gradient(135deg, {COLOR_PRIMARY}, {COLOR_ACCENT});
        color: white; font-size: 11px; font-weight: 700;
        padding: 8px 20px; border-radius: 99px;
        letter-spacing: 0.05em; text-transform: uppercase;
        box-shadow: 0 4px 14px rgba(14,165,233,0.30);
    }}
</style>
""", unsafe_allow_html=True)

# ─── Hero ───────────────────────────────────────────
st.markdown("""
<div class='ocu-hero'>
    <div class='ocu-ring'></div>
    <div class='ocu-ring ocu-ring-2'></div>
    <span class='ocu-hero-icon'>📊</span>
    <div class='ocu-hero-title'>Módulo de Ocupación</div>
    <div class='ocu-hero-sub'>
        Análisis de ocupación, shrinkage, capacidad y cobertura del equipo.<br>
        Próximamente disponible para el equipo Workforce Management.
    </div>
    <span class='ocu-badge'>En Desarrollo · 2026</span>
</div>
""", unsafe_allow_html=True)

# ─── Feature preview cards ──────────────────────────
st.markdown("""
<div class='ocu-features'>
    <div class='ocu-feat' style='--fc:#0EA5E9'>
        <span class='ocu-feat-icon'>🕐</span>
        <div class='ocu-feat-title'>Ocupación por Hora</div>
        <div class='ocu-feat-desc'>Distribución de agentes conectados vs. requeridos por franja horaria y campaña.</div>
    </div>
    <div class='ocu-feat' style='--fc:#8B5CF6'>
        <span class='ocu-feat-icon'>📉</span>
        <div class='ocu-feat-title'>Shrinkage</div>
        <div class='ocu-feat-desc'>Cálculo de shrinkage planificado y real, desglosado por tipo de ausencia y equipo.</div>
    </div>
    <div class='ocu-feat' style='--fc:#10B981'>
        <span class='ocu-feat-icon'>🎯</span>
        <div class='ocu-feat-title'>Nivel de Servicio</div>
        <div class='ocu-feat-desc'>Correlación entre ocupación, adherencia y nivel de servicio alcanzado por período.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Coming soon banner ─────────────────────────────
st.markdown("""
<div class='ocu-soon'>
    <div class='ocu-soon-icon'>🚀</div>
    <div>
        <div class='ocu-soon-title'>¿Cuándo estará disponible?</div>
        <div class='ocu-soon-desc'>
            El equipo WFM está construyendo este módulo con los mismos estándares del tablero de Adherencia.
            Cuando esté listo, aparecerá automáticamente en esta página con todos los datos cargados.
        </div>
    </div>
    <span class='ocu-soon-tag'>Próximamente</span>
</div>
""", unsafe_allow_html=True)
