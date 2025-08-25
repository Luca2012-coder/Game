import streamlit as st

st.set_page_config(page_title="Maffia Sollicitatie", page_icon="💼", layout="centered")

# Init opslag van sollicitanten
if "sollicitanten" not in st.session_state:
    st.session_state["sollicitanten"] = []

st.title("💼 Maffia Sollicitatie Portaal")
st.write("Welkom bij de officiële sollicitatie van *La Famiglia*. "
         "Beantwoord de vragen eerlijk. "
         "Wees gewaarschuwd... verkeerde antwoorden kunnen gevolgen hebben. 😉")

st.header("👤 Persoonlijke Gegevens")
naam = st.text_input("Wat is je naam?")
leeftijd = st.number_input("Wat is je leeftijd?", min_value=16, max_value=120, step=1)
specialiteit = st.text_input("Wat is je 'specialiteit'? (bijv. geld tellen, pokerface, zwijgplicht)")

st.header("🕵️ Achtergrondcheck")
ervaring = st.multiselect(
    "Welke 'ervaringen' heb je?",
    [
        "Transport van waardevolle koffers",
        "Winnaar van pokeravonden",
        "Bekend met de Italiaanse keuken",
        "Geheimen bewaren",
        "Goede alibi's verzinnen",
        "Rijden zonder papieren"
    ]
)

st.header("🧪 Testjes")

st.subheader("1. De Politietest 🚔")
politie = st.radio(
    "De politie klopt bij je aan. Wat doe je?",
    [
        "Ik doe alsof ik niet thuis ben",
        "Ik bied ze espresso aan en laat ze binnen",
        "Ik zeg: 'Ik weet van niks' en blijf daarbij",
        "Ik vertel alles meteen"
    ]
)

st.subheader("2. Geldmanagement 💰")
geld = st.radio(
    "Je krijgt €50.000 cash om te bewaren. Wat doe je?",
    [
        "Ik geef het netjes aan de baas terug",
        "Ik steek de helft in eigen zak",
        "Ik investeer het slim en maak winst",
        "Ik doneer het aan een goed doel 🤔"
    ]
)

st.subheader("3. Rijtest 🚗")
rijbewijs = st.checkbox("Ik heb een rijbewijs (of iets wat erop lijkt).")

st.subheader("4. Loyauteit 🤌")
loyaal = st.checkbox("Ik zweer eeuwige trouw aan La Famiglia.")

st.subheader("5. Rekensom 🧮")
antwoord = st.number_input("Hoeveel is 17 + 23?", min_value=0, max_value=100, step=1)

# Eindresultaat
if st.button("📜 Verstuur sollicitatie"):
    st.subheader("🔎 Uitslag van je sollicitatie:")

    score = 0

    # Politietest
    if politie == "Ik zeg: 'Ik weet van niks' en blijf daarbij":
        score += 2
    elif politie == "Ik doe alsof ik niet thuis ben":
        score += 1
    elif politie == "Ik vertel alles meteen":
        score -= 3

    # Geldtest
    if geld == "Ik geef het netjes aan de baas terug":
        score += 2
    elif geld == "Ik steek de helft in eigen zak":
        score -= 2
    elif geld == "Ik investeer het slim en maak winst":
        score += 1
    elif geld == "Ik doneer het aan een goed doel 🤔":
        score -= 3

    # Rijbewijs
    if rijbewijs:
        score += 1

    # Loyaliteit
    if loyaal:
        score += 3
    else:
        score -= 3

    # Ervaringen
    if len(ervaring) >= 2:
        score += 2

    # Rekensom
    if antwoord == 40:
        score += 1
    else:
        score -= 1

    # Uitslag bepalen
    if score >= 6:
        st.success(f"Gefeliciteerd {naam}! 🎉 Je bent aangenomen bij La Famiglia. "
                   "We nemen snel contact met je op... of je het wilt of niet. 😉")
        st.session_state["sollicitanten"].append((naam, "Aangenomen"))
    elif score >= 3:
        st.warning(f"{naam}, je sollicitatie is twijfelachtig. "
                   "Je mag voorlopig op proef komen werken. 👀")
        st.session_state["sollicitanten"].append((naam, "Op proef"))
    else:
        st.error(f"Helaas {naam}, je sollicitatie is afgewezen. "
                 "Misschien beter bij de pizzeria proberen. 🍕")
        st.session_state["sollicitanten"].append((naam, "Afgewezen"))

st.header("📋 Overzicht sollicitanten tot nu toe")
if st.session_state["sollicitanten"]:
    for idx, (persoon, status) in enumerate(st.session_state["sollicitanten"], 1):
        st.write(f"{idx}. **{persoon}** – {status}")
else:
    st.write("Nog geen sollicitanten...")
