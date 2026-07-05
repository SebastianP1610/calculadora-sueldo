#!/usr/bin/env python3
"""
Calculadora de Extras Quincenal - Colombia
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

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import calendar as cal_module

# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTANTES (valores por defecto)
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

# Colores — tema oscuro
C_BG = "#2c2f33"
C_DARK = "#23272a"
C_NAV = "#36393f"
C_BTN = "#4f545c"
C_GREEN = "#43b581"
C_RED = "#f04747"
C_BLUE = "#7289da"
C_GOLD = "#faa61a"
C_WHITE = "#ffffff"
C_MUTED = "#99aab5"
C_TEXT = "#dcddde"

C_SUN_HDR = "#e67e22"
C_NORM_HDR = "#5a6268"
C_SUN_BG = "#fff8ee"
C_NORM_BG = "#f0f2f5"
C_REST_BG = "#dee2e6"

CHIP_COLORS = {
    "diurna_normal": "#4a90d9",
    "nocturna_normal": "#7b68ee",
    "diurna_dominical": "#e67e22",
    "nocturna_dominical": "#e74c3c",
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
#  WIDGET: TARJETA DE DÍA
# ═══════════════════════════════════════════════════════════════════════════════


class DayCard(tk.Frame):
    def __init__(self, master: tk.Widget, day: date, **kw):
        _is_sunday = day.weekday() == 6
        _is_holiday = day in HOLIDAYS_2026
        self._is_dominical = _is_sunday or _is_holiday
        self._holiday_not_sunday = _is_holiday and not _is_sunday
        bg = C_SUN_BG if self._is_dominical else C_NORM_BG
        super().__init__(master, bg=bg, relief="solid", bd=1, **kw)
        self.day = day
        self._build()

    def _build(self) -> None:
        bg = self.cget("bg")
        hdr_bg = C_SUN_HDR if self._is_dominical else C_NORM_HDR
        day_lbl = DAYS_ES[self.day.weekday()]
        if self._holiday_not_sunday:
            suffix = " 🇨🇴"
        elif self._is_dominical:
            suffix = " 🟠"
        else:
            suffix = ""

        hdr = tk.Frame(self, bg=hdr_bg, pady=3)
        hdr.pack(fill="x")
        tk.Label(
            hdr,
            text=str(self.day.day),
            font=("Helvetica", 15, "bold"),
            bg=hdr_bg,
            fg=C_WHITE,
        ).pack(side="left", padx=5)
        tk.Label(
            hdr, text=day_lbl + suffix, font=("Helvetica", 9), bg=hdr_bg, fg=C_WHITE
        ).pack(side="right", padx=5)

        body = tk.Frame(self, bg=bg, pady=2)
        body.pack(fill="x", padx=4)
        self._working = tk.BooleanVar(value=True)
        tk.Radiobutton(
            body,
            text="Trabajo",
            variable=self._working,
            value=True,
            bg=bg,
            font=("Helvetica", 8),
            command=self._on_toggle,
        ).pack(side="left")
        tk.Radiobutton(
            body,
            text="Descanso",
            variable=self._working,
            value=False,
            bg=bg,
            font=("Helvetica", 8),
            command=self._on_toggle,
        ).pack(side="right")

        tf = tk.Frame(self, bg=bg)
        tf.pack(fill="x", padx=6, pady=(2, 6))

        tk.Label(
            tf, text="Entrada:", bg=bg, font=("Helvetica", 8), width=7, anchor="w"
        ).grid(row=0, column=0, sticky="w")
        self._start_var = tk.StringVar(value="08:00")
        self._start_e = ttk.OptionMenu(
            tf, self._start_var, self._start_var.get(), *HOUR_OPTIONS
        )
        self._start_e.grid(row=0, column=1)

        tk.Label(
            tf, text="Salida:", bg=bg, font=("Helvetica", 8), width=7, anchor="w"
        ).grid(row=1, column=0, sticky="w")
        self._end_var = tk.StringVar(value="17:00")
        self._end_e = ttk.OptionMenu(
            tf, self._end_var, self._end_var.get(), *HOUR_OPTIONS
        )
        self._end_e.grid(row=1, column=1)

    def _on_toggle(self) -> None:
        working = self._working.get()
        state = "normal" if working else "disabled"
        self._start_e.config(state=state)
        self._end_e.config(state=state)
        new_bg = (
            (C_SUN_BG if self._is_dominical else C_NORM_BG) if working else C_REST_BG
        )
        self.config(bg=new_bg)

    @property
    def is_working(self) -> bool:
        return self._working.get()

    def set_working(self, value: bool) -> None:
        self._working.set(value)
        self._on_toggle()

    def set_times(self, start: str, end: str) -> None:
        self._start_var.set(start)
        self._end_var.set(end)

    def get_breakdown(self, rates: dict[str, int]) -> dict[str, float]:
        if not self._working.get():
            return {k: 0.0 for k in rates}
        start = HOUR_DICT.get(self._start_var.get())
        end = HOUR_DICT.get(self._end_var.get())
        if start is None or end is None:
            raise ValueError(
                f"Formato de hora inválido: {self._start_var.get()} / {self._end_var.get()}"
            )
        return shift_breakdown(start, end, self._is_dominical, rates)


# ═══════════════════════════════════════════════════════════════════════════════
#  APLICACIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("💼 Calculadora de Sueldo Quincenal — Colombia")
        self.geometry("960x860")
        self.minsize(720, 620)
        self.configure(bg=C_BG)

        today = date.today()
        self._year = today.year
        self._month = today.month
        self._first = today.day <= 15
        self._cards: list[DayCard] = []

        self._rates = dict(DEFAULT_RATES)
        self._sueldo_base = DEFAULT_SUELDO_BASE

        self._build_ui()
        self._refresh_period()

    # ── Rates conviene ─────────────────────────────────────────────────────────

    @property
    def rates(self) -> dict[str, int]:
        return self._rates

    @property
    def sueldo_base(self) -> int:
        return self._sueldo_base

    # ── Construcción de la interfaz ───────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_title()
        self._build_rate_chips()
        self._build_config_panel()
        self._build_nav()
        self._build_bulk_actions()
        self._build_day_grid()
        self._build_summary()
        self._build_calc_button()

    def _build_title(self) -> None:
        tb = tk.Frame(self, bg=C_DARK, pady=10)
        tb.pack(fill="x")
        tk.Label(
            tb,
            text="💼  Calculadora de Sueldo Quincenal",
            font=("Helvetica", 20, "bold"),
            bg=C_DARK,
            fg=C_WHITE,
        ).pack()
        tk.Label(
            tb,
            text="🇨🇴  Extras: nocturnas y dominicales/festivos  ·  Base y tarifas editables  ·  Nocturnas desde las 19:00 h",
            font=("Helvetica", 10),
            bg=C_DARK,
            fg=C_MUTED,
        ).pack(pady=(2, 0))

    def _build_rate_chips(self) -> None:
        rc = tk.Frame(self, bg=C_BG, pady=6)
        rc.pack(fill="x", padx=10)

        base_chip = tk.Frame(rc, bg=C_GOLD, padx=10, pady=5)
        base_chip.pack(side="left", padx=4)
        tk.Label(
            base_chip,
            text="💼  Sueldo Base",
            bg=C_GOLD,
            fg=C_WHITE,
            font=("Helvetica", 8, "bold"),
        ).pack()
        self._base_chip_value = tk.Label(
            base_chip,
            text=f"${self._sueldo_base:,} quincenal",
            bg=C_GOLD,
            fg=C_WHITE,
            font=("Helvetica", 9),
        )
        self._base_chip_value.pack()

        chips = [
            ("nocturna_normal", "🌙  Nocturna Normal"),
            ("diurna_dominical", "☀  Diurna Dominical"),
            ("nocturna_dominical", "🌙  Nocturna Dominical"),
        ]
        self._chip_labels: dict[str, tk.Label] = {}
        for key, label in chips:
            color = CHIP_COLORS[key]
            chip = tk.Frame(rc, bg=color, padx=10, pady=5)
            chip.pack(side="left", padx=4)
            tk.Label(
                chip, text=label, bg=color, fg=C_WHITE, font=("Helvetica", 8, "bold")
            ).pack()
            lbl = tk.Label(
                chip,
                text=f"${self._rates[key]:,} / hora",
                bg=color,
                fg=C_WHITE,
                font=("Helvetica", 9),
            )
            lbl.pack()
            self._chip_labels[key] = lbl

    def _build_config_panel(self) -> None:
        cfg = tk.Frame(self, bg=C_NAV, pady=6)
        cfg.pack(fill="x", padx=10)

        tk.Label(
            cfg,
            text="⚙️  Configuración de Tarifas",
            bg=C_NAV,
            fg=C_GOLD,
            font=("Helvetica", 10, "bold"),
        ).pack(anchor="w", padx=6)

        row = tk.Frame(cfg, bg=C_NAV, pady=4)
        row.pack(fill="x", padx=6)

        def _with_label(parent, text, bg, default_val, key):
            f = tk.Frame(parent, bg=bg)
            f.pack(side="left", padx=4)
            tk.Label(f, text=text, bg=bg, fg=C_MUTED, font=("Helvetica", 7)).pack(
                anchor="w"
            )
            var = tk.IntVar(value=default_val)
            var.trace_add("write", lambda *_: self._on_config_change())
            e = tk.Entry(f, textvariable=var, width=10, font=("Helvetica", 9))
            e.pack()
            return var, f

        self._cfg_sueldo, _ = _with_label(
            row, "Sueldo Base", C_NAV, self._sueldo_base, "sueldo"
        )
        self._cfg_noct_norm, _ = _with_label(
            row, "Noct. Normal $/h", C_NAV, self._rates["nocturna_normal"], "nn"
        )
        self._cfg_diur_dom, _ = _with_label(
            row, "Diur. Dom. $/h", C_NAV, self._rates["diurna_dominical"], "dd"
        )
        self._cfg_noct_dom, _ = _with_label(
            row, "Noct. Dom. $/h", C_NAV, self._rates["nocturna_dominical"], "nd"
        )
        self._cfg_diur_norm, _ = _with_label(
            row, "Diur. Normal $/h", C_NAV, self._rates["diurna_normal"], "dn"
        )

        btn_frame = tk.Frame(cfg, bg=C_NAV, pady=3)
        btn_frame.pack()
        tk.Button(
            btn_frame,
            text="↺ Restaurar Valores por Defecto",
            command=self._reset_config,
            bg=C_BTN,
            fg=C_WHITE,
            relief="flat",
            font=("Helvetica", 8, "bold"),
            padx=10,
        ).pack()

        tk.Label(
            cfg,
            text="Las horas diurnas normales están cubiertas por el sueldo base y no generan recargo adicional.",
            bg=C_NAV,
            fg=C_MUTED,
            font=("Helvetica", 7),
        ).pack()

    def _on_config_change(self) -> None:
        try:
            self._sueldo_base = self._cfg_sueldo.get()
            self._rates = {
                "nocturna_normal": self._cfg_noct_norm.get(),
                "diurna_dominical": self._cfg_diur_dom.get(),
                "nocturna_dominical": self._cfg_noct_dom.get(),
                "diurna_normal": self._cfg_diur_norm.get(),
            }
        except tk.TclError:
            return
        self._refresh_chips()
        self._reset_summary()

    def _reset_config(self) -> None:
        self._sueldo_base = DEFAULT_SUELDO_BASE
        self._rates = dict(DEFAULT_RATES)
        self._cfg_sueldo.set(self._sueldo_base)
        self._cfg_noct_norm.set(self._rates["nocturna_normal"])
        self._cfg_diur_dom.set(self._rates["diurna_dominical"])
        self._cfg_noct_dom.set(self._rates["nocturna_dominical"])
        self._cfg_diur_norm.set(self._rates["diurna_normal"])
        self._refresh_chips()
        self._reset_summary()

    def _refresh_chips(self) -> None:
        self._base_chip_value.config(text=f"${self._sueldo_base:,} quincenal")
        for key, lbl in self._chip_labels.items():
            lbl.config(text=f"${self._rates[key]:,} / hora")

    def _build_nav(self) -> None:
        nav = tk.Frame(self, bg=C_NAV, pady=7)
        nav.pack(fill="x")
        tk.Button(
            nav,
            text="◀  Anterior",
            command=self._prev,
            bg=C_BTN,
            fg=C_WHITE,
            relief="flat",
            font=("Helvetica", 10, "bold"),
            padx=14,
        ).pack(side="left", padx=12)
        self._period_lbl = tk.Label(
            nav, text="", bg=C_NAV, fg=C_WHITE, font=("Helvetica", 13, "bold")
        )
        self._period_lbl.pack(side="left", expand=True)
        tk.Button(
            nav,
            text="Siguiente  ▶",
            command=self._next,
            bg=C_BTN,
            fg=C_WHITE,
            relief="flat",
            font=("Helvetica", 10, "bold"),
            padx=14,
        ).pack(side="right", padx=12)

    def _build_bulk_actions(self) -> None:
        ba = tk.Frame(self, bg=C_BG, pady=5)
        ba.pack(fill="x", padx=10)

        tk.Label(
            ba, text="Aplicar a todos:", bg=C_BG, fg=C_MUTED, font=("Helvetica", 9)
        ).pack(side="left", padx=(0, 6))
        tk.Button(
            ba,
            text="✔ Trabajo",
            command=lambda: self._set_all(True),
            bg=C_GREEN,
            fg=C_WHITE,
            relief="flat",
            font=("Helvetica", 8, "bold"),
            padx=8,
        ).pack(side="left", padx=2)
        tk.Button(
            ba,
            text="✖ Descanso",
            command=lambda: self._set_all(False),
            bg=C_RED,
            fg=C_WHITE,
            relief="flat",
            font=("Helvetica", 8, "bold"),
            padx=8,
        ).pack(side="left", padx=2)

        tk.Label(
            ba, text="  Horario masivo:", bg=C_BG, fg=C_MUTED, font=("Helvetica", 9)
        ).pack(side="left", padx=(12, 4))
        self._bulk_start = tk.StringVar(value="08:00")
        self._bulk_end = tk.StringVar(value="17:00")
        ttk.OptionMenu(
            ba, self._bulk_start, self._bulk_start.get(), *HOUR_OPTIONS
        ).pack(side="left", padx=2)
        tk.Label(ba, text="→", bg=C_BG, fg=C_WHITE).pack(side="left")
        ttk.OptionMenu(ba, self._bulk_end, self._bulk_end.get(), *HOUR_OPTIONS).pack(
            side="left", padx=2
        )
        tk.Button(
            ba,
            text="Aplicar horario",
            command=self._apply_bulk_times,
            bg=C_BLUE,
            fg=C_WHITE,
            relief="flat",
            font=("Helvetica", 8, "bold"),
            padx=8,
        ).pack(side="left", padx=4)

    def _build_day_grid(self) -> None:
        outer = tk.Frame(self, bg=C_BG)
        outer.pack(fill="both", expand=True, padx=6, pady=4)

        self._canvas = tk.Canvas(outer, bg=C_BG, highlightthickness=0)
        vscroll = ttk.Scrollbar(outer, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._grid_frame = tk.Frame(self._canvas, bg=C_BG)
        self._cwin = self._canvas.create_window(
            (0, 0), window=self._grid_frame, anchor="nw"
        )

        self._grid_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )
        self._canvas.bind(
            "<Configure>",
            lambda e: self._canvas.itemconfig(self._cwin, width=e.width),
        )
        self._canvas.bind_all(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"),
        )
        self._canvas.bind_all(
            "<Button-4>", lambda e: self._canvas.yview_scroll(-1, "units")
        )
        self._canvas.bind_all(
            "<Button-5>", lambda e: self._canvas.yview_scroll(1, "units")
        )

    def _build_summary(self) -> None:
        sp = tk.Frame(self, bg=C_DARK, pady=8)
        sp.pack(fill="x")

        base_row = tk.Frame(sp, bg=C_DARK)
        base_row.pack(fill="x", padx=16, pady=1)
        tk.Label(
            base_row,
            text="💼  Sueldo Base",
            width=22,
            anchor="w",
            bg=C_DARK,
            fg=C_GOLD,
            font=("Helvetica", 10, "bold"),
        ).pack(side="left")
        self._base_display = tk.Label(
            base_row, text="", bg=C_DARK, fg=C_TEXT, font=("Helvetica", 10)
        )
        self._base_display.pack(side="left", padx=6)

        self._sum_vars: dict[str, tk.StringVar] = {}
        rows_cfg = [
            ("nocturna_normal", "🌙  Nocturna Normal", CHIP_COLORS["nocturna_normal"]),
            (
                "diurna_dominical",
                "☀  Diurna Dominical",
                CHIP_COLORS["diurna_dominical"],
            ),
            (
                "nocturna_dominical",
                "🌙  Nocturna Dominical",
                CHIP_COLORS["nocturna_dominical"],
            ),
        ]
        for key, name, color in rows_cfg:
            v = tk.StringVar(value="0.00 hrs  ·  $0")
            self._sum_vars[key] = v
            row = tk.Frame(sp, bg=C_DARK)
            row.pack(fill="x", padx=16, pady=1)
            tk.Label(
                row,
                text=name,
                width=22,
                anchor="w",
                bg=C_DARK,
                fg=color,
                font=("Helvetica", 10, "bold"),
            ).pack(side="left")
            tk.Label(
                row, textvariable=v, bg=C_DARK, fg=C_TEXT, font=("Helvetica", 10)
            ).pack(side="left", padx=6)

        tk.Frame(sp, bg=C_BTN, height=1).pack(fill="x", padx=16, pady=5)

        total_row = tk.Frame(sp, bg=C_DARK)
        total_row.pack(fill="x", padx=16)
        tk.Label(
            total_row,
            text="💰  TOTAL QUINCENA",
            width=22,
            anchor="w",
            bg=C_DARK,
            fg=C_GOLD,
            font=("Helvetica", 14, "bold"),
        ).pack(side="left")
        self._total_var = tk.StringVar(value="")
        tk.Label(
            total_row,
            textvariable=self._total_var,
            bg=C_DARK,
            fg=C_GREEN,
            font=("Helvetica", 16, "bold"),
        ).pack(side="left", padx=8)

    def _build_calc_button(self) -> None:
        bf = tk.Frame(self, bg=C_BG, pady=8)
        bf.pack(fill="x")
        tk.Button(
            bf,
            text="  💰  Calcular Quincena  ",
            command=self._calculate,
            bg=C_GREEN,
            fg=C_WHITE,
            font=("Helvetica", 13, "bold"),
            relief="flat",
            pady=8,
        ).pack()

    # ── Manejo de la quincena ─────────────────────────────────────────────────

    def _refresh_period(self) -> None:
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
        self._base_display.config(text=f"${self._sueldo_base:,}  (quincenal)")
        for v in self._sum_vars.values():
            v.set("0.00 hrs  ·  $0")
        self._total_var.set(f"${self._sueldo_base:,}")

    def _prev(self) -> None:
        if self._first:
            self._first = False
            self._month -= 1
            if self._month == 0:
                self._month = 12
                self._year -= 1
        else:
            self._first = True
        self._refresh_period()

    def _next(self) -> None:
        if self._first:
            self._first = False
        else:
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
        s_dec = HOUR_DICT[s]
        e_dec = HOUR_DICT[e]
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
        rates = self._rates
        sueldo_base = self._sueldo_base
        totals: dict[str, float] = {k: 0.0 for k in rates}
        errors: list[str] = []

        for card in self._cards:
            try:
                bd = card.get_breakdown(rates)
                for k in rates:
                    totals[k] += bd[k]
            except ValueError as err:
                errors.append(f"Día {card.day.day}: {err}")

        if errors:
            messagebox.showerror("Errores de entrada", "\n".join(errors))
            return

        extras_keys = ("nocturna_normal", "diurna_dominical", "nocturna_dominical")
        extras_total = sum(totals[k] * rates[k] for k in extras_keys)
        total = sueldo_base + extras_total

        for k in extras_keys:
            hrs = totals[k]
            pay = hrs * rates[k]
            self._sum_vars[k].set(f"{hrs:.2f} hrs  ·  ${pay:,.0f}")
        self._total_var.set(f"${total:,.0f}")


# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    App().mainloop()
