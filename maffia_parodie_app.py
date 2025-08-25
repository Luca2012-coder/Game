
import random
import time
from datetime import datetime
import streamlit as st
import pandas as pd

st.set_page_config(page_title="La Famiglia – Parodie Portaal", page_icon="🍝", layout="wide")

# -------------------------
# Session State Init
# -------------------------
if "sollicitanten" not in st.session_state:
    st.session_state["sollicitanten"] = []  # list of dicts: {naam, leeftijd, status, score, tijd}
if "targets_score" not in st.session_state:
    st.session_state["targets_score"] = 0
if "targets_ammo" not in st.session_state:
    st.session_state["targets_ammo"] = 12
if "targets_start" not in st.session_state:
    st.session_state["targets_start"] = None
if "targets_grid" not in st.session_state:
    st.session_state["targets_grid"] = (6, 6)  # rows, cols
if "targets_pos" not in st.session_state:
    st.session_state["targets_pos"] = (random.randrange(6), random.randrange(6))
if "targets_running" not in st.session_state:
    st.session_state["targets_running"] = False

# -------------------------
# Helper Functions
# -------------------------
def beoordeling_score(antwoorden):
    score = 0

    # Politietest (omschreven als 'lastige vragen' om het luchtig te houden)
    if antwoorden.get("politie") == "Ik blijf rustig, geef geen onnodige info en verwijs netjes door.":
        score += 2
    elif antwoorden.get("politie") == "Ik ga in discussie en deel te veel details.":
        score -= 2
    elif antwoorden.get("politie") == "Ik raak in paniek en zeg van alles door elkaar.":
        score -= 1
    else:
        score += 1  # "Ik bied espresso aan en vraag naar de aanleiding."

    # Geld
    if antwoorden.get("geld") == "Ik tel, registreer en lever het verantwoord in.":
        score += 2
    elif antwoorden.get("geld") == "Ik investeer slim met toestemming.":
        score += 1
    elif antwoorden.get("geld") == "Ik neem een 'beheerfee' zonder te melden.":
        score -= 2
    else:
        score -= 1  # "Ik doneer het" (grappig maar niet volgens opdracht)

    # Rijbewijs
    if antwoorden.get("rijbewijs"):
        score += 1

    # Loyaliteit
    if antwoorden.get("loyaal"):
        score += 3
    else:
        score -= 3

    # Ervaringen / specialiteiten (parodie)
    specials = antwoorden.get("specialiteiten", [])
    if "Creatieve boekhouding (legaal-ish) 📚" in specials:
        score += 1
    if "Pizzabakken 🍕" in specials:
        score += 1
    if "Discretie & zwijgplicht 🤐" in specials:
        score += 1
    if "Netwerken & deals sluiten 🤝" in specials:
        score += 1
    if "Oma’s ‘helpen’ met technologie 👵 (foei!)" in specials:
        score -= 1

    # Rekentest
    if antwoorden.get("rekensom") == 40:
        score += 1
    else:
        score -= 1

    # Extra mini-quiz (pasta-etiquette)
    if antwoorden.get("pasta") == "Kip hoort niet in klassieke Italiaanse pasta.":
        score += 1
    else:
        score -= 1

    return score

def bepaal_status(score):
    # Strenger, realistisch: niet snel aangenomen
    if score >= 8:
        return "Aangenomen"
    elif score >= 5:
        return "Op proef"
    else:
        return "Afgewezen"

def reset_targets():
    st.session_state["targets_score"] = 0
    st.session_state["targets_ammo"] = 12
    st.session_state["targets_start"] = time.time()
    st.session_state["targets_pos"] = (
        random.randrange(st.session_state["targets_grid"][0]),
        random.randrange(st.session_state["targets_grid"][1]),
    )
    st.session_state["targets_running"] = True

def stop_targets():
    st.session_state["targets_running"] = False

def tijd_over():
    if not st.session_state["targets_running"] or st.session_state["targets_start"] is None:
        return 30
    elapsed = time.time() - st.session_state["targets_start"]
    left = max(0, 30 - int(elapsed))
    if left == 0:
        stop_targets()
    return left

def verplaats_target():
    r, c = st.session_state["targets_grid"]
    st.session_state["targets_pos"] = (random.randrange(r), random.randrange(c))

# -------------------------
# UI – Tabs
# -------------------------
tab1, tab2, tab3 = st.tabs(["📝 Sollicitatie", "🎯 Targets (speeltje)", "📋 Overzicht"])

