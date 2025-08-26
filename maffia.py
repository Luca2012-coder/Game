import streamlit as st
import random
from datetime import datetime

st.set_page_config(page_title="La Famiglia – Parodie Game", page_icon="🍝", layout="wide")

# -------------------------
# Initialization
# -------------------------
if "profiles" not in st.session_state:
    st.session_state["profiles"] = {}  # name -> profile dict

if "current_profile" not in st.session_state:
    st.session_state["current_profile"] = None

# Default shop items (cosmetic only, parodie-stijl)
SHOP_ITEMS = {
    "Fedora": {"price": 100, "emoji": "🎩", "xp": 10},
    "Sunglasses": {"price": 150, "emoji": "🕶️", "xp": 15},
    "Gold Chain": {"price": 300, "emoji": "📿", "xp": 30},
    "Fancy Suit": {"price": 500, "emoji": "🤵", "xp": 50},
    "Black Boots": {"price": 120, "emoji": "👞", "xp": 12},
    "Nonna's Recipe": {"price": 80, "emoji": "📜", "xp": 8},
    "Motorcycle": {"price": 800, "emoji": "🏍️", "xp": 80}
}

RANKS = [
    (0, "Rookie"),
    (100, "Associate"),
    (300, "Caporegime"),
    (700, "Consigliere"),
    (1500, "Underboss"),
    (3000, "Boss")
]

# -------------------------
# Helper functions
# -------------------------
def create_profile(name, age, bio):
    profile = {
        "name": name,
        "age": age,
        "bio": bio,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "money": 200,
        "xp": 0,
        "level": 1,
        "items": [],
        "history": [],
        "avatar": {"base": "😎", "items": []},
    }
    st.session_state["profiles"][name] = profile
    st.session_state["current_profile"] = name
    return profile

def get_profile(name):
    return st.session_state["profiles"].get(name)

def save_event(profile, text):
    profile["history"].append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text": text})

def add_money(profile, amount, reason=""):
    profile["money"] += amount
    save_event(profile, f"+€{amount} {reason}")

def add_xp(profile, amount, reason=""):
    profile["xp"] += amount
    save_event(profile, f"+{amount} XP {reason}")

def get_rank(xp):
    current_rank = "Rookie"
    for req, title in RANKS:
        if xp >= req:
            current_rank = title
    return current_rank

def render_avatar(profile):
    return profile["avatar"]["base"] + "".join(profile["avatar"]["items"])

# -------------------------
# Tabs
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📜 Profiel", "🎮 Spelen", "🛍️ Shop", "⭐ Rang & Geschiedenis"])

# -------------------------
# Profiel
# -------------------------
with tab1:
    st.header("Sollicitatieformulier – Word lid van La Famiglia 🍝")

    if st.session_state["current_profile"] is None:
        with st.form("new_profile"):
            name = st.text_input("Naam")
            age = st.number_input("Leeftijd", min_value=10, max_value=99, value=18)
            bio = st.text_area("Vertel iets over jezelf")
            submit = st.form_submit_button("Indienen")

        if submit and name:
            if name in st.session_state["profiles"]:
                st.warning("Deze naam bestaat al, kies een andere.")
            else:
                profile = create_profile(name, age, bio)
                st.success(f"Welkom {name}! Je bent nu een rookie in de familie.")
    else:
        profile = get_profile(st.session_state["current_profile"])
        st.subheader(f"Actief profiel: {profile['name']}")
        st.write("Avatar:", render_avatar(profile))
        st.write("💰 Geld:", profile["money"])
        st.write("⭐ XP:", profile["xp"])
        st.write("🎖️ Rang:", get_rank(profile["xp"]))
        if st.button("Uitloggen"):
            st.session_state["current_profile"] = None

# -------------------------
# Spelen
# -------------------------
with tab2:
    st.header("🎮 Familie-minigames")

    if st.session_state["current_profile"] is None:
        st.info("Maak eerst een profiel aan bij 📜 Profiel.")
    else:
        profile = get_profile(st.session_state["current_profile"])

        st.subheader("Maffia Quiz")
        q = st.radio("Wat is de favoriete maaltijd van de familie?", ["Pizza", "Sushi", "Hamburger"])
        if st.button("Beantwoord"):
            if q == "Pizza":
                add_money(profile, 50, "Quiz beloning")
                add_xp(profile, 20, "Quiz beloning")
                st.success("Correct! Je hebt geld en XP verdiend.")
            else:
                st.error("Fout! Geen beloning deze keer.")

        st.subheader("Geluksrad")
        if st.button("Draai het rad"):
            outcome = random.choice(["Geld", "XP", "Niks"])
            if outcome == "Geld":
                add_money(profile, 100, "Geluksrad")
                st.success("Je won €100!")
            elif outcome == "XP":
                add_xp(profile, 50, "Geluksrad")
                st.success("Je won 50 XP!")
            else:
                st.warning("Helaas, niks gewonnen...")

        st.subheader("Klik-spelletje")
        if "click_score" not in profile:
            profile["click_score"] = 0
        if st.button("Klik!"):
            profile["click_score"] += 1
            if profile["click_score"] % 5 == 0:
                add_money(profile, 20, "Klik-spel")
                add_xp(profile, 10, "Klik-spel")
                st.balloons()
            st.write("Score:", profile["click_score"])

# -------------------------
# Shop
# -------------------------
with tab3:
    st.header("🛍️ Shop – Koop attributen voor je avatar")

    if st.session_state["current_profile"] is None:
        st.info("Maak eerst een profiel aan bij 📜 Profiel.")
    else:
        profile = get_profile(st.session_state["current_profile"])
        st.write("💰 Jouw geld:", profile["money"])
        for item, data in SHOP_ITEMS.items():
            col1, col2, col3 = st.columns([2,1,1])
            with col1:
                st.write(f"{data['emoji']} {item} – €{data['price']} (+{data['xp']} XP)")
            with col2:
                if item in profile["items"]:
                    st.success("Gekocht")
                else:
                    if st.button(f"Koop {item}", key=item):
                        if profile["money"] >= data["price"]:
                            profile["money"] -= data["price"]
                            profile["items"].append(item)
                            profile["avatar"]["items"].append(data["emoji"])
                            add_xp(profile, data["xp"], f"Gekocht: {item}")
                            save_event(profile, f"Kocht {item}")
                            st.experimental_rerun()
                        else:
                            st.error("Niet genoeg geld!")

# -------------------------
# Rang & Geschiedenis
# -------------------------
with tab4:
    st.header("⭐ Jouw Familie-status")
    if st.session_state["current_profile"] is None:
        st.info("Maak eerst een profiel aan bij 📜 Profiel.")
    else:
        profile = get_profile(st.session_state["current_profile"])
        st.write("Naam:", profile["name"])
        st.write("Avatar:", render_avatar(profile))
        st.write("💰 Geld:", profile["money"])
        st.write("⭐ XP:", profile["xp"])
        st.write("🎖️ Rang:", get_rank(profile["xp"]))

        st.subheader("📜 Geschiedenis")
        for h in reversed(profile["history"]):
            st.write(f"{h['time']}: {h['text']}")
