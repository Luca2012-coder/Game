import streamlit as st

st.set_page_config(page_title="Kartonnen Wapen Clicker", layout="centered")

# Geld opslaan in session_state
if "money" not in st.session_state:
    st.session_state.money = 0

st.title("🧻 Kartonnen Wapen Clicker")

st.write("Klik op het kartonnen wapen om geld te verdienen 💰")

st.subheader(f"Geld: €{st.session_state.money}")

# Optie 1: met afbeelding
# Zet een afbeelding online of gebruik een emoji knop
if st.button("🧻 Kartonnen Wapen"):
    st.session_state.money += 1
    st.rerun()

st.divider()

# Extra knop om te resetten
if st.button("🔄 Reset geld"):
    st.session_state.money = 0
    st.rerun()
