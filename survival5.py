import streamlit as st
import random
import json
import os
import matplotlib.pyplot as plt

# -----------------------------
# SPEL INSTELLINGEN
# -----------------------------
START_HEALTH = 100
START_FOOD = 50
START_WATER = 50
START_WOOD = 0
START_STONE = 0
START_MEAT_RAW = 0
START_MEAT_COOKED = 0

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
if "initialized" not in st.session_state:
    st.session_state.health = START_HEALTH
    st.session_state.food = START_FOOD
    st.session_state.water = START_WATER
    st.session_state.wood = START_WOOD
    st.session_state.stone = START_STONE
    st.session_state.meat_raw = START_MEAT_RAW
    st.session_state.meat_cooked = START_MEAT_COOKED
    st.session_state.days = 0
    st.session_state.alive = True
    st.session_state.message = "Je bent gestrand in de wildernis. Overleef zo lang mogelijk!"
    st.session_state.inventory = {"kampvuur": False, "speer": False, "waterfilter": False}
    st.session_state.logboek = []
    st.session_state.action_taken = False
    st.session_state.health_history = []
    st.session_state.food_history = []
    st.session_state.water_history = []
    st.session_state.initialized = True

# -----------------------------
# DAG UPDATE FUNCTIE
# -----------------------------
def end_day():
    st.session_state.days += 1

    # Dagelijkse consumptie
    st.session_state.food -= DAILY_FOOD_CONSUMPTION
    st.session_state.water -= DAILY_WATER_CONSUMPTION

    # Voedsel en water kunnen niet negatief
    if st.session_state.food < 0:
        st.session_state.food = 0
    if st.session_state.water < 0:
        st.session_state.water = 0

    # Slaan stats op voor grafieken
    st.session_state.health_history.append(st.session_state.health)
    st.session_state.food_history.append(st.session_state.food)
    st.session_state.water_history.append(st.session_state.water)

    # Weer events (behalve bij rusten!)
    if st.session_state.last_action != "rusten":
        if random.random() < 0.2:
            storm_dmg = random.randint(5, 15)
            st.session_state.health -= storm_dmg
            st.session_state.message += f"\n🌩️ Er was een storm! Je verloor {storm_dmg} gezondheid."
            st.session_state.logboek.append(f"Storm: -{storm_dmg} gezondheid.")

    # Gevaar door eten/water gebrek
    if st.session_state.food == 0:
        st.session_state.health -= 20
        st.session_state.message += "\nJe hebt geen eten meer! Je verliest 20 gezondheid."
        st.session_state.logboek.append("Geen eten: -20 gezondheid.")
    if st.session_state.water == 0:
        st.session_state.health -= 30
        st.session_state.message += "\nJe hebt geen water meer! Je verliest 30 gezondheid."
        st.session_state.logboek.append("Geen water: -30 gezondheid.")

    # Controleer dood
    if st.session_state.health <= 0:
        st.session_state.alive = False
        st.session_state.message += f"\n💀 Je bent overleden na {st.session_state.days} dagen."
        st.session_state.logboek.append(f"Overleden na {st.session_state.days} dagen.")
        save_highscore(st.session_state.days)

    st.session_state.action_taken = False

# -----------------------------
# ACTIE FUNCTIES
# -----------------------------
def search_food():
    found = random.randint(10, 30)
    st.session_state.food += found
    st.session_state.message = f"🍖 Je ging eten zoeken en vond {found} voedsel."
    st.session_state.logboek.append(f"Eten zoeken: +{found} voedsel.")

    # Kans op wilde dieren aanval
    if random.random() < 0.3:
        base_dmg = random.randint(5, 25)
        dmg = base_dmg
        # Speer vermindert schade met 50%
        if st.session_state.inventory["speer"]:
            dmg = int(dmg / 2)
        st.session_state.health -= dmg
        meat_found = random.randint(1, 3)
        st.session_state.meat_raw += meat_found
        st.session_state.message += f" 🐺 Een wild dier viel je aan! Je verloor {dmg} gezondheid en kreeg {meat_found} rauw vlees."
        st.session_state.logboek.append(f"Aanval wild dier: -{dmg} gezondheid, +{meat_found} rauw vlees.")

    end_day()

def collect_water():
    found = random.randint(20, 40)
    st.session_state.water += found
    st.session_state.message = f"💧 Je haalde water en vond {found} eenheden water."
    st.session_state.logboek.append(f"Water halen: +{found} water.")

    # Kans op besmet water zonder filter
    if not st.session_state.inventory["waterfilter"] and random.random() < 0.2:
        base_dmg = random.randint(5, 20)
        st.session_state.health -= base_dmg
        st.session_state.message += f" ⚠️ Het water was besmet! Je verloor {base_dmg} gezondheid."
        st.session_state.logboek.append(f"Besmet water: -{base_dmg} gezondheid.")

    end_day()

