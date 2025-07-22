import streamlit as st
import random
import json
import os

# -----------------------------
# SPEL INSTELLINGEN
# -----------------------------
START_HEALTH = 100
START_FOOD = 50
START_WATER = 50
DAILY_FOOD_CONSUMPTION = 10
DAILY_WATER_CONSUMPTION = 10

SAVE_FILE = "survival_highscore.json"

# -----------------------------
# HIGHSCORE OPSLAG
# -----------------------------
def load_highscore():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {"best_days": 0}

def save_highscore(days):
    score = load_highscore()
    if days > score.get("best_days", 0):
        score["best_days"] = days
        with open(SAVE_FILE, "w") as f:
            json.dump(score, f)

# -----------------------------
# SPEL INITIALISATIE
# -----------------------------
if "health" not in st.session_state:
    st.session_state.health = START_HEALTH
    st.session_state.food = START_FOOD
    st.session_state.water = START_WATER
    st.session_state.days = 0
    st.session_state.alive = True
    st.session_state.message = "Je bent gestrand in de wildernis. Overleef zolang mogelijk!"
    st.session_state.events = []

# -----------------------------
# DAG UPDATE FUNCTIE
# -----------------------------
def end_day():
    st.session_state.days += 1
    st.session_state.food -= DAILY_FOOD_CONSUMPTION
    st.session_state.water -= DAILY_WATER_CONSUMPTION

    # Als eten of water op is, verlies je gezondheid
    if st.session_state.food <= 0:
        st.session_state.health -= 20
        st.session_state.message += "\nJe hebt geen eten meer! Je verliest 20 gezondheid."
    if st.session_state.water <= 0:
        st.session_state.health -= 30
        st.session_state.message += "\nJe hebt geen water meer! Je verliest 30 gezondheid."

    if st.session_state.health <= 0:
        st.session_state.alive = False
        st.session_state.message += "\n💀 Je bent overleden na " + str(st.session_state.days) + " dagen."
        save_highscore(st.session_state.days)

# -----------------------------
# ACTIES
# -----------------------------
def search_food():
    found = random.randint(0, 30)
    st.session_state.food += found
    st.session_state.message = f"Je ging eten zoeken en vond {found} voedsel."
    # Risico: dierlijke aanval
    if random.random() < 0.3:
        dmg = random.randint(5, 25)
        st.session_state.health -= dmg
        st.session_state.message += f" Maar een wild dier viel je aan! Je verloor {dmg} gezondheid."
    end_day()

def collect_water():
    found = random.randint(0, 40)
    st.session_state.water += found
    st.session_state.message = f"Je haalde water en vond {found} eenheden water."
    # Kans op ziek worden
    if random.random() < 0.2:
        dmg = random.randint(5, 20)
        st.session_state.health -= dmg
        st.session_state.message += f" Maar het water was besmet! Je verloor {dmg} gezondheid."
    end_day()

def rest():
    heal = random.randint(10, 25)
    st.session_state.health += heal
    st.session_state.message = f"Je rustte en herstelde {heal} gezondheid."
    end_day()

def explore():
    chance = random.random()
    if chance < 0.2:
        st.session_state.message = "🎉 Je bent gered door een helikopter! Je hebt overleefd!"
        st.session_state.alive = False
        save_highscore(st.session_state.days)
    elif chance < 0.5:
        loot = random.randint(10, 40)
        st.session_state.food += loot
        st.session_state.water += loot
        st.session_state.message = f"Je verkende de omgeving en vond {loot} voedsel en {loot} water!"
    else:
        dmg = random.randint(10, 35)
        st.session_state.health -= dmg
        st.session_state.message = f"Tijdens het verkennen werd je aangevallen en verloor je {dmg} gezondheid."
    end_day()

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Survival Simulatie", page_icon="🌲", layout="centered")
st.title("🌲 Survival Simulatie")
st.write("Probeer zo veel mogelijk dagen te overleven in de wildernis!")

highscore = load_highscore()
st.sidebar.header("Status")
st.sidebar.write(f"**Dagen Overleefd:** {st.session_state.days}")
st.sidebar.write(f"**Gezondheid:** {st.session_state.health}")
st.sidebar.write(f"**Eten:** {st.session_state.food}")
st.sidebar.write(f"**Water:** {st.session_state.water}")
st.sidebar.write(f"🏆 **Beste Score:** {highscore.get('best_days', 0)} dagen")

st.subheader("Dag " + str(st.session_state.days))
st.write(st.session_state.message)

if st.session_state.alive:
    st.write("Kies je actie voor vandaag:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🍖 Eten Zoeken"):
            search_food()
        if st.button("💧 Water Halen"):
            collect_water()
    with col2:
        if st.button("🛏️ Rusten"):
            rest()
        if st.button("🧭 Verkennen"):
            explore()
else:
    if st.button("🔄 Opnieuw Spelen"):
        st.session_state.health = START_HEALTH
        st.session_state.food = START_FOOD
        st.session_state.water = START_WATER
        st.session_state.days = 0
        st.session_state.alive = True
        st.session_state.message = "Je bent gestrand in de wildernis. Overleef zolang mogelijk!"

st.markdown("---")
st.caption("Gemaakt met ❤️ in Streamlit - Overleef jij langer dan " + str(highscore.get("best_days", 0)) + " dagen?")
