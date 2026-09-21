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
    st.markdown(f"""<style>
    .ebi-top{{position:relative;overflow:hidden;border-radius:20px;padding:22px 30px;
        margin-bottom:18px;display:flex;justify-content:space-between;align-items:center;
        gap:20px;border:1px solid rgba(255,255,255,0.10);
        background:linear-gradient(110deg,rgba(56,189,248,.075),rgba(129,140,248,.05) 55%,rgba(167,139,250,.05));
        box-shadow:0 18px 46px -18px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.08);}}
    .ebi-top::before{{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;
        background:linear-gradient(180deg,{BLUE},{VIOLET});}}
    .ebi-top::after{{content:'';position:absolute;top:-60px;right:-60px;width:200px;height:200px;
        border-radius:50%;background:radial-gradient(circle,rgba(129,140,248,.14),transparent 70%);}}
    .ebi-top-copy{{position:relative;z-index:1;}}
    .ebi-top-context{{display:inline-flex;align-items:center;gap:7px;font-size:10px;font-weight:800;
        letter-spacing:.14em;text-transform:uppercase;color:{BLUE};margin-bottom:8px;}}
    .ebi-top-context i{{width:6px;height:6px;border-radius:50%;background:{TEAL};
        box-shadow:0 0 8px {TEAL};display:inline-block;}}
    .ebi-top h1{{font-family:'Space Grotesk',sans-serif;font-size:27px;font-weight:700;color:#fff;
        margin:0 0 6px;letter-spacing:-0.6px;}}
    .ebi-top p{{font-size:12.5px;color:rgba(255,255,255,0.60);margin:0;}}
    .ebi-period{{position:relative;z-index:1;text-align:right;flex-shrink:0;padding-left:20px;
        border-left:1px solid rgba(255,255,255,0.12);}}
    .ebi-period span{{display:block;font-size:9px;font-weight:800;letter-spacing:.12em;
        text-transform:uppercase;color:rgba(255,255,255,0.40);margin-bottom:4px;}}
    .ebi-period b{{font-family:'Space Grotesk',sans-serif;font-size:15px;color:#fff;font-weight:700;}}

    .ebi-overview{{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px;margin-bottom:6px;}}
    .ebi-overview-card{{position:relative;overflow:hidden;border-radius:16px;padding:16px 16px 14px;
        background:linear-gradient(160deg,rgba(255,255,255,0.055) 0%,rgba(255,255,255,0.015) 100%);
        border:1px solid rgba(255,255,255,0.10);box-shadow:0 14px 30px -16px rgba(0,0,0,0.6);}}
    .ebi-overview-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;
        background:var(--accent,{BLUE});box-shadow:0 0 14px -2px var(--accent,{BLUE});}}
    .ebi-overview-icon{{width:28px;height:28px;border-radius:9px;display:flex;align-items:center;
        justify-content:center;font-size:13px;margin-bottom:10px;
        background:{_rgba("#000000",0.22)};border:1px solid var(--accent,{BLUE});color:var(--accent,{BLUE});}}
    .ebi-overview-card strong{{display:block;font-family:'Space Grotesk',sans-serif;font-size:22px;
        font-weight:700;color:#fff;letter-spacing:-0.4px;line-height:1.1;}}
    .ebi-overview-card small{{display:block;font-size:10px;font-weight:700;text-transform:uppercase;
        letter-spacing:.07em;color:rgba(255,255,255,0.45);margin-top:5px;}}
    .ebi-overview-detail{{display:block;font-size:10.5px;color:rgba(255,255,255,0.38);margin-top:3px;}}
    .ebi-overview-track{{background:rgba(255,255,255,0.08);border-radius:99px;height:4px;
        margin-top:9px;overflow:hidden;}}
    .ebi-overview-track i{{display:block;height:4px;border-radius:99px;background:var(--accent,{BLUE});
        box-shadow:0 0 8px -1px var(--accent,{BLUE});}}
    @media (max-width:1100px){{.ebi-overview{{grid-template-columns:repeat(3,minmax(0,1fr));}}}}
    @media (max-width:640px){{.ebi-overview{{grid-template-columns:repeat(2,minmax(0,1fr));}}}}

    .ebi-section{{display:flex;align-items:center;gap:10px;margin:28px 0 10px;}}
    .ebi-section span{{font-size:10px;font-weight:900;letter-spacing:.16em;color:{BLUE};
        width:22px;height:22px;border-radius:7px;display:flex;align-items:center;justify-content:center;
        background:{_rgba(BLUE,0.12)};border:1px solid {_rgba(BLUE,0.28)};flex-shrink:0;}}
    .ebi-section b{{font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;color:#fff;
        letter-spacing:-0.2px;}}
    .ebi-section i{{height:1px;flex:1;background:linear-gradient(90deg,rgba(255,255,255,.14),transparent);}}

    .ebi-head{{display:flex;align-items:center;gap:11px;margin:10px 0 8px;padding:11px 14px;
        border-left:2px solid {BLUE};background:linear-gradient(90deg,{_rgba(BLUE,0.07)},transparent);
        border-radius:0 12px 12px 0;}}
    .ebi-icon{{width:31px;height:31px;display:flex;align-items:center;justify-content:center;
        border-radius:9px;background:rgba(255,255,255,.07);font-size:15px;flex-shrink:0;}}
    .ebi-copy{{flex:1;min-width:0;}}
    .ebi-title{{font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:700;color:#fff;}}
    .ebi-sub{{font-size:10.5px;color:rgba(255,255,255,.45);margin-top:2px;}}
    .ebi-tag{{font-size:8.5px;font-weight:800;letter-spacing:.10em;text-transform:uppercase;
        color:#7DD3FC;border:1px solid {_rgba(BLUE,0.28)};border-radius:99px;padding:4px 9px;
        flex-shrink:0;white-space:nowrap;}}

    .ebi-selected{{display:flex;flex-wrap:wrap;gap:8px;margin:2px 0 10px;}}
    .ebi-selected span{{font-size:10.5px;color:rgba(255,255,255,.55);
        background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.10);
        border-radius:99px;padding:3px 10px;}}
    .ebi-selected span::first-letter{{color:var(--dot,{BLUE});}}

    .ebi-inc-scroll{{display:flex;flex-direction:column;gap:8px;max-height:420px;overflow-y:auto;
        padding-right:4px;}}
    .ebi-incident{{display:flex;align-items:center;gap:12px;padding:11px 14px;border-radius:12px;
        background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
        border-left:3px solid var(--incident,{AMBER});}}
    .ebi-incident.warning{{--incident:{AMBER};}}
    .ebi-incident.critical{{--incident:{RED};}}
    .ebi-inc-dot{{color:var(--incident,{AMBER});font-size:10px;flex-shrink:0;}}
    .ebi-inc-body{{flex:1;min-width:0;}}
    .ebi-inc-name{{font-size:12.5px;font-weight:700;color:#fff;}}
    .ebi-inc-sup{{font-size:10px;color:rgba(255,255,255,.40);margin-top:1px;}}
    .ebi-inc-main{{font-size:11px;color:rgba(255,255,255,.70);margin-top:4px;}}
    .ebi-inc-main strong{{color:#fff;}}
    .ebi-inc-main span{{color:rgba(255,255,255,.45);margin-left:6px;}}
    .ebi-inc-foot{{display:flex;gap:14px;margin-top:5px;font-size:10px;color:rgba(255,255,255,.40);}}
    .ebi-inc-foot b{{color:rgba(255,255,255,.70);}}
    .ebi-inc-badge{{font-size:9px;font-weight:800;letter-spacing:.06em;color:var(--incident,{AMBER});
        border:1px solid var(--incident,{AMBER});border-radius:99px;padding:4px 9px;flex-shrink:0;}}
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


def banner_header(eyebrow: str, title_html: str, subtitle: str, period_label: str, period_value: str) -> None:
    """Igual contenido que top_banner pero sin la tarjeta '.ebi-top' propia — para
    insertar dentro de un st.container(key=...) que ya trae su propio fondo/borde
    (como el banner '.st-key-hdrbanner' que ya tiene cada página de Dashboard WFM).
    `title_html` puede traer su propia clase (ej. 'hb-title') para el tamaño de fuente."""
    st.markdown(
        f"<div style='display:flex;justify-content:space-between;align-items:flex-start;"
        f"gap:20px;flex-wrap:wrap;'><div>"
        f"<div class='ebi-top-context'><i></i>{_safe(eyebrow)}</div>"
        f"{title_html}"
        f"<p style='font-size:12.5px;color:rgba(255,255,255,0.62);margin:6px 0 0;'>{_safe(subtitle)}</p>"
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