with tab1:
    st.title("🍝 La Famiglia – Sollicitatie (Parodie)")
    st.caption("Luchtig roleplay, geen echte criminele instructies. Fouten zijn **geen** ‘game over’, maar geven gewoon een lagere score.")

    st.header("👤 Persoonlijke Gegevens")
    naam = st.text_input("Naam")
    leeftijd = st.number_input("Leeftijd", min_value=16, max_value=120, step=1, value=18)

    st.header("🧰 ‘Specialiteiten’ (parodie)")
    specialiteiten = st.multiselect(
        "Kies wat bij je past (tong-in-cheek):",
        [
            "Pizzabakken 🍕",
            "Chauffeur & logistiek 🚚",
            "Beveiliging / portier 💪",
            "Netwerken & deals sluiten 🤝",
            "Creatieve boekhouding (legaal-ish) 📚",
            "PR & reputatiemanagement 🗞️",
            "Discretie & zwijgplicht 🤐",
            "Spaghetti chef (nonna-approved) 👵🍝",
            "Pokerface & onderhandelen ♠️",
            "Oma’s ‘helpen’ met technologie 👵 (foei!)",
            "Wasmachine expert (wit op 40°C) 🧼",
            "Mystery shopper (veldwerk) 🕵️",
        ]
    )

    st.header("🧪 Testjes")
    politie = st.radio(
        "Iemand met autoriteit stelt lastige vragen. Wat doe je?",
        [
            "Ik blijf rustig, geef geen onnodige info en verwijs netjes door.",
            "Ik bied espresso aan en vraag naar de aanleiding.",
            "Ik ga in discussie en deel te veel details.",
            "Ik raak in paniek en zeg van alles door elkaar.",
        ]
    )

    geld = st.radio(
        "Je bewaart een envelop met €50.000 voor de organisatie. Wat doe je?",
        [
            "Ik tel, registreer en lever het verantwoord in.",
            "Ik investeer slim met toestemming.",
            "Ik neem een 'beheerfee' zonder te melden.",
            "Ik doneer het aan een goed doel.",
        ]
    )

    rijbewijs = st.checkbox("Ik heb een geldig rijbewijs.")
    loyaal = st.checkbox("Ik blijf loyaal aan het team (professioneel & discreet).")

    rekensom = st.number_input("Rekentest: 17 + 23 = ?", min_value=0, max_value=200, step=1)
    pasta = st.radio(
        "Pasta-etiquette (Italië 101):",
        [
            "Kip hoort niet in klassieke Italiaanse pasta.",
            "Room in carbonara is altijd goed.",
            "Spaghetti breek je eerst doormidden voor het koken.",
        ]
    )

    if st.button("📤 Verstuur sollicitatie"):
        antwoorden = {
            "politie": politie,
            "geld": geld,
            "rijbewijs": rijbewijs,
            "loyaal": loyaal,
            "specialiteiten": specialiteiten,
            "rekensom": rekensom,
            "pasta": pasta,
        }
        score = beoordeling_score(antwoorden)
        status = bepaal_status(score)

        tijd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state["sollicitanten"].append(
            {"naam": naam or "Onbekend", "leeftijd": int(leeftijd), "status": status, "score": score, "tijd": tijd}
        )

        st.subheader("🔎 Uitslag")
        if status == "Aangenomen":
            st.success(f"Gefeliciteerd {naam or 'kandidaat'}! Je bent **{status}**. (Score: {score})")
        elif status == "Op proef":
            st.warning(f"{naam or 'kandidaat'}, je bent **{status}**. Laat nog even zien wat je kunt. (Score: {score})")
        else:
            st.error(f"Helaas {naam or 'kandidaat'}, je bent **{status}**. Probeer het later opnieuw. (Score: {score})")

with tab2:
    st.title("🎯 Targets – Nerf/Waterballon Galerij (Parodie)")
    st.caption("Klik op het doelwit 🎯 om punten te scoren. Geen geweld; gewoon een reflex-spelletje.")

    colA, colB, colC = st.columns([1, 1, 2])
    with colA:
        if st.button("▶️ Start/Reset (30s)"):
            reset_targets()
    with colB:
        if st.button("⏹️ Stop"):
            stop_targets()
    with colC:
        st.metric("⏱️ Tijd over (s)", tijd_over())
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Score", st.session_state["targets_score"])
    with col2:
        st.metric("🔫 Ammo", st.session_state["targets_ammo"])
    with col3:
        status_txt = "Bezig" if st.session_state["targets_running"] else "Gepauzeerd"
        st.metric("Status", status_txt)

    rows, cols = st.session_state["targets_grid"]
    tr, tc = st.session_state["targets_pos"]

    def klik(r, c):
        if not st.session_state["targets_running"]:
            return
        if st.session_state["targets_ammo"] <= 0:
            return
        # "Schot" gelost
        st.session_state["targets_ammo"] -= 1
        if (r, c) == (tr, tc):
            st.session_state["targets_score"] += 1
            verplaats_target()
        # auto-stop bij tijd op
        tijd_over()

    # Grid met knoppen
    for r in range(rows):
        cols_container = st.columns(cols)
        for c in range(cols):
            with cols_container[c]:
                label = "🎯" if (r, c) == (tr, tc) else " "
                st.button(label, key=f"btn_{r}_{c}", on_click=klik, args=(r, c))

with tab3:
    st.title("📋 Overzicht sollicitanten")
    if st.session_state["sollicitanten"]:
        df = pd.DataFrame(st.session_state["sollicitanten"])
        st.dataframe(df, use_container_width=True)
        # Optioneel: export
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv, file_name="sollicitanten.csv", mime="text/csv")
    else:
        st.info("Nog geen sollicitanten ingediend.")

st.sidebar.title("🍷 La Famiglia (Parodie)")
st.sidebar.markdown(
    "- Dit is een humoristische roleplay-app.\n"
    "- Geen echte criminele instructies of geweld.\n"
    "- Speel het als een party-game!"
)
