#!/usr/bin/env python3
"""
Calculadora de Extras Quincenal - Colombia (Streamlit)
Calcula los recargos extras (nocturnas y dominicales/festivos) sobre un
sueldo base quincenal editable.

Tarifas de extras (COP por hora) — valores por defecto:
  - Hora Nocturna Normal:      $10.700  (días ordinarios, a partir 19:00 h)
  - Hora Diurna Dominical:     $14.300  (domingos y festivos)
  - Hora Nocturna Dominical:   $17.100  (domingos y festivos, a partir 19:00 h)

Las horas diurnas normales están cubiertas por el sueldo base y no generan
recargo adicional.

Todos los valores monetarios son editables desde el panel de configuración.

Festivos Colombia 2026 incluidos.
"""

import streamlit as st
from datetime import date
import calendar as cal_module

# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Calculadora de Sueldo Quincenal — Colombia",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTANTES (valores por defecto — no se usan directamente en el cálculo)
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_RATES: dict[str, int] = {
    "diurna_normal": 7_950,
    "nocturna_normal": 10_700,
    "diurna_dominical": 14_300,
    "nocturna_dominical": 17_100,
}

DEFAULT_SUELDO_BASE = 929_964

NIGHT_START = 19

HOUR_OPTIONS = [f"{h:02d}:00" for h in range(24)]

HOUR_DICT = {f"{h:02d}:00": float(h) for h in range(24)}

DAYS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
MONTHS_ES = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]

GRID_COLS = 5

# Festivos Colombia 2026
HOLIDAYS_2026: set[date] = {
    date(2026, 1, 1),
    date(2026, 1, 12),
    date(2026, 3, 23),
    date(2026, 4, 2),
    date(2026, 4, 3),
    date(2026, 5, 1),
    date(2026, 5, 18),
    date(2026, 6, 8),
    date(2026, 6, 15),
    date(2026, 6, 29),
    date(2026, 7, 20),
    date(2026, 8, 7),
    date(2026, 8, 17),
    date(2026, 10, 12),
    date(2026, 11, 2),
    date(2026, 11, 16),
    date(2026, 12, 8),
    date(2026, 12, 25),
}

# ═══════════════════════════════════════════════════════════════════════════════
#  LÓGICA DE CÁLCULO
# ═══════════════════════════════════════════════════════════════════════════════


def quincena_dates(year: int, month: int, first: bool) -> list[date]:
    if first:
        return [date(year, month, d) for d in range(1, 16)]
    last = cal_module.monthrange(year, month)[1]
    return [date(year, month, d) for d in range(16, last + 1)]


def parse_hhmm(text: str) -> float:
    """Convierte 'HH:MM' a horas decimales. Lanza ValueError si el formato es inválido."""
    text = text.strip()
    if ":" not in text:
        raise ValueError(f"Formato inválido '{text}' — use HH:MM (ej: 08:00)")
    parts = text.split(":", 1)
    try:
        h, m = int(parts[0]), int(parts[1])
    except ValueError:
        raise ValueError(
            f"Formato inválido '{text}' — los valores deben ser numéricos (ej: 08:00)"
        )
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError(f"Hora fuera de rango '{text}' — horas 0–23, minutos 0–59")
    return h + m / 60.0


def shift_breakdown(
    start: float, end: float, is_sunday: bool, rates: dict[str, int]
) -> dict[str, float]:
    def _split(a: float, b: float) -> tuple[float, float]:
        night = float(NIGHT_START)
        day_h = max(0.0, min(b, night) - a)
        night_h = max(0.0, b - max(a, night))
        return day_h, night_h

    if end >= start:
        dh, nh = _split(start, end)
    else:
        d1, n1 = _split(start, 24.0)
        d2, n2 = _split(0.0, end)
        dh, nh = d1 + d2, n1 + n2

    key_d = "diurna_dominical" if is_sunday else "diurna_normal"
    key_n = "nocturna_dominical" if is_sunday else "nocturna_normal"

    result: dict[str, float] = {k: 0.0 for k in rates}
    result[key_d] = dh
    result[key_n] = nh
    return result


# ═══════════════════════════════════════════════════════════════════════════════
#  INICIALIZACIÓN DE SESIÓN
# ═══════════════════════════════════════════════════════════════════════════════

if "rates" not in st.session_state:
    st.session_state.rates = dict(DEFAULT_RATES)
    st.session_state.sueldo_base = DEFAULT_SUELDO_BASE

