import streamlit as st
import random

# --- Start van het spel ---
if 'leeftijd' not in st.session_state:
    st.session_state.leeftijd = 0
    st.session_state.geld = 1000
    st.session_state.geluk = 50
    st.session_state.gezondheid = 50
    st.session_state.max_leeftijd = random.randint(80, 120)
    st.session_state.spelen = True
    st.session_state.dood = ""

st.title("BitLife Streamlit Edition")
st.write(f"Je zult waarschijnlijk rond de {st.session_state.max_leeftijd} jaar oud worden.")

# --- Creatieve dood ---
def creatieve_dood():
    doodsredenen = [
        "Je bent vredig in je slaap overleden.",
        "Je bent gevallen tijdens een epische danswedstrijd.",
        "Je bent een beroemdheid geworden en overleefde je eigen filmset niet.",
        "Je bent gestorven tijdens het redden van een kat uit een boom.",
        "Je hart stopte na een te veel aan chocolade."
    ]
    st.session_state.dood = random.choice(doodsredenen)
    st.session_state.spelen = False

# --- Levenskeuzes ---
keuzes = [
    "Werken (+geld, -geluk)",
    "Studeren (+geluk, +kans op betere baan)",
    "Sporten (+gezondheid, -geld)",
    "Feesten (+geluk, -gezondheid)",
    "Vrijwilligerswerk (+geluk, -geld)",
    "Sparen (+geld, -geluk)",
    "Riskante actie doen (+geld, kans op -gezondheid)",
    "Relatie beginnen (+geluk, kans op -geld)",
    "Gezond eten (+gezondheid, -geld)",
    "Huis kopen (-geld, +geluk)",
    "Reizen (-geld, +geluk)",
    "Niks doen (-geluk, -gezondheid)"
]

def kies_actie(index):
    if index == 0:
        st.session_state.geld += 500
        st.session_state.geluk -= 5
    elif index == 1:
        st.session_state.geluk += 5
        st.session_state.geld += 100
    elif index == 2:
        st.session_state.gezondheid += 5
        st.session_state.geld -= 50
    elif index == 3:
        st.session_state.geluk += 10
        st.session_state.gezondheid -= 5
    elif index == 4:
        st.session_state.geluk += 5
        st.session_state.geld -= 100
    elif index == 5:
        st.session_state.geld += 200
        st.session_state.geluk -= 5
    elif index == 6:
        winst = random.randint(-200, 1000)
        st.session_state.geld += winst
        st.session_state.gezondheid -= random.randint(0, 10)
    elif index == 7:
        st.session_state.geluk += 10
        st.session_state.geld -= random.randint(0, 200)
    elif index == 8:
        st.session_state.gezondheid += 5
        st.session_state.geld -= 50
    elif index == 9:
        st.session_state.geluk += 10
        st.session_state.geld -= 500
    elif index == 10:
        st.session_state.geluk += 10
        st.session_state.geld -= 300
    elif index == 11:
        st.session_state.geluk -= 5
        st.session_state.gezondheid -= 5

    st.session_state.gezondheid = max(0, min(100, st.session_state.gezondheid))
    st.session_state.geluk = max(0, min(100, st.session_state.geluk))
    st.session_state.leeftijd += 1

    if st.session_state.leeftijd >= st.session_state.max_leeftijd or st.session_state.gezondheid <= 0:
        creatieve_dood()

# --- Streamlit interface ---
if st.session_state.spelen:
    st.write(f"\n--- Leeftijd: {st.session_state.leeftijd} jaar ---")
    st.write(f"Geld: {st.session_state.geld}, Geluk: {st.session_state.geluk}, Gezondheid: {st.session_state.gezondheid}")

    for i, actie in enumerate(keuzes):
        if st.button(actie, key=i):
            kies_actie(i)
else:
    st.write("💀 Je leven is voorbij!")
    st.write(st.session_state.dood)
    st.write(f"Eindleeftijd: {st.session_state.leeftijd}, Geld: {st.session_state.geld}, Geluk: {st.session_state.geluk}, Gezondheid: {st.session_state.gezondheid}")

# Optioneel: knop om opnieuw te spelen
if st.button("Opnieuw spelen"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.experimental_rerun()
