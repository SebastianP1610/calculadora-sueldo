# 💼 Calculadora de Sueldo Quincenal — Colombia

Aplicación para calcular el sueldo quincenal de trabajadores en Colombia. Disponible en dos versiones:
- **Streamlit** (`calculadora_sueldo_streamlit.py`) — interfaz web, ideal para despliegue.
- **Tkinter** (`calculadora_sueldo.py`) — aplicación de escritorio nativa.

## Tarifas aplicadas (COP por hora) — valores por defecto

| Tipo de hora              | Tarifa     |
|---------------------------|------------|
| ☀ Diurna Normal           | $7.950     |
| 🌙 Nocturna Normal         | $10.700    |
| ☀ Diurna Dominical        | $14.300    |
| 🌙 Nocturna Dominical      | $17.100    |

> Las horas nocturnas aplican a partir de las **19:00 h** (7 PM).
> **Todos los valores monetarios (sueldo base y tarifas) son editables** desde el panel de configuración dentro de la app.

## Características

- 📅 Visualización de la quincena completa (primera: días 1–15 / segunda: días 16–fin de mes).
- 🗓️ Navegación entre quincenas con botones **Anterior / Siguiente**.
- ✅ Por día: elección entre **Trabajo** o **Descanso**.
- ⏰ Por día de trabajo: **menú desplegable** de hora de entrada y salida (opciones cada hora, 00:00 → 23:00).
- 🌙 Soporte para **turnos nocturnos que cruzan la medianoche** (ej: 22:00 → 06:00).
- 🟠 Los **domingos** y **festivos** se destacan visualmente y usan tarifas dominicales automáticamente.
- ⚡ Acciones masivas:
  - Marcar todos los días como **Trabajo** o **Descanso** con un clic.
  - Asignar el mismo horario a todos los días de trabajo de la quincena.
- ⚙️ **Panel de configuración de tarifas**: sueldo base quincenal + tarifas por hora, editables en cualquier momento.
- 💰 Panel de resumen con desglose por tipo de hora y **total de la quincena**.

## Requisitos

- Python **3.9 o superior**

### Streamlit
```bash
pip install -r requirements.txt
```

### Tkinter (escritorio)
`tkinter` está incluido en la instalación estándar de Python. En algunas distribuciones de Linux puede ser necesario instalarlo por separado:
```bash
sudo apt install python3-tk
```

## Cómo ejecutar

### Versión web (Streamlit)
```bash
streamlit run calculadora_sueldo_streamlit.py
```

### Versión escritorio (Tkinter)
```bash
python calculadora_sueldo.py
```

## Uso rápido

1. **Ajustá las tarifas** (opcional) en el panel ⚙️ Configuración de Tarifas.
2. **Navegá** a la quincena deseada con los botones ◀ / ▶.
3. **Marcá** cada día como *Trabajo* o *Descanso*.
4. **Seleccioná** la hora de entrada y salida con los menús desplegables.
5. Usá los botones de **acción masiva** para aplicar un horario estándar a toda la quincena.
6. Hacé clic en **💰 Calcular Quincena** para ver el desglose y el total.
