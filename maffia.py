import streamlit as st

st.set_page_config(page_title="Maffia Sollicitatie", page_icon="💼", layout="centered")

st.title("💼 Maffia Sollicitatie Formulier")
st.write("Welkom bij je sollicitatie voor *La Famiglia*. Vul dit formulier eerlijk in... of anders. 😉")

st.header("👤 Persoonlijke Gegevens")
naam = st.text_input("Wat is je naam?")
leeftijd = st.number_input("Wat is je leeftijd?", min_value=0, max_value=120, step=1)
specialiteit = st.text_input("Wat is je 'specialiteit'? (bijv. geld tellen, pokerface, pizzabakker)")

st.header("🕵️ Ervaringen")
ervaring = st.multiselect(
    "Welke 'ervaringen' heb je?",
    ["Geld transporteren", "Pokeravonden gewonnen", "Geheimen bewaren", "Handel in... dingen", "Goede alibi's verzinnen"]
)

st.header("💰 Testjes")

st.subheader("1. Hoe ga je om met geld?")
geld = st.radio(
    "Er ligt €10.000 cash op tafel. Wat doe je?",
    ["Ik neem het mee naar de baas", "Ik stop het in mijn zak", "Ik tel het driemaal na en dan rapporteer ik", "Ik doneer het aan een goed doel 🤔"]
)

st.subheader("2. Wat is je ideale rol in de familie?")
rol = st.selectbox(
    "Kies je voorkeur:",
    ["Chauffeur 🚗", "Bewaker 💪", "Onderhandelaar 🗣️", "Rekenmeester 📊", "Chef-kok 🍝"]
)

st.subheader("3. Loyauteitstest")
loyaal = st.checkbox("Ik zweer trouw aan La Famiglia 🤌")

# Eindresultaat
if st.button("📜 Verstuur sollicitatie"):
    st.subheader("🔎 Uitslag van je sollicitatie:")

    score = 0

    if geld == "Ik neem het mee naar de baas":
        score += 2
    elif geld == "Ik tel het driemaal na en dan rapporteer ik":
        score += 1
    elif geld == "Ik doneer het aan een goed doel 🤔":
        score -= 2

    if loyaal:
        score += 3
    else:
        score -= 3

    if len(ervaring) >= 2:
        score += 2

    if rol == "Chef-kok 🍝":
        score += 1  # bonuspunten voor pasta 🍝

    if score >= 5:
        st.success(f"Gefeliciteerd {naam}! Je bent aangenomen in La Famiglia. 🍷")
    elif score >= 2:
        st.warning(f"{naam}, je mag misschien meedoen, maar we houden je in de gaten... 👀")
    else:
        st.error(f"{naam}, helaas... je sollicitatie is afgewezen. Misschien beter bij de pizzeria proberen. 🍕")
import streamlit as st

st.set_page_config(page_title="Maffia Sollicitatie", page_icon="💼", layout="centered")

st.title("💼 Maffia Sollicitatie Formulier")
st.write("Welkom bij je sollicitatie voor *La Famiglia*. Vul dit formulier eerlijk in... of anders. 😉")

st.header("👤 Persoonlijke Gegevens")
naam = st.text_input("Wat is je naam?")
leeftijd = st.number_input("Wat is je leeftijd?", min_value=0, max_value=120, step=1)
specialiteit = st.text_input("Wat is je 'specialiteit'? (bijv. geld tellen, pokerface, pizzabakker)")

st.header("🕵️ Ervaringen")
ervaring = st.multiselect(
    "Welke 'ervaringen' heb je?",
    ["Geld transporteren", "Pokeravonden gewonnen", "Geheimen bewaren", "Handel in... dingen", "Goede alibi's verzinnen"]
)

st.header("💰 Testjes")

st.subheader("1. Hoe ga je om met geld?")
geld = st.radio(
    "Er ligt €10.000 cash op tafel. Wat doe je?",
    ["Ik neem het mee naar de baas", "Ik stop het in mijn zak", "Ik tel het driemaal na en dan rapporteer ik", "Ik doneer het aan een goed doel 🤔"]
)

st.subheader("2. Wat is je ideale rol in de familie?")
rol = st.selectbox(
    "Kies je voorkeur:",
    ["Chauffeur 🚗", "Bewaker 💪", "Onderhandelaar 🗣️", "Rekenmeester 📊", "Chef-kok 🍝"]
)

st.subheader("3. Loyauteitstest")
loyaal = st.checkbox("Ik zweer trouw aan La Famiglia 🤌")

# Eindresultaat
if st.button("📜 Verstuur sollicitatie"):
    st.subheader("🔎 Uitslag van je sollicitatie:")

    score = 0

    if geld == "Ik neem het mee naar de baas":
        score += 2
    elif geld == "Ik tel het driemaal na en dan rapporteer ik":
        score += 1
    elif geld == "Ik doneer het aan een goed doel 🤔":
        score -= 2

    if loyaal:
        score += 3
    else:
        score -= 3

    if len(ervaring) >= 2:
        score += 2

    if rol == "Chef-kok 🍝":
        score += 1  # bonuspunten voor pasta 🍝

    if score >= 5:
        st.success(f"Gefeliciteerd {naam}! Je bent aangenomen in La Famiglia. 🍷")
    elif score >= 2:
        st.warning(f"{naam}, je mag misschien meedoen, maar we houden je in de gaten... 👀")
    else:
        st.error(f"{naam}, helaas... je sollicitatie is afgewezen. Misschien beter bij de pizzeria proberen. 🍕")
