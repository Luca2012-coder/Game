import streamlit as st
import random
import matplotlib.pyplot as plt

# --- Initialisatie ---
if "initialized" not in st.session_state:
    st.session_state.health = 100
    st.session_state.food = 20
    st.session_state.water = 20
    st.session_state.wood = 0
    st.session_state.stone = 0
    st.session_state.meat_raw = 0
    st.session_state.meat_cooked = 0
    st.session_state.inventory = {"kampvuur": False, "speer": False, "waterfilter": False}
    st.session_state.days = 1
    st.session_state.message = "Welkom bij Survival Simulatie!"
    st.session_state.action_taken = False
    st.session_state.health_history = []
    st.session_state.food_history = []
    st.session_state.water_history = []
    st.session_state.logboek = []
    st.session_state.alive = True
    st.session_state.initialized = True

def update_stats():
    st.session_state.health_history.append(st.session_state.health)
    st.session_state.food_history.append(st.session_state.food)
    st.session_state.water_history.append(st.session_state.water)

def search_food():
    food_found = random.randint(5, 15)
    bonus = random.choices([0, 5], weights=[0.8, 0.2])[0]  # 20% kans op bonus 5 voedsel
    total_food = food_found + bonus
    st.session_state.food += total_food
    st.session_state.message = f"🍎 Je vond {total_food} voedsel! (Bonus: {bonus})"
    st.session_state.logboek.append(f"Dag {st.session_state.days}: Eten gezocht, +{total_food} voedsel.")

def collect_water():
    water_found = random.randint(5, 12)
    bonus = random.choices([0, 3], weights=[0.85, 0.15])[0]
    total_water = water_found + bonus
    st.session_state.water += total_water
    st.session_state.message = f"💧 Je haalde {total_water} water! (Bonus: {bonus})"
    st.session_state.logboek.append(f"Dag {st.session_state.days}: Water gehaald, +{total_water} water.")

def gather_materials():
    wood_found = random.randint(3, 8)
    stone_found = random.randint(1, 5)
    st.session_state.wood += wood_found
    st.session_state.stone += stone_found
    st.session_state.message = f"🪵 Je verzamelde {wood_found} hout en {stone_found} steen."
    st.session_state.logboek.append(f"Dag {st.session_state.days}: Materialen verzameld, +{wood_found} hout, +{stone_found} steen.")

def rest():
    health_gain = random.randint(5, 15)
    st.session_state.health = min(100, st.session_state.health + health_gain)
    st.session_state.message = f"🛌 Je rustte uit en kreeg {health_gain} gezondheid terug."
    st.session_state.logboek.append(f"Dag {st.session_state.days}: Uitgerust, +{health_gain} gezondheid.")

def explore():
    event = random.choice(["niets", "rauw vlees", "rauw vlees", "wilde bes"])
    if event == "niets":
        st.session_state.message = "🌲 Je verkende de omgeving maar vond niets bijzonders."
        st.session_state.logboek.append(f"Dag {st.session_state.days}: Verkennen - niets gevonden.")
    elif event == "rauw vlees":
        st.session_state.meat_raw += 1
        st.session_state.message = "🦌 Je vond rauw vlees tijdens het verkennen."
        st.session_state.logboek.append(f"Dag {st.session_state.days}: Verkennen - rauw vlees gevonden.")
    elif event == "wilde bes":
        st.session_state.food += 3
        st.session_state.message = "🍇 Je vond wilde bessen en kreeg +3 voedsel."
        st.session_state.logboek.append(f"Dag {st.session_state.days}: Verkennen - wilde bessen.")

def craft(item):
    costs = {"kampvuur": {"wood":5, "stone":3}, "speer": {"wood":4, "stone":2}, "waterfilter": {"stone":5}}
    if st.session_state.inventory[item]:
        st.session_state.message = f"Je hebt al een {item}."
        return
    can_craft = all(st.session_state.get(res, 0) >= amt for res, amt in costs[item].items())
    if can_craft:
        for res, amt in costs[item].items():
            st.session_state[res] -= amt
        st.session_state.inventory[item] = True
        st.session_state.message = f"⚒️ Je hebt een {item} gemaakt!"
        st.session_state.logboek.append(f"Dag {st.session_state.days}: {item} gemaakt.")
    else:
        st.session_state.message = f"Niet genoeg materialen voor {item}."

