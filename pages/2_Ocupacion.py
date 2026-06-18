import streamlit as st
import base64

COLOR_PRIMARY = "#28053F"
COLOR_ACCENT  = "#0EA5E9"

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

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');
    * {{ font-family: 'Inter', sans-serif !important; }}
    /* restaurar la fuente de íconos Material */
    span[data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="collapsedControl"] span,
    .material-symbols-rounded, .material-symbols-outlined, .material-icons {{
        font-family: 'Material Symbols Rounded','Material Symbols Outlined','Material Icons' !important;
    }}
    /* ocultar el menú automático del sidebar */
    [data-testid="stSidebarNav"] {{ display:none !important; }}

    /* ── Fondo claro con tinte suave (idea de diseño de la home) ── */
    .main {{
        background:
            radial-gradient(ellipse 55% 45% at 0% 0%,   rgba(14,165,233,0.07) 0%, transparent 55%),
            radial-gradient(ellipse 50% 45% at 100% 6%, rgba(139,92,246,0.07) 0%, transparent 55%),
            radial-gradient(ellipse 60% 50% at 90% 100%, rgba(52,211,153,0.05) 0%, transparent 55%),
            #F4F7FB;
        background-attachment: fixed;
    }}
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
    [data-testid="stSidebarCollapseButton"] span {{ color: rgba(255,255,255,0.80) !important; font-size:20px !important; }}
    div[data-testid="collapsedControl"] span {{ color: {COLOR_PRIMARY} !important; font-size:20px !important; }}
    div[data-testid="stSidebarContent"] {{ width:100%!important; box-sizing:border-box!important; padding-right:0.75rem!important; }}
    div[data-testid="stSidebarContent"] > div {{ width:100%!important; }}

    /* ══ SIDEBAR BASE · mismo fondo aurora (sin grid) ══ */
    section[data-testid="stSidebar"] > div:first-child {{
        background:
            radial-gradient(ellipse 95% 42% at 8% 0%,    rgba(14,165,233,0.30) 0%, transparent 55%),
            radial-gradient(ellipse 90% 42% at 100% 26%, rgba(129,140,248,0.28) 0%, transparent 55%),
            radial-gradient(ellipse 85% 42% at 50% 102%, rgba(52,211,153,0.15) 0%, transparent 55%),
            linear-gradient(160deg, #0B0518 0%, #14082b 45%, #0A0414 100%);
        border-right: 1px solid rgba(255,255,255,0.07);
    }}
    div[data-testid="stSidebarContent"] * {{ color: white !important; }}

    /* ══ Scala arriba + footer anclado al fondo ══ */
    [data-testid="stSidebarHeader"] {{ padding-top:0.1rem!important; padding-bottom:0!important; min-height:0!important; }}
    [data-testid="stSidebarUserContent"] {{ padding-top:0!important; }}
    section[data-testid="stSidebar"] .block-container {{ padding-top:0.5rem!important; }}
    section[data-testid="stSidebar"] > div:first-child {{
        display:flex!important; flex-direction:column!important; min-height:100vh!important; }}
    [data-testid="stSidebarUserContent"] {{
        flex:1 1 auto!important; display:flex!important; flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] > div {{ flex:1 1 auto!important; display:flex!important; flex-direction:column!important; }}
    [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:last-of-type {{
        margin-top:auto!important; }}

    /* ══ ANIMATIONS ══ */
    @keyframes sbcBar {{ 0% {{ background-position:0% 0%; }} 100% {{ background-position:200% 0%; }} }}
    @keyframes sbcPulse {{ 0%,100% {{ opacity:1; transform:scale(1); }} 50% {{ opacity:.3; transform:scale(.6); }} }}
    @keyframes float {{ 0%,100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-12px); }} }}
    @keyframes pulse-ring {{ 0% {{ transform: scale(1); opacity: 0.6; }} 100% {{ transform: scale(1.8); opacity: 0; }} }}

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

    /* ── HEADER · banner grande con fondo aurora del sidebar ── */
    .st-key-hdrbanner {{
        position: relative; overflow: hidden;
        background:
            radial-gradient(ellipse 70% 130% at 2% -15%,  rgba(14,165,233,0.34) 0%, transparent 60%),
            radial-gradient(ellipse 65% 130% at 100% 120%, rgba(129,140,248,0.34) 0%, transparent 60%),
            radial-gradient(ellipse 55% 110% at 72% 130%,  rgba(52,211,153,0.16) 0%, transparent 60%),
            linear-gradient(155deg, #0B0518 0%, #14082b 50%, #0A0414 100%);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 24px; padding: 36px 42px; margin-bottom: 26px;
        box-shadow: 0 24px 60px rgba(0,0,0,0.32), inset 0 1px 0 rgba(255,255,255,0.08);
    }}
    .hb-eyebrow {{ display:inline-flex;align-items:center;gap:9px;
        background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.16);
        border-radius:99px;padding:6px 15px;margin-bottom:16px;
        font-size:10.5px;font-weight:700;color:rgba(255,255,255,0.78);
        letter-spacing:0.12em;text-transform:uppercase; }}
    .hb-dot {{ width:7px;height:7px;border-radius:50%;background:#34D399;
        box-shadow:0 0 9px #34D399;animation:sbcPulse 1.8s ease-in-out infinite; }}
    .hb-title {{ font-family:'Space Grotesk',sans-serif!important;
        font-size:38px;font-weight:700;color:white;margin:0 0 12px;
        letter-spacing:-1.2px;line-height:1.04; }}
    .hb-sub {{ font-size:13.5px;color:rgba(255,255,255,0.62);margin:0;line-height:1.55; }}
    .hb-sub b {{ color:rgba(255,255,255,0.92);font-weight:700; }}
    .menu-lbl {{ display:flex;align-items:center;justify-content:flex-end;gap:7px;
        font-size:10px;font-weight:800;letter-spacing:0.16em;text-transform:uppercase;
        color:rgba(255,255,255,0.50);margin-bottom:10px; }}
    .menu-lbl::before {{ content:'';flex:1;height:1px;
        background:linear-gradient(90deg,transparent,rgba(255,255,255,0.18)); }}
    .st-key-hdrbanner [data-testid="stVerticalBlock"] {{ gap: 0.45rem !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button {{
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        color: rgba(255,255,255,0.92) !important; border-radius: 11px !important;
        font-size: 12px !important; font-weight: 700 !important;
        height: 42px !important; min-height: 42px !important; padding: 0 6px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.06) !important;
        transition: transform .2s ease, background .2s ease, border-color .2s ease, box-shadow .2s ease !important;
    }}
    .st-key-hdrbanner [data-testid="stButton"] > button:hover {{
        background: rgba(255,255,255,0.16) !important;
        border-color: rgba(56,189,248,0.5) !important; transform: translateY(-2px) !important;
    }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"] {{
        background: linear-gradient(135deg,#38BDF8,#818CF8) !important; color: white !important;
        border: 1px solid transparent !important;
        box-shadow: 0 8px 22px -6px rgba(56,189,248,0.65) !important; }}
    .st-key-hdrbanner [data-testid="stButton"] > button[kind="primary"]:hover {{
        filter: brightness(1.08) !important; transform: translateY(-2px) !important; }}

    /* ── Section label (fondo claro) ── */
    .ocu-seclbl {{ display:flex;align-items:center;gap:12px;margin:30px 0 18px;
        font-size:11px;font-weight:800;letter-spacing:0.16em;text-transform:uppercase;color:#64748B; }}
    .ocu-seclbl::before {{ content:'';width:26px;height:2px;border-radius:2px;
        background:linear-gradient(90deg,#0EA5E9,#8B5CF6); }}
    .ocu-seclbl::after {{ content:'';flex:1;height:1px;
        background:linear-gradient(90deg,#CBD5E1,transparent); }}

    /* ── Feature preview cards ── */
    .ocu-features {{ display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:28px; }}
    .ocu-feat {{ background:white;border-radius:20px;padding:30px 24px;
        box-shadow:0 10px 34px rgba(15,23,42,0.08);border:1px solid rgba(0,0,0,0.04);
        text-align:center;position:relative;overflow:hidden;
        transition:transform 0.24s ease, box-shadow 0.24s ease; }}
    .ocu-feat:hover {{ transform:translateY(-6px);box-shadow:0 18px 46px rgba(15,23,42,0.14); }}
    .ocu-feat::before {{ content:'';position:absolute;top:0;left:0;right:0;height:5px;
        background:var(--fc, {COLOR_PRIMARY});border-radius:20px 20px 0 0; }}
    .ocu-feat::after {{ content:'';position:absolute;top:-30px;right:-30px;width:100px;height:100px;
        background:radial-gradient(circle,var(--fc, {COLOR_PRIMARY}),transparent 70%);opacity:0.10;border-radius:50%; }}
    .ocu-feat-ico {{ width:60px;height:60px;border-radius:17px;margin:0 auto 14px;
        display:flex;align-items:center;justify-content:center;font-size:30px;
        background:var(--fcbg);border:1px solid rgba(0,0,0,0.04);
        box-shadow:0 8px 18px -6px rgba(15,23,42,0.25);position:relative;z-index:1;
        animation:float 4s ease-in-out infinite; }}
    .ocu-feat-title {{ font-size:15px;font-weight:800;color:#1E293B;margin:0 0 7px;letter-spacing:-0.2px;position:relative;z-index:1; }}
    .ocu-feat-desc {{ font-size:12px;color:#94A3B8;line-height:1.6;margin:0;position:relative;z-index:1; }}

    /* ── Coming soon banner ── */
    .ocu-soon {{ border-radius:20px;padding:30px 32px;
        display:flex;align-items:center;gap:22px;position:relative;overflow:hidden;
        background:
            radial-gradient(ellipse at 12% 40%, rgba(255,255,255,0.16) 0%, transparent 55%),
            radial-gradient(ellipse at 92% 130%, rgba(0,0,0,0.22) 0%, transparent 55%),
            linear-gradient(120deg, {COLOR_PRIMARY} 0%, #0EA5E9 100%);
        box-shadow:0 18px 42px -12px rgba(15,23,42,0.45);
        border:1px solid rgba(255,255,255,0.12); }}
    .ocu-soon::after {{ content:'';position:absolute;right:-35px;bottom:-45px;width:150px;height:150px;
        background:rgba(255,255,255,0.07);border-radius:50%; }}
    .ocu-soon-icon {{ width:64px;height:64px;border-radius:18px;flex-shrink:0;position:relative;z-index:1;
        background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.28);
        display:flex;align-items:center;justify-content:center;font-size:32px;
        box-shadow:0 8px 18px -6px rgba(0,0,0,0.4); }}
    .ocu-soon-title {{ font-size:19px;font-weight:800;color:white;margin:0 0 6px;letter-spacing:-0.3px;position:relative;z-index:1; }}
    .ocu-soon-desc  {{ font-size:13px;color:rgba(255,255,255,0.80);margin:0;line-height:1.6;position:relative;z-index:1; }}
    .ocu-soon-tag {{ margin-left:auto;flex-shrink:0;position:relative;z-index:1;
        background:rgba(255,255,255,0.92);color:{COLOR_PRIMARY};font-size:11px;font-weight:800;
        padding:9px 20px;border-radius:99px;letter-spacing:0.05em;text-transform:uppercase;
        box-shadow:0 6px 16px -6px rgba(0,0,0,0.3); }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ENCABEZADO (banner + menú)
# ─────────────────────────────────────────────
_home_pg = st.Page("home.py", title="Inicio", icon="🏠", default=True)
_adh_pg  = st.Page("pages/1_Adherencia.py", title="Adherencia", icon="🎯")

with st.container(key="hdrbanner"):
    htitle, hmenu = st.columns([2.0, 2.0], vertical_alignment="center")
    with htitle:
        st.markdown("""
        <div class='hb-eyebrow'><span class='hb-dot'></span>Centro de Control · Uniminuto 2026</div>
        <div class='hb-title'>Módulo de Ocupación</div>
        <div class='hb-sub'>🚧 <b>En desarrollo</b> &nbsp;·&nbsp; Próximamente disponible</div>
        """, unsafe_allow_html=True)
    with hmenu:
        st.markdown("<div class='menu-lbl'>⚡ Menú</div>", unsafe_allow_html=True)
        if st.button("🏠  Inicio", key="hdr_home", use_container_width=True):
            st.switch_page(_home_pg)
        mb1, mb2 = st.columns(2, gap="small")
        with mb1:
            if st.button("🎯 Adherencia", key="hdr_adh", use_container_width=True):
                st.switch_page(_adh_pg)
        with mb2:
            st.button("📊 Ocupación", key="hdr_ocu", use_container_width=True, type="primary")

# ─────────────────────────────────────────────
# VISTA PREVIA DEL MÓDULO
# ─────────────────────────────────────────────
st.markdown("<div class='ocu-seclbl'>Vista previa del módulo</div>", unsafe_allow_html=True)

st.markdown("""
<div class='ocu-features'>
    <div class='ocu-feat' style='--fc:#0EA5E9;--fcbg:linear-gradient(135deg,rgba(14,165,233,0.18),rgba(14,165,233,0.05))'>
        <div class='ocu-feat-ico'>🕐</div>
        <div class='ocu-feat-title'>Ocupación por Hora</div>
        <div class='ocu-feat-desc'>Distribución de agentes conectados vs. requeridos por franja horaria y campaña.</div>
    </div>
    <div class='ocu-feat' style='--fc:#8B5CF6;--fcbg:linear-gradient(135deg,rgba(139,92,246,0.18),rgba(139,92,246,0.05))'>
        <div class='ocu-feat-ico'>📉</div>
        <div class='ocu-feat-title'>Shrinkage</div>
        <div class='ocu-feat-desc'>Cálculo de shrinkage planificado y real, desglosado por tipo de ausencia y equipo.</div>
    </div>
    <div class='ocu-feat' style='--fc:#10B981;--fcbg:linear-gradient(135deg,rgba(16,185,129,0.18),rgba(16,185,129,0.05))'>
        <div class='ocu-feat-ico'>🎯</div>
        <div class='ocu-feat-title'>Nivel de Servicio</div>
        <div class='ocu-feat-desc'>Correlación entre ocupación, adherencia y nivel de servicio alcanzado por período.</div>
    </div>
</div>
""", unsafe_allow_html=True)

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
