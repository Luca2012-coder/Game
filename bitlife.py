import streamlit as st
import random

# --- Initialisatie van de speler ---
if "player" not in st.session_state:
    st.session_state.player = {
        "naam": "",
        "leeftijd": 0,
        "geld": 1000,
        "gezondheid": 100,
        "geluk": 50,
        "slimheid": 50,
        "relaties": [],
        "leven_actief": False
    }

# --- Functie om stats te tonen ---
def toon_stats(speler):
    st.subheader(f"Leeftijd: {speler['leeftijd']}")
    st.progress(speler['gezondheid']/100)
    st.write(f"Geld: ${speler['geld']}")
    st.progress(speler['geluk']/100)
    st.write(f"Geluk: {speler['geluk']}")
    st.progress(speler['slimheid']/100)
    st.write(f"Slimheid: {speler['slimheid']}")
    st.write(f"Relaties: {', '.join(speler['relaties']) if speler['relaties'] else 'Geen'}")

# --- Begin scherm ---
st.title("BitLife-achtige Game in Streamlit")

if not st.session_state.player["leven_actief"]:
    naam = st.text_input("Wat is je naam?")
    if st.button("Start leven") and naam:
        st.session_state.player["naam"] = naam
        st.session_state.player["leeftijd"] = 0
        st.session_state.player["geld"] = 1000
        st.session_state.player["gezondheid"] = 100
        st.session_state.player["geluk"] = 50
        st.session_state.player["slimheid"] = 50
        st.session_state.player["relaties"] = []
        st.session_state.player["leven_actief"] = True
        st.experimental_rerun()

# --- Spel logica ---
if st.session_state.player["leven_actief"]:
    speler = st.session_state.player
    toon_stats(speler)

    st.markdown("### Kies je actie voor dit jaar:")
    actie = st.radio("", ["Studeren", "Werken", "Sporten", "Uitgaan", "Rust nemen", "Nieuwe relatie zoeken"])

    if st.button("Volgend jaar"):
        speler["leeftijd"] += 1

        # Actie effecten
        if actie == "Studeren":
            speler["slimheid"] += random.randint(1, 5)
            speler["geluk"] -= random.randint(0, 3)
        elif actie == "Werken":
            inkomen = random.randint(500, 2000)
            speler["geld"] += inkomen
            speler["geluk"] -= random.randint(0, 5)
        elif actie == "Sporten":
            speler["gezondheid"] += random.randint(5, 10)
            speler["geluk"] += random.randint(1, 3)
        elif actie == "Uitgaan":
            speler["geluk"] += random.randint(5, 10)
            speler["geld"] -= random.randint(50, 200)
            speler["gezondheid"] -= random.randint(1, 5)
        elif actie == "Rust nemen":
            speler["gezondheid"] += random.randint(1, 5)
            speler["geluk"] += random.randint(1, 5)
        elif actie == "Nieuwe relatie zoeken":
            kans = random.randint(1, 3)
            if kans == 1:
                naam_relatie = f"Partner{speler['leeftijd']}"
                speler["relaties"].append(naam_relatie)
                st.success(f"Gefeliciteerd! Je hebt een nieuwe relatie met {naam_relatie}.")
            else:
                st.warning("Geen nieuwe relatie dit jaar.")

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
        elif gebeurtenis == 3:
            ziekte = random.randint(5, 20)
            speler["gezondheid"] -= ziekte
            st.error(f"Helaas! Je bent ziek geworden en verliest {ziekte} gezondheid.")

        # Grenzen voor stats
        speler["gezondheid"] = min(max(speler["gezondheid"], 0), 100)
        speler["geluk"] = min(max(speler["geluk"], 0), 100)
        speler["slimheid"] = min(max(speler["slimheid"], 0), 100)

        # Controleer of speler overleden is
        if speler["gezondheid"] <= 0 or speler["leeftijd"] >= 100:
            st.session_state.player["leven_actief"] = False
            st.error(f"{speler['naam']} is overleden op leeftijd {speler['leeftijd']}.")
        st.experimental_rerun()