def gather_materials():
    wood_found = random.randint(1, 5)
    stone_found = random.randint(0, 5)
    st.session_state.wood += wood_found
    st.session_state.stone += stone_found
    st.session_state.message = f"🪓 Je verzamelde {wood_found} hout en {stone_found} steen."
    st.session_state.logboek.append(f"Materialen verzamelen: +{wood_found} hout, +{stone_found} steen.")
    end_day()

def rest():
    heal = random.randint(15, 30)
    if st.session_state.inventory["kampvuur"]:
        heal = int(heal * 1.5)  # Beter herstel bij kampvuur
    st.session_state.health = min(100, st.session_state.health + heal)
    st.session_state.message = f"🛏️ Je rustte en herstelde {heal} gezondheid."
    st.session_state.logboek.append(f"Rust: +{heal} gezondheid.")
    end_day()

def explore():
    chance = random.random()
    if chance < 0.3:
        loot = random.randint(15, 40)
        st.session_state.food += loot
        st.session_state.water += loot
        st.session_state.message = f"🧭 Je verkende de omgeving en vond {loot} voedsel en {loot} water!"
        st.session_state.logboek.append(f"Verkennen: +{loot} voedsel en water.")
    elif chance < 0.6:
        base_dmg = random.randint(10, 35)
        dmg = base_dmg
        if st.session_state.inventory["speer"]:
            dmg = int(dmg / 2)
        st.session_state.health -= dmg
        st.session_state.message = f"🧭 Tijdens het verkennen werd je aangevallen en verloor je {dmg} gezondheid."
        st.session_state.logboek.append(f"Verkennen aanval: -{dmg} gezondheid.")
    else:
        treasure = random.choice(["goud", "edelstenen", "extra voedsel", "kampvuur"])
        if treasure == "kampvuur":
            st.session_state.inventory["kampvuur"] = True
            st.session_state.message = f"🏕️ Je vond materialen voor een kampvuur! Je kan nu beter rusten en vlees koken."
            st.session_state.logboek.append("Verkennen: kampvuur gevonden.")
        else:
            bonus = 30
            st.session_state.food += bonus
            st.session_state.water += bonus
            st.session_state.message = f"🧭 Je vond een voorraad {treasure}! +{bonus} eten en water."
            st.session_state.logboek.append(f"Verkennen: voorraad {treasure} gevonden.")

    end_day()

# -----------------------------
# CRAFTING
# -----------------------------
def craft(item):
    if item == "kampvuur":
        if st.session_state.wood >= 5 and st.session_state.stone >= 3:
            st.session_state.wood -= 5
            st.session_state.stone -= 3
            if not st.session_state.inventory["kampvuur"]:
                st.session_state.inventory["kampvuur"] = True
                st.session_state.message = "🔥 Je hebt een kampvuur gemaakt! Je kan nu vlees koken en rusten gaat beter."
                st.session_state.logboek.append("Gemaakt: kampvuur.")
            else:
                st.session_state.message = "Je hebt al een kampvuur."
        else:
            st.session_state.message = "Je hebt niet genoeg materialen om een kampvuur te maken."
    elif item == "speer":
        if st.session_state.wood >= 4 and st.session_state.stone >= 2:
            st.session_state.wood -= 4
            st.session_state.stone -= 2
            if not st.session_state.inventory["speer"]:
                st.session_state.inventory["speer"] = True
                st.session_state.message = "🔪 Je hebt een speer gemaakt! Je loopt minder risico bij aanvallen."
                st.session_state.logboek.append("Gemaakt: speer.")
            else:
                st.session_state.message = "Je hebt al een speer."
        else:
            st.session_state.message = "Je hebt niet genoeg materialen om een speer te maken."
    elif item == "waterfilter":
        if st.session_state.stone >= 5:
            st.session_state.stone -= 5
            if not st.session_state.inventory["waterfilter"]:
                st.session_state.inventory["waterfilter"] = True
                st.session_state.message = "💧 Je hebt een waterfilter gemaakt! Je wordt niet meer ziek van water."
                st.session_state.logboek.append("Gemaakt: waterfilter.")
            else:
                st.session_state.message = "Je hebt al een waterfilter."
        else:
            st.session_state.message = "Je hebt niet genoeg stenen om een waterfilter te maken."
    else:
        st.session_state.message = "Onbekend item."

