"""Sistema de diseño compartido "Executive BI" (clases .ebi-*), portado desde el
módulo Inscripciones de Dashboard Operativo y re-coloreado a la familia morada de
Dashboard WFM. Se importa desde cada página (`import _ui`) en vez de copiar y pegar
este CSS/helpers por página, que es como está hecho hoy en Dashboard Operativo.

No reemplaza el CSS de shell que cada página de WFM ya tiene (fondo aurora, sidebar,
tablas, tarjeta de gráfico Plotly) — solo agrega las clases de componente (banner,
KPIs, secciones, headers de gráfico, chips, tarjetas de alerta) que en Operativo
reemplazaron a `.kpi-card` / `.sec-header` / `.chart-hdr`.
"""
import html

import streamlit as st

# ─────────────────────────────────────────────
# PALETA
# ─────────────────────────────────────────────
GREEN  = "#10B981"
TEAL   = "#34D399"
BLUE   = "#38BDF8"
INDIGO = "#818CF8"
VIOLET = "#A78BFA"
AMBER  = "#F59E0B"
RED    = "#F43F5E"
MUTED  = "#94A3B8"
PALETTE = [BLUE, VIOLET, TEAL, INDIGO, AMBER, "#EC4899", "#22D3EE", "#FB7185"]


def _safe(value) -> str:
    return html.escape(str(value))


