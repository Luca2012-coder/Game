import streamlit as st
import random
import matplotlib.pyplot as plt

st.set_page_config(page_title="Survival Simulator", layout="wide")

# --- INITIALISATIE ---
if "health" not in st.session_state:
    st.session_state.health = 100
if "food" not in st.session_state:
    st.session_state.food = 20
if "wood" not in st.session_state:
    st.session_state.wood = 0
if "stone" not in st.session_state:
    st.session_state.stone = 0
if "weapon" not in st.session_state:
    st.session_state.weapon = None
if "days" not in st.session_state:
    st.session_state.days = 1
if "record_days" not in st.session_state:
    st.session_state.record_days = 1
if "location" not in st.session_state:
    st.session_state.location = "Startgebied"
if "health_history" not in st.session_state:
    st.session_state.health_history = [100]
if "food_history" not in st.session_state:
    st.session_state.food_history = [20]
if "message" not in st.session_state:
    st.session_state.message = ""
if "alive" not in st.session_state:
    st.session_state.alive = True

# --- LANDEN MET BONUS ---
locations = {
    "Startgebied": {"food_bonus": 0, "loot_bonus": 0},
    "Fruiteiland": {"food_bonus": 10, "loot_bonus": 5},
    "Mijnvallei": {"food_bonus": 0, "loot_bonus": 15},
}

# --- DAG UPDATEN ---
def next_day():
    st.session_state.days += 1
    if st.session_state.days > st.session_state.record_days:
        st.session_state.record_days = st.session_state.days
    st.session_state.food -= 5
    if st.session_state.food < 0:
        st.session_state.food = 0
        st.session_state.health -= 10
    st.session_state.health_history.append(st.session_state.health)
    st.session_state.food_history.append(st.session_state.food)
    if st.session_state.health <= 0:
        st.session_state.alive = False
        st.session_state.message = f"Je bent gestorven na {st.session_state.days} dagen!"

# --- ACTIES ---
def explore():
    bonus = locations[st.session_state.location]
    found_food = random.randint(5, 15) + bonus["food_bonus"]
    found_wood = random.randint(0, 5) + bonus["loot_bonus"] // 5
    found_stone = random.randint(0, 3) + bonus["loot_bonus"] // 10
    st.session_state.food += found_food
    st.session_state.wood += found_wood
    st.session_state.stone += found_stone
    st.session_state.message = f"Je vond {found_food} voedsel, {found_wood} hout en {found_stone} steen."

    # Kans om nieuw land te ontdekken
    if random.random() < 0.2:
        new_place = random.choice(list(locations.keys())[1:])
        st.session_state.location = new_place
        st.session_state.message += f" Je ontdekte een nieuw gebied: {new_place}!"

    next_day()

def rest():
    heal = random.randint(5, 15)
    st.session_state.health += heal
    if st.session_state.health > 100:
        st.session_state.health = 100
    st.session_state.message = f"Je rustte uit en herstelde {heal} gezondheid."
    next_day()

def fight():
    if not st.session_state.weapon:
        damage = random.randint(20, 40)
        st.session_state.health -= damage
        st.session_state.message = f"Je had geen wapen en kreeg {damage} schade!"
    else:
        loot = random.randint(10, 30)
        st.session_state.food += loot
        st.session_state.message = f"Je vocht met je {st.session_state.weapon} en won! Je vond {loot} voedsel."
    next_day()

def craft_weapon():
    if st.session_state.wood >= 5 and st.session_state.stone >= 3:
        st.session_state.weapon = "Speer"
        st.session_state.wood -= 5
        st.session_state.stone -= 3
        st.session_state.message = "Je hebt een speer gemaakt!"
    else:
        st.session_state.message = "Niet genoeg materialen om een wapen te maken."

# --- RESET BIJ DOOD ---
def reset_game():
    st.session_state.health = 100
    st.session_state.food = 20
    st.session_state.wood = 0
    st.session_state.stone = 0
    st.session_state.weapon = None
    st.session_state.days = 1
    st.session_state.location = "Startgebied"
    st.session_state.health_history = [100]
    st.session_state.food_history = [20]
    st.session_state.alive = True
    st.session_state.message = ""

# --- INTERFACE ---
st.title("🌲 Survival Simulator")
st.write(f"**Dag {st.session_state.days}** - Locatie: {st.session_state.location}")
st.write(f"**Record: {st.session_state.record_days} dagen overleefd**")

col1, col2 = st.columns([2,1])

with col1:
    if st.session_state.alive:
        st.subheader("Acties")
        if st.button("🔍 Verkennen"):
            explore()
        if st.button("😴 Rusten"):
            rest()
        if st.button("⚔️ Vechten"):
            fight()
        if st.button("🛠️ Wapen maken"):
            craft_weapon()
    else:
        st.subheader("Je bent dood!")
        if st.button("🔄 Opnieuw beginnen"):
            reset_game()

    st.write(st.session_state.message)

    # Grafiek
    fig, ax = plt.subplots()
    days = list(range(1, len(st.session_state.health_history)+1))
    ax.plot(days, st.session_state.health_history, label="Gezondheid")
    ax.plot(days, st.session_state.food_history, label="Voedsel")
    ax.set_xlabel("Dag")
    ax.set_ylabel("Waarde")
    ax.legend()
    st.pyplot(fig)

with col2:
    st.subheader("Inventaris")
    st.write(f"❤️ Gezondheid: {st.session_state.health}")
    st.write(f"🍖 Voedsel: {st.session_state.food}")
    st.write(f"🪵 Hout: {st.session_state.wood}")
    st.write(f"🪨 Steen: {st.session_state.stone}")
    st.write(f"⚔️ Wapen: {st.session_state.weapon if st.session_state.weapon else 'Geen'}")
