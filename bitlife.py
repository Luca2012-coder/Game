import streamlit as st
import random

st.set_page_config(page_title="Mini BitLife", page_icon="🧬")

# =====================
# SESSION STATE
# =====================
if 'leeftijd' not in st.session_state:
    st.session_state.leeftijd = 0
    st.session_state.maand = 1
    st.session_state.geld = 1000
    st.session_state.geluk = 50
    st.session_state.gezondheid = 50
    st.session_state.studiejaren = 0
    st.session_state.max_leeftijd = random.randint(80, 120)
    st.session_state.dood = False

# =====================
# KEUZES
# =====================
keuzes = [
    "Werken",
    "Studeren",
    "Sporten",
    "Feesten",
    "Vrijwilligerswerk",
    "Sparen",
    "Riskante actie",
    "Relatie beginnen",
    "Gezond eten",
    "Huis kopen",
    "Reizen",
    "Niks doen"
]

# =====================
# LEVENSKEUZE FUNCTIE
# =====================
def levenskeuze(keuze):
    # ---- WERKEN ----
    if keuze == "Werken":
        if st.session_state.leeftijd < 21:
            st.warning("❌ Je bent te jong om te werken!")
            return
        salaris = (
            500 +
            st.session_state.studiejaren * 200 +
            st.session_state.geluk * 5
        )
        st.session_state.geld += salaris
        st.session_state.geluk -= 5
        st.success(f"💼 Je verdiende €{salaris}")

    # ---- STUDEREN ----
    elif keuze == "Studeren":
        st.session_state.studiejaren += 1
        st.session_state.geluk += 3
        st.session_state.geld -= 200
        st.success("📚 Je hebt een jaar gestudeerd!")

    elif keuze == "Sporten":
        st.session_state.gezondheid += 5
        st.session_state.geld -= 50

    elif keuze == "Feesten":
        st.session_state.geluk += 10
        st.session_state.gezondheid -= 5

    elif keuze == "Vrijwilligerswerk":
        st.session_state.geluk += 5

    elif keuze == "Sparen":
        st.session_state.geld += 200
        st.session_state.geluk -= 3

    elif keuze == "Riskante actie":
        st.session_state.geld += random.randint(-300, 1000)
        st.session_state.gezondheid -= random.randint(0, 20)

    elif keuze == "Relatie beginnen":
        st.session_state.geluk += 8
        st.session_state.geld -= random.randint(0, 150)

    elif keuze == "Gezond eten":
        st.session_state.gezondheid += 5
        st.session_state.geld -= 50

    elif keuze == "Huis kopen":
        st.session_state.geld -= 500
        st.session_state.geluk += 10

    elif keuze == "Reizen":
        st.session_state.geld -= 300
        st.session_state.geluk += 10

    elif keuze == "Niks doen":
        st.session_state.geluk -= 5
        st.session_state.gezondheid -= 5

    # Grenzen
    st.session_state.gezondheid = max(0, min(100, st.session_state.gezondheid))
    st.session_state.geluk = max(0, min(100, st.session_state.geluk))
    st.session_state.geld = max(0, st.session_state.geld)

# =====================
# DOOD
# =====================
def creatieve_dood():
    doods = [
        f"Je viel rustig in slaap en werd {st.session_state.leeftijd} jaar oud.",
        f"Je stierf rijk maar moe op {st.session_state.leeftijd} jaar.",
        f"Je struikelde over je eigen succes op {st.session_state.leeftijd} jaar.",
        f"Je werd een legende en overleed op {st.session_state.leeftijd} jaar."
    ]
    st.session_state.dood = True
    st.error("💀 Je bent overleden")
    st.write(random.choice(doods))

# =====================
# UI
# =====================
st.title("🧬 Mini BitLife")

st.write(
    f"🎂 Leeftijd: {st.session_state.leeftijd} | "
    f"💰 Geld: €{st.session_state.geld} | "
    f"😊 Geluk: {st.session_state.geluk} | "
    f"❤️ Gezondheid: {st.session_state.gezondheid} | "
    f"📚 Studie: {st.session_state.studiejaren} jaar"
)

st.write(f"📆 Maand {st.session_state.maand} van jaar {st.session_state.leeftijd + 1}")

# =====================
# SPELEN
# =====================
if not st.session_state.dood:
    keuze = st.radio("Wat wil je doen?", keuzes)

    if st.button("Bevestig keuze"):
        levenskeuze(keuze)
        st.session_state.maand += 1

        if st.session_state.maand > 12:
            st.session_state.maand = 1
            st.session_state.leeftijd += 1

        if (
            st.session_state.gezondheid <= 0 or
            st.session_state.leeftijd >= st.session_state.max_leeftijd
        ):
            creatieve_dood()

        st.rerun()