if "year" not in st.session_state:
    today = date.today()
    st.session_state.year = today.year
    st.session_state.month = today.month
    st.session_state.first = today.day <= 15
    st.session_state.day_states = {}
    st.session_state.summary_visible = False


# ═══════════════════════════════════════════════════════════════════════════════
#  FUNCIÓN AUXILIAR: INICIALIZAR ESTADO DE DÍAS
# ═══════════════════════════════════════════════════════════════════════════════


def initialize_day_state(d: date) -> None:
    key = str(d)
    if key not in st.session_state.day_states:
        st.session_state.day_states[key] = {
            "working": True,
            "start": "08:00",
            "end": "17:00",
        }


def get_day_state(d: date) -> dict:
    initialize_day_state(d)
    return st.session_state.day_states[str(d)]


# ═══════════════════════════════════════════════════════════════════════════════
#  INTERFAZ
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    rates = st.session_state.rates
    sueldo_base = st.session_state.sueldo_base

    # ── Título ──
    st.markdown(
        """
        <h1 style='text-align: center; color: #faa61a;'>💼 Calculadora de Sueldo Quincenal</h1>
        <p style='text-align: center; color: #99aab5; font-size: 14px;'>
        🇨🇴 Extras: nocturnas y dominicales/festivos · Base y tarifas editables · Nocturnas desde las 19:00 h
        </p>
        """,
        unsafe_allow_html=True,
    )

    # ── Rate chips (ahora reflejan los valores en sesión) ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💼 Sueldo Base", f"${sueldo_base:,}", "quincenal")
    with col2:
        st.metric(
            "🌙 Nocturna Normal", f"${rates['nocturna_normal']:,}/h", "días ordinarios"
        )
    with col3:
        st.metric(
            "☀ Diurna Dominical",
            f"${rates['diurna_dominical']:,}/h",
            "domingos/festivos",
        )
    with col4:
        st.metric(
            "🌙 Nocturna Dominical",
            f"${rates['nocturna_dominical']:,}/h",
            "domingos/festivos",
        )

    st.divider()

    # ── Panel de configuración de tarifas ──
    with st.expander("⚙️ Configuración de Tarifas", expanded=False):
        st.caption(
            "Modificá los valores y los cálculos se actualizarán automáticamente."
        )

        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        with col_a:
            nuevo_sueldo = st.number_input(
                "Sueldo Base Quincenal",
                min_value=0,
                value=sueldo_base,
                step=1000,
                key="cfg_sueldo_base",
                format="%d",
            )
            st.session_state.sueldo_base = int(nuevo_sueldo)

        with col_b:
            nuevo_rn = st.number_input(
                "Nocturna Normal ($/h)",
                min_value=0,
                value=rates["nocturna_normal"],
                step=100,
                key="cfg_nocturna_normal",
                format="%d",
            )
            st.session_state.rates["nocturna_normal"] = int(nuevo_rn)

        with col_c:
            nuevo_rd = st.number_input(
                "Diurna Dominical ($/h)",
                min_value=0,
                value=rates["diurna_dominical"],
                step=100,
                key="cfg_diurna_dominical",
                format="%d",
            )
            st.session_state.rates["diurna_dominical"] = int(nuevo_rd)

        with col_d:
            nuevo_rnd = st.number_input(
                "Nocturna Dominical ($/h)",
                min_value=0,
                value=rates["nocturna_dominical"],
                step=100,
                key="cfg_nocturna_dominical",
                format="%d",
            )
            st.session_state.rates["nocturna_dominical"] = int(nuevo_rnd)

        with col_e:
            nuevo_dn = st.number_input(
                "Diurna Normal ($/h)",
                min_value=0,
                value=rates["diurna_normal"],
                step=100,
                key="cfg_diurna_normal",
                format="%d",
                help="No genera recargo extra; solo informativo.",
            )
            st.session_state.rates["diurna_normal"] = int(nuevo_dn)

        if st.button("↺ Restaurar Valores por Defecto", key="btn_reset_config"):
            st.session_state.rates = dict(DEFAULT_RATES)
            st.session_state.sueldo_base = DEFAULT_SUELDO_BASE
            st.rerun()

        st.caption(
            "Las horas diurnas normales están cubiertas por el sueldo base y no generan recargo adicional."
        )

    st.divider()

    # Recargar por si se editaron
    rates = st.session_state.rates
    sueldo_base = st.session_state.sueldo_base

    # ── Navegación de período ──
    col_prev, col_period, col_next = st.columns([1, 3, 1])

    with col_prev:
        if st.button("◀ Anterior", key="btn_prev", use_container_width=True):
            if st.session_state.first:
                st.session_state.first = False
                st.session_state.month -= 1
                if st.session_state.month == 0:
                    st.session_state.month = 12
                    st.session_state.year -= 1
            else:
                st.session_state.first = True
            st.session_state.day_states = {}
            st.rerun()

    with col_period:
        q = "Primera" if st.session_state.first else "Segunda"
        m = MONTHS_ES[st.session_state.month - 1]
        st.markdown(
            f"<h3 style='text-align: center;'>{m} {st.session_state.year} — {q} Quincena</h3>",
            unsafe_allow_html=True,
        )

    with col_next:
        if st.button("Siguiente ▶", key="btn_next", use_container_width=True):
            if st.session_state.first:
                st.session_state.first = False
            else:
                st.session_state.first = True
                st.session_state.month += 1
                if st.session_state.month == 13:
                    st.session_state.month = 1
                    st.session_state.year += 1
            st.session_state.day_states = {}
            st.rerun()

    st.divider()

    # ── Acciones masivas ──
    st.subheader("⚡ Acciones Masivas")
    col_btn1, col_btn2, col_sep, col_label, col_start, col_arrow, col_end, col_apply = (
        st.columns([1, 1, 0.5, 1.5, 1, 0.3, 1, 1.5])
    )

    with col_btn1:
        if st.button("✔ Trabajo", use_container_width=True, key="btn_all_work"):
            for d in quincena_dates(
                st.session_state.year, st.session_state.month, st.session_state.first
            ):
                st.session_state.day_states[str(d)] = {
                    "working": True,
                    "start": st.session_state.day_states.get(str(d), {}).get(
                        "start", "08:00"
                    ),
                    "end": st.session_state.day_states.get(str(d), {}).get(
                        "end", "17:00"
                    ),
                }
            st.rerun()

    with col_btn2:
        if st.button("✖ Descanso", use_container_width=True, key="btn_all_rest"):
            for d in quincena_dates(
                st.session_state.year, st.session_state.month, st.session_state.first
            ):
                st.session_state.day_states[str(d)] = {
                    "working": False,
                    "start": "08:00",
                    "end": "17:00",
                }
            st.rerun()

    with col_label:
        st.write("Horario masivo:")

    with col_start:
        bulk_start = st.selectbox(
            "Entrada",
            options=HOUR_OPTIONS,
            index=8,  # 08:00
            key="bulk_start_input",
            label_visibility="collapsed",
        )

    with col_arrow:
        st.write("→")

    with col_end:
        bulk_end = st.selectbox(
            "Salida",
            options=HOUR_OPTIONS,
            index=17,  # 17:00
            key="bulk_end_input",
            label_visibility="collapsed",
        )

    with col_apply:
        if st.button("Aplicar", key="btn_apply_bulk", use_container_width=True):
            e_dec = HOUR_DICT[bulk_end]
            s_dec = HOUR_DICT[bulk_start]
            if e_dec < s_dec:
                st.warning(
                    f"La salida ({bulk_end}) es anterior a la entrada ({bulk_start}). "
                    "¿Es un turno que cruza la medianoche?",
                    icon="⚠️",
                )
            for d in quincena_dates(
                st.session_state.year, st.session_state.month, st.session_state.first
            ):
                state = get_day_state(d)
                if state["working"]:
                    state["start"] = bulk_start
                    state["end"] = bulk_end
            st.rerun()

    st.divider()

    # ── Grilla de días ──
    st.subheader("📅 Días de la Quincena")

    dates = quincena_dates(
        st.session_state.year, st.session_state.month, st.session_state.first
    )

    for row_idx in range(0, len(dates), GRID_COLS):
        cols = st.columns(GRID_COLS)
        for col_idx, col in enumerate(cols):
            day_idx = row_idx + col_idx
            if day_idx < len(dates):
                d = dates[day_idx]
                state = get_day_state(d)

                is_sunday = d.weekday() == 6
                is_holiday = d in HOLIDAYS_2026
                is_dominical = is_sunday or is_holiday
                holiday_not_sunday = is_holiday and not is_sunday

                day_name = DAYS_ES[d.weekday()]
                if holiday_not_sunday:
                    suffix = " 🇨🇴"
                elif is_dominical:
                    suffix = " 🟠"
                else:
                    suffix = ""

                with col:
                    card_bg = "#fff8ee" if is_dominical else "#f0f2f5"
                    hdr_color = "#e67e22" if is_dominical else "#5a6268"

                    st.markdown(
                        f"""
                        <div style='background-color: {card_bg}; padding: 12px; border-radius: 8px; border: 1px solid #ddd;'>
                        <h4 style='margin: 0; color: {hdr_color};'>{d.day} {day_name}{suffix}</h4>
                        """,
                        unsafe_allow_html=True,
                    )

                    working = st.radio(
                        "Estado",
                        options=[True, False],
                        format_func=lambda x: "Trabajo" if x else "Descanso",
                        index=0 if state["working"] else 1,
                        key=f"radio_{d}",
                        label_visibility="collapsed",
                    )
                    state["working"] = working

                    if working:
                        col_in, col_out = st.columns(2)
                        with col_in:
                            try:
                                start_idx = HOUR_OPTIONS.index(state["start"])
                            except ValueError:
                                start_idx = 8
                            start_time = st.selectbox(
                                "Entrada",
                                options=HOUR_OPTIONS,
                                index=start_idx,
                                key=f"start_{d}",
                                label_visibility="collapsed",
                            )
                            state["start"] = start_time
                        with col_out:
                            try:
                                end_idx = HOUR_OPTIONS.index(state["end"])
                            except ValueError:
                                end_idx = 17
                            end_time = st.selectbox(
                                "Salida",
                                options=HOUR_OPTIONS,
                                index=end_idx,
                                key=f"end_{d}",
                                label_visibility="collapsed",
                            )
                            state["end"] = end_time
                    else:
                        st.write("(sin horas)")

                    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ── Botón calcular ──
    col_calc = st.columns([1, 3, 1])[1]
    with col_calc:
        if st.button(
            "💰 Calcular Quincena", use_container_width=True, key="btn_calculate"
        ):
            st.session_state.summary_visible = True
            st.rerun()

    # ── Resumen y cálculo ──
    if st.session_state.summary_visible:
        st.divider()
        st.subheader("📊 Resumen de Cálculo")

        totals: dict[str, float] = {k: 0.0 for k in rates}
        errors: list[str] = []

        for d in dates:
            state = get_day_state(d)
            if state["working"]:
                is_dominical = d.weekday() == 6 or d in HOLIDAYS_2026
                start = HOUR_DICT.get(state["start"])
                end = HOUR_DICT.get(state["end"])
                if start is None or end is None:
                    errors.append(
                        f"Día {d.day}: formato de hora inválido ({state['start']} / {state['end']})"
                    )
                    continue
                bd = shift_breakdown(start, end, is_dominical, rates)
                for k in rates:
                    totals[k] += bd[k]
            else:
                bd = {k: 0.0 for k in rates}

        if errors:
            st.error("Errores de entrada:\n" + "\n".join(errors))
        else:
            col_label, col_value = st.columns([2, 2])

            with col_label:
                st.markdown("**💼 Sueldo Base**")
            with col_value:
                st.markdown(f"**${sueldo_base:,}**")

            for key in ("nocturna_normal", "diurna_dominical", "nocturna_dominical"):
                hrs = totals[key]
                pay = hrs * rates[key]
                labels = {
                    "nocturna_normal": "🌙 Nocturna Normal",
                    "diurna_dominical": "☀ Diurna Dominical",
                    "nocturna_dominical": "🌙 Nocturna Dominical",
                }
                with col_label:
                    st.markdown(f"**{labels[key]}**")
                with col_value:
                    st.markdown(f"{hrs:.2f} hrs · **${pay:,.0f}**")

            st.divider()

            extras_total = sum(
                totals[k] * rates[k]
                for k in ("nocturna_normal", "diurna_dominical", "nocturna_dominical")
            )
            total = sueldo_base + extras_total

            col_total_label, col_total_value = st.columns([2, 2])
            with col_total_label:
                st.markdown("## 💰 TOTAL QUINCENA")
            with col_total_value:
                st.markdown(f"# ${total:,.0f}")


if __name__ == "__main__":
    main()
