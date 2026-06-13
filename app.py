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
    .channel-badge-disney {
        background: linear-gradient(135deg, #1f305e 0%, #111a30 100%);
        color: #00e5ff;
        border: 1px solid rgba(0, 229, 255, 0.3);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 5px;
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

# Base de datos de jugadores (delanteros y mediocampistas clave) para los 48 equipos
TEAM_PLAYERS = {
    "Alemania": ["Jamal Musiala", "Florian Wirtz", "Kai Havertz", "Niclas Füllkrug", "Serge Gnabry"],
    "Arabia Saudí": ["Salem Al-Dawsari", "Firas Al-Buraikan", "Saleh Al-Shehri", "Abdulrahman Ghareeb"],
    "Argelia": ["Riyad Mahrez", "Islam Slimani", "Baghdad Bounedjah", "Amine Gouiri", "Houssem Aouar"],
    "Argentina": ["Lionel Messi", "Lautaro Martínez", "Julián Álvarez", "Alexis Mac Allister", "Rodrigo De Paul", "Angel Di María"],
    "Australia": ["Mitchell Duke", "Craig Goodwin", "Martin Boyle", "Jackson Irvine", "Mathew Leckie"],
    "Austria": ["Marcel Sabitzer", "Marko Arnautović", "Michael Gregoritsch", "Christoph Baumgartner", "Konrad Laimer"],
    "Bosnia y Herzegovina": ["Edin Džeko", "Ermedin Demirović", "Miroslav Stevanović", "Rade Krunić"],
    "Brasil": ["Vinicius Jr.", "Rodrygo", "Neymar Jr.", "Raphinha", "Endrick", "Gabriel Martinelli"],
    "Bélgica": ["Romelu Lukaku", "Kevin De Bruyne", "Leandro Trossard", "Jérémy Doku", "Loïs Openda"],
    "Cabo Verde": ["Bebé", "Ryan Mendes", "Garry Rodrigues", "Jovane Cabral"],
    "Canadá": ["Jonathan David", "Alphonso Davies", "Cyle Larin", "Tajon Buchanan", "Jacob Shaffelburg"],
    "Catar": ["Akram Afif", "Almoez Ali", "Hassan Al-Haydos", "Mohammed Muntari"],
    "Colombia": ["Luis Díaz", "James Rodríguez", "Rafael Santos Borré", "Jhon Durán", "Luis Sinisterra"],
    "Corea del Sur": ["Son Heung-min", "Hwang Hee-chan", "Cho Gue-sung", "Lee Kang-in", "Lee Jae-sung"],
    "Costa de Marfil": ["Sébastien Haller", "Simon Adingra", "Franck Kessié", "Nicolas Pépé", "Ibrahim Sangaré"],
    "Croacia": ["Andrej Kramarić", "Luka Modrić", "Ivan Perišić", "Mario Pašalić", "Bruno Petković"],
    "Curazao": ["Rangelo Janga", "Leandro Bacuna", "Kenji Gorré", "Jearl Margaritha"],
    "Dinamarca": ["Rasmus Højlund", "Christian Eriksen", "Jonas Wind", "Yussuf Poulsen", "Andreas Skov Olsen"],
    "Ecuador": ["Enner Valencia", "Kendry Páez", "Jordy Caicedo", "Jeremy Sarmiento", "Moises Caicedo"],
    "Escocia": ["Scott McTominay", "John McGinn", "Ché Adams", "Lyndon Dykes", "Ryan Christie"],
    "España": ["Álvaro Morata", "Nico Williams", "Lamine Yamal", "Dani Olmo", "Ferran Torres", "Pedri"],
    "Estados Unidos": ["Christian Pulisic", "Folarin Balogun", "Timothy Weah", "Weston McKennie", "Gio Reyna", "Brenden Aaronson"],
    "Francia": ["Kylian Mbappé", "Antoine Griezmann", "Olivier Giroud", "Ousmane Dembélé", "Bradley Barcola", "Marcus Thuram"],
    "Ghana": ["Mohammed Kudus", "Jordan Ayew", "Iñaki Williams", "Antoine Semenyo", "Osman Bukari"],
    "Haití": ["Duckens Nazon", "Frantzdy Pierrot", "Wilde-Donald Guerrier", "Carnejy Antoine"],
    "Inglaterra": ["Harry Kane", "Jude Bellingham", "Bukayo Saka", "Phil Foden", "Marcus Rashford", "Ollie Watkins"],
    "Irak": ["Aymen Hussein", "Mohanad Ali", "Ali Jasim", "Bashar Resan"],
    "Japón": ["Kaoru Mitoma", "Takumi Minamino", "Takefusa Kubo", "Ayase Ueda", "Daizen Maeda"],
    "Jordania": ["Yazan Al-Naimat", "Ali Olwan", "Hamza Al-Dardour", "Mahmoud Al-Mardi"],
    "Marruecos": ["Hakim Ziyech", "Youssef En-Nesyri", "Sofiane Boufal", "Achraf Hakimi", "Brahim Díaz"],
    "México": ["Santiago Giménez", "Henry Martín", "Hirving Lozano", "Uriel Antuna", "Luis Chávez", "Orbelín Pineda"],
    "Nigeria": ["Victor Osimhen", "Ademola Lookman", "Alex Iwobi", "Samuel Chukwueze", "Kelechi Iheanacho"],
    "Noruega": ["Erling Haaland", "Martin Ødegaard", "Alexander Sørloth", "Mohamed Elyounoussi", "Oscar Bobb"],
    "Nueva Zelanda": ["Chris Wood", "Matthew Garbett", "Ben Waine", "Callum McCowatt"],
    "Panamá": ["José Fajardo", "Eduardo Guerrero", "Yoel Bárcenas", "Cecilio Waterman"],
    "Paraguay": ["Antonio Sanabria", "Miguel Almirón", "Julio Enciso", "Adam Bareiro", "Ramón Sosa"],
    "Países Bajos": ["Memphis Depay", "Cody Gakpo", "Donyell Malen", "Wout Weghorst", "Xavi Simons"],
    "Portugal": ["Cristiano Ronaldo", "Bruno Fernandes", "Bernardo Silva", "Diogo Jota", "João Félix", "Rafael Leão"],
    "R.D. del Congo": ["Yoane Wissa", "Cédric Bakambu", "Théo Bongonda", "Meschack Elia"],
    "República Checa": ["Patrik Schick", "Tomáš Souček", "Mojmír Chytil", "Adam Hložek", "Jan Kuchta"],
    "Senegal": ["Sadio Mané", "Nicolas Jackson", "Ismaïla Sarr", "Habib Diallo", "Idrissa Gueye"],
    "Sudáfrica": ["Percy Tau", "Themba Zwane", "Teboho Mokoena", "Evidence Makgopa"],
    "Suecia": ["Viktor Gyökeres", "Alexander Isak", "Dejan Kulusevski", "Emil Forsberg", "Anthony Elanga"],
    "Suiza": ["Breel Embolo", "Xherdan Shaqiri", "Zeki Amdouni", "Ruben Vargas", "Granit Xhaka"],
    "Turquía": ["Barış Alper Yılmaz", "Arda Güler", "Hakan Çalhanoğlu", "Kerem Aktürkoğlu", "Cenk Tosun"],
    "Túnez": ["Youssef Msakni", "Aïssa Laïdouni", "Elias Achouri", "Hamza Rafia"],
    "Uruguay": ["Darwin Núñez", "Luis Suárez", "Facundo Pellistri", "Federico Valverde", "Nicolás De la Cruz"],
    "Uzbekistán": ["Eldor Shomurodov", "Jaloliddin Masharipov", "Oston Urunov", "Abbosbek Fayzullaev"]
}

# Helper para autogenerar goleadores realistas
def generate_random_scorers(team_name, goals):
    import random
    roster = TEAM_PLAYERS.get(team_name, [])
    if not roster:
        roster = [f"Jugador de {team_name}"]
    minutes = sorted([random.randint(1, 90) for _ in range(goals)])
    return [f"{random.choice(roster)} ({m}')" for m in minutes]

# Cargar base de datos inicial o de sesión
def load_data():
    if not os.path.exists(DATA_FILE):
        st.error(f"Archivo de datos no encontrado en {DATA_FILE}. Por favor verifica el directorio.")
        return None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    # Migración/validación de goleadores
    modified = False
    for m in db.get("matches", []):
        if "scorers" not in m:
            m["scorers"] = {"team_a": [], "team_b": []}
            # Si el partido ya tiene goles asignados pero no tiene goleadores, los autogeneramos
            if m["goals_a"] is not None and m["goals_a"] > 0 and not m["scorers"]["team_a"]:
                m["scorers"]["team_a"] = generate_random_scorers(m["team_a"], m["goals_a"])
            if m["goals_b"] is not None and m["goals_b"] > 0 and not m["scorers"]["team_b"]:
                m["scorers"]["team_b"] = generate_random_scorers(m["team_b"], m["goals_b"])
            modified = True
            
    if modified:
        save_data(db)
        
    return db

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

def auto_update_past_matches(db):
    from datetime import datetime, timedelta
    import random
    
    current_time = datetime.now()
    updated = False
    
    # Pre-defined real-world results for matches that already played
    real_results = {
        1: (2, 0),  # México vs Sudáfrica: 2 - 0
        2: (2, 1),  # Corea del Sur vs República Checa: 2 - 1
        3: (1, 1),  # Canadá vs Bosnia: 1 - 1
        7: (4, 1)   # Estados Unidos vs Paraguay: 4 - 1
    }
    
    # Goleadores oficiales del mundo real para los partidos disputados
    real_scorers = {
        1: {
            "team_a": ["Santiago Giménez (23')", "Hirving Lozano (78')"],
            "team_b": []
        },
        2: {
            "team_a": ["Son Heung-min (45')", "Hwang Hee-chan (82')"],
            "team_b": ["Patrik Schick (60')"]
        },
        3: {
            "team_a": ["Jonathan David (34')"],
            "team_b": ["Edin Džeko (75')"]
        },
        7: {
            "team_a": ["Christian Pulisic (12')", "Folarin Balogun (40')", "Christian Pulisic (55')", "Weston McKennie (70')"],
            "team_b": ["Miguel Almirón (30')"]
        }
    }
    
    for m in db["matches"]:
        m_id = m["id"]
        match_datetime_str = f"{m['date']} {m['time_clt']}"
        match_datetime = datetime.strptime(match_datetime_str, "%Y-%m-%d %H:%M")
        
        # A match is finished 2 hours after kickoff
        if match_datetime + timedelta(hours=2) < current_time:
            # If the match has no result registered yet
            if m["goals_a"] is None or m["goals_b"] is None:
                if m_id in real_results:
                    m["goals_a"] = real_results[m_id][0]
                    m["goals_b"] = real_results[m_id][1]
                    m["scorers"] = real_scorers[m_id]
                else:
                    # Simulate realistic scores
                    goal_pool = [0, 0, 1, 1, 1, 2, 2, 3, 4]
                    m["goals_a"] = random.choice(goal_pool)
                    m["goals_b"] = random.choice(goal_pool)
                    
                    # Knockout tie-breaker
                    if m_id >= 73 and m["goals_a"] == m["goals_b"]:
                        if random.random() < 0.5:
                            m["goals_a"] += 1
                        else:
                            m["goals_b"] += 1
                            
                    m["scorers"] = {
                        "team_a": generate_random_scorers(m["team_a"], m["goals_a"]),
                        "team_b": generate_random_scorers(m["team_b"], m["goals_b"])
                    }
                updated = True
                
    if updated:
        save_data(db)
        
    return db

# Inicializar sesión
if "db" not in st.session_state:
    st.session_state.db = load_data()
if "preds" not in st.session_state:
    st.session_state.preds = load_predictions()

# Inicializar configuración de simulación automática
if "auto_sim" not in st.session_state:
    st.session_state.auto_sim = True

# Si la actualización automática está activada, procesar partidos
if st.session_state.auto_sim:
    st.session_state.db = auto_update_past_matches(st.session_state.db)

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

# Helper para calcular la tabla de goleadores
def get_top_scorers(db):
    scorers_dict = {}
    for m in db["matches"]:
        if m["goals_a"] is not None and "scorers" in m:
            for s in m["scorers"].get("team_a", []):
                player = s.split(" (")[0].strip()
                if player:
                    key = (player, m["team_a"])
                    scorers_dict[key] = scorers_dict.get(key, 0) + 1
            for s in m["scorers"].get("team_b", []):
                player = s.split(" (")[0].strip()
                if player:
                    key = (player, m["team_b"])
                    scorers_dict[key] = scorers_dict.get(key, 0) + 1
                    
    scorers_list = []
    for (player, team), goals in scorers_dict.items():
        scorers_list.append({
            "Jugador": player,
            "Selección": team,
            "Goles": goals
        })
    df = pd.DataFrame(scorers_list)
    if not df.empty:
        df = df.sort_values(by=["Goles", "Jugador"], ascending=[False, True]).reset_index(drop=True)
        df.index += 1
    return df

# Calcular estadísticas globales para el Sidebar y Dashboard
matches_played = sum(1 for m in db["matches"] if m["goals_a"] is not None)
total_matches = len(db["matches"])
pct_completed = (matches_played / total_matches) * 100 if total_matches > 0 else 0
total_goals = sum((m["goals_a"] or 0) + (m["goals_b"] or 0) for m in db["matches"] if m["goals_a"] is not None)

# SIDEBAR / PANEL DE CONTROL
with st.sidebar:
    st.image("data/logo.png", width=120)
    st.title("Control del Torneo")
    
    st.markdown("---")
    st.subheader("📊 Progreso del Mundial")
    st.metric("Partidos Jugados", f"{matches_played} / {total_matches}", f"{pct_completed:.1f}%")
    st.metric("Goles Totales", total_goals)
    
    st.markdown("---")
    st.subheader("🏆 Transmisiones en Chile")
    st.markdown("""
    - **📺 Señal Abierta:** Chilevisión transmite 34 partidos seleccionados.
    - **🔒 Señal de Pago:**
        - **DSports / DGO / Paramount+** transmite **el 100% de los 104 partidos** en español.
        - **Disney+ Premium (ESPN)** transmite un paquete selecto de **30 partidos** en vivo (fase de grupos, eliminatorias y final).
    """)
    
    # Configuración de actualización automática
    st.markdown("---")
    st.subheader("⚙️ Configuración")
    auto_sim = st.toggle(
        "Actualización Automática", 
        value=st.session_state.get("auto_sim", True), 
        help="Simula o actualiza automáticamente los resultados de partidos cuyos horarios ya hayan transcurrido en tiempo real."
    )
    if auto_sim != st.session_state.get("auto_sim", True):
        st.session_state.auto_sim = auto_sim
        st.rerun()
        
    # Botón para restablecer base de datos
    st.markdown("---")
    if st.button("🔄 Reiniciar Resultados", help="Borra todos los marcadores ingresados"):
        for m in db["matches"]:
            m["goals_a"] = None
            m["goals_b"] = None
            m["scorers"] = {"team_a": [], "team_b": []}
        save_data(db)
        st.session_state.db = db
        st.rerun()
        
    st.markdown("<p style='font-size:0.75rem; color:#8892b0; font-style:italic;'>Nota: Desactiva 'Actualización Automática' si deseas ingresar o limpiar todos los marcadores desde cero manualmente.</p>", unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #8892b0; font-size: 0.85rem;'>© Anthony Odgers Briones</div>", unsafe_allow_html=True)

# CUERPO PRINCIPAL
col_title1, col_title2 = st.columns([1, 6])
with col_title1:
    st.image("data/logo.png", width=100)
with col_title2:
    st.markdown("<h1 style='margin-top: 5px; color: white;'>FIFA WORLD CUP 2026</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8892b0; font-size: 1.1rem; margin-top: -15px;'>Calendario Interactivo, Resultados en Vivo y Tabla de Posiciones para Chile</p>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Partidos y Resultados", 
    "📊 Tablas de Posiciones", 
    "⚽ Goleadores",
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
        filtro_canal = st.selectbox("Filtrar por Transmisión", [
            "Todos", 
            "Señal Abierta (Chilevisión)", 
            "Exclusivos de Pago (DSports/DGO/Paramount+)",
            "Disney+ Premium (30 partidos)"
        ])
    with col_f3:
        filtro_estado = st.selectbox("Filtrar por Estado", ["Todos", "Por jugar", "Finalizados"])
    with col_f4:
        filtro_busqueda = st.text_input("🔍 Buscar Selección", placeholder="Ej: Chile, Argentina")
        
    # Aplicar filtros y ordenar cronológicamente
    matches_filtered = sorted(db["matches"], key=lambda x: (x["date"], x["time_clt"]))
    if filtro_grupo != "Todos":
        matches_filtered = [m for m in matches_filtered if m["group"] == filtro_grupo]
        
    if filtro_canal == "Señal Abierta (Chilevisión)":
        matches_filtered = [m for m in matches_filtered if m["channel_free"] is not None]
    elif filtro_canal == "Exclusivos de Pago (DSports/DGO/Paramount+)":
        matches_filtered = [m for m in matches_filtered if m["channel_free"] is None]
    elif filtro_canal == "Disney+ Premium (30 partidos)":
        matches_filtered = [m for m in matches_filtered if "Disney+ Premium" in m.get("channel_pay", "")]
        
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
                        # Formatear canales de pago
                        pay_channels = match["channel_pay"].split(" / ")
                        main_pay = [c for c in pay_channels if c != "Disney+ Premium"]
                        main_pay_str = " / ".join(main_pay)
                        
                        badge_pay = f"<span class='channel-badge-pay'>🔑 {main_pay_str}</span>"
                        if "Disney+ Premium" in pay_channels:
                            badge_pay += " <span class='channel-badge-disney'>✨ Disney+ Premium</span>"
                        
                        # Formatear goleadores para mostrar en la tarjeta
                        scorers_row_html = ""
                        if match["goals_a"] is not None:
                            scorers_a = match.get("scorers", {}).get("team_a", [])
                            scorers_b = match.get("scorers", {}).get("team_b", [])
                            scorers_a_str = "<br>".join([f"⚽ {s}" for s in scorers_a])
                            scorers_b_str = "<br>".join([f"⚽ {s}" for s in scorers_b])
                            
                            scorers_row_html = f"""
                            <div class="scorers-row" style="display: flex; justify-content: space-between; margin-top: -5px; margin-bottom: 10px; font-size: 0.8rem; color: #a8b2d1;">
                                <div style="width: 38%; text-align: center; line-height: 1.2;">
                                    {scorers_a_str}
                                </div>
                                <div style="width: 24%;"></div>
                                <div style="width: 38%; text-align: center; line-height: 1.2;">
                                    {scorers_b_str}
                                </div>
                            </div>
                            """
                            
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
                            {scorers_row_html}
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
                            new_team_a = match["team_a"]
                            new_team_b = match["team_b"]
                            
                            # Si es partido de eliminación directa (id >= 73), permitir editar nombres de selecciones
                            if match["id"] >= 73:
                                st.markdown("<p style='font-size:0.85rem; color:#8892b0; margin-bottom:2px;'>Definir Selecciones Clasificadas:</p>", unsafe_allow_html=True)
                                col_name1, col_name2 = st.columns(2)
                                new_team_a = col_name1.text_input(f"Selección A", value=match["team_a"], key=f"name_a_{match['id']}")
                                new_team_b = col_name2.text_input(f"Selección B", value=match["team_b"], key=f"name_b_{match['id']}")
                                
                            col_inp1, col_inp2 = st.columns(2)
                            val_a = match["goals_a"] if match["goals_a"] is not None else 0
                            val_b = match["goals_b"] if match["goals_b"] is not None else 0
                            
                            new_a = col_inp1.number_input(f"Goles {new_team_a}", min_value=0, max_value=25, value=int(val_a), key=f"inp_a_{match['id']}")
                            new_b = col_inp2.number_input(f"Goles {new_team_b}", min_value=0, max_value=25, value=int(val_b), key=f"inp_b_{match['id']}")
                            
                            # Inputs para goleadores
                            scorers_a_val = ", ".join(match.get("scorers", {}).get("team_a", []))
                            scorers_b_val = ", ".join(match.get("scorers", {}).get("team_b", []))
                            
                            col_scr1, col_scr2 = st.columns(2)
                            new_scr_a_str = col_scr1.text_input(
                                f"Goleadores {new_team_a}", 
                                value=scorers_a_val, 
                                key=f"scr_a_{match['id']}",
                                help="Separados por coma, ej: Lionel Messi (10'), Julián Álvarez (45')"
                            )
                            new_scr_b_str = col_scr2.text_input(
                                f"Goleadores {new_team_b}", 
                                value=scorers_b_val, 
                                key=f"scr_b_{match['id']}",
                                help="Separados por coma, ej: Patrik Schick (60')"
                            )
                            
                            col_btn1, col_btn2 = st.columns(2)
                            if col_btn1.button("Guardar Marcador", key=f"btn_save_{match['id']}"):
                                # Parsear goleadores
                                list_scr_a = [s.strip() for s in new_scr_a_str.split(",") if s.strip()]
                                list_scr_b = [s.strip() for s in new_scr_b_str.split(",") if s.strip()]
                                
                                # Si hay goles pero no se especificaron goleadores, autogenerar
                                if new_a > 0 and not list_scr_a:
                                    list_scr_a = generate_random_scorers(new_team_a, new_a)
                                if new_b > 0 and not list_scr_b:
                                    list_scr_b = generate_random_scorers(new_team_b, new_b)
                                    
                                # Forzar listas vacías si los goles son 0
                                if new_a == 0:
                                    list_scr_a = []
                                if new_b == 0:
                                    list_scr_b = []
                                    
                                # Actualizar datos en sesión y archivo
                                for m in db["matches"]:
                                    if m["id"] == match["id"]:
                                        m["goals_a"] = new_a
                                        m["goals_b"] = new_b
                                        m["team_a"] = new_team_a
                                        m["team_b"] = new_team_b
                                        m["scorers"] = {
                                            "team_a": list_scr_a,
                                            "team_b": list_scr_b
                                        }
                                save_data(db)
                                st.session_state.db = db
                                st.success("¡Resultado oficial y goleadores guardados!")
                                st.rerun()
                                
                            if match["goals_a"] is not None:
                                if col_btn2.button("Limpiar Marcador", key=f"btn_clear_{match['id']}", type="secondary"):
                                    for m in db["matches"]:
                                        if m["id"] == match["id"]:
                                            m["goals_a"] = None
                                            m["goals_b"] = None
                                            m["scorers"] = {"team_a": [], "team_b": []}
                                            # Volver a los marcadores de posición predeterminados si es eliminatoria
                                            if m["id"] >= 73:
                                                placeholders = {
                                                    73: ("2° Grupo A", "2° Grupo B"),
                                                    74: ("1° Grupo E", "3° Grupo A/B/C/D/F"),
                                                    75: ("1° Grupo F", "2° Grupo C"),
                                                    76: ("1° Grupo C", "2° Grupo F"),
                                                    77: ("1° Grupo I", "3° Grupo C/D/F/G/H"),
                                                    78: ("2° Grupo E", "2° Grupo I"),
                                                    79: ("1° Grupo A", "3° Grupo C/E/F/H/I"),
                                                    80: ("1° Grupo L", "3° Grupo E/H/I/J/K"),
                                                    81: ("1° Grupo D", "3° Grupo B/E/F/I/J"),
                                                    82: ("1° Grupo G", "3° Grupo A/E/H/I/J"),
                                                    83: ("2° Grupo K", "2° Grupo L"),
                                                    84: ("1° Grupo H", "2° Grupo J"),
                                                    85: ("1° Grupo B", "3° Grupo E/F/G/I/J"),
                                                    86: ("1° Grupo J", "2° Grupo H"),
                                                    87: ("1° Grupo K", "3° Grupo D/E/I/J/L"),
                                                    88: ("2° Grupo D", "2° Grupo G"),
                                                    89: ("Ganador M74", "Ganador M77"),
                                                    90: ("Ganador M73", "Ganador M75"),
                                                    91: ("Ganador M76", "Ganador M78"),
                                                    92: ("Ganador M79", "Ganador M80"),
                                                    93: ("Ganador M83", "Ganador M84"),
                                                    94: ("Ganador M81", "Ganador M82"),
                                                    95: ("Ganador M86", "Ganador M88"),
                                                    96: ("Ganador M85", "Ganador M87"),
                                                    97: ("Ganador M89", "Ganador M90"),
                                                    98: ("Ganador M93", "Ganador M94"),
                                                    99: ("Ganador M91", "Ganador M92"),
                                                    100: ("Ganador M95", "Ganador M96"),
                                                    101: ("Ganador M97", "Ganador M98"),
                                                    102: ("Ganador M99", "Ganador M100"),
                                                    103: ("Perdedor M101", "Perdedor M102"),
                                                    104: ("Ganador M101", "Ganador M102")
                                                }
                                                if m["id"] in placeholders:
                                                    m["team_a"], m["team_b"] = placeholders[m["id"]]
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

# TAB 3: GOLEADORES
with tab3:
    st.markdown("<h2 class='section-title'>⚽ Goleadores del Mundial</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8892b0;'>Estadísticas de goleo acumuladas durante el torneo en tiempo real.</p>", unsafe_allow_html=True)
    
    df_scorers = get_top_scorers(db)
    
    if df_scorers.empty:
        st.info("Aún no se han registrado goles en el torneo.")
    else:
        col_l, col_r = st.columns([1, 2])
        
        with col_l:
            st.markdown("### 🏆 Bota de Oro")
            max_goals = df_scorers["Goles"].max()
            leaders = df_scorers[df_scorers["Goles"] == max_goals]
            
            if len(leaders) == 1:
                leader_row = leaders.iloc[0]
                name = leader_row["Jugador"]
                team = leader_row["Selección"]
                goals = leader_row["Goles"]
                iso = db["team_iso"].get(team, "un")
                flag_img = f'<img src="https://flagcdn.com/w40/{iso}.png" width="28" style="vertical-align: middle; border-radius: 2px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);" />'
                
                card_html = f"""
                <div style="background: linear-gradient(135deg, #ffe066 0%, #f5b041 100%); padding: 25px; border-radius: 16px; text-align: center; color: #1a1a1a; box-shadow: 0 8px 24px rgba(245, 176, 65, 0.3); border: 1px solid rgba(255,255,255,0.2);">
                    <div style="font-size: 3rem; margin-bottom: 10px;">👟⚽</div>
                    <div style="font-size: 0.9rem; font-weight: 800; letter-spacing: 1.5px; color: #5d4037; text-transform: uppercase;">Líder de Goleadores</div>
                    <div style="font-size: 1.8rem; font-weight: 800; margin: 10px 0; color: #000;">{name}</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: #2e1c0c; margin-bottom: 15px;">
                        {flag_img} {team}
                    </div>
                    <div style="display: inline-block; background: #1a1a1a; color: #ffe066; padding: 6px 16px; border-radius: 20px; font-weight: 800; font-size: 1.2rem;">
                        {goals} Goles
                    </div>
                </div>
                """
            else:
                names_list = leaders["Jugador"].tolist()
                team_list = leaders["Selección"].tolist()
                goals = max_goals
                
                leaders_html = ""
                for idx, (n, t) in enumerate(zip(names_list, team_list)):
                    iso = db["team_iso"].get(t, "un")
                    flag_img = f'<img src="https://flagcdn.com/w30/{iso}.png" width="20" style="vertical-align: middle; border-radius: 2px; box-shadow: 0 1px 3px rgba(0,0,0,0.3);" />'
                    leaders_html += f"<div style='margin-bottom: 8px; font-size: 1.1rem; font-weight: 700;'>• {n} ({flag_img} {t})</div>"
                    
                card_html = f"""
                <div style="background: linear-gradient(135deg, #ffe066 0%, #f5b041 100%); padding: 25px; border-radius: 16px; text-align: center; color: #1a1a1a; box-shadow: 0 8px 24px rgba(245, 176, 65, 0.3); border: 1px solid rgba(255,255,255,0.2);">
                    <div style="font-size: 3rem; margin-bottom: 10px;">👟⚽</div>
                    <div style="font-size: 0.9rem; font-weight: 800; letter-spacing: 1.5px; color: #5d4037; text-transform: uppercase;">Líderes de Goleadores</div>
                    <div style="margin: 15px 0; text-align: left; max-height: 150px; overflow-y: auto; color: #000; padding-left: 10px;">
                        {leaders_html}
                    </div>
                    <div style="display: inline-block; background: #1a1a1a; color: #ffe066; padding: 6px 16px; border-radius: 20px; font-weight: 800; font-size: 1.2rem;">
                        {goals} Goles c/u
                    </div>
                </div>
                """
            st.markdown(card_html, unsafe_allow_html=True)
            
        with col_r:
            st.markdown("### 📊 Tabla de Goleadores")
            st.dataframe(
                df_scorers,
                use_container_width=True,
                column_config={
                    "Jugador": st.column_config.TextColumn("Nombre"),
                    "Selección": st.column_config.TextColumn("País"),
                    "Goles": st.column_config.NumberColumn("Goles", help="Total de goles anotados")
                }
            )

# TAB 4: POLLA / PRONÓSTICOS DE AMIGOS
with tab4:
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
                    
                    # Mostrar partidos ordenados cronológicamente
                    for match in sorted(db["matches"], key=lambda x: (x["date"], x["time_clt"])):
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

# TAB 5: ESTADÍSTICAS Y MÉTRICAS
with tab5:
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
            disney_count = sum(1 for m in db["matches"] if "Disney+ Premium" in m.get("channel_pay", ""))
            
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1);'>
                <p style='margin: 0;'><b>Distribución de Transmisiones:</b></p>
                <ul style='margin-bottom: 0;'>
                    <li>📺 <b>Señal Abierta (Chilevisión):</b> {free_count} partidos</li>
                    <li>🔑 <b>DSports / DGO / Paramount+:</b> 104 partidos (100% de la Copa Mundial)</li>
                    <li>✨ <b>Disney+ Premium (ESPN):</b> {disney_count} partidos seleccionados</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
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
    "Desarrollado por <b>Anthony Odgers Briones</b> © 2026 • Todos los derechos reservados"
    "</div>",
    unsafe_allow_html=True
)
