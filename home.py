import streamlit as st
import base64

COLOR_PRIMARY = "#28053F"
COLOR_ACCENT  = "#0EA5E9"

# objetos de página (mismos parámetros que en Dashboard.py → switch_page funciona)
adh_pg = st.Page("pages/1_Adherencia.py", title="Adherencia", icon="🎯")
ocu_pg = st.Page("pages/2_Ocupacion.py",  title="Ocupación",  icon="📊")
nov_pg = st.Page("pages/3_Novedades.py",  title="Novedades",  icon="📢")

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
        padding:30px 50px 26px; text-align:center; margin-bottom:20px;
        background:
            linear-gradient(135deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.015) 100%);
        border:1px solid rgba(255,255,255,0.10);
        box-shadow:0 30px 80px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.10);
        backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
        animation:fadeUp 0.7s ease both;
    }}
    .hero-aurora {{ position:absolute; border-radius:50%; filter:blur(46px); pointer-events:none; z-index:0; }}
    .ha1 {{ width:380px;height:380px;background:radial-gradient(circle,rgba(14,165,233,0.45),transparent 65%);top:-140px;left:-90px;animation:auroraMove 14s ease-in-out infinite; }}
    .ha2 {{ width:340px;height:340px;background:radial-gradient(circle,rgba(129,140,248,0.42),transparent 65%);bottom:-150px;right:-70px;animation:auroraMove 18s ease-in-out infinite reverse; }}
    .ha3 {{ width:260px;height:260px;background:radial-gradient(circle,rgba(52,211,153,0.30),transparent 65%);top:30%;right:18%;animation:auroraMove 22s ease-in-out infinite; }}
    .hero::before {{
        content:''; position:absolute; inset:0; z-index:0;
        background-image:linear-gradient(rgba(255,255,255,0.04) 1px,transparent 1px),
                         linear-gradient(90deg,rgba(255,255,255,0.04) 1px,transparent 1px);
        background-size:46px 46px;
        mask-image:radial-gradient(ellipse 70% 70% at 50% 40%,black,transparent 80%);
        -webkit-mask-image:radial-gradient(ellipse 70% 70% at 50% 40%,black,transparent 80%);
    }}
    .hero-inner {{ position:relative; z-index:1; }}
    .hero-badge {{ display:inline-flex;align-items:center;gap:9px;
        background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.16);
        border-radius:99px;padding:7px 18px;margin-bottom:30px;
        font-size:11px;font-weight:700;color:rgba(255,255,255,0.78);
        letter-spacing:0.14em;text-transform:uppercase;
        box-shadow:0 4px 20px rgba(0,0,0,0.25); }}
    .hero-badge-dot {{ position:relative;width:8px;height:8px; }}
    .hero-badge-dot::after {{ content:'';position:absolute;inset:0;border-radius:50%;background:#34D399; }}
    .hero-badge-dot::before {{ content:'';position:absolute;inset:0;border-radius:50%;border:2px solid #34D399;animation:ring 1.8s ease-out infinite; }}
    .hero-title {{ font-family:'Space Grotesk',sans-serif!important;
        font-size:40px;font-weight:700;color:white;margin:0 0 10px;
        letter-spacing:-1.4px;line-height:1.05;text-shadow:0 4px 40px rgba(0,0,0,0.4); }}
    .hero-title .grad {{ background:linear-gradient(90deg,#38BDF8 0%,#818CF8 35%,#34D399 70%,#38BDF8 100%);
        background-size:220% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;animation:shimmer 4s linear infinite; }}
    .hero-sub {{ font-size:15px;color:rgba(255,255,255,0.58);max-width:560px;
        margin:0 auto 22px;line-height:1.65;font-weight:400; }}

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

    /* ══ HERO · tarjetas de estado (más objetos visuales) ══ */
    .hero-cards {{ display:flex;justify-content:center;gap:13px;flex-wrap:wrap;margin-top:6px; }}
    .hcard {{ display:flex;align-items:center;gap:11px;
        background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);
        border-radius:14px;padding:11px 17px;backdrop-filter:blur(6px);
        transition:transform .22s ease,border-color .22s ease,background .22s ease; }}
    .hcard:hover {{ transform:translateY(-3px);border-color:rgba(56,189,248,0.45);background:rgba(255,255,255,0.10); }}
    .hcard-ico {{ width:38px;height:38px;border-radius:11px;display:flex;align-items:center;justify-content:center;
        font-size:18px;flex-shrink:0;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.14); }}
    .hcard-txt {{ text-align:left;line-height:1.2; }}
    .hcard-lbl {{ font-size:9px;font-weight:700;letter-spacing:0.10em;text-transform:uppercase;color:rgba(255,255,255,0.45); }}
    .hcard-val {{ font-size:14px;font-weight:800;color:white;margin-top:2px; }}
    .hcard-val .dot {{ display:inline-block;width:7px;height:7px;border-radius:50%;background:#34D399;
        box-shadow:0 0 8px #34D399;margin-right:5px;animation:sbcPulse 1.8s ease-in-out infinite; }}

    /* ══ TICKER EN VIVO ══ */
    @keyframes nticker {{ 0% {{ transform:translateX(0); }} 100% {{ transform:translateX(-50%); }} }}
    .nticker-shell {{ display:flex;align-items:stretch;overflow:hidden;border-radius:12px;
        background:rgba(245,158,11,0.05);border:1px solid rgba(245,158,11,0.20);
        margin:24px 0 0; }}
    .nticker-label {{ flex-shrink:0;display:flex;align-items:center;gap:7px;
        padding:10px 16px;font-size:9px;font-weight:800;letter-spacing:0.16em;
        text-transform:uppercase;color:#F59E0B;
        background:rgba(245,158,11,0.13);border-right:1px solid rgba(245,158,11,0.20); }}
    .nticker-dot {{ width:6px;height:6px;border-radius:50%;background:#F59E0B;
        animation:sbcPulse 1.8s ease-in-out infinite;flex-shrink:0; }}
    .nticker-track {{ overflow:hidden;flex:1; }}
    .nticker-inner {{ display:flex;width:max-content;
        animation:nticker 36s linear infinite;padding:10px 0; }}
    .nticker-inner:hover {{ animation-play-state:paused; }}
    .nticker-item {{ display:flex;align-items:center;gap:10px;
        padding:0 44px;white-space:nowrap;
        font-size:12.5px;color:rgba(255,255,255,0.70);font-weight:500; }}
    .nticker-sep {{ color:rgba(245,158,11,0.40);margin-left:4px; }}
    .ntag {{ font-size:8.5px;font-weight:800;padding:2px 8px;border-radius:5px;
        text-transform:uppercase;letter-spacing:0.08em;flex-shrink:0; }}
    .ntag-a {{ background:rgba(244,63,94,0.18);color:#FB7185;border:1px solid rgba(244,63,94,0.28); }}
    .ntag-u {{ background:rgba(14,165,233,0.18);color:#38BDF8;border:1px solid rgba(14,165,233,0.28); }}
    .ntag-n {{ background:rgba(52,211,153,0.18);color:#34D399;border:1px solid rgba(52,211,153,0.28); }}
    .ntag-r {{ background:rgba(245,158,11,0.18);color:#FCD34D;border:1px solid rgba(245,158,11,0.28); }}

    /* ══ NEWS GRID ══ */
    .nws-grid {{ display:grid;grid-template-columns:1.65fr 1fr;
        grid-template-rows:auto auto;gap:14px;
        margin:20px 0 32px;animation:fadeUp 1.05s ease both; }}
    .ncard-feat {{ grid-row:1/3; }}

    .ncard {{ position:relative;overflow:hidden;border-radius:20px;
        padding:26px 28px;display:flex;flex-direction:column;
        background:linear-gradient(145deg,rgba(255,255,255,0.06) 0%,rgba(255,255,255,0.015) 100%);
        border:1px solid rgba(255,255,255,0.09);
        box-shadow:0 12px 32px rgba(0,0,0,0.28),inset 0 1px 0 rgba(255,255,255,0.06);
        transition:transform .28s cubic-bezier(.2,.8,.2,1),border-color .28s ease,background .28s ease; }}
    .ncard:hover {{ transform:translateY(-5px);border-color:rgba(255,255,255,0.22);
        background:rgba(255,255,255,0.08); }}

    /* Noticia destacada */
    .ncard-feat {{ padding:34px 32px 28px;
        background:linear-gradient(145deg,rgba(245,158,11,0.11) 0%,rgba(245,158,11,0.03) 55%,rgba(14,165,233,0.06) 100%);
        border-color:rgba(245,158,11,0.24); }}
    .ncard-feat:hover {{ border-color:rgba(245,158,11,0.48);
        box-shadow:0 24px 60px rgba(0,0,0,0.40),0 0 40px -12px rgba(245,158,11,0.18); }}
    .ncard-ghost {{ position:absolute;bottom:-18px;right:-10px;
        font-family:'Space Grotesk',sans-serif;font-size:168px;font-weight:900;
        line-height:1;color:rgba(245,158,11,0.055);pointer-events:none;
        user-select:none;letter-spacing:-8px;z-index:0; }}

    .ncard-eyebrow {{ display:flex;align-items:center;gap:9px;
        margin-bottom:14px;position:relative;z-index:1; }}
    .ncard-date {{ font-size:10px;font-weight:600;letter-spacing:0.06em;
        color:rgba(255,255,255,0.32);text-transform:uppercase; }}
    .ncard-title-feat {{ font-family:'Space Grotesk',sans-serif;
        font-size:22px;font-weight:700;color:white;
        line-height:1.28;letter-spacing:-0.4px;
        margin-bottom:14px;flex:1;position:relative;z-index:1; }}
    .ncard-body {{ font-size:13px;color:rgba(255,255,255,0.48);
        line-height:1.65;flex:1;position:relative;z-index:1; }}
    .ncard-title {{ font-size:13.5px;font-weight:700;color:rgba(255,255,255,0.88);
        line-height:1.40;letter-spacing:-0.1px;position:relative;z-index:1; }}
    .ncard-body-sm {{ font-size:12.5px;color:rgba(255,255,255,0.46);
        line-height:1.58;position:relative;z-index:1;margin-top:6px; }}

    .ncard-footer {{ display:flex;align-items:center;gap:10px;
        margin-top:auto;padding-top:18px;
        border-top:1px solid rgba(255,255,255,0.07);position:relative;z-index:1; }}
    .ncard-avatar {{ width:30px;height:30px;border-radius:9px;
        background:linear-gradient(135deg,#F59E0B,#FB923C);
        display:flex;align-items:center;justify-content:center;
        font-size:14px;flex-shrink:0; }}
    .ncard-byline {{ font-size:10.5px;color:rgba(255,255,255,0.38);line-height:1.3; }}
    .ncard-byline strong {{ font-size:11.5px;font-weight:700;
        color:rgba(255,255,255,0.72);display:block;margin-bottom:1px; }}
    .ncard-arrow {{ margin-left:auto;font-size:18px;
        color:rgba(245,158,11,0.55);transition:transform .2s ease,color .2s ease; }}
    .ncard-feat:hover .ncard-arrow {{ transform:translateX(4px);color:#F59E0B; }}
</style>
""", unsafe_allow_html=True)

# ── HERO ─────────────────────────────────
st.markdown("""
<div class='hero'>
    <div class='hero-aurora ha1'></div>
    <div class='hero-aurora ha2'></div>
    <div class='hero-aurora ha3'></div>
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
        <div class='hero-cards'>
            <div class='hcard'><div class='hcard-ico'>🟢</div><div class='hcard-txt'>
                <div class='hcard-lbl'>Estado</div><div class='hcard-val'><span class='dot'></span>En línea</div></div></div>
            <div class='hcard'><div class='hcard-ico'>👥</div><div class='hcard-txt'>
                <div class='hcard-lbl'>Seguimiento</div><div class='hcard-val'>Por equipo</div></div></div>
            <div class='hcard'><div class='hcard-ico'>📅</div><div class='hcard-txt'>
                <div class='hcard-lbl'>Período</div><div class='hcard-val'>2026</div></div></div>
            <div class='hcard'><div class='hcard-ico'>🤝</div><div class='hcard-txt'>
                <div class='hcard-lbl'>Alianza</div><div class='hcard-val'>Uniminuto</div></div></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── NOTICIAS ─────────────────────────────
st.markdown("""
<div class='nticker-shell'>
    <div class='nticker-label'><span class='nticker-dot'></span>EN VIVO</div>
    <div class='nticker-track'>
        <div class='nticker-inner'>
            <div class='nticker-item'><span class='ntag ntag-n'>Logro</span>Adherencia supera meta del 90 % en semana 22 <span class='nticker-sep'>·</span></div>
            <div class='nticker-item'><span class='ntag ntag-u'>Actualización</span>Módulo de Ocupación disponible desde esta semana <span class='nticker-sep'>·</span></div>
            <div class='nticker-item'><span class='ntag ntag-r'>Recordatorio</span>Campaña de capacitación — miércoles 18 de junio, 2 p.m. <span class='nticker-sep'>·</span></div>
            <div class='nticker-item'><span class='ntag ntag-a'>Atención</span>Verificar asignación de turnos antes del inicio de semana 25 <span class='nticker-sep'>·</span></div>
            <div class='nticker-item'><span class='ntag ntag-n'>Logro</span>Adherencia supera meta del 90 % en semana 22 <span class='nticker-sep'>·</span></div>
            <div class='nticker-item'><span class='ntag ntag-u'>Actualización</span>Módulo de Ocupación disponible desde esta semana <span class='nticker-sep'>·</span></div>
            <div class='nticker-item'><span class='ntag ntag-r'>Recordatorio</span>Campaña de capacitación — miércoles 18 de junio, 2 p.m. <span class='nticker-sep'>·</span></div>
            <div class='nticker-item'><span class='ntag ntag-a'>Atención</span>Verificar asignación de turnos antes del inicio de semana 25 <span class='nticker-sep'>·</span></div>
        </div>
    </div>
</div>

<div class='sec-lbl' style='margin-top:30px'>Noticias · Pulso WFM</div>

<div class='nws-grid'>

    <!-- DESTACADA -->
    <div class='ncard ncard-feat'>
        <div class='ncard-ghost'>01</div>
        <div class='ncard-eyebrow'>
            <span class='ntag ntag-u'>Actualización</span>
            <span class='ncard-date'>Jun 2026</span>
        </div>
        <div class='ncard-title-feat'>
            El módulo de Ocupación ya está disponible para todos los equipos WFM
        </div>
        <div class='ncard-body'>
            A partir de esta semana el equipo puede monitorear en tiempo real la ocupación y el contacto
            de cada experto. El módulo incluye tendencias por supervisor, tiempo programado efectivo,
            detalle de llamadas y la distribución de abandonos por supervisor.
            Accede directamente desde la pantalla principal del dashboard.
        </div>
        <div class='ncard-footer'>
            <div class='ncard-avatar'>⚡</div>
            <div class='ncard-byline'>
                <strong>Equipo Workforce Management</strong>
                Scala Learning · Uniminuto
            </div>
            <span class='ncard-arrow'>→</span>
        </div>
    </div>

    <!-- CARD 1 -->
    <div class='ncard'>
        <div class='ncard-eyebrow'>
            <span class='ntag ntag-n'>Logro</span>
            <span class='ncard-date'>Sem 22 · Jun 2026</span>
        </div>
        <div class='ncard-title'>Adherencia supera la meta del 90 % por tercer período consecutivo</div>
        <div class='ncard-body-sm'>
            El equipo consolidó un promedio de 90.8 %. Ana Milena (92.9 %) y Karen Julieth (91.5 %)
            lideran el ranking de supervisores.
        </div>
    </div>

    <!-- CARD 2 -->
    <div class='ncard'>
        <div class='ncard-eyebrow'>
            <span class='ntag ntag-r'>Recordatorio</span>
            <span class='ncard-date'>Sem 25 · Jun 2026</span>
        </div>
        <div class='ncard-title'>Capacitación obligatoria y revisión de horarios — semana 25</div>
        <div class='ncard-body-sm'>
            Confirmar asignación de turnos antes del lunes. Capacitación para nuevos expertos
            el miércoles 18 de junio a las 2:00 p.m.
        </div>
    </div>

</div>
""", unsafe_allow_html=True)

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
        --accent:linear-gradient(90deg,#F59E0B,#FB923C);
        --accent-solid:#FBBF24;
        --glow:rgba(245,158,11,0.55);
        --icobg:linear-gradient(135deg,rgba(245,158,11,0.22),rgba(251,146,60,0.10));'>
        <div class='mod-glow'></div>
        <div class='mod-head'>
            <div class='mod-ico'>📢</div>
            <span class='mod-badge' style='background:rgba(245,158,11,0.14);color:#FBBF24;border:1px solid rgba(245,158,11,0.30);'>
                <span class='mod-badge-dot' style='background:#FBBF24'></span>En Desarrollo
            </span>
        </div>
        <div class='mod-title'>Novedades</div>
        <div class='mod-desc'>
            Comunicados, anuncios y registro de cambios del tablero.
            Mantente al día con las últimas actualizaciones del equipo Workforce Management.
        </div>
        <div class='mod-feats'>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Anuncios y comunicados del equipo</div>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Registro de cambios del tablero</div>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Alertas y recordatorios</div>
            <div class='mfeat'><span class='mfeat-ck'>✓</span>Próximamente disponible</div>
        </div>
        <div class='mod-div'></div>
        <div class='mod-foot'>
            <div class='mod-chips'>
                <span class='mchip'>🆕 <b>v1.0</b></span>
                <span class='mchip'>📅 <b>2026</b></span>
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
    if st.button("📢  Ver Novedades →", key="btn_nov",
                 use_container_width=True, type="secondary"):
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
