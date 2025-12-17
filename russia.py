import streamlit as st
import random

# --- Initialisatie ---
if "player" not in st.session_state:
    st.session_state.player = {
        "naam": "",
        "leeftijd": 0,
        "geld": 1000,
        "gezondheid": 100,
        "geluk": 50,
        "slimheid": 50,
        "leven_actief": False
    }

# --- Begin van het spel ---
st.title("Mini-BitLife in Streamlit")

if not st.session_state.player["leven_actief"]:
    naam = st.text_input("Wat is je naam?")
    if st.button("Start leven") and naam:
        st.session_state.player["naam"] = naam
        st.session_state.player["leeftijd"] = 0
        st.session_state.player["geld"] = 1000
        st.session_state.player["gezondheid"] = 100
        st.session_state.player["geluk"] = 50
        st.session_state.player["slimheid"] = 50
        st.session_state.player["leven_actief"] = True
        st.experimental_rerun()

# --- Spel logica per jaar ---
if st.session_state.player["leven_actief"]:
    speler = st.session_state.player
    st.subheader(f"Leeftijd: {speler['leeftijd']}")
    st.write(f"Geld: ${speler['geld']}")
    st.write(f"Gezondheid: {speler['gezondheid']}")
    st.write(f"Geluk: {speler['geluk']}")
    st.write(f"Slimheid: {speler['slimheid']}")

    st.markdown("### Kies je actie voor dit jaar:")
    keuze = st.radio("", ["Studeren", "Werken", "Sporten", "Uitgaan", "Rust nemen"])

    if st.button("Volgend jaar"):
        speler["leeftijd"] += 1

        # Actie effecten
        if keuze == "Studeren":
            speler["slimheid"] += random.randint(1, 5)
            speler["geluk"] -= random.randint(0, 3)
        elif keuze == "Werken":
            inkomen = random.randint(500, 2000)
            speler["geld"] += inkomen
            speler["geluk"] -= random.randint(0, 5)
        elif keuze == "Sporten":
            speler["gezondheid"] += random.randint(5, 10)
            speler["geluk"] += random.randint(1, 3)
        elif keuze == "Uitgaan":
            speler["geluk"] += random.randint(5, 10)
            speler["geld"] -= random.randint(50, 200)
            speler["gezondheid"] -= random.randint(1, 5)
        elif keuze == "Rust nemen":
            speler["gezondheid"] += random.randint(1, 5)
            speler["geluk"] += random.randint(1, 5)

        # Willekeurige gebeurtenissen
        gebeurtenis = random.randint(1, 10)
        if gebeurtenis == 1:
            verlies = random.randint(50, 200)
            speler["geld"] -= verlies
            st.warning(f"Oeps! Je hebt ${verlies} verloren aan een ongeluk.")
        elif gebeurtenis == 2:
            winst = random.randint(100, 500)
            speler["geld"] += winst
            st.success(f"Geluk! Je hebt ${winst} gewonnen.")

        # Gezondheid check
        if speler["gezondheid"] <= 0 or speler["leeftijd"] > 100:
            st.session_state.player["leven_actief"] = False
            st.error(f"{speler['naam']} is overleden op leeftijd {speler['leeftijd']}.")
        st.experimental_rerun()
