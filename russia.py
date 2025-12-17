import streamlit as st
import random

st.set_page_config(page_title="Russische Roulette vs Debbie", page_icon="🔫")

st.title("🔫 Russische Roulette")
st.subheader("Final Boss: Debbie 😈")

# --- Session state ---
if "geld" not in st.session_state:
    st.session_state.geld = 0

if "lening" not in st.session_state:
    st.session_state.lening = 0

if "bericht" not in st.session_state:
    st.session_state.bericht = ""

# --- Info ---
st.markdown("""
**Regels:**
- 6 kamers, **4 kogels**
- Win → **+€100**
- Verlies → **-€90**
- Je kan **in schuld** gaan
- Je kan een **lening van €10.000** opnemen
""")

st.divider()

# --- Status ---
st.metric("💰 Geld", f"€{st.session_state.geld}")
st.metric("🏦 Lening", f"€{st.session_state.lening}")

st.write(st.session_state.bericht)

st.divider()

# --- Acties ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🔫 Trek de trekker"):
        kamers = ["kogel"] * 4 + ["leeg"] * 2
        uitkomst = random.choice(kamers)

        if uitkomst == "kogel":
            st.session_state.geld -= 90
            st.session_state.bericht = "💥 **BOEM!** Debbie lacht. Je verliest €90."
        else:
            st.session_state.geld += 100
            st.session_state.bericht = "😮 **KLIK!** Je overleeft en wint €100!"

with col2:
    if st.button("🏦 Neem lening (€10.000)"):
        st.session_state.geld += 10000
        st.session_state.lening += 10000
        st.session_state.bericht = "📄 Je hebt een lening van €10.000 opgenomen."

# --- Game over check ---
if st.session_state.geld < -20000:
    st.error("☠️ Je schuld is te groot... Debbie heeft gewonnen. GAME OVER.")
    if st.button("🔁 Opnieuw spelen"):
        st.session_state.geld = 0
        st.session_state.lening = 0
        st.session_state.bericht = ""
