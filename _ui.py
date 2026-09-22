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
import calendar

import numpy as np
import pandas as pd
import plotly.graph_objects as go
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


def toggle_dataframe(frame: pd.DataFrame, label: str, key: str, **kwargs) -> bool:
    """Tabla bajo demanda. Todas arrancan cerradas para que el análisis visual sea
    la primera capa del dashboard."""
    visible_key = f"{key}__visible"
    visible = bool(st.session_state.get(visible_key, False))
    icon = "🙈" if visible else "👁️"
    action = "Ocultar" if visible else "Ver"
    if st.button(f"{icon}  {action} tabla · {label}", key=f"{key}__toggle"):
        st.session_state[visible_key] = not visible
        st.rerun()
    if st.session_state.get(visible_key, False):
        kwargs.setdefault("hide_index", True)
        kwargs.setdefault("use_container_width", True)
        st.dataframe(frame, **kwargs)
        return True
    return False


def glow_line(
    fig: go.Figure, x, y, color: str, name: str = "", width: float = 2.5,
    dash: str = "solid", marker: bool = True, hovertemplate: str | None = None,
    showlegend: bool = False,
) -> None:
    """Agrega una línea con halo (glow) debajo de la línea nítida: una traza
    ancha y translúcida detrás + la línea con marcadores encima. Mismo truco
    visual que ya usaba "Tendencia de Adherencia", generalizado para que
    cualquier gráfico de línea/tendencia se vea con el mismo relieve."""
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines",
        line=dict(color=_rgba(color, .18), width=width * 4, shape="spline", dash=dash),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines+markers" if marker else "lines", name=name,
        line=dict(color=color, width=width, shape="spline", dash=dash),
        marker=dict(size=6, color="white", line=dict(color=color, width=2)) if marker else None,
        showlegend=showlegend,
        hovertemplate=hovertemplate or (
            f"<b>{_safe(name)}</b><br>%{{x}}: %{{y}}<extra></extra>" if name else "%{x}: %{y}<extra></extra>"
        ),
    ))


