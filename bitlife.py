import streamlit as st
import random

st.set_page_config(page_title="Mini BitLife", page_icon="🧬")

# Sessiestatus om levensloop bij te houden
if 'leeftijd' not in st.session_state:
    st.session_state.leeftijd = 0
    st.session_state.geld = 1000
    st.session_state.geluk = 50
    st.session_state.gezondheid = 50
    st.session_state.max_leeftijd = random.randint(80, 120)
    st.session_state.maand = 1
    st.session_state.dood = False

# Functie voor keuzes
def levenskeuze(keuze_num):
    if keuze_num == 1:
        st.session_state.geld += 500
        st.session_state.geluk -= 5
    elif keuze_num == 2:
        st.session_state.geluk += 5
        st.session_state.geld += 100
    elif keuze_num == 3:
        st.session_state.gezondheid += 5
        st.session_state.geld -= 50
    elif keuze_num == 4:
        st.session_state.geluk += 10
        st.session_state.gezondheid -= 5
    elif keuze_num == 5:
        st.session_state.geluk += 5
        st.session_state.geld -= 100
    elif keuze_num == 6:
        st.session_state.geld += 200
        st.session_state.geluk -= 5
    elif keuze_num == 7:
        winst = random.randint(-200, 1000)
        st.session_state.geld += winst
        st.session_state.gezondheid -= random.randint(0, 15)
    elif keuze_num == 8:
        st.session_state.geluk += 10
        st.session_state.geld -= random.randint(0, 200)
    elif keuze_num == 9:
        st.session_state.gezondheid += 5
        st.session_state.geld -= 50
    elif keuze_num == 10:
        st.session_state.geluk += 10
        st.session_state.geld -= 500
    elif keuze_num == 11:
        st.session_state.geluk += 10
        st.session_state.geld -= 300
    elif keuze_num == 12:
        st.session_state.geluk -= 5
        st.session_state.gezondheid -= 5

    # Grenzen controleren
    st.session_state.gezondheid = max(0, min(100, st.session_state.gezondheid))
    st.session_state.geluk = max(0, min(100, st.session_state.geluk))
    st.session_state.geld = max(0, st.session_state.geld)

# Creatieve dood
def creatieve_dood():
    doods_scenario = [
        f"Je viel in slaap en werd nooit meer wakker op {st.session_state.leeftijd}-jarige leeftijd.",
        f"Je werd beroemd en stierf vredig in je mansion op {st.session_state.leeftijd}-jarige leeftijd.",
        f"Je werd opgegeten door een gigantische pinguïn op {st.session_state.leeftijd}-jarige leeftijd. (Ja, echt!)",
        f"Je stierf lachend tijdens een grap op {st.session_state.leeftijd}-jarige leeftijd.",
        f"Je werd een legende en stierf als held op {st.session_state.leeftijd}-jarige leeftijd."
    ]
    st.session_state.dood = True
    st.write("💀 **Je leven is voorbij!**")
    st.write(random.choice(doods_scenario))
    st.write(f"**Eindstats:** Geld: {st.session_state.geld}, Geluk: {st.session_state.geluk}, Gezondheid: {st.session_state.gezondheid}")

# Titel
st.title("🧬 Mini BitLife")
st.write(f"Leeftijd: {st.session_state.leeftijd} | Geld: {st.session_state.geld} | Geluk: {st.session_state.geluk} | Gezondheid: {st.session_state.gezondheid}")
st.write(f"Maand {st.session_state.maand} van jaar {st.session_state.leeftijd + 1}")

# Keuzeknoppen
keuzes = [
    "Werken", "Studeren", "Sporten", "Feesten", "Vrijwilligerswerk", "Sparen",
    "Riskante actie", "Relatie beginnen", "Gezond eten", "Huis kopen", "Reizen", "Niks doen"
]

if not st.session_state.dood:
    for i, optie in enumerate(keuzes):
        if st.button(optie, key=f"maand_{st.session_state.maand}_{i}"):
            levenskeuze(i + 1)
            st.session_state.maand += 1
            if st.session_state.gezondheid <= 0 or st.session_state.leeftijd >= st.session_state.max_leeftijd:
                creatieve_dood()
            elif st.session_state.maand > 12:
                st.session_state.maand = 1
                st.session_state.leeftijd += 1
                if st.session_state.gezondheid <= 0 or st.session_state.leeftijd >= st.session_state.max_leeftijd:
                    creatieve_dood()
            st.experimental_rerun()
