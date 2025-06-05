# streamlit_app.py
import streamlit as st
import random
import time
from PIL import Image
import requests
from io import BytesIO

# Zet als eerste regel de page config
st.set_page_config(page_title="Onze School & Mini Games", page_icon="🎮", layout="wide")

# Afbeelding laden functie
def laad_afbeelding(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return Image.open(BytesIO(r.content))
        else:
            return None
    except:
        return None

# ---- HEADER SCHOOL ----
st.subheader("Hallo wij zijn Sweder en Luca 👋")
st.title("Leerlingen van het Stedelijk Gymnasium Breda")
st.write("Welkom op onze website! Hier zie je informatie over onze school.")
st.write("[Bezoek onze schoolsite >](https://www.gymnasiumbreda.nl/)")

school_foto = laad_afbeelding("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Gymnasium_Breda_voorgevel.JPG/800px-Gymnasium_Breda_voorgevel.JPG")
if school_foto:
    st.image(school_foto, caption="Het Stedelijk Gymnasium Breda", use_container_width=True)


st.write("---")
left_column, right_column = st.columns(2)

with left_column:
    st.header("Waarom is onze school leuk?")
    st.write("""
    ✅ Je krijgt Grieks en Latijn  
    ✅ Leuke leraren  
    ✅ Je kiest zelf flexlessen  
    ✅ Het is een gezellige school
    """)
    st.write("[📸 Instagram](https://www.instagram.com/gymnasiumbreda/)")
    st.write("[▶️ YouTube](https://www.youtube.com/@stedelijkgymnasiumbreda7346/videos)")
    st.write("[📘 Facebook](https://www.facebook.com/gymnasiumbreda/)")

# ---- MINIGAMES ----

# Pagina bijhouden
if "pagina" not in st.session_state:
    st.session_state.pagina = "home"

# Navigatieknoppen
st.sidebar.title("🎮 Mini Games")
games = [
    "Raad het Getal", "Steen Papier Schaar", "Tic Tac Toe", 
    "Dobbelsteen", "flappy"
]

for game in games:
    if st.sidebar.button(game):
        st.session_state.pagina = game.lower().replace(" ", "_")

if st.sidebar.button("🏠 Home"):
    st.session_state.pagina = "home"

# ---- HOMEPAGE ----
if st.session_state.pagina == "home":
    st.title("🎮 Welkom bij Mini Games!")
    st.write("Kies een spel in het menu aan de linkerkant.")
    st.image("https://cdn.pixabay.com/photo/2017/01/31/21/22/game-2028329_1280.png", use_container_width=True)

# ---- GAMES IMPLEMENTATIES ----
from raad_het_getal import raad_het_getal
from steen_papier_schaar import steen_papier_schaar
from tic_tac_toe import tic_tac_toe
from memory_game import memory_game
from dobbelsteen import dobbelsteen
import flappy

# Match pagina met functie
game_functions = {
    "raad_het_getal": raad_het_getal,
    "steen_papier_schaar": steen_papier_schaar,
    "tic_tac_toe": tic_tac_toe,
    "memory_game": memory_game,
    "dobbelsteen": dobbelsteen,
    "flappy": flappy,
}

if st.session_state.pagina in game_functions:
    game_functions[st.session_state.pagina]()
