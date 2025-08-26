import streamlit as st
import random
import time
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="La Famiglia – Parodie Game", page_icon="🍝", layout="wide")

# -------------------------
# Initialization
# -------------------------
if "profiles" not in st.session_state:
    st.session_state["profiles"] = {}  # name -> profile dict

if "current_profile" not in st.session_state:
    st.session_state["current_profile"] = None

# Default shop items (cosmetic)
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
    profile["history"].append(
        {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text": text}
    )

def add_money(profile, amount, reason=""):
    profile["money"] += amount
    save_event(profile, f"+€{amount} {reason}")

def add_xp(profile, amount):
    profile["xp"] += amount
    save_event(profile, f"+{amount} XP")

def get_rank(profile):
    rank_name = "Rookie"
    for xp_needed, rank in RANKS:
        if profile["xp"] >= xp_needed:
            rank_name = rank
    return rank_name

def render_avatar(profile):
    base = profile["avatar"]["base"]
    items = "".join([SHOP_ITEMS[it]["emoji"] for it in profile["items"]])
    return base + items

# -------------------------
# Minigames
# -------------------------
def quiz_game(profile):
    st.subheader("🧠 Mafia Trivia")
    q = random.choice([
        ("Wat is de favoriete Italiaanse maaltijd van de familie?", ["Pizza", "Sushi", "Taco"], "Pizza"),
        ("Hoe zeg je 'familie' in het Italiaans?", ["Familia", "Famiglia", "Famille"], "Famiglia"),
        ("Welke saus hoort bij spaghetti?", ["Tomaat", "Chocolade", "Ketchup"], "Tomaat")
    ])
    answer = st.radio(q[0], q[1], key="quiz")
    if st.button("Beantwoord quiz"):
        if answer == q[2]:
            st.success("Correct! Je verdient €50 en 20 XP.")
            add_money(profile, 50, "Quiz winst")
            add_xp(profile, 20)
        else:
            st.error("Fout! Geen beloning dit keer.")
            save_event(profile, "Fout in quiz")

def luck_game(profile):
    st.subheader("🎲 Geluksrad")
    if st.button("Draai aan het rad"):
        result = random.randint(1, 10)
        if result == 10:
            st.success("Jackpot! Je wint €500 en 100 XP")
            add_money(profile, 500, "Jackpot")
            add_xp(profile, 100)
        elif result > 6:
            st.info("Je wint €100")
            add_money(profile, 100, "Geluksrad")
        else:
            st.warning("Helaas, niets dit keer")
            save_event(profile, "Leeg geluksrad")

def shooting_game(profile):
    st.subheader("🎯 Waterballon Schietspel")
    if "shooting_score" not in st.session_state:
        st.session_state["shooting_score"] = 0
    if st.button("Gooi waterballon! 💦"):
        hit = random.choice([True, False, False, True])
        if hit:
            st.session_state["shooting_score"] += 1
            st.success("Raak! +€20")
            add_money(profile, 20, "Raak target")
        else:
            st.warning("Mis! Probeer opnieuw.")
    st.write(f"Score: {st.session_state['shooting_score']}")

# -------------------------
# Shop
# -------------------------
def shop(profile):
    st.subheader("🛒 Shop – Koop attributen")
    st.write(f"Huidig geld: €{profile['money']}")
    for item, data in SHOP_ITEMS.items():
        if item in profile["items"]:
            st.write(f"{data['emoji']} {item} – AL GEKOCHT")
        else:
            if st.button(f"Koop {data['emoji']} {item} (€{data['price']})"):
                if profile["money"] >= data["price"]:
                    profile["money"] -= data["price"]
                    profile["items"].append(item)
                    add_xp(profile, data["xp"])
                    save_event(profile, f"Kocht {item}")
                    st.success(f"{item} gekocht!")
                else:
                    st.error("Niet genoeg geld!")

# -------------------------
# Pages
# -------------------------
st.title("🍝 La Famiglia – Parodie Mafia Sollicitatie Game")

tab1, tab2, tab3, tab4 = st.tabs(["Profiel", "Spelen", "Shop", "Rang & Geschiedenis"])

with tab1:
    st.header("Maak of kies je profiel")
    existing = list(st.session_state["profiles"].keys())
    if existing:
        choice = st.selectbox("Bestaand profiel", ["--"] + existing)
        if choice != "--":
            st.session_state["current_profile"] = choice

    with st.form("new_profile"):
        st.subheader("Nieuw profiel")
        name = st.text_input("Naam")
        age = st.number_input("Leeftijd", 10, 99)
        bio = st.text_area("Korte bio")
        submitted = st.form_submit_button("Maak profiel")
        if submitted and name:
            if name in st.session_state["profiles"]:
                st.error("Naam bestaat al")
            else:
                create_profile(name, age, bio)
                st.success(f"Profiel {name} aangemaakt!")

    if st.session_state["current_profile"]:
        profile = get_profile(st.session_state["current_profile"])
        st.subheader("Actief Profiel")
        st.write(f"Naam: {profile['name']} | Leeftijd: {profile['age']}")
        st.write(f"Bio: {profile['bio']}")
        st.write("Avatar: " + render_avatar(profile))
        st.write(f"Geld: €{profile['money']} | XP: {profile['xp']} | Rang: {get_rank(profile)}")

with tab2:
    if not st.session_state["current_profile"]:
        st.warning("Maak eerst een profiel aan.")
    else:
        profile = get_profile(st.session_state["current_profile"])
        st.header("Minigames")
        game = st.radio("Kies een spel", ["Quiz", "Geluksrad", "Schietspel"])
        if game == "Quiz":
            quiz_game(profile)
        elif game == "Geluksrad":
            luck_game(profile)
        elif game == "Schietspel":
            shooting_game(profile)

with tab3:
    if not st.session_state["current_profile"]:
        st.warning("Maak eerst een profiel aan.")
    else:
        profile = get_profile(st.session_state["current_profile"])
        shop(profile)

with tab4:
    if not st.session_state["current_profile"]:
        st.warning("Maak eerst een profiel aan.")
    else:
        profile = get_profile(st.session_state["current_profile"])
        st.header("Familie Rang & Geschiedenis")
        st.write(f"Rang: {get_rank(profile)}")
        st.write(f"Avatar: {render_avatar(profile)}")
        st.write("### Geschiedenis")
        df = pd.DataFrame(profile["history"])
        if not df.empty:
            st.table(df)
        else:
            st.info("Nog geen gebeurtenissen")