import streamlit as st

st.set_page_config(page_title="Maffia Sollicitatie", page_icon="💼", layout="centered")

st.title("💼 Maffia Sollicitatie Formulier")
st.write("Welkom bij je sollicitatie voor *La Famiglia*. Vul dit formulier eerlijk in... of anders. 😉")

st.header("👤 Persoonlijke Gegevens")
naam = st.text_input("Wat is je naam?")
leeftijd = st.number_input("Wat is je leeftijd?", min_value=0, max_value=120, step=1)
specialiteit = st.text_input("Wat is je 'specialiteit'? (bijv. geld tellen, pokerface, pizzabakker)")

st.header("🕵️ Ervaringen")
ervaring = st.multiselect(
    "Welke 'ervaringen' heb je?",
    ["Geld transporteren", "Pokeravonden gewonnen", "Geheimen bewaren", "Handel in... dingen", "Goede alibi's verzinnen"]
)

st.header("💰 Testjes")

st.subheader("1. Hoe ga je om met geld?")
geld = st.radio(
    "Er ligt €10.000 cash op tafel. Wat doe je?",
    ["Ik neem het mee naar de baas", "Ik stop het in mijn zak", "Ik tel het driemaal na en dan rapporteer ik", "Ik doneer het aan een goed doel 🤔"]
)

st.subheader("2. Wat is je ideale rol in de familie?")
rol = st.selectbox(
    "Kies je voorkeur:",
    ["Chauffeur 🚗", "Bewaker 💪", "Onderhandelaar 🗣️", "Rekenmeester 📊", "Chef-kok 🍝"]
)

st.subheader("3. Loyauteitstest")
loyaal = st.checkbox("Ik zweer trouw aan La Famiglia 🤌")

# Eindresultaat
if st.button("📜 Verstuur sollicitatie"):
    st.subheader("🔎 Uitslag van je sollicitatie:")

    score = 0

    if geld == "Ik neem het mee naar de baas":
        score += 2
    elif geld == "Ik tel het driemaal na en dan rapporteer ik":
        score += 1
    elif geld == "Ik doneer het aan een goed doel 🤔":
        score -= 2

    if loyaal:
        score += 3
    else:
        score -= 3

    if len(ervaring) >= 2:
        score += 2

    if rol == "Chef-kok 🍝":
        score += 1  # bonuspunten voor pasta 🍝

    if score >= 5:
        st.success(f"Gefeliciteerd {naam}! Je bent aangenomen in La Famiglia. 🍷")
    elif score >= 2:
        st.warning(f"{naam}, je mag misschien meedoen, maar we houden je in de gaten... 👀")
    else:
        st.error(f"{naam}, helaas... je sollicitatie is afgewezen. Misschien beter bij de pizzeria proberen. 🍕")
import streamlit as st

st.set_page_config(page_title="Maffia Sollicitatie", page_icon="💼", layout="centered")

st.title("💼 Maffia Sollicitatie Formulier")
st.write("Welkom bij je sollicitatie voor *La Famiglia*. Vul dit formulier eerlijk in... of anders. 😉")

st.header("👤 Persoonlijke Gegevens")
naam = st.text_input("Wat is je naam?")
leeftijd = st.number_input("Wat is je leeftijd?", min_value=0, max_value=120, step=1)
specialiteit = st.text_input("Wat is je 'specialiteit'? (bijv. geld tellen, pokerface, pizzabakker)")

st.header("🕵️ Ervaringen")
ervaring = st.multiselect(
    "Welke 'ervaringen' heb je?",
    ["Geld transporteren", "Pokeravonden gewonnen", "Geheimen bewaren", "Handel in... dingen", "Goede alibi's verzinnen"]
)

st.header("💰 Testjes")

st.subheader("1. Hoe ga je om met geld?")
geld = st.radio(
    "Er ligt €10.000 cash op tafel. Wat doe je?",
    ["Ik neem het mee naar de baas", "Ik stop het in mijn zak", "Ik tel het driemaal na en dan rapporteer ik", "Ik doneer het aan een goed doel 🤔"]
)

st.subheader("2. Wat is je ideale rol in de familie?")
rol = st.selectbox(
    "Kies je voorkeur:",
    ["Chauffeur 🚗", "Bewaker 💪", "Onderhandelaar 🗣️", "Rekenmeester 📊", "Chef-kok 🍝"]
)

st.subheader("3. Loyauteitstest")
loyaal = st.checkbox("Ik zweer trouw aan La Famiglia 🤌")

# Eindresultaat
if st.button("📜 Verstuur sollicitatie"):
    st.subheader("🔎 Uitslag van je sollicitatie:")

    score = 0

    if geld == "Ik neem het mee naar de baas":
        score += 2
    elif geld == "Ik tel het driemaal na en dan rapporteer ik":
        score += 1
    elif geld == "Ik doneer het aan een goed doel 🤔":
        score -= 2

    if loyaal:
        score += 3
    else:
        score -= 3

    if len(ervaring) >= 2:
        score += 2

    if rol == "Chef-kok 🍝":
        score += 1  # bonuspunten voor pasta 🍝

    if score >= 5:
        st.success(f"Gefeliciteerd {naam}! Je bent aangenomen in La Famiglia. 🍷")
    elif score >= 2:
        st.warning(f"{naam}, je mag misschien meedoen, maar we houden je in de gaten... 👀")
    else:
        st.error(f"{naam}, helaas... je sollicitatie is afgewezen. Misschien beter bij de pizzeria proberen. 🍕")