def eat_meat(cooked=True):
    if cooked:
        if st.session_state.meat_cooked > 0:
            st.session_state.meat_cooked -= 1
            st.session_state.food += 15
            st.session_state.message = "🍖 Je at gekookt vlees en kreeg 15 voedsel."
            st.session_state.logboek.append(f"Dag {st.session_state.days}: Gekookt vlees gegeten.")
        else:
            st.session_state.message = "Je hebt geen gekookt vlees."
    else:
        if st.session_state.meat_raw > 0:
            st.session_state.meat_raw -= 1
            dmg = random.randint(5, 20)
            st.session_state.health -= dmg
            st.session_state.message = f"🍖 Je at rauw vlees en verloor {dmg} gezondheid door ziekte!"
            st.session_state.logboek.append(f"Dag {st.session_state.days}: Rauw vlees gegeten, ziekte -{dmg} gezondheid.")
        else:
            st.session_state.message = "Je hebt geen rauw vlees."

def cook_meat():
    if st.session_state.inventory["kampvuur"]:
        if st.session_state.meat_raw > 0:
            st.session_state.meat_raw -= 1
            st.session_state.meat_cooked += 1
            st.session_state.message = "🔥 Je hebt rauw vlees gekookt."
            st.session_state.logboek.append(f"Dag {st.session_state.days}: Vlees gekookt.")
        else:
            st.session_state.message = "Je hebt geen rauw vlees om te koken."
    else:
        st.session_state.message = "Je hebt geen kampvuur."

# ------------------- UI ---------------------

st.title("🌲 Survival Simulatie")

# Sidebar voor inventaris
with st.sidebar:
    st.header("📦 Inventaris")
    st.write(f"**Gezondheid:** {st.session_state.health}")
    st.write(f"**Eten:** {st.session_state.food}")
    st.write(f"**Water:** {st.session_state.water}")
    st.write(f"**Hout:** {st.session_state.wood}")
    st.write(f"**Steen:** {st.session_state.stone}")
    st.write(f"**Rauw vlees:** {st.session_state.meat_raw}")
    st.write(f"**Gekookt vlees:** {st.session_state.meat_cooked}")
    st.write("---")
    st.write("Gemaakt:")
    for item, done in st.session_state.inventory.items():
        if done:
            st.write(f"✔️ {item}")
    if not any(st.session_state.inventory.values()):
        st.write("Nog niets")

# Hoofdvenster met acties
if st.session_state.alive:
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Eten zoeken"):
            if not st.session_state.action_taken:
                search_food()
                st.session_state.action_taken = True
    with col2:
        if st.button("Water halen"):
            if not st.session_state.action_taken:
                collect_water()
                st.session_state.action_taken = True
    with col3:
        if st.button("Materialen verzamelen"):
            if not st.session_state.action_taken:
                gather_materials()
                st.session_state.action_taken = True

    col4, col5 = st.columns(2)
    with col4:
        if st.button("Rust nemen"):
            if not st.session_state.action_taken:
                rest()
                st.session_state.action_taken = True
    with col5:
        if st.button("Omgeving verkennen"):
            if not st.session_state.action_taken:
                explore()
                st.session_state.action_taken = True

    st.write("---")
    st.subheader("Craften")
    craft_col1, craft_col2, craft_col3 = st.columns(3)
    with craft_col1:
        if st.button("Kampvuur (5 hout, 3 steen)"):
            craft("kampvuur")
    with craft_col2:
        if st.button("Speer (4 hout, 2 steen)"):
            craft("speer")
    with craft_col3:
        if st.button("Waterfilter (5 steen)"):
            craft("waterfilter")

    st.write("---")
    st.subheader("Vlees")
    meat_col1, meat_col2 = st.columns(2)
    with meat_col1:
        if st.button("Kook vlees"):
            cook_meat()
    with meat_col2:
        if st.button("Eet rauw vlees"):
            eat_meat(cooked=False)
        if st.button("Eet gekookt vlees"):
            eat_meat(cooked=True)

    # Toon de laatste actie / melding
    st.info(st.session_state.message)

else:
    st.error("💀 Je bent overleden.")
    st.write(f"Je hebt {st.session_state.days} dagen overleefd.")
    if st.button("Opnieuw beginnen"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()

# Logboek en grafieken
with st.expander("📖 Logboek"):
    for line in st.session_state.logboek[-20:]:
        st.write(line)

with st.expander("📊 Statistieken"):
    days = list(range(1, st.session_state.days+1))
    if days:
        fig, ax = plt.subplots(figsize=(8,4))
        ax.plot(days, st.session_state.health_history, label="Gezondheid")
        ax.plot(days, st.session_state.food_history, label="Eten")
        ax.plot(days, st.session_state.water_history, label="Water")
        ax.set_xlabel("Dag")
        ax.set_ylabel("Waarde")
        ax.legend()
        st.pyplot(fig)
    else:
        st.write("Speel een dag om statistieken te zien.")
