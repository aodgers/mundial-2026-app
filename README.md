# 🏆 Copa Mundial FIFA 2026 - Streamlit Web App

Esta es una aplicación web interactiva y visualmente impactante diseñada para realizar el seguimiento del Mundial 2026. Cuenta con un diseño oscuro (dark mode), tarjetas interactivas de partidos, canales de transmisión oficiales para Chile (Chilevisión y Mega), y un sistema dinámico que calcula las estadísticas y tablas de posiciones de los grupos en tiempo real a medida que ingresas resultados.

## 🚀 Características principales
- **Calendario Interactivo**: Visualiza los partidos con horarios en hora chilena (CLT), sedes y canales de transmisión.
- **Ingreso de Resultados en Vivo**: Formularios integrados en cada tarjeta de partido para registrar o actualizar los marcadores.
- **Tablas de Posiciones Dinámicas**: Cálculo automático de Puntos (PTS), Partidos Jugados (PJ), Diferencia de Goles (DG), etc., para los 12 grupos.
- **Estilo Visual Premium**: Interfaz moderna de estilo "App de Deportes" oscura, con tarjetas elegantes y efectos de transición.
- **Gráficos Estadísticos**: Visualizaciones de goles anotados por país, promedios de goles por sede y cobertura de transmisión.

---

## 🛠️ Instrucciones para Ejecución Local

### 1. Requisitos Previos
Asegúrate de tener instalado Python 3.8 o superior.

### 2. Instalación de Dependencias
Abre una terminal en el directorio del proyecto y ejecuta:
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación
Inicia el servidor local de desarrollo de Streamlit:
```bash
streamlit run app.py
```
La aplicación se abrirá automáticamente en tu navegador web en `http://localhost:8501`.

---

## ☁️ Pasos para desplegar GRATIS en Streamlit Cloud

Sigue estos sencillos pasos para publicar tu aplicación y compartirla con tus amigos:

### Paso 1: Subir tu código a GitHub
1. Crea un nuevo repositorio en tu cuenta de [GitHub](https://github.com) (ej: `mundial-2026-app`).
2. Sube todos los archivos del proyecto a la rama principal (`main` o `master`):
   - `.streamlit/config.toml` (Configuración de colores y tema oscuro)
   - `data/matches.json` (Base de datos de partidos y selecciones)
   - `app.py` (Lógica y diseño de la aplicación)
   - `requirements.txt` (Lista de dependencias)
   - `README.md` (Este archivo)

### Paso 2: Crear cuenta en Streamlit Community Cloud
1. Ve a [Streamlit Share](https://share.streamlit.io/).
2. Inicia sesión haciendo clic en **"Continue with GitHub"** y autoriza el acceso a tu cuenta.

### Paso 3: Desplegar la Aplicación
1. En tu panel de Streamlit Cloud, haz clic en el botón **"New app"** (o "Deploy an app").
2. Completa los campos solicitados:
   - **Repository**: Selecciona tu repositorio de GitHub recién creado (ej. `tu-usuario/mundial-2026-app`).
   - **Branch**: Generalmente `main`.
   - **Main file path**: Escribe `app.py`.
3. Haz clic en **"Deploy!"**.

¡Listo! Streamlit Cloud instalará las librerías indicadas en `requirements.txt` y desplegará tu app en pocos minutos. Recibirás una URL única (ej: `https://tu-app-mundial.streamlit.app/`) que podrás compartir.
