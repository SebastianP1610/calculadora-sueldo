#!/usr/bin/env python3
"""
Calculadora de Sueldo Quincenal - Colombia
Calcula el sueldo quincenal basado en horas trabajadas por día.

Tarifas (COP por hora):
  - Hora Diurna Normal:        $7.950
  - Hora Nocturna Normal:      $10.700
  - Hora Diurna Dominical:     $14.300
  - Hora Nocturna Dominical:   $17.100

Las horas nocturnas rigen a partir de las 19:00 h.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import calendar as cal_module

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────

RATES: dict[str, int] = {
    "diurna_normal":      7_950,
    "nocturna_normal":   10_700,
    "diurna_dominical":  14_300,
    "nocturna_dominical": 17_100,
}

NIGHT_START = 19  # Las horas nocturnas empiezan a las 19:00 h (7 PM)

DAYS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
MONTHS_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

GRID_COLS = 5  # Número de columnas en la grilla de días

# Colores — tema oscuro
C_BG       = "#2c2f33"
C_DARK     = "#23272a"
C_NAV      = "#36393f"
C_BTN      = "#4f545c"
C_GREEN    = "#43b581"
C_RED      = "#f04747"
C_BLUE     = "#7289da"
C_GOLD     = "#faa61a"
C_WHITE    = "#ffffff"
C_MUTED    = "#99aab5"
C_TEXT     = "#dcddde"

C_SUN_HDR  = "#e67e22"
C_NORM_HDR = "#5a6268"
C_SUN_BG   = "#fff8ee"
C_NORM_BG  = "#f0f2f5"
C_REST_BG  = "#dee2e6"

CHIP_COLORS = {
    "diurna_normal":      "#4a90d9",
    "nocturna_normal":    "#7b68ee",
    "diurna_dominical":   "#e67e22",
    "nocturna_dominical": "#e74c3c",
}


# ─────────────────────────────────────────────────────────────────────────────
#  LÓGICA DE CÁLCULO
# ─────────────────────────────────────────────────────────────────────────────

def quincena_dates(year: int, month: int, first: bool) -> list[date]:
    """Retorna la lista de fechas que componen la quincena indicada."""
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
        raise ValueError(f"Formato inválido '{text}' — los valores deben ser numéricos (ej: 08:00)")
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError(f"Hora fuera de rango '{text}' — horas 0–23, minutos 0–59")
    return h + m / 60.0


def shift_breakdown(start: float, end: float, is_sunday: bool) -> dict[str, float]:
    """
    Calcula las horas diurnas y nocturnas de un turno.

    Parámetros:
        start  — hora de entrada en formato decimal (ej: 8.5 = 08:30)
        end    — hora de salida en formato decimal. Si end < start, el turno
                 cruza la medianoche (turno nocturno).
        is_sunday — True si el día es domingo (aplican tarifas dominicales).

    Retorna un dict con las horas acumuladas por tipo de tarifa.
    """

    def _split(a: float, b: float) -> tuple[float, float]:
        """Divide el segmento [a, b) entre horas diurnas y nocturnas."""
        night = float(NIGHT_START)
        day_h   = max(0.0, min(b, night) - a)
        night_h = max(0.0, b - max(a, night))
        return day_h, night_h

    if end >= start:
        dh, nh = _split(start, end)
    else:
        # Turno que cruza la medianoche: [start, 24) + [0, end)
        d1, n1 = _split(start, 24.0)
        d2, n2 = _split(0.0, end)
        dh, nh = d1 + d2, n1 + n2

    key_d = "diurna_dominical"   if is_sunday else "diurna_normal"
    key_n = "nocturna_dominical" if is_sunday else "nocturna_normal"

    result: dict[str, float] = {k: 0.0 for k in RATES}
    result[key_d] = dh
    result[key_n] = nh
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  WIDGET: TARJETA DE DÍA
# ─────────────────────────────────────────────────────────────────────────────

class DayCard(tk.Frame):
    """Tarjeta que representa un día de la quincena."""

    def __init__(self, master: tk.Widget, day: date, **kw):
        self._is_sunday = day.weekday() == 6
        bg = C_SUN_BG if self._is_sunday else C_NORM_BG
        super().__init__(master, bg=bg, relief="solid", bd=1, **kw)
        self.day = day
        self._build()

    # ── Construcción del widget ───────────────────────────────────────────────

    def _build(self) -> None:
        bg      = self.cget("bg")
        hdr_bg  = C_SUN_HDR if self._is_sunday else C_NORM_HDR
        day_lbl = DAYS_ES[self.day.weekday()]
        suffix  = " 🟠" if self._is_sunday else ""

        # Encabezado con número de día y nombre
        hdr = tk.Frame(self, bg=hdr_bg, pady=3)
        hdr.pack(fill="x")
        tk.Label(hdr, text=str(self.day.day),
                 font=("Helvetica", 15, "bold"),
                 bg=hdr_bg, fg=C_WHITE).pack(side="left", padx=5)
        tk.Label(hdr, text=day_lbl + suffix,
                 font=("Helvetica", 9),
                 bg=hdr_bg, fg=C_WHITE).pack(side="right", padx=5)

        # Selector Trabajo / Descanso
        body = tk.Frame(self, bg=bg, pady=2)
        body.pack(fill="x", padx=4)
        self._working = tk.BooleanVar(value=True)
        tk.Radiobutton(body, text="Trabajo",  variable=self._working, value=True,
                       bg=bg, font=("Helvetica", 8),
                       command=self._on_toggle).pack(side="left")
        tk.Radiobutton(body, text="Descanso", variable=self._working, value=False,
                       bg=bg, font=("Helvetica", 8),
                       command=self._on_toggle).pack(side="right")

        # Entradas de hora
        tf = tk.Frame(self, bg=bg)
        tf.pack(fill="x", padx=6, pady=(2, 6))
        tk.Label(tf, text="Entrada:", bg=bg,
                 font=("Helvetica", 8), width=7, anchor="w").grid(row=0, column=0, sticky="w")
        self._start_var = tk.StringVar(value="08:00")
        self._start_e = tk.Entry(tf, textvariable=self._start_var,
                                 width=6, font=("Helvetica", 9))
        self._start_e.grid(row=0, column=1)

        tk.Label(tf, text="Salida:", bg=bg,
                 font=("Helvetica", 8), width=7, anchor="w").grid(row=1, column=0, sticky="w")
        self._end_var = tk.StringVar(value="17:00")
        self._end_e = tk.Entry(tf, textvariable=self._end_var,
                               width=6, font=("Helvetica", 9))
        self._end_e.grid(row=1, column=1)

    # ── Eventos ───────────────────────────────────────────────────────────────

    def _on_toggle(self) -> None:
        working = self._working.get()
        state  = "normal" if working else "disabled"
        self._start_e.config(state=state)
        self._end_e.config(state=state)
        new_bg = (C_SUN_BG if self._is_sunday else C_NORM_BG) if working else C_REST_BG
        self.config(bg=new_bg)

    # ── API pública ───────────────────────────────────────────────────────────

    @property
    def is_working(self) -> bool:
        return self._working.get()

    def set_working(self, value: bool) -> None:
        self._working.set(value)
        self._on_toggle()

    def set_times(self, start: str, end: str) -> None:
        self._start_var.set(start)
        self._end_var.set(end)

    def get_breakdown(self) -> dict[str, float]:
        """Retorna el desglose de horas del día. Lanza ValueError si las horas son inválidas."""
        if not self._working.get():
            return {k: 0.0 for k in RATES}
        start = parse_hhmm(self._start_var.get())
        end   = parse_hhmm(self._end_var.get())
        return shift_breakdown(start, end, self._is_sunday)


# ─────────────────────────────────────────────────────────────────────────────
#  APLICACIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("💼 Calculadora de Sueldo Quincenal — Colombia")
        self.geometry("960x780")
        self.minsize(720, 620)
        self.configure(bg=C_BG)

        today = date.today()
        self._year  = today.year
        self._month = today.month
        self._first = today.day <= 15
        self._cards: list[DayCard] = []

        self._build_ui()
        self._refresh_period()

    # ── Construcción de la interfaz ───────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_title()
        self._build_rate_chips()
        self._build_nav()
        self._build_bulk_actions()
        self._build_day_grid()
        self._build_summary()
        self._build_calc_button()

    def _build_title(self) -> None:
        tb = tk.Frame(self, bg=C_DARK, pady=10)
        tb.pack(fill="x")
        tk.Label(tb, text="💼  Calculadora de Sueldo Quincenal",
                 font=("Helvetica", 20, "bold"),
                 bg=C_DARK, fg=C_WHITE).pack()
        tk.Label(tb, text="🇨🇴  Horas nocturnas desde las 19:00 h  ·  Formato de hora: HH:MM",
                 font=("Helvetica", 10), bg=C_DARK, fg=C_MUTED).pack(pady=(2, 0))

    def _build_rate_chips(self) -> None:
        rc = tk.Frame(self, bg=C_BG, pady=6)
        rc.pack(fill="x", padx=10)
        chips = [
            ("diurna_normal",      "☀  Diurna Normal"),
            ("nocturna_normal",    "🌙  Nocturna Normal"),
            ("diurna_dominical",   "☀  Diurna Dominical"),
            ("nocturna_dominical", "🌙  Nocturna Dominical"),
        ]
        for key, label in chips:
            color = CHIP_COLORS[key]
            chip = tk.Frame(rc, bg=color, padx=10, pady=5)
            chip.pack(side="left", padx=4)
            tk.Label(chip, text=label,
                     bg=color, fg=C_WHITE, font=("Helvetica", 8, "bold")).pack()
            tk.Label(chip, text=f"${RATES[key]:,} / hora",
                     bg=color, fg=C_WHITE, font=("Helvetica", 9)).pack()

    def _build_nav(self) -> None:
        nav = tk.Frame(self, bg=C_NAV, pady=7)
        nav.pack(fill="x")
        tk.Button(nav, text="◀  Anterior", command=self._prev,
                  bg=C_BTN, fg=C_WHITE, relief="flat",
                  font=("Helvetica", 10, "bold"), padx=14).pack(side="left", padx=12)
        self._period_lbl = tk.Label(nav, text="", bg=C_NAV, fg=C_WHITE,
                                    font=("Helvetica", 13, "bold"))
        self._period_lbl.pack(side="left", expand=True)
        tk.Button(nav, text="Siguiente  ▶", command=self._next,
                  bg=C_BTN, fg=C_WHITE, relief="flat",
                  font=("Helvetica", 10, "bold"), padx=14).pack(side="right", padx=12)

    def _build_bulk_actions(self) -> None:
        ba = tk.Frame(self, bg=C_BG, pady=5)
        ba.pack(fill="x", padx=10)

        tk.Label(ba, text="Aplicar a todos:", bg=C_BG, fg=C_MUTED,
                 font=("Helvetica", 9)).pack(side="left", padx=(0, 6))
        tk.Button(ba, text="✔ Trabajo",  command=lambda: self._set_all(True),
                  bg=C_GREEN, fg=C_WHITE, relief="flat",
                  font=("Helvetica", 8, "bold"), padx=8).pack(side="left", padx=2)
        tk.Button(ba, text="✖ Descanso", command=lambda: self._set_all(False),
                  bg=C_RED, fg=C_WHITE, relief="flat",
                  font=("Helvetica", 8, "bold"), padx=8).pack(side="left", padx=2)

        tk.Label(ba, text="  Horario masivo:", bg=C_BG, fg=C_MUTED,
                 font=("Helvetica", 9)).pack(side="left", padx=(12, 4))
        self._bulk_start = tk.StringVar(value="08:00")
        self._bulk_end   = tk.StringVar(value="17:00")
        tk.Entry(ba, textvariable=self._bulk_start, width=6,
                 font=("Helvetica", 9)).pack(side="left", padx=2)
        tk.Label(ba, text="→", bg=C_BG, fg=C_WHITE).pack(side="left")
        tk.Entry(ba, textvariable=self._bulk_end, width=6,
                 font=("Helvetica", 9)).pack(side="left", padx=2)
        tk.Button(ba, text="Aplicar horario", command=self._apply_bulk_times,
                  bg=C_BLUE, fg=C_WHITE, relief="flat",
                  font=("Helvetica", 8, "bold"), padx=8).pack(side="left", padx=4)

    def _build_day_grid(self) -> None:
        outer = tk.Frame(self, bg=C_BG)
        outer.pack(fill="both", expand=True, padx=6, pady=4)

        self._canvas = tk.Canvas(outer, bg=C_BG, highlightthickness=0)
        vscroll = ttk.Scrollbar(outer, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._grid_frame = tk.Frame(self._canvas, bg=C_BG)
        self._cwin = self._canvas.create_window((0, 0), window=self._grid_frame, anchor="nw")

        self._grid_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )
        self._canvas.bind(
            "<Configure>",
            lambda e: self._canvas.itemconfig(self._cwin, width=e.width),
        )
        # Soporte para rueda del ratón
        self._canvas.bind_all(
            "<MouseWheel>", lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units")
        )
        self._canvas.bind_all("<Button-4>", lambda e: self._canvas.yview_scroll(-1, "units"))
        self._canvas.bind_all("<Button-5>", lambda e: self._canvas.yview_scroll(1, "units"))

    def _build_summary(self) -> None:
        sp = tk.Frame(self, bg=C_DARK, pady=8)
        sp.pack(fill="x")

        self._sum_vars: dict[str, tk.StringVar] = {}
        rows_cfg = [
            ("diurna_normal",      "☀  Diurna Normal",       CHIP_COLORS["diurna_normal"]),
            ("nocturna_normal",    "🌙  Nocturna Normal",     CHIP_COLORS["nocturna_normal"]),
            ("diurna_dominical",   "☀  Diurna Dominical",    CHIP_COLORS["diurna_dominical"]),
            ("nocturna_dominical", "🌙  Nocturna Dominical",  CHIP_COLORS["nocturna_dominical"]),
        ]
        for key, name, color in rows_cfg:
            v = tk.StringVar(value="0.00 hrs  ·  $0")
            self._sum_vars[key] = v
            row = tk.Frame(sp, bg=C_DARK)
            row.pack(fill="x", padx=16, pady=1)
            tk.Label(row, text=name, width=22, anchor="w",
                     bg=C_DARK, fg=color,
                     font=("Helvetica", 10, "bold")).pack(side="left")
            tk.Label(row, textvariable=v, bg=C_DARK, fg=C_TEXT,
                     font=("Helvetica", 10)).pack(side="left", padx=6)

        tk.Frame(sp, bg=C_BTN, height=1).pack(fill="x", padx=16, pady=5)

        total_row = tk.Frame(sp, bg=C_DARK)
        total_row.pack(fill="x", padx=16)
        tk.Label(total_row, text="💰  TOTAL QUINCENA", width=22, anchor="w",
                 bg=C_DARK, fg=C_GOLD,
                 font=("Helvetica", 14, "bold")).pack(side="left")
        self._total_var = tk.StringVar(value="$0")
        tk.Label(total_row, textvariable=self._total_var,
                 bg=C_DARK, fg=C_GREEN,
                 font=("Helvetica", 16, "bold")).pack(side="left", padx=8)

    def _build_calc_button(self) -> None:
        bf = tk.Frame(self, bg=C_BG, pady=8)
        bf.pack(fill="x")
        tk.Button(bf, text="  💰  Calcular Quincena  ",
                  command=self._calculate,
                  bg=C_GREEN, fg=C_WHITE,
                  font=("Helvetica", 13, "bold"),
                  relief="flat", pady=8).pack()

    # ── Manejo de la quincena ─────────────────────────────────────────────────

    def _refresh_period(self) -> None:
        """Reconstruye la grilla de tarjetas para la quincena actual."""
        for w in self._grid_frame.winfo_children():
            w.destroy()
        self._cards.clear()

        q = "Primera" if self._first else "Segunda"
        m = MONTHS_ES[self._month - 1]
        self._period_lbl.config(text=f"{m}  {self._year}  —  {q} Quincena")

        dates = quincena_dates(self._year, self._month, self._first)
        for i, d in enumerate(dates):
            row, col = divmod(i, GRID_COLS)
            card = DayCard(self._grid_frame, d)
            card.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            self._cards.append(card)

        for c in range(GRID_COLS):
            self._grid_frame.columnconfigure(c, weight=1)

        self._reset_summary()

    def _reset_summary(self) -> None:
        for v in self._sum_vars.values():
            v.set("0.00 hrs  ·  $0")
        self._total_var.set("$0")

    def _prev(self) -> None:
        if self._first:
            # Ir a la segunda quincena del mes anterior
            self._first = False
            self._month -= 1
            if self._month == 0:
                self._month = 12
                self._year -= 1
        else:
            # Ir a la primera quincena del mismo mes
            self._first = True
        self._refresh_period()

    def _next(self) -> None:
        if self._first:
            # Ir a la segunda quincena del mismo mes
            self._first = False
        else:
            # Ir a la primera quincena del mes siguiente
            self._first = True
            self._month += 1
            if self._month == 13:
                self._month = 1
                self._year += 1
        self._refresh_period()

    # ── Acciones masivas ──────────────────────────────────────────────────────

    def _set_all(self, working: bool) -> None:
        for card in self._cards:
            card.set_working(working)

    def _apply_bulk_times(self) -> None:
        s, e = self._bulk_start.get(), self._bulk_end.get()
        try:
            s_dec = parse_hhmm(s)
            e_dec = parse_hhmm(e)
        except ValueError as err:
            messagebox.showerror("Error en horario masivo", str(err))
            return
        if e_dec < s_dec:
            if not messagebox.askyesno(
                "Turno nocturno cruzando medianoche",
                f"La salida ({e}) es anterior a la entrada ({s}).\n"
                "¿Confirmas que es un turno que cruza la medianoche?",
            ):
                return
        for card in self._cards:
            if card.is_working:
                card.set_times(s, e)

    # ── Cálculo ───────────────────────────────────────────────────────────────

    def _calculate(self) -> None:
        totals: dict[str, float] = {k: 0.0 for k in RATES}
        errors: list[str] = []

        for card in self._cards:
            try:
                bd = card.get_breakdown()
                for k in RATES:
                    totals[k] += bd[k]
            except ValueError as err:
                errors.append(f"Día {card.day.day}: {err}")

        if errors:
            messagebox.showerror("Errores de entrada", "\n".join(errors))
            return

        total = sum(totals[k] * RATES[k] for k in RATES)
        for k in RATES:
            hrs = totals[k]
            pay = hrs * RATES[k]
            self._sum_vars[k].set(f"{hrs:.2f} hrs  ·  ${pay:,.0f}")
        self._total_var.set(f"${total:,.0f}")


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    App().mainloop()