def donut(
    labels, values, colors, center_value: str, center_label: str,
    height: int = 370, hole: float = 0.6, pull_first: bool = True, min_share: float = 0.02,
) -> None:
    """Dona con etiquetas afuera y total al centro — mismo lenguaje visual
    que "Cierre de Abandonos" en Ocupación, reutilizable para cualquier
    distribución (Llegadas, motivos, etc.).

    Las categorías por debajo de `min_share` del total se agrupan en "Otros"
    (poner min_share=0 para desactivarlo) — con etiqueta afuera, una categoría
    minúscula igual imprime su texto completo y amontona el gráfico."""
    labels, values, colors = list(labels), [float(v) for v in values], list(colors)
    total = sum(values) or 1
    if min_share > 0 and labels:
        grandes = [(l, v, c) for l, v, c in zip(labels, values, colors) if v / total >= min_share]
        resto = sum(v for l, v, c in zip(labels, values, colors) if v / total < min_share)
        if resto > 0:
            grandes.append(("Otros", resto, MUTED))
        if grandes:
            labels, values, colors = (list(x) for x in zip(*grandes))
    pull = ([0.05] + [0] * (len(labels) - 1)) if (pull_first and labels) else None
    fig = go.Figure(go.Pie(
        labels=labels, values=list(values), hole=hole, sort=False,
        marker=dict(colors=list(colors), line=dict(color="#0A0813", width=2)),
        texttemplate="%{label}<br><b>%{percent}</b>", textposition="outside",
        textfont=dict(size=11, family="Inter", color="rgba(255,255,255,.85)"),
        pull=pull,
        hovertemplate="<b>%{label}</b><br>%{value:,} · %{percent}<extra></extra>",
    ))
    fig.update_layout(
        height=height, margin=dict(l=70, r=70, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False, font=dict(family="Inter", color="rgba(255,255,255,.72)"),
        annotations=[dict(
            text=f"{_safe(center_value)}<br><span style='font-size:11px;color:rgba(255,255,255,.45)'>{_safe(center_label)}</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=26, family="Space Grotesk", color="rgba(255,255,255,.92)"),
        )],
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def incident_list(items, scroll_height: int | None = 560) -> None:
    """Lista de incidencias puntuales (agente + fecha + qué falló) con las
    tarjetas `.ebi-incident` del sistema de diseño (definidas en el CSS pero
    sin usar hasta ahora). Más accionable que un ranking agregado: en vez de
    "quién va peor en promedio" muestra el caso concreto que hay que revisar.

    `items`: lista de dicts con:
      name (str), sup (str), date (str), value (str), label (str),
      severity ("critical" | "warning"), badge (str opcional),
      foot (lista opcional de tuplas (etiqueta, valor))."""
    if not items:
        st.info("Sin incidencias en el período filtrado.")
        return
    _badges_es = {"critical": "CRÍTICO", "warning": "ALERTA"}
    cards = []
    for it in items:
        sev = it.get("severity", "warning")
        foot_html = "".join(
            f"<span>{_safe(label)}: <b>{_safe(value)}</b></span>" for label, value in it.get("foot", [])
        )
        cards.append(
            f"<div class='ebi-incident {sev}'>"
            f"<div class='ebi-inc-dot'>●</div>"
            f"<div class='ebi-inc-body'>"
            f"<div class='ebi-inc-name'>{_safe(it['name'])}</div>"
            f"<div class='ebi-inc-sup'>{_safe(it.get('sup', ''))} · {_safe(it.get('date', ''))}</div>"
            f"<div class='ebi-inc-main'><strong>{_safe(it['value'])}</strong><span>{_safe(it['label'])}</span></div>"
            f"{f'<div class=\"ebi-inc-foot\">{foot_html}</div>' if foot_html else ''}"
            f"</div>"
            f"<span class='ebi-inc-badge'>{_safe(it.get('badge', _badges_es.get(sev, sev.upper())))}</span>"
            f"</div>"
        )
    style = f" style='max-height:{scroll_height}px'" if scroll_height else ""
    st.markdown(f"<div class='ebi-inc-scroll'{style}>{''.join(cards)}</div>", unsafe_allow_html=True)


def comparison_bar(
    values: pd.Series, eje_titulo: str, value_fmt, meta: float | None = None,
    color_fn=None, color_fija=None, height: int | None = None,
    extra=None, extra_label: str = "", tickformat: str | None = None,
) -> None:
    """Barra horizontal tipo "progreso": un carril de fondo tenue al 100 % del
    eje y la barra de valor superpuesta, con la franja de meta sombreada en
    verde y una línea vertical en el umbral. Es el lenguaje visual de
    "Comparativo por Supervisor" en Ocupación, reutilizable para cualquier
    ranking con una meta (o sin ella, si `meta` es None).

    `values`: Series (index=categoría, values=métrica) ya ordenada ascendente."""
    if values is None or values.empty:
        return
    cats = values.index.tolist()
    vals = values.tolist()
    if color_fn is not None:
        colors = [color_fn(v) for v in vals]
    elif isinstance(color_fija, list):
        colors = color_fija
    else:
        colors = [color_fija or PALETTE[0]] * len(vals)
    x_max = max(vals + ([meta] if meta is not None else [])) * 1.15 or 1
    customdata = extra.reindex(values.index).tolist() if extra is not None else None
    if extra is not None:
        hover = f"<b>%{{y}}</b><br>{_safe(extra_label)}: %{{customdata}}<br>{_safe(eje_titulo)}: <b>%{{text}}</b><extra></extra>"
    else:
        hover = f"<b>%{{y}}</b><br>{_safe(eje_titulo)}: <b>%{{text}}</b><extra></extra>"

    fig = go.Figure()
    if meta is not None:
        fig.add_vrect(x0=meta, x1=x_max, fillcolor="rgba(16,185,129,.06)", layer="below", line_width=0)
    fig.add_trace(go.Bar(
        x=[x_max] * len(vals), y=cats, orientation="h",
        marker=dict(color="rgba(255,255,255,.07)", line=dict(width=0)),
        showlegend=False, hoverinfo="skip", width=.55,
    ))
    fig.add_trace(go.Bar(
        x=vals, y=cats, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[value_fmt(v) for v in vals], textposition="outside", constraintext="none",
        textfont=dict(size=11, color="#CBD3F2", family="Inter"),
        customdata=customdata, hovertemplate=hover, width=.55,
    ))
    if meta is not None:
        fig.add_vline(x=meta, line_dash="dot", line_color="rgba(125,211,252,.75)", line_width=1.5)
        fig.add_annotation(
            x=meta, xref="x", y=1, yref="paper", yanchor="bottom", yshift=6,
            text=f"Meta {value_fmt(meta)}", showarrow=False,
            font=dict(size=10, color="#7DD3FC"),
        )
    fig.update_layout(
        barmode="overlay", height=height or max(280, len(cats) * 36 + 60),
        margin=dict(l=0, r=55, t=32, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            range=[0, x_max], gridcolor="rgba(255,255,255,.08)", showgrid=True, tickformat=tickformat,
            tickfont=dict(size=10, family="Inter", color="rgba(255,255,255,.62)"),
        ),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11, family="Inter", color="rgba(255,255,255,.75)")),
        showlegend=False, font=dict(family="Inter", size=11, color="rgba(255,255,255,.72)"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def percentage_matrix(
    frame: pd.DataFrame, row_col: str, date_col: str, metrics: dict[str, str],
    key: str, title: str, row_options=None, binary_metrics: set[str] | None = None,
) -> None:
    """Heatmap diario de porcentajes con semáforo: verde >=90 %, alerta 70–89,9 %
    y crítico <70 %. El selector de métrica y período es local a cada matriz.

    Los indicadores listados en `binary_metrics` se leen como Sí/No cuando la
    celda corresponde a un único registro (promedio exactamente 0 o 1, como en
    la matriz por experto); si la celda promedia varias personas (matriz por
    supervisor) se sigue mostrando el % agregado."""
    binary_metrics = binary_metrics or set()
    data = frame[[row_col, date_col] + list(metrics.values())].copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data = data.dropna(subset=[row_col, date_col])
    if row_options is not None:
        data = data[data[row_col].isin(row_options)]
    if data.empty:
        st.info("Sin datos para construir esta matriz.")
        return
    data["_month"] = data[date_col].dt.to_period("M").astype(str)
    months = sorted(data["_month"].unique())
    c1, c2 = st.columns(2)
    with c1:
        month = st.selectbox("Mes", months, index=len(months) - 1, key=f"{key}_month")
    with c2:
        metric_label = st.selectbox("Indicador", list(metrics), key=f"{key}_metric")
    metric_col = metrics[metric_label]
    is_binary = metric_label in binary_metrics
    selected = data[data["_month"] == month].copy()
    selected["_day"] = selected[date_col].dt.day
    rows = sorted(selected[row_col].astype(str).unique())
    year, mon = map(int, month.split("-"))
    days = list(range(1, calendar.monthrange(year, mon)[1] + 1))
    pivot = selected.groupby([row_col, "_day"])[metric_col].mean().unstack().reindex(index=rows, columns=days)
    values = pivot.astype(float).to_numpy()
    values[np.isnan(values)] = -0.05

    def _estado(v: float) -> str:
        return "sin registro" if v < 0 else ("cumple" if v >= .90 else "alerta" if v >= .70 else "crítico")

    def _label(v: float) -> str:
        if v < 0:
            return "—"
        if is_binary:
            if v >= .999:
                return "Sí"
            if v <= .001:
                return "No"
        return f"{v:.0%}"

    def _cell_text(v: float) -> str:
        # Etiqueta selectiva: el color ya comunica el estado en cada celda; el
        # número solo se imprime donde hace falta actuar (alerta o crítico),
        # para que la matriz no se vuelva ilegible con ~30 columnas por fila.
        # Sin el signo "%" (el eje y la leyenda ya dejan claro que es un
        # porcentaje) para que quepa en columnas tan angostas.
        if _estado(v) not in ("alerta", "crítico"):
            return ""
        return _label(v).rstrip("%")

    labels = np.vectorize(_cell_text)(values)
    hover = np.empty(values.shape, dtype=object)
    for i, name in enumerate(rows):
        for j, day in enumerate(days):
            value = values[i, j]
            hover[i, j] = f"<b>{html.escape(name)}</b><br>{day:02d}/{mon:02d}/{year}<br>{html.escape(metric_label)}: {_label(value)}<br>Estado: {_estado(value)}<extra></extra>"
    colors = [[0, "#1E293B"], [.049, "#1E293B"], [.05, "#F43F5E"], [.70, "#F43F5E"], [.7001, "#F59E0B"], [.90, "#F59E0B"], [.9001, "#10B981"], [1, "#10B981"]]
    fig = go.Figure(go.Heatmap(
        z=values, x=[f"{d:02d}" for d in days], y=rows, zmin=-.05, zmax=1,
        colorscale=colors, text=labels, texttemplate="%{text}",
        textfont=dict(size=10, family="Inter", color="rgba(255,255,255,.96)"),
        xgap=2, ygap=2,
        hovertext=hover, hovertemplate="%{hovertext}", showscale=False,
    ))
    fig.update_layout(
        height=max(320, len(rows) * 32 + 105), margin=dict(l=170, r=20, t=12, b=36),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
        font=dict(family="Inter"),
        xaxis=dict(side="top", showgrid=False, color="rgba(255,255,255,.55)", tickfont=dict(size=9.5)),
        yaxis=dict(showgrid=False, color="rgba(255,255,255,.70)", tickfont=dict(size=10.5)),
    )
    st.caption("Verde ≥ 90 % · amarillo 70–89,9 % · rojo < 70 % · gris: sin registro")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"{key}_chart")


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
