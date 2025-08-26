# Writing the full Streamlit mafia parody game app to a file

code = r'''
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

# Default shop items (cosmetic parody items)
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
    profile["history"].append({"time": datetime.now().strftime("%H:%M:%S"), "text": text})

def add_money(profile, amount, reason=""):
    profile["money"] += amount
    save_event(profile, f"+€{amount} {reason}")

def add_xp(profile, amount, reason=""):
    profile["xp"] += amount
    save_event(profile, f"+{amount} XP {reason}")
    # Level up logic
    profile["level"] = 1 + profile["xp"] // 100

def get_rank(profile):
    rank = "Rookie"
    for threshold, title in RANKS:
        if profile["xp"] >= threshold:
            rank = title
    return rank

def buy_item(profile, item_name):
    item = SHOP_ITEMS[item_name]
    if profile["money"] >= item["price"]:
        profile["money"] -= item["price"]
        profile["items"].append(item_name)
        profile["avatar"]["items"].append(item["emoji"])
        add_xp(profile, item["xp"], f"voor {item_name}")
        save_event(profile, f"Kocht {item_name} {item['emoji']}")
        return True
    return False

# -------------------------
# UI Tabs
# -------------------------
tabs = st.tabs(["Profiel", "Spelen", "Shop", "Rang & Geschiedenis"])

# -------------------------
# Profiel Tab
# -------------------------
with tabs[0]:
    st.header("👤 Profiel aanmaken / kiezen")
    name = st.text_input("Naam")
    age = st.number_input("Leeftijd", min_value=16, max_value=120, step=1)
    bio = st.text_area("Korte bio", "Ik ben klaar om de familie te dienen.")

    if st.button("Maak profiel"):
        if name.strip():
            profile = create_profile(name.strip(), age, bio)
            st.success(f"Profiel voor {name} aangemaakt!")
        else:
            st.error("Naam mag niet leeg zijn.")

    if st.session_state["profiles"]:
        chosen = st.selectbox("Bestaande profielen", list(st.session_state["profiles"].keys()))
        if st.button("Kies profiel"):
            st.session_state["current_profile"] = chosen

    if st.session_state["current_profile"]:
        p = get_profile(st.session_state["current_profile"])
        st.subheader(f"Huidig profiel: {p['name']} ({p['age']} jaar)")
        st.write(f"Bio: {p['bio']}")
        st.write(f"Avatar: {p['avatar']['base']} {' '.join(p['avatar']['items'])}")
        st.write(f"Geld: €{p['money']} | XP: {p['xp']} | Level: {p['level']} | Rang: {get_rank(p)}")

# -------------------------
# Spelen Tab
# -------------------------
with tabs[1]:
    st.header("🎲 Spelletjes voor geld & XP")
    if not st.session_state["current_profile"]:
        st.info("Maak of kies eerst een profiel.")
    else:
        p = get_profile(st.session_state["current_profile"])

        st.subheader("Mini-quiz")
        q = st.radio("Wat is de geheime saus van La Famiglia?", ["Tomaat", "Pesto", "Pizza", "Olijfolie"])
        if st.button("Beantwoord quiz"):
            if q == "Tomaat":
                add_money(p, 50, "quiz winst")
                add_xp(p, 20, "quiz")
                st.success("Correct! Je verdient €50 en 20 XP.")
            else:
                st.warning("Fout! Geen beloning.")

        st.subheader("Geluksrad 🎡")
        if st.button("Draai het rad"):
            prize = random.choice([0, 20, 50, 100, 200])
            if prize > 0:
                add_money(p, prize, "geluksrad")
                st.success(f"Je won €{prize}!")
            else:
                st.info("Helaas, niets gewonnen.")

        st.subheader("Target Spel 🎯")
        if st.button("Schiet!"):
            hit = random.random() < 0.5
            if hit:
                add_money(p, 30, "target hit")
                add_xp(p, 10, "target hit")
                st.success("Raak! Je verdient €30 en 10 XP.")
            else:
                st.info("Mis!")

# -------------------------
# Shop Tab
# -------------------------
with tabs[2]:
    st.header("🛒 Shop")
    if not st.session_state["current_profile"]:
        st.info("Maak of kies eerst een profiel.")
    else:
        p = get_profile(st.session_state["current_profile"])
        st.write(f"Geld: €{p['money']}")
        for item_name, item in SHOP_ITEMS.items():
            cols = st.columns([2,1,1])
            with cols[0]:
                st.write(f"{item_name} {item['emoji']} - €{item['price']} (+{item['xp']} XP)")
            with cols[1]:
                owned = item_name in p["items"]
                st.write("✅" if owned else "❌")
            with cols[2]:
                if not item_name in p["items"]:
                    if st.button(f"Koop {item_name}", key=f"buy_{item_name}"):
                        if buy_item(p, item_name):
                            st.success(f"Gekocht: {item_name}!")
                        else:
                            st.error("Niet genoeg geld.")

# -------------------------
# Rang & Geschiedenis Tab
# -------------------------
with tabs[3]:
    st.header("📜 Familie-status")
    if not st.session_state["current_profile"]:
        st.info("Maak of kies eerst een profiel.")
    else:
        p = get_profile(st.session_state["current_profile"])
        st.subheader(f"{p['name']} – Rang: {get_rank(p)} | Level {p['level']}")
        st.write(f"Avatar: {p['avatar']['base']} {' '.join(p['avatar']['items'])}")
        st.write(f"Geld: €{p['money']} | XP: {p['xp']}")

        st.markdown("### Geschiedenis")
        for e in reversed(p["history"]):
            st.write(f"[{e['time']}] {e['text']}")
'''

path = "/mnt/data/la_famiglia_game.py"
with open(path, "w", encoding="utf-8") as f:
    f.write(code)

path