# -----------------------------
# VLEES ETEN
# -----------------------------
def eat_meat(cooked=True):
    if cooked:
        if st.session_state.meat_cooked > 0:
            st.session_state.meat_cooked -= 1
            st.session_state.food += 20
            st.session_state.message = "🍖 Je at gekookt vlees en kreeg 20 voedsel."
            st.session_state.logboek.append("Gekookt vlees gegeten: +20 voedsel.")
        else:
            st.session_state.message = "Je hebt geen gekookt vlees om te eten."
    else:
        if st.session_state.meat_raw > 0:
            st.session_state.meat_raw -= 1
            st.session_state.food += 10
            # Kans op ziekte door rauw vlees
            if random.random() < 0.4:
                dmg = random.randint(10, 25)
                st.session_state.health -= dmg
                st.session_state.message = f"🍖 Je at rauw vlees maar werd ziek en verloor {dmg} gezondheid!"
                st.session_state.logboek.append(f"Rauw vlees ziekte: -{dmg} gezondheid.")
            else:
                st.session_state.message = "🍖 Je at rauw vlees en kreeg 10 voedsel."
                st.session_state.logboek.append("Rauw vlees gegeten: +10 voedsel.")
        else:
            st.session_state.message = "Je hebt geen rauw vlees om te eten."

# -----------------------------
# VLEES KOKEN
# -----------------------------
def cook_meat():
    if st.session_state.inventory["kampvuur"]:
        if st.session_state.meat_raw > 0:
            st.session_state.meat_raw -= 1
            st.session_state.meat_cooked += 1
            st.session_state.message = "🔥 Je hebt rauw vlees gekookt tot gekookt vlees."
            st.session_state.logboek.append("Vlees gekookt.")
        else:
            st.session_state.message = "Je hebt geen rauw vlees om te koken."
    else:
        st.session_state.message = "Je hebt geen kampvuur om vlees te koken."

# -----------------------------
# START UI
# -----------------------------
st.title("🌲 Survival Simulatie")

st.write(f"**Dag:** {st.session_state.days}")
st.write(f"**Gezondheid:** {st.session_state.health}")
st.write(f"**Eten:** {st.session_state.food}")
st.write(f"**Water:** {st.session_state.water}")
st.write(f"**Hout:** {st.session_state.wood}")
st.write(f"**Steen:** {st.session_state.stone}")
st.write(f"**Rauw vlees:** {st.session_state.meat_raw}")
st.write(f"**Gekookt vlees:** {st.session_state.meat_cooked}")

st.write("**Gemaakt:** " + ", ".join([item for item, done in st.session_state.inventory.items() if done]) or "Nog niets")

st.write("---")

# ---- Acties ----
if st.session_state.alive:
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Eten zoeken"):
            if not st.session_state.action_taken:
                st.session_state.last_action = "eten zoeken"
                search_food()
                st.session_state.action_taken = True

        if st.button("Water halen"):
            if not st.session_state.action_taken:
                st.session_state.last_action = "water halen"
                collect_water()
                st.session_state.action_taken = True

        if st.button("Materialen verzamelen"):
            if not st.session_state.action_taken:
                st.session_state.last_action = "materialen verzamelen"
                gather_materials()
                st.session_state.action_taken = True

    with col2:
        if st.button("Rust nemen"):
            if not st.session_state.action_taken:
                st.session_state.last_action = "rusten"
                rest()
                st.session_state.action_taken = True

        if st.button("Omgeving verkennen"):
            if not st.session_state.action_taken:
                st.session_state.last_action = "verkennen"
                explore()
                st.session_state.action_taken = True

    with col3:
        st.subheader("Craften")
        if st.button("Kampvuur (5 hout, 3 steen)"):
            craft("kampvuur")
        if st.button("Speer (4 hout, 2 steen)"):
            craft("speer")
        if st.button("Waterfilter (5 steen)"):
            craft("waterfilter")

        st.subheader("Vlees")
        if st.button("Kook vlees"):
            cook_meat()
        if st.button("Eet rauw vlees"):
            eat_meat(cooked=False)
        if st.button("Eet gekookt vlees"):
            eat_meat(cooked=True)

else:
    st.write("💀 Je bent overleden.")
    st.write(f"Je hebt {st.session_state.days} dagen overleefd.")
    highscore = load_highscore()
    st.write(f"Beste score ooit: {highscore['best_days']} dagen.")

    if st.button("Opnieuw beginnen"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()

st.write("---")

# -----------------------------
# LOGBOEK
# -----------------------------
with st.expander("📖 Bekijk logboek van gebeurtenissen"):
    for line in st.session_state.logboek[-20:]:
        st.write(line)

# -----------------------------
# GRAFIEKEN
# -----------------------------
with st.expander("📊 Statistieken"):
    days = list(range(1, st.session_state.days+1))
    if days:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(days, st.session_state.health_history, label="Gezondheid")
        ax.plot(days, st.session_state.food_history, label="Eten")
        ax.plot(days, st.session_state.water_history, label="Water")
        ax.set_xlabel("Dag")
        ax.set_ylabel("Waarde")
        ax.set_title("Overlevingsstatistieken")
        ax.legend()
        st.pyplot(fig)
    else:
        st.write("Speel een dag om statistieken te zien.")

