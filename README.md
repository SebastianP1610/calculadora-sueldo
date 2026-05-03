# 💼 Calculadora de Sueldo Quincenal — Colombia

Aplicación de escritorio en Python con interfaz visual (tkinter) para calcular el sueldo quincenal de trabajadores en Colombia.

## Tarifas aplicadas (COP por hora)

| Tipo de hora              | Tarifa     |
|---------------------------|------------|
| ☀ Diurna Normal           | $7.950     |
| 🌙 Nocturna Normal         | $10.700    |
| ☀ Diurna Dominical        | $14.300    |
| 🌙 Nocturna Dominical      | $17.100    |

> Las horas nocturnas aplican a partir de las **19:00 h** (7 PM).

## Características

- 📅 Visualización de la quincena completa (primera: días 1–15 / segunda: días 16–fin de mes).
- 🗓️ Navegación entre quincenas con botones **Anterior / Siguiente**.
- ✅ Por día: elección entre **Trabajo** o **Descanso**.
- ⏰ Por día de trabajo: campos de **hora de entrada** y **hora de salida** (formato `HH:MM`).
- 🌙 Soporte para **turnos nocturnos que cruzan la medianoche** (ej: 22:00 → 06:00).
- 🟠 Los **domingos** se destacan visualmente y usan tarifas dominicales automáticamente.
- ⚡ Acciones masivas:
  - Marcar todos los días como **Trabajo** o **Descanso** con un clic.
  - Asignar el mismo horario a todos los días de trabajo de la quincena.
- 💰 Panel de resumen con desglose por tipo de hora y **total de la quincena**.

## Requisitos

- Python **3.9 o superior**
- `tkinter` (incluido en la instalación estándar de Python)

## Cómo ejecutar

```bash
python calculadora_sueldo.py
```

> En algunas distribuciones de Linux puede ser necesario instalar tkinter por separado:
> ```bash
> sudo apt install python3-tk
> ```

## Uso rápido

1. **Navega** a la quincena deseada con los botones ◀ / ▶.
2. **Marca** cada día como *Trabajo* o *Descanso*.
3. **Ingresa** la hora de entrada y salida para cada día de trabajo (`HH:MM`).
4. Usa los botones de **acción masiva** para aplicar un horario estándar a toda la quincena.
5. Haz clic en **💰 Calcular Quincena** para ver el desglose y el total.
