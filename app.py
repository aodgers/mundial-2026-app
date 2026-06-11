import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from PIL import Image

# Configuración de página
st.set_page_config(
    page_title="Mundial 2026 - Dashboard & Calendario",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyectar CSS personalizado para estética premium, oscura y deportiva
st.markdown("""
<style>
    /* Estilos del contenedor principal */
    .reportview-container {
        background: #0a0e17;
    }
    
    /* Títulos y fuentes */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Estilo de Tarjetas de Partidos */
    .match-card {
        background: rgba(19, 26, 43, 0.8);
        border: 1px solid rgba(230, 57, 70, 0.15);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(4px);
        transition: transform 0.2s, border-color 0.2s;
    }
    .match-card:hover {
        transform: translateY(-3px);
        border-color: rgba(230, 57, 70, 0.6);
    }
    
    /* Cabecera del partido */
    .match-header {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        color: #8892b0;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 6px;
    }
    
    /* Equipos y Marcadores */
    .match-body {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 15px 0;
    }
    .team-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 38%;
        text-align: center;
    }
    .team-flag {
        font-size: 2.8rem;
        margin-bottom: 6px;
        filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.5));
    }
    .team-name {
        font-weight: 600;
        font-size: 1.1rem;
        color: #e0e6f0;
    }
    .score-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 24%;
    }
    .score-display {
        font-size: 2.2rem;
        font-weight: 800;
        color: #e63946;
        letter-spacing: 4px;
        background: rgba(0, 0, 0, 0.2);
        padding: 5px 15px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .score-vs {
        font-size: 0.9rem;
        color: #8892b0;
        font-weight: bold;
    }
    .score-pending {
        font-size: 1.2rem;
        font-weight: 500;
        color: #8892b0;
        background: rgba(255, 255, 255, 0.05);
        padding: 4px 12px;
        border-radius: 8px;
        font-style: italic;
    }
    
    /* Pie de la tarjeta */
    .match-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 12px;
        font-size: 0.85rem;
        color: #8892b0;
    }
    .channel-badge-free {
        background: linear-gradient(135deg, #e63946 0%, #b31928 100%);
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 5px;
        display: inline-block;
    }
    .channel-badge-pay {
        background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .channel-badge-exclusive {
        background: rgba(255, 255, 255, 0.08);
        color: #8892b0;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 5px;
        display: inline-block;
    }
    
    /* Títulos de sección */
    .section-title {
        color: #ffffff;
        font-weight: 800;
        border-left: 5px solid #e63946;
        padding-left: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Rutas de los archivos de datos
DATA_FILE = "data/matches.json"
PRED_FILE = "data/predictions.json"

# Cargar base de datos inicial o de sesión
def load_data():
    if not os.path.exists(DATA_FILE):
        st.error(f"Archivo de datos no encontrado en {DATA_FILE}. Por favor verifica el directorio.")
        return None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Cargar predicciones
def load_predictions():
    if not os.path.exists(PRED_FILE):
        return {"participants": {}}
    try:
        with open(PRED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"participants": {}}

def save_predictions(data):
    os.makedirs(os.path.dirname(PRED_FILE), exist_ok=True)
    with open(PRED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Inicializar sesión
if "db" not in st.session_state:
    st.session_state.db = load_data()
if "preds" not in st.session_state:
    st.session_state.preds = load_predictions()

db = st.session_state.db
preds = st.session_state.preds

if db is None:
    st.stop()

# Helper para calcular estadísticas de los grupos
def calculate_group_standings(group_name):
    teams = db["groups"][group_name]
    standings = {team: {"PJ": 0, "PG": 0, "PE": 0, "PP": 0, "GF": 0, "GC": 0, "DG": 0, "PTS": 0} for team in teams}
    
    # Procesar cada partido del grupo
    for match in db["matches"]:
        if match["group"] == group_name:
            team_a = match["team_a"]
            team_b = match["team_b"]
            g_a = match["goals_a"]
            g_b = match["goals_b"]
            
            # Solo procesar si el resultado ha sido ingresado
            if g_a is not None and g_b is not None:
                standings[team_a]["PJ"] += 1
                standings[team_b]["PJ"] += 1
                standings[team_a]["GF"] += g_a
                standings[team_a]["GC"] += g_b
                standings[team_b]["GF"] += g_b
                standings[team_b]["GC"] += g_a
                
                if g_a > g_b:
                    standings[team_a]["PG"] += 1
                    standings[team_a]["PTS"] += 3
                    standings[team_b]["PP"] += 1
                elif g_b > g_a:
                    standings[team_b]["PG"] += 1
                    standings[team_b]["PTS"] += 3
                    standings[team_a]["PP"] += 1
                else:
                    standings[team_a]["PE"] += 1
                    standings[team_a]["PTS"] += 1
                    standings[team_b]["PE"] += 1
                    standings[team_b]["PTS"] += 1
                    
                # Recalcular diferencias de gol
                standings[team_a]["DG"] = standings[team_a]["GF"] - standings[team_a]["GC"]
                standings[team_b]["DG"] = standings[team_b]["GF"] - standings[team_b]["GC"]
                
    # Convertir a DataFrame y ordenar
    df = pd.DataFrame.from_dict(standings, orient='index')
    df = df.reset_index().rename(columns={"index": "Equipo"})
    # Ordenar por Puntos, Diferencia de Gol, Goles a Favor, y alfabético
    df = df.sort_values(by=["PTS", "DG", "GF", "Equipo"], ascending=[False, False, False, True])
    df = df.reset_index(drop=True)
    df.index += 1  # 1-indexed para la posición de la tabla
    return df

# Calcular la tabla de puntuación de amigos (La Polla)
def calculate_predictions_leaderboard():
    leaderboard = []
    
    for participant, data in preds["participants"].items():
        points = 0
        exact_hits = 0
        outcome_hits = 0
        matches_predicted = 0
        
        participant_preds = data.get("predictions", {})
        
        for match in db["matches"]:
            match_id_str = str(match["id"])
            if match["goals_a"] is not None and match["goals_b"] is not None:
                # El partido ya tiene resultado real
                if match_id_str in participant_preds:
                    matches_predicted += 1
                    pred_a = participant_preds[match_id_str].get("goals_a")
                    pred_b = participant_preds[match_id_str].get("goals_b")
                    
                    if pred_a is not None and pred_b is not None:
                        real_a = match["goals_a"]
                        real_b = match["goals_b"]
                        
                        # Regla 1: Marcador exacto (3 puntos)
                        if pred_a == real_a and pred_b == real_b:
                            points += 3
                            exact_hits += 1
                        # Regla 2: Acertar tendencia (Ganador/Empate) pero no marcador exacto (1 punto)
                        elif (pred_a > pred_b and real_a > real_b) or (pred_a < pred_b and real_a < real_b) or (pred_a == pred_b and real_a == real_b):
                            points += 1
                            outcome_hits += 1
                            
        leaderboard.append({
            "Participante": participant,
            "Pronósticos Hechos": matches_predicted,
            "Aciertos Exactos (3 pts)": exact_hits,
            "Aciertos Tendencia (1 pt)": outcome_hits,
            "Puntos Totales": points
        })
        
    df = pd.DataFrame(leaderboard)
    if not df.empty:
        df = df.sort_values(by="Puntos Totales", ascending=False).reset_index(drop=True)
        df.index += 1
    return df

# Calcular estadísticas globales para el Sidebar y Dashboard
matches_played = sum(1 for m in db["matches"] if m["goals_a"] is not None)
total_matches = len(db["matches"])
pct_completed = (matches_played / total_matches) * 100 if total_matches > 0 else 0
total_goals = sum((m["goals_a"] or 0) + (m["goals_b"] or 0) for m in db["matches"] if m["goals_a"] is not None)

# SIDEBAR / PANEL DE CONTROL
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/43/2026_FIFA_World_Cup_logo.svg", width=120)
    st.title("Control del Torneo")
    
    st.markdown("---")
    st.subheader("📊 Progreso del Mundial")
    st.metric("Partidos Jugados", f"{matches_played} / {total_matches}", f"{pct_completed:.1f}%")
    st.metric("Goles Totales", total_goals)
    
    st.markdown("---")
    st.subheader("🏆 Transmisiones en Chile")
    st.markdown("""
    - **📺 Señal Abierta:** Chilevisión transmite 34 partidos seleccionados.
    - **🔒 Señal de Pago:** **DSports / DGO / Paramount+** transmite **el 100% de los 104 partidos** en español.
    """)
    
    # Botón para restablecer base de datos
    st.markdown("---")
    if st.button("🔄 Reiniciar Resultados", help="Borra todos los marcadores ingresados"):
        for m in db["matches"]:
            m["goals_a"] = None
            m["goals_b"] = None
        save_data(db)
        st.session_state.db = db
        st.rerun()

# CUERPO PRINCIPAL
st.markdown("<h1 style='text-align: center; color: white;'>🏆 FIFA WORLD CUP 2026 🏆</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8892b0; font-size: 1.2rem;'>Calendario Interactivo, Resultados en Vivo y Tabla de Posiciones para Chile</p>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Partidos y Resultados", 
    "📊 Tablas de Posiciones", 
    "🔮 Polla / Pronósticos", 
    "📈 Estadísticas & Métricas"
])

# TAB 1: CALENDARIO Y REGISTRO DE GOLES
with tab1:
    st.markdown("<h2 class='section-title'>Calendario e Ingreso de Resultados Reales</h2>", unsafe_allow_html=True)
    
    # Filtros
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        filtro_grupo = st.selectbox("Filtrar por Grupo", ["Todos"] + sorted(list(db["groups"].keys())))
    with col_f2:
        filtro_canal = st.selectbox("Filtrar por Transmisión", ["Todos", "Señal Abierta (Chilevisión)", "Exclusivos de Pago (DSports/DGO/Paramount+)"])
    with col_f3:
        filtro_estado = st.selectbox("Filtrar por Estado", ["Todos", "Por jugar", "Finalizados"])
    with col_f4:
        filtro_busqueda = st.text_input("🔍 Buscar Selección", placeholder="Ej: Chile, Argentina")
        
    # Aplicar filtros
    matches_filtered = db["matches"]
    if filtro_grupo != "Todos":
        matches_filtered = [m for m in matches_filtered if m["group"] == filtro_grupo]
        
    if filtro_canal == "Señal Abierta (Chilevisión)":
        matches_filtered = [m for m in matches_filtered if m["channel_free"] is not None]
    elif filtro_canal == "Exclusivos de Pago (DSports/DGO/Paramount+)":
        matches_filtered = [m for m in matches_filtered if m["channel_free"] is None]
        
    if filtro_estado == "Por jugar":
        matches_filtered = [m for m in matches_filtered if m["goals_a"] is None]
    elif filtro_estado == "Finalizados":
        matches_filtered = [m for m in matches_filtered if m["goals_a"] is not None]
        
    if filtro_busqueda:
        busqueda_clean = filtro_busqueda.strip().lower()
        matches_filtered = [
            m for m in matches_filtered 
            if busqueda_clean in m["team_a"].lower() or busqueda_clean in m["team_b"].lower()
        ]

    if not matches_filtered:
        st.info("No se encontraron partidos para los filtros aplicados.")
    else:
        # Mostrar partidos en cuadrícula de 2 columnas
        for i in range(0, len(matches_filtered), 2):
            cols = st.columns(2)
            for j in range(2):
                idx = i + j
                if idx < len(matches_filtered):
                    match = matches_filtered[idx]
                    with cols[j]:
                        iso_a = db["team_iso"].get(match["team_a"], "un")
                        iso_b = db["team_iso"].get(match["team_b"], "un")
                        
                        flag_a_img = f'<img src="https://flagcdn.com/w80/{iso_a}.png" width="56" style="box-shadow: 0px 4px 10px rgba(0,0,0,0.45); border-radius: 4px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 6px;" />'
                        flag_b_img = f'<img src="https://flagcdn.com/w80/{iso_b}.png" width="56" style="box-shadow: 0px 4px 10px rgba(0,0,0,0.45); border-radius: 4px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 6px;" />'
                        
                        # Generar HTML para el diseño de tarjeta deportiva
                        score_html = ""
                        if match["goals_a"] is not None and match["goals_b"] is not None:
                            score_html = f"<div class='score-display'>{match['goals_a']} - {match['goals_b']}</div>"
                        else:
                            score_html = "<div class='score-pending'>VS</div>"
                            
                        # Badges de transmisión
                        badge_free = ""
                        if match["channel_free"]:
                            badge_free = f"<span class='channel-badge-free'>📺 {match['channel_free']}</span>"
                        else:
                            badge_free = "<span class='channel-badge-exclusive'>🔒 Solo por Pago</span>"
                            
                        badge_pay = f"<span class='channel-badge-pay'>🔑 {match['channel_pay']}</span>"
                        
                        card_html = f"""
                        <div class="match-card">
                            <div class="match-header">
                                <span>📅 {match['date']} | ⏰ {match['time_clt']} (CLT)</span>
                                <span>Grupo {match['group']} • {match['phase']}</span>
                            </div>
                            <div class="match-body">
                                <div class="team-section">
                                    {flag_a_img}
                                    <span class="team-name">{match['team_a']}</span>
                                </div>
                                <div class="score-section">
                                    {score_html}
                                </div>
                                <div class="team-section">
                                    {flag_b_img}
                                    <span class="team-name">{match['team_b']}</span>
                                </div>
                            </div>
                            <div class="match-footer">
                                <span>🏟️ {match['stadium']}, {match['city']}</span>
                                <div>
                                    {badge_free}
                                    {badge_pay}
                                </div>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # Expander para registrar resultados del partido
                        with st.expander(f"✏️ Registrar / Editar Marcador Oficial (Partido {match['id']})"):
                            col_inp1, col_inp2 = st.columns(2)
                            val_a = match["goals_a"] if match["goals_a"] is not None else 0
                            val_b = match["goals_b"] if match["goals_b"] is not None else 0
                            
                            new_a = col_inp1.number_input(f"Goles {match['team_a']}", min_value=0, max_value=25, value=int(val_a), key=f"inp_a_{match['id']}")
                            new_b = col_inp2.number_input(f"Goles {match['team_b']}", min_value=0, max_value=25, value=int(val_b), key=f"inp_b_{match['id']}")
                            
                            col_btn1, col_btn2 = st.columns(2)
                            if col_btn1.button("Guardar Marcador", key=f"btn_save_{match['id']}"):
                                # Actualizar datos en sesión y archivo
                                for m in db["matches"]:
                                    if m["id"] == match["id"]:
                                        m["goals_a"] = new_a
                                        m["goals_b"] = new_b
                                save_data(db)
                                st.session_state.db = db
                                st.success("¡Resultado oficial guardado!")
                                st.rerun()
                                
                            if match["goals_a"] is not None:
                                if col_btn2.button("Limpiar Marcador", key=f"btn_clear_{match['id']}", type="secondary"):
                                    for m in db["matches"]:
                                        if m["id"] == match["id"]:
                                            m["goals_a"] = None
                                            m["goals_b"] = None
                                    save_data(db)
                                    st.session_state.db = db
                                    st.warning("Marcador oficial limpiado.")
                                    st.rerun()

# TAB 2: TABLAS DE POSICIONES
with tab2:
    st.markdown("<h2 class='section-title'>Tabla de Posiciones por Grupos</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8892b0;'>Las posiciones se recalculan en tiempo real a medida que ingresas resultados en la pestaña de partidos.</p>", unsafe_allow_html=True)
    
    # Mostrar grupos en un grid de 2 columnas
    groups_list = sorted(list(db["groups"].keys()))
    for i in range(0, len(groups_list), 2):
        cols = st.columns(2)
        for j in range(2):
            idx = i + j
            if idx < len(groups_list):
                grp = groups_list[idx]
                with cols[j]:
                    st.markdown(f"### 📋 Grupo {grp}")
                    df_standing = calculate_group_standings(grp)
                    
                    # Dar estilo a la tabla usando st.dataframe
                    def highlight_rows(row):
                        pos = row.name
                        if pos <= 2:
                            return ['background-color: rgba(46, 117, 89, 0.25); border-left: 4px solid #2e7559'] * len(row)
                        elif pos == 3:
                            return ['background-color: rgba(224, 153, 36, 0.15); border-left: 4px solid #e09924'] * len(row)
                        return [''] * len(row)
                    
                    styled_df = df_standing.style.apply(highlight_rows, axis=1)
                    
                    st.dataframe(
                        styled_df,
                        use_container_width=True,
                        column_config={
                            "Equipo": st.column_config.TextColumn("Selección", help="Nombre del país"),
                            "PJ": st.column_config.NumberColumn("PJ", help="Partidos Jugados"),
                            "PG": st.column_config.NumberColumn("PG", help="Partidos Ganados"),
                            "PE": st.column_config.NumberColumn("PE", help="Partidos Empatados"),
                            "PP": st.column_config.NumberColumn("PP", help="Partidos Perdidos"),
                            "GF": st.column_config.NumberColumn("GF", help="Goles a Favor"),
                            "GC": st.column_config.NumberColumn("GC", help="Goles en Contra"),
                            "DG": st.column_config.NumberColumn("DG", help="Diferencia de Goles"),
                            "PTS": st.column_config.NumberColumn("PTS", help="Puntos"),
                        }
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

# TAB 3: POLLA / PRONÓSTICOS DE AMIGOS
with tab3:
    st.markdown("<h2 class='section-title'>🔮 La Polla Mundialista</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8892b0;'>¡Compite con tus amigos! Ingresa los pronósticos de cada uno y mira quién va liderando el torneo de predicciones.</p>", unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([1, 2])
    
    with col_p1:
        st.markdown("### 👥 Participantes")
        
        # Agregar amigo
        with st.form("add_friend_form", clear_on_submit=True):
            nuevo_nombre = st.text_input("Nombre del Amigo/Familiar:")
            submitted = st.form_submit_button("Añadir Participante")
            if submitted and nuevo_nombre:
                name_clean = nuevo_nombre.strip()
                if name_clean and name_clean not in preds["participants"]:
                    preds["participants"][name_clean] = {"predictions": {}}
                    save_predictions(preds)
                    st.session_state.preds = preds
                    st.success(f"¡{name_clean} ha sido añadido!")
                    st.rerun()
                elif name_clean in preds["participants"]:
                    st.warning("Este participante ya existe.")
        
        # Eliminar amigo
        if preds["participants"]:
            amigo_a_eliminar = st.selectbox("Eliminar participante:", ["Selecciona..."] + list(preds["participants"].keys()))
            if amigo_a_eliminar != "Selecciona...":
                if st.button("❌ Eliminar Permanentemente", type="primary"):
                    del preds["participants"][amigo_a_eliminar]
                    save_predictions(preds)
                    st.session_state.preds = preds
                    st.warning(f"Se ha eliminado a {amigo_a_eliminar}")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 🏆 Tabla de Posiciones de la Polla")
        
        if not preds["participants"]:
            st.info("Aún no hay participantes agregados. ¡Añade a tus amigos!")
        else:
            df_leaderboard = calculate_predictions_leaderboard()
            
            # Formato de visualización de tabla de amigos
            st.dataframe(
                df_leaderboard,
                use_container_width=True,
                column_config={
                    "Participante": st.column_config.TextColumn("Nombre"),
                    "Pronósticos Hechos": st.column_config.NumberColumn("Partidos Predichos"),
                    "Aciertos Exactos (3 pts)": st.column_config.NumberColumn("🎯 Exactos"),
                    "Aciertos Tendencia (1 pt)": st.column_config.NumberColumn("👍 Tendencia"),
                    "Puntos Totales": st.column_config.NumberColumn("Puntos", help="Exacto = 3 pts | Tendencia = 1 pt"),
                }
            )
            
            st.markdown("""
            **Reglamento de Puntos:**
            - 🎯 **3 Puntos**: Acierto exacto del marcador (ej: predicción 2-1, resultado 2-1).
            - 👍 **1 Punto**: Acierto de la tendencia (ganador o empate) pero no del marcador exacto.
            - ❌ **0 Puntos**: Predicción incorrecta.
            """)
            
    with col_p2:
        st.markdown("### ✍️ Registrar Pronósticos")
        
        if not preds["participants"]:
            st.info("Por favor, agrega al menos un participante en la columna izquierda para ingresar pronósticos.")
        else:
            amigo_select = st.selectbox("Selecciona para quién vas a ingresar pronósticos:", list(preds["participants"].keys()))
            
            if amigo_select:
                st.markdown(f"Ingresando pronósticos para **{amigo_select}**")
                
                # Crear formulario para guardar todos los cambios juntos
                with st.form(f"form_preds_{amigo_select}"):
                    # Traer predicciones existentes
                    current_preds = preds["participants"][amigo_select].get("predictions", {})
                    
                    new_preds_data = {}
                    
                    # Mostrar partidos
                    for match in db["matches"]:
                        match_id_str = str(match["id"])
                        saved_pred = current_preds.get(match_id_str, {"goals_a": 0, "goals_b": 0})
                        
                        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns([2, 1, 1, 1, 2])
                        
                        iso_a = db["team_iso"].get(match["team_a"], "un")
                        iso_b = db["team_iso"].get(match["team_b"], "un")
                        col_m1.markdown(f'<img src="https://flagcdn.com/w40/{iso_a}.png" width="24" style="vertical-align: middle; margin-right: 8px; border-radius: 2px; border: 1px solid rgba(255,255,255,0.1);" /> **{match["team_a"]}**', unsafe_allow_html=True)
                        
                        # Si el partido ya se jugó en la realidad, mostrar resultado real
                        if match["goals_a"] is not None:
                            col_m2.markdown(f"*(Real: {match['goals_a']}-{match['goals_b']}*")
                        else:
                            col_m2.markdown("")
                            
                        pred_val_a = col_m3.number_input(
                            "A", 
                            min_value=0, 
                            max_value=20, 
                            value=int(saved_pred.get("goals_a", 0)), 
                            key=f"p_a_{amigo_select}_{match['id']}",
                            label_visibility="collapsed"
                        )
                        pred_val_b = col_m4.number_input(
                            "B", 
                            min_value=0, 
                            max_value=20, 
                            value=int(saved_pred.get("goals_b", 0)), 
                            key=f"p_b_{amigo_select}_{match['id']}",
                            label_visibility="collapsed"
                        )
                        
                        col_m5.markdown(f'**{match["team_b"]}** <img src="https://flagcdn.com/w40/{iso_b}.png" width="24" style="vertical-align: middle; margin-left: 8px; border-radius: 2px; border: 1px solid rgba(255,255,255,0.1);" />', unsafe_allow_html=True)
                        
                        new_preds_data[match_id_str] = {"goals_a": pred_val_a, "goals_b": pred_val_b}
                        st.markdown("<hr style='margin: 0.3rem 0; opacity: 0.15;' />", unsafe_allow_html=True)
                        
                    # Botón para guardar predicciones
                    btn_save_preds = st.form_submit_button(f"Guardar todos los Pronósticos de {amigo_select}")
                    if btn_save_preds:
                        preds["participants"][amigo_select]["predictions"] = new_preds_data
                        save_predictions(preds)
                        st.session_state.preds = preds
                        st.success(f"¡Todos los pronósticos de {amigo_select} guardados correctamente!")
                        st.rerun()

# TAB 4: ESTADÍSTICAS Y MÉTDRICAS
with tab4:
    st.markdown("<h2 class='section-title'>Análisis de Datos y Estadísticas</h2>", unsafe_allow_html=True)
    
    if matches_played == 0:
        st.warning("Por favor, ingresa al menos un resultado real en la primera pestaña para generar estadísticas.")
    else:
        # 1. Goles por selección
        st.subheader("⚽ Goles anotados por Selección (Top 10)")
        goals_data = {}
        for m in db["matches"]:
            if m["goals_a"] is not None:
                goals_data[m["team_a"]] = goals_data.get(m["team_a"], 0) + m["goals_a"]
                goals_data[m["team_b"]] = goals_data.get(m["team_b"], 0) + m["goals_b"]
        
        df_goals = pd.DataFrame(list(goals_data.items()), columns=["Selección", "Goles"]).sort_values(by="Goles", ascending=False).head(10)
        
        fig_goals = px.bar(
            df_goals,
            x="Goles",
            y="Selección",
            orientation='h',
            color="Goles",
            color_continuous_scale="Reds",
            template="plotly_dark",
            title="Goles Anotados por País"
        )
        fig_goals.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_goals, use_container_width=True)
        
        # 2. Distribución de partidos por canal y estadio
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("📺 Cobertura de Transmisión en Chile")
            free_count = sum(1 for m in db["matches"] if m["channel_free"] is not None)
            pay_count = sum(1 for m in db["matches"] if m["channel_free"] is None)
            coverage_data = pd.DataFrame({
                "Tipo de Transmisión": ["Chilevisión (Señal Abierta)", "Exclusivos de Pago (DSports/DGO/Paramount+)"],
                "Cantidad de Partidos": [free_count, pay_count]
            })
            
            fig_channels = px.pie(
                coverage_data,
                values="Cantidad de Partidos",
                names="Tipo de Transmisión",
                color="Tipo de Transmisión",
                color_discrete_map={"Chilevisión (Señal Abierta)": "#e63946", "Exclusivos de Pago (DSports/DGO/Paramount+)": "#00b4d8"},
                template="plotly_dark",
                hole=0.4
            )
            fig_channels.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_channels, use_container_width=True)
            
        with col_chart2:
            st.subheader("🏟️ Promedio de Goles por Sede")
            stadium_goals = {}
            stadium_counts = {}
            for m in db["matches"]:
                if m["goals_a"] is not None:
                    stadium = m["stadium"]
                    goals = m["goals_a"] + m["goals_b"]
                    stadium_goals[stadium] = stadium_goals.get(stadium, 0) + goals
                    stadium_counts[stadium] = stadium_counts.get(stadium, 0) + 1
            
            avg_goals = {st: (stadium_goals[st] / stadium_counts[st]) for st in stadium_goals}
            df_avg_goals = pd.DataFrame(list(avg_goals.items()), columns=["Estadio", "Promedio de Goles"]).sort_values(by="Promedio de Goles", ascending=False)
            
            fig_stadiums = px.bar(
                df_avg_goals,
                x="Estadio",
                y="Promedio de Goles",
                color="Promedio de Goles",
                color_continuous_scale="Blues",
                template="plotly_dark"
            )
            fig_stadiums.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_stadiums, use_container_width=True)

# Footer Informativo de la App
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #8892b0; font-size: 0.9rem; padding-bottom: 20px;'>"
    "Desarrollado con ❤️ para los amantes del fútbol en Chile • Datos cargados desde archivo local json"
    "</div>",
    unsafe_allow_html=True
)