def _rgba(hex_color: str, alpha: float) -> str:
    value = hex_color.lstrip("#")
    red, green, blue = (int(value[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({red},{green},{blue},{alpha})"


def number_es(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def percent_es(value: float) -> str:
    return f"{value:.1f}".replace(".", ",") + " %"


# ─────────────────────────────────────────────
# CSS — solo las clases de componente (.ebi-*), no el shell de la página
# ─────────────────────────────────────────────
def inject_css() -> None:
    """Puerto del CSS .ebi-* de Inscripciones (Dashboard Operativo).

    El fondo general lo conserva cada página WFM; los componentes se mantienen con
    las proporciones y acentos del dashboard de referencia."""
    st.markdown(f"""<style>
    .ebi-top{{position:relative;overflow:hidden;margin:0 0 10px;padding:19px 22px;border:1px solid rgba(56,189,248,.16);border-radius:16px;background:linear-gradient(110deg,rgba(56,189,248,.075),rgba(16,185,129,.035) 55%,rgba(129,140,248,.045));display:flex;align-items:center;justify-content:space-between;gap:24px;box-shadow:inset 0 1px 0 rgba(255,255,255,.035)}}
    .ebi-top::before{{content:'';position:absolute;inset:0 auto 0 0;width:3px;background:linear-gradient(180deg,{BLUE},{TEAL})}}.ebi-top::after{{content:'';position:absolute;width:260px;height:160px;right:-90px;top:-105px;border-radius:50%;background:radial-gradient(circle,rgba(56,189,248,.11),transparent 70%);pointer-events:none}}.ebi-top-copy{{position:relative;z-index:1;min-width:0}}.ebi-top-context{{display:flex;align-items:center;gap:7px;margin-bottom:5px;font-size:8px;font-weight:850;letter-spacing:.18em;color:#7DD3FC}}.ebi-top-context i{{display:block;width:18px;height:1px;background:{BLUE}}}.ebi-top h1,.ebi-top-title{{font-family:'Space Grotesk',sans-serif!important;font-size:26px!important;line-height:1.08!important;color:white;margin:0!important}}.ebi-top p,.ebi-top-sub{{font-size:10px;color:rgba(255,255,255,.43);margin:6px 0 0}}.ebi-period{{position:relative;z-index:1;display:flex;flex-direction:column;align-items:flex-end;gap:3px;flex:0 0 auto;padding-left:22px;border-left:1px solid rgba(255,255,255,.09)}}.ebi-period span{{font-size:7px;font-weight:800;letter-spacing:.15em;color:rgba(255,255,255,.35)}}.ebi-period b{{font-family:'Space Grotesk',sans-serif;font-size:11px;letter-spacing:.04em;color:#7DD3FC;white-space:nowrap}}
    .ebi-overview{{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:11px;margin:14px 0 6px}}.ebi-overview-card{{position:relative;overflow:hidden;min-width:0;text-align:center;padding:18px 10px 15px;border-radius:16px;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.08)}}.ebi-overview-icon{{width:36px;height:36px;margin:0 auto 11px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:15px;color:var(--accent);background:linear-gradient(150deg,color-mix(in srgb,var(--accent) 24%,transparent),color-mix(in srgb,var(--accent) 6%,transparent));border:1px solid color-mix(in srgb,var(--accent) 35%,transparent)}}.ebi-overview-card>strong{{display:block;font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;line-height:1;color:#fff}}.ebi-overview-card>small{{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:rgba(255,255,255,.42);font-size:8px;letter-spacing:.06em;text-transform:uppercase;margin-top:7px}}.ebi-overview-detail{{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:rgba(255,255,255,.28);font-size:7.5px;margin-top:3px}}.ebi-overview-track{{height:3px;margin-top:9px;border-radius:99px;background:rgba(255,255,255,.08);overflow:hidden}}.ebi-overview-track i{{display:block;height:100%;border-radius:inherit;background:var(--accent)}}
    .ebi-section{{display:flex;align-items:center;gap:10px;margin:22px 0 9px}}.ebi-section span{{font-size:9px;font-weight:800;letter-spacing:.16em;color:{BLUE}}}.ebi-section b{{font-family:'Space Grotesk',sans-serif;font-size:15px;color:white}}.ebi-section i{{height:1px;flex:1;background:linear-gradient(90deg,rgba(255,255,255,.14),transparent)}}
    .ebi-head{{display:flex;align-items:center;gap:11px;margin:10px 0 5px;padding:10px 12px;border-left:2px solid {BLUE};background:linear-gradient(90deg,rgba(56,189,248,.07),transparent);border-radius:0 12px 12px 0}}.ebi-icon{{width:31px;height:31px;display:flex;align-items:center;justify-content:center;border-radius:9px;background:rgba(255,255,255,.07)}}.ebi-copy{{flex:1}}.ebi-title{{font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:700;color:#fff}}.ebi-sub{{font-size:10px;color:rgba(255,255,255,.43);margin-top:2px}}.ebi-tag{{font-size:8px;font-weight:800;letter-spacing:.10em;color:#7DD3FC;border:1px solid rgba(56,189,248,.24);border-radius:99px;padding:4px 8px}}
    .ebi-selected{{display:flex;flex-wrap:wrap;gap:6px;margin:2px 0 7px}}.ebi-selected span{{font-size:9px;color:rgba(255,255,255,.58);padding:3px 7px;border:1px solid rgba(255,255,255,.08);border-radius:99px;background:rgba(255,255,255,.025)}}.ebi-selected span::first-letter{{color:var(--dot)}}
    .st-key-wfm_module_nav{{margin:0 0 14px;padding:7px 10px;border:1px solid rgba(255,255,255,.10);border-radius:16px;background:rgba(255,255,255,.025)}}.st-key-wfm_module_nav [data-testid="stVerticalBlock"]{{gap:0!important}}.st-key-wfm_module_nav [data-testid="stButton"]>button{{height:39px!important;min-height:39px!important;border:0!important;border-radius:12px!important;background:transparent!important;color:rgba(255,255,255,.52)!important;font-size:12px!important;font-weight:700!important;box-shadow:none!important}}.st-key-wfm_module_nav [data-testid="stButton"]>button:hover{{background:rgba(255,255,255,.045)!important;color:rgba(255,255,255,.86)!important}}.st-key-wfm_module_nav [data-testid="stButton"]>button[kind="primary"]{{border:1px solid rgba(56,189,248,.34)!important;background:rgba(56,189,248,.13)!important;color:#7DD3FC!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.05)!important}}
    /* Compatibilidad: los módulos aún con HTML antiguo heredan el mismo lenguaje
       compacto en tanto se conservan sus gráficos y cálculos específicos. */
    .kpi-card{{min-height:0!important;height:auto!important;text-align:center!important;padding:18px 10px 15px!important;border-radius:16px!important;background:rgba(255,255,255,.035)!important;border:1px solid rgba(255,255,255,.08)!important;box-shadow:none!important;display:block!important}}.kpi-card::before,.kpi-card::after{{display:none!important}}.kpi-bg-icon{{position:static!important;display:flex!important;width:36px!important;height:36px!important;margin:0 auto 11px!important;align-items:center!important;justify-content:center!important;border-radius:10px!important;font-size:15px!important;opacity:1!important;background:color-mix(in srgb,var(--kc) 16%,transparent)!important;border:1px solid color-mix(in srgb,var(--kc) 38%,transparent)!important}}.kpi-label{{margin-top:7px!important;color:rgba(255,255,255,.42)!important;font-size:8px!important;letter-spacing:.06em!important}}.kpi-value{{margin:0!important;color:#fff!important;font-size:22px!important;line-height:1.15!important;text-shadow:none!important}}.kpi-sub{{font-size:7.5px!important;color:rgba(255,255,255,.28)!important;margin-top:3px!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important}}.kpi-bar-wrap{{height:3px!important;margin-top:9px!important;background:rgba(255,255,255,.08)!important}}.kpi-bar-fill{{height:3px!important}}.sec-header{{padding:0!important;margin:22px 0 9px!important;background:transparent!important;border:0!important;border-radius:0!important;box-shadow:none!important;gap:10px!important}}.sec-header::before,.sec-header::after,.sec-wash,.sec-icon,.sec-meta,.sec-tag{{display:none!important}}.sec-title{{font-family:'Space Grotesk',sans-serif!important;font-size:15px!important;color:#fff!important}}.sec-desc{{display:none!important}}.sec-header .sec-text::before{{content:'A';font-size:9px;font-weight:800;letter-spacing:.16em;color:{BLUE};margin-right:10px}}.sec-header .sec-text{{display:flex!important;align-items:center!important}}.chart-hdr{{margin:10px 0 5px!important;padding:10px 12px!important;border-left:2px solid var(--cc,{BLUE})!important;border-radius:0 12px 12px 0!important;background:linear-gradient(90deg,rgba(56,189,248,.07),transparent)!important;box-shadow:none!important}}
    .ebi-inc-scroll{{max-height:560px;overflow-y:auto;padding:2px 6px 2px 1px;scrollbar-width:thin;scrollbar-color:rgba(148,163,184,.35) transparent}}.ebi-incident{{position:relative;display:flex;gap:10px;margin:0 0 9px;padding:13px 12px;border-radius:12px;background:linear-gradient(120deg,rgba(255,255,255,.045),rgba(255,255,255,.018));border:1px solid rgba(255,255,255,.07);border-left:3px solid var(--incident);box-shadow:0 8px 22px -18px rgba(0,0,0,.9)}}.ebi-incident.warning{{--incident:{AMBER}}}.ebi-incident.critical{{--incident:{RED}}}.ebi-inc-dot{{color:var(--incident);font-size:10px;padding-top:3px}}.ebi-inc-body{{min-width:0;flex:1}}.ebi-inc-name{{font-size:12px;font-weight:750;color:rgba(255,255,255,.94);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.ebi-inc-sup{{font-size:9px;color:rgba(255,255,255,.40);margin:2px 0 9px}}.ebi-inc-main{{display:flex;flex-direction:column;gap:2px}}.ebi-inc-main strong{{font-family:'Space Grotesk',sans-serif;font-size:13px;color:white}}.ebi-inc-main span{{font-size:9px;color:rgba(255,255,255,.52)}}.ebi-inc-foot{{display:flex;gap:12px;flex-wrap:wrap;margin-top:9px;padding-top:7px;border-top:1px solid rgba(255,255,255,.06);font-size:8px;color:rgba(255,255,255,.38)}}.ebi-inc-foot b{{color:rgba(255,255,255,.70)}}.ebi-inc-badge{{align-self:flex-start;font-size:7px;font-weight:850;letter-spacing:.08em;color:var(--incident);background:color-mix(in srgb,var(--incident) 10%,transparent);border:1px solid color-mix(in srgb,var(--incident) 28%,transparent);border-radius:99px;padding:3px 6px;white-space:nowrap}}
    @media(max-width:1100px){{.ebi-overview{{grid-template-columns:repeat(3,minmax(0,1fr))}}.ebi-inc-scroll{{max-height:500px}}}}
    @media(max-width:720px){{.ebi-top{{align-items:flex-start;flex-direction:column;gap:13px}}.ebi-period{{align-items:flex-start;padding:0;border-left:0}}.ebi-overview{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
    </style>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# COMPONENTES
# ─────────────────────────────────────────────
def top_banner(eyebrow: str, title: str, subtitle: str, period_label: str, period_value: str) -> None:
    """Card independiente '.ebi-top' (banner + badge de período), para páginas que no
    tengan ya su propio contenedor de banner con look de tarjeta."""
    st.markdown(
        f"<div class='ebi-top'><div class='ebi-top-copy'>"
        f"<div class='ebi-top-context'><i></i>{_safe(eyebrow)}</div>"
        f"<h1>{_safe(title)}</h1><p>{_safe(subtitle)}</p></div>"
        f"<div class='ebi-period'><span>{_safe(period_label)}</span><b>{_safe(period_value)}</b></div></div>",
        unsafe_allow_html=True,
    )


def banner_header(eyebrow: str, title: str, subtitle: str, period_label: str, period_value: str) -> None:
    """Igual contenido/tipografía que top_banner (mismas clases .ebi-top-title/.ebi-top-sub,
    idénticas al h1/p reales de '.ebi-top') pero sin la tarjeta '.ebi-top' propia — para
    insertar dentro de un st.container(key=...) que ya trae su propio fondo/borde (como el
    banner '.st-key-hdrbanner' que ya tiene cada página de Dashboard WFM)."""
    st.markdown(
        f"<div style='display:flex;justify-content:space-between;align-items:flex-start;"
        f"gap:20px;flex-wrap:wrap;'><div>"
        f"<div class='ebi-top-context'><i></i>{_safe(eyebrow)}</div>"
        f"<div class='ebi-top-title'>{_safe(title)}</div>"
        f"<p class='ebi-top-sub'>{_safe(subtitle)}</p>"
        f"</div><div class='ebi-period'><span>{_safe(period_label)}</span><b>{_safe(period_value)}</b></div></div>",
        unsafe_allow_html=True,
    )


def overview_kpis(cards) -> None:
    """cards: lista de tuplas (icon, label, value, detail, color, extra_html).
    El número de columnas del grid se ajusta al número de tarjetas (Operativo usa 6
    para Inscripciones; otras páginas pueden tener menos KPIs con sentido propio)."""
    html_cards = "".join(
        f"<article class='ebi-overview-card' style='--accent:{color}'>"
        f"<div class='ebi-overview-icon'>{icon}</div>"
        f"<strong>{value}</strong><small>{_safe(label)}</small>"
        f"<span class='ebi-overview-detail'>{_safe(detail)}</span>"
        f"{extra}</article>"
        for icon, label, value, detail, color, extra in cards
    )
    st.markdown(
        f"<div class='ebi-overview' style='grid-template-columns:repeat({len(cards)},minmax(0,1fr))'>"
        f"{html_cards}</div>",
        unsafe_allow_html=True,
    )


def section(label: str, title: str) -> None:
    st.markdown(
        f"<div class='ebi-section'><span>{_safe(label)}</span><b>{_safe(title)}</b><i></i></div>",
        unsafe_allow_html=True,
    )


def module_nav(active: str, items) -> None:
    """Navegación plana, con las mismas proporciones del módulo Inscripciones.

    items recibe tuplas ``(id, etiqueta, página)``; la página activa no navega.
    """
    with st.container(key="wfm_module_nav"):
        columns = st.columns(len(items))
        for column, (item_id, label, page) in zip(columns, items):
            with column:
                if item_id == active:
                    st.button(label, key=f"wfm_nav_{item_id}", use_container_width=True, type="primary")
                elif st.button(label, key=f"wfm_nav_{item_id}", use_container_width=True):
                    st.switch_page(page)


def panel_title(icon: str, title: str, description: str, tag: str = "") -> None:
    badge = f"<span class='ebi-tag'>{_safe(tag)}</span>" if tag else ""
    st.markdown(
        f"<div class='ebi-head'><div class='ebi-icon'>{icon}</div>"
        f"<div class='ebi-copy'><div class='ebi-title'>{_safe(title)}</div>"
        f"<div class='ebi-sub'>{_safe(description)}</div></div>{badge}</div>",
        unsafe_allow_html=True,
    )


def selected_chips(selected, palette=None) -> None:
    palette = palette or PALETTE
    if len(selected) <= 5:
        chips = "".join(
            f"<span style='--dot:{palette[i % len(palette)]}'>● {_safe(s)}</span>"
            for i, s in enumerate(selected)
        )
    else:
        chips = f"<span>{len(selected)} seleccionados</span>"
    st.markdown(f"<div class='ebi-selected'>{chips}</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FILTROS LOCALES (multiselect "Todos" excluyente)
# ─────────────────────────────────────────────
def _exclusive_change(key: str, exclusive: str) -> None:
    current = list(st.session_state.get(key, []))
    previous = list(st.session_state.get(f"{key}__previous", []))
    if exclusive in current and exclusive not in previous:
        current = [exclusive]
    elif exclusive in current and any(v != exclusive and v not in previous for v in current):
        current = [v for v in current if v != exclusive]
    st.session_state[key] = current
    st.session_state[f"{key}__previous"] = current


def exclusive_multiselect(label, options, key, exclusive, default=None, empty_means_all=False, **kwargs):
    choices = [exclusive] + list(options)
    valid = set(choices)
    had_value = key in st.session_state
    if had_value:
        cleaned = [v for v in st.session_state[key] if v in valid]
        if exclusive in cleaned and len(cleaned) > 1:
            cleaned = [exclusive]
        st.session_state[key] = cleaned
    initial = list(default or [])
    st.session_state.setdefault(f"{key}__previous", initial)
    selected = st.multiselect(
        label, choices, default=None if had_value else initial, key=key,
        on_change=_exclusive_change, args=(key, exclusive), **kwargs,
    )
    if exclusive in selected:
        return list(options) if exclusive == "Todos" else []
    if not selected and empty_means_all:
        return list(options)
    return [v for v in selected if v in options]


def multiselect_all(label, options, key, default_all=True):
    return exclusive_multiselect(
        label, options, key, "Todos", ["Todos"] if default_all else [], empty_means_all=True,
    )
