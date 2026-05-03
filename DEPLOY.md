# 🚀 Instrucciones de Despliegue

## Opción 1: Ejecutar localmente (prueba)

```bash
pip install streamlit
streamlit run calculadora_sueldo_streamlit.py
```

Se abrirá en `http://localhost:8501` en tu navegador.

---

## Opción 2: Desplegar en Streamlit Cloud (RECOMENDADO - Gratis)

### Paso 1: Preparar el repositorio
1. Crea una carpeta `calculadora-sueldo` en GitHub (o usa la que ya tienes)
2. Sube estos archivos:
   - `calculadora_sueldo_streamlit.py`
   - `requirements.txt`
   - `.gitignore` (opcional, pero recomendado)

### Paso 2: Desplegar en Streamlit Cloud
1. Ve a https://share.streamlit.io
2. Inicia sesión con tu cuenta de GitHub (o crea una)
3. Haz clic en "New app"
4. Selecciona:
   - Repository: `tu-usuario/calculadora-sueldo`
   - Branch: `main`
   - Main file path: `calculadora_sueldo_streamlit.py`
5. Haz clic en "Deploy"

**¡Listo!** En 1-2 minutos tendrás una URL pública como:
```
https://calculadora-sueldo.streamlit.app
```

Comparte esa URL con tu pareja y ella puede usar la calculadora desde cualquier dispositivo. ✅

---

## Notas

- **Cero costo**: Streamlit Cloud es gratis para apps públicas
- **Actualización automática**: Cada vez que hagas push a GitHub, la app se actualiza automáticamente
- **Responsivo**: Funciona perfecto en móvil, tablet, desktop
- **Toda la lógica preservada**: Nada de los cálculos cambió, solo la interfaz

---

## Cambios realizados en la conversión

✅ Lógica de cálculo: **100% idéntica**  
✅ Constantes y festivos: **Preservados**  
✅ Funciones: `quincena_dates()`, `parse_hhmm()`, `shift_breakdown()` — **Sin cambios**  
✅ UI: Adaptada a Streamlit manteniendo funcionalidad y colores  
✅ Estado de sesión: Gestión de formularios con `st.session_state`

---

## Troubleshooting

Si tienes problemas al desplegar en Streamlit Cloud:
1. Asegúrate de que `calculadora_sueldo_streamlit.py` esté en la raíz del repo
2. Verifica que `requirements.txt` incluya `streamlit==1.28.1`
3. Los archivos deben estar en un repositorio **público** de GitHub
