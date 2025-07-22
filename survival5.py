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
START_WOOD = 0
START_STONE = 0
START_MEAT = 0
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
    st.session_state.wood = START_WOOD
    st.session_state.stone = START_STONE
    st.session_state.meat = START_MEAT
    st.session_state.days = 0
    st.session_state.alive = True
    st.session_state.message = "Je bent gestrand in de wildernis. Overleef zolang mogelijk!"
    st.session_state.inventory = {"kampvuur": False, "speer": False, "waterfilter": False}

# -----------------------------
# DAG UPDATE FUNCTIE
# -----------------------------
def end_day():
    st.session_state.days += 1
    st.session_state.food -= DAILY_FOOD_CONSUMPTION
    st.session_state.water -= DAILY_WATER_CONSUMPTION

    # Weer events
    if random.random() < 0.2:
        storm_dmg = random.randint(5, 15)
        st.session_state.health -= storm_dmg
        st.session_state.message += f"\n🌩️ Er was een storm! Je verloor {storm_dmg} gezondheid."

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
    # Kans op vlees en aanval
    if random.random() < 0.3:
        dmg = random.randint(5, 25)
        st.session_state.health -= dmg
        st.session_state.meat += random.randint(1, 3)
        st.session_state.message += f" Maar een wild dier viel je aan! Je verloor {dmg} gezondheid en kreeg wat vlees."
    end_day()

def collect_water():
    found = random.randint(0, 40)
    st.session_state.water += found
    st.session_state.message = f"Je haalde water en vond {found} eenheden water."
    # Kans op besmet water
    if not st.session_state.inventory["waterfilter"] and random.random() < 0.2:
        dmg = random.randint(5, 20)
        st.session_state.health -= dmg
        st.session_state.message += f" Het water was besmet! Je verloor {dmg} gezondheid."
    end_day()

def gather_materials():
    wood_found = random.randint(0, 5)
    stone_found = random.randint(0, 5)
    st.session_state.wood += wood_found
    st.session_state.stone += stone_found
    st.session_state.message = f"Je verzamelde {wood_found} hout en {stone_found} steen."
    end_day()

def rest():
    heal = random.randint(10, 25)
    st.session_state.health = min(100, st.session_state.health + heal)
    st.session_state.message = f"Je rustte en herstelde {heal} gezondheid."
    end_day()

def explore():
    chance = random.random()
    if chance < 0.3:
        loot = random.randint(10, 40)
        st.session_state.food += loot
        st.session_state.water += loot
        st.session_state.message = f"Je verkende de omgeving en vond {loot} voedsel en {loot} water!"
    elif chance < 0.6:
        dmg = random.randint(10, 35)
        st.session_state.health -= dmg
        st.session_state.message = f"Tijdens het verkennen werd je aangevallen en verloor je {dmg} gezondheid."
    else:
        treasure = random.choice(["goud", "edelstenen", "extra voedsel", "kampvuur"])
        if treasure == "kampvuur":
            st.session_state.inventory["kampvuur"] = True
            st.session_state.message = f"Je vond materialen voor een kampvuur! Je kan nu koken."
        else:
            st.session_state.food += 30
            st.session_state.water += 30
            st.session_state.message = f"Je vond een voorraad {treasure}! Extra eten en water voor je reis."
    end_day()

# -----------------------------
# CRAFTING
# -----------------------------
def craft(item):
    if item == "kampvuur" and st.session_state.wood >= 5 and st.session_state.stone >= 3:
        st.session_state.wood -= 5
        st.session_state.stone -= 3
        st.session_state.inventory["kampvuur"] = True
        st.session_state.message = "Je hebt een kampvuur gemaakt! Je kan vlees koken en beter rusten."
    elif item == "speer" and st.session_state.wood >= 4 and st.session_state.stone >= 2:
        st.session_state.wood -= 4
        st.session_state.stone -= 2
        st.session_state.inventory["speer"] = True
        st.session_state.message = "Je hebt een speer gemaakt! Je bent veiliger tegen aanvallen."
    elif item == "waterfilter" and st.session_state.stone >= 5:
        st.session_state.stone -= 5
        st.session_state.inventory["waterfilter"] = True
        st.session_state.message = "Je hebt een waterfilter gemaakt! Geen ziek water meer."
    else:
        st.session_state.message = "Je hebt niet genoeg materialen om dit te maken."

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Survival Simulatie", page_icon="🌲", layout="centered")
st.title("🌲 Survival Simulatie")
st.write("Probeer zo veel mogelijk dagen te overleven in de wildernis!")

highscore = load_highscore()

# Statusbalken
st.sidebar.header("Status")
st.sidebar.progress(st.session_state.health / 100)
st.sidebar.write(f"**Gezondheid:** {st.session_state.health}/100")
st.sidebar.write(f"**Eten:** {st.session_state.food}")
st.sidebar.write(f"**Water:** {st.session_state.water}")
st.sidebar.write(f"**Hout:** {st.session_state.wood}")
st.sidebar.write(f"**Steen:** {st.session_state.stone}")
st.sidebar.write(f"**Vlees:** {st.session_state.meat}")
st.sidebar.write(f"🏆 **Beste Score:** {highscore.get('best_days', 0)} dagen")
st.sidebar.write(f"**Dagen Overleefd:** {st.session_state.days}")

st.subheader("Dag " + str(st.session_state.days))
st.write(st.session_state.message)

if st.session_state.alive:
    st.write("Kies je actie voor vandaag:")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🍖 Eten Zoeken"):
            search_food()
        if st.button("💧 Water Halen"):
            collect_water()
    with col2:
        if st.button("🪓 Materialen Verzamelen"):
            gather_materials()
        if st.button("🛏️ Rusten"):
            rest()
    with col3:
        if st.button("🧭 Verkennen"):
            explore()

    st.markdown("### Crafting")
    if st.button("🔥 Maak Kampvuur (5 hout, 3 steen)"):
        craft("kampvuur")
    if st.button("🔪 Maak Speer (4 hout, 2 steen)"):
        craft("speer")
    if st.button("💦 Maak Waterfilter (5 steen)"):
        craft("waterfilter")
else:
    if st.button("🔄 Opnieuw Spelen"):
        for key in ["health", "food", "water", "wood", "stone", "meat", "days", "alive", "message", "inventory"]:
            st.session_state.pop(key, None)
        st.experimental_rerun()

st.markdown("---")
st.caption("Gemaakt met ❤️ in Streamlit - Overleef jij langer dan "
           + str(highscore.get("best_days", 0)) + " dagen?")
