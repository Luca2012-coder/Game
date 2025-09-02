# la_famiglia_secure_game.py

# Complete Streamlit app: profiles with password, city choice, avatar, hard earning,

# 1x/day random mission, shop, ranks, and persistent profiles.json.

#

# Run:

#   pip install streamlit

#   streamlit run la_famiglia_secure_game.py

 

import streamlit as st

import json

import random

import hashlib

from datetime import date, datetime

from pathlib import Path

 

# -----------------------

# Config

# -----------------------

DATA_FILE = Path("profiles.json")

st.set_page_config(page_title="La Famiglia – Secure Parody Game", page_icon="🍝", layout="wide")

 

CITIES = [

    "Florence", "Bologna", "Milaan", "Sicilië", "Sardinië", "Rome", "Palermo",

    "Bari", "Turijn", "Lombardo", "Venetië", "Empoli", "Napels", "Genua",

    "Verona", "Parma", "Calabrië"

]

 

SHOP_ITEMS = {

    "Fedora": {"price": 300, "emoji": "🎩", "pos": "top", "xp": 18},

    "Sunglasses": {"price": 350, "emoji": "🕶️", "pos": "eyes", "xp": 22},

    "Gold Chain": {"price": 600, "emoji": "📿", "pos": "neck", "xp": 44},

    "Fancy Suit": {"price": 1200, "emoji": "🤵", "pos": "torso", "xp": 90},

    "Black Boots": {"price": 420, "emoji": "👞", "pos": "feet", "xp": 24},

    "Motorcycle": {"price": 2200, "emoji": "🏍️", "pos": "side", "xp": 150},

    "Recipe Scroll": {"price": 280, "emoji": "📜", "pos": "side", "xp": 20}

}

 

BASE_AVATARS = ["😎", "🕵️", "👨‍🍳", "🧑‍💼", "🧑‍🏭", "👴", "👩‍🦳"]

 

RANKS = [

    (0, "Groentje"),

    (100, "Rekruut"),

    (200, "Piccioto"),

    (400, "Soldato"),

    (800, "Capodecino"),

    (1600, "Capo Bastone"),

    (3200, "Capo"),

    (6400, "Consigliere"),

    (12800, "Ambasciatore della Famiglia"),

    (25600, "Don"),

    (51200, "Capo di Capo"),

    (102400, "Lid van de Maffia Commiccie"),

]

 

# -----------------------

# Persistence helpers

# -----------------------

def load_profiles():

    if DATA_FILE.exists():

        try:

            with DATA_FILE.open("r", encoding="utf-8") as f:

                return json.load(f)

        except Exception:

            # corrupt: back up

            backup = DATA_FILE.with_suffix(".broken.json")

            DATA_FILE.replace(backup)

            return {}

    return {}

 

def save_profiles(profiles):

    try:

        with DATA_FILE.open("w", encoding="utf-8") as f:

            json.dump(profiles, f, ensure_ascii=False, indent=2)

    except Exception as e:

        st.error(f"Kon profielen niet opslaan: {e}")

 

def autosave():

    save_profiles(st.session_state["profiles"])

 

# -----------------------

# Security helpers

# -----------------------

def hash_password(password: str, salt: str) -> str:

    # simple salted sha256 (ok for this game demo)

    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

 

def make_salt(name: str) -> str:

    # deterministic salt per username; not cryptographically strong but OK here

    return hashlib.sha256(("salt:" + name).encode("utf-8")).hexdigest()[:16]

 

# -----------------------

# Session init

# -----------------------

if "profiles" not in st.session_state:

    st.session_state["profiles"] = load_profiles()  # mapping name -> profile dict

 

if "logged_in" not in st.session_state:

    st.session_state["logged_in"] = False

if "username" not in st.session_state:

    st.session_state["username"] = None

 

# -----------------------

# Profile model helpers

# -----------------------

def new_profile_struct(name, password, city, age, bio, specialities):

    salt = make_salt(name)

    return {

        "name": name,

        "password_hash": hash_password(password, salt),

        "salt": salt,

        "city": city,

        "age": age,

        "bio": bio,

        "specialities": specialities,

        "created": datetime.now().isoformat(timespec="seconds"),

        "money": 100,  # low starting money to keep it slow

        "xp": 0,

        "level": 1,

        "items": [],

        "avatar": {"base": random.choice(BASE_AVATARS), "top":"", "eyes":"", "neck":"", "torso":"", "feet":"", "side":""},

        "history": [],

        "last_mission_date": None

    }

 

def verify_login(profiles, name, password):

    if name not in profiles:

        return False

    prof = profiles[name]

    salt = prof.get("salt", make_salt(name))

    return hash_password(password, salt) == prof.get("password_hash", "")

 

def save_event(profile, text):

    profile.setdefault("history", []).append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text": text})

    autosave()

 

def get_rank(xp):

    rank = RANKS[0][1]

    for req, title in RANKS:

        if xp >= req:

            rank = title

    return rank

 

def render_avatar(profile):

    a = profile["avatar"]

    # assemble lines: top, eyes/face, neck, torso, feet

    lines = [

        a.get("top",""),

        f"{a.get('base','😎')}{a.get('eyes','')}",

        a.get("neck",""),

        a.get("torso",""),

        a.get("feet","")

    ]

    side = a.get("side","")

    avatar_str = "\n".join(lines)

    if side:

        avatar_str = avatar_str.replace("\n", f" {side}\n")

    return avatar_str

 

# -----------------------

# UI: Sidebar: login/create

# -----------------------

st.sidebar.title("Account")

if st.session_state["logged_in"]:

    st.sidebar.markdown(f"**Ingelogd als:** {st.session_state['username']}")

    if st.sidebar.button("Uitloggen"):

        st.session_state["logged_in"] = False

        st.session_state["username"] = None

        st.success("Uitgelogd")

else:

    st.sidebar.subheader("Nieuw account aanmaken")

    with st.sidebar.form("create_account"):

        new_name = st.text_input("Gebruikersnaam", key="new_name")

        new_pass = st.text_input("Wachtwoord", type="password", key="new_pass")

        city = st.selectbox("Stad", CITIES, key="new_city")

        age = st.number_input("Leeftijd", min_value=16, max_value=99, value=25, key="new_age")

        bio = st.text_area("Korte bio", key="new_bio")

        special = st.multiselect("Specialiteiten (parodie)", ["Pizzabakken","Logistiek","Onderhandelen","Discretie","Financieel inzicht","PR","Technische hulp (IT)"], key="new_special")

        create_sub = st.form_submit_button("Maak account")

    if create_sub:

        if not new_name.strip() or not new_pass:

            st.sidebar.error("Naam en wachtwoord verplicht.")

        elif new_name in st.session_state["profiles"]:

            st.sidebar.error("Naam bestaat al. Kies een andere.")

        else:

            prof = new_profile_struct(new_name.strip(), new_pass, city, age, bio, special)

            st.session_state["profiles"][new_name.strip()] = prof

            autosave()

            st.sidebar.success("Account aangemaakt. Log in onderaan.")

    st.sidebar.markdown("---")

    st.sidebar.subheader("Inloggen")

    with st.sidebar.form("login"):

        login_name = st.text_input("Naam", key="login_name")

        login_pass = st.text_input("Wachtwoord", type="password", key="login_pass")

        login_sub = st.form_submit_button("Login")

    if login_sub:

        if verify_login(st.session_state["profiles"], login_name.strip(), login_pass):

            st.session_state["logged_in"] = True

            st.session_state["username"] = login_name.strip()

            st.sidebar.success("Succesvol ingelogd")

        else:

            st.sidebar.error("Login mislukt. Controleer naam/wachtwoord.")

 

st.sidebar.markdown("---")

st.sidebar.markdown("Veiligheid: wachtwoorden worden hashed (lokale opslag). Deel ze niet met anderen.")

 

# -----------------------

# Main layout: tabs

# -----------------------

tab_profile, tab_earn, tab_mission, tab_shop, tab_rank = st.tabs([

    "📝 Mijn profiel", "💼 Verdien (moeilijk)", "🎯 Dagelijkse missie", "🛍️ Shop & Avatar", "📜 Rang & Historie"

])

 

# -----------------------

# Tab: Profile

# -----------------------

with tab_profile:

    st.header("Mijn profiel & instellingen")

    if not st.session_state["logged_in"]:

        st.info("Log in of maak een account via de zijbalk.")

    else:

        name = st.session_state["username"]

        profile = st.session_state["profiles"][name]

        col1, col2 = st.columns([1,2])

        with col1:

            st.markdown(f"<div style='font-size:96px; white-space:pre'>{render_avatar(profile)}</div>", unsafe_allow_html=True)

            st.write("Stad:", profile.get("city", "—"))

            st.write("Leeftijd:", profile.get("age", "—"))

            st.write("Specialiteiten:", ", ".join(profile.get("specialities", [])) or "—")

            if st.button("Account verwijderen"):

                # require password confirmation

                pwd = st.text_input("Herhaal wachtwoord ter bevestiging", type="password", key="delpwd")

                if pwd:

                    if verify_login(st.session_state["profiles"], name, pwd):

                        del st.session_state["profiles"][name]

                        autosave()

                        st.session_state["logged_in"] = False

                        st.session_state["username"] = None

                        st.success("Account verwijderd")

                    else:

                        st.error("Verkeerd wachtwoord")

        with col2:

            st.subheader(profile["name"])

            st.write("Bio:", profile.get("bio",""))

            st.write("Geld: €", profile.get("money",0))

            st.write("XP:", profile.get("xp",0))

            st.write("Level:", profile.get("level",1))

            st.write("Rang:", get_rank(profile.get("xp",0)))

            if st.button("Exporteer mijn profiel"):

                st.download_button("Download JSON", data=json.dumps(profile, ensure_ascii=False, indent=2), file_name=f"profile_{profile['name']}.json")

 

# -----------------------

# Tab: Always-available earning (hard)

# -----------------------

with tab_earn:

    st.header("Verdien (altijd mogelijk — maar moeilijk)")

    if not st.session_state["logged_in"]:

        st.info("Log in om acties uit te voeren.")

    else:

        profile = st.session_state["profiles"][st.session_state["username"]]

        st.write("Deze acties zijn ontworpen om **traag** te laten groeien: kleine opbrengst, risico op verlies.")

        st.markdown("---")

        # Protection run

        st.subheader("Bescherming innen")

        st.caption("~48% kans op bescheiden winst, anders verlies.")

        if st.button("Probeer binnen te halen"):

            r = random.random()

            if r < 0.48:

                gain = random.randint(10,24)

                xp = random.randint(3,7)

                profile["money"] += gain

                profile["xp"] += xp

                save_event(profile, f"Bescherming gelukt: +€{gain}, +{xp} XP")

                st.success(f"Succes! +€{gain}, +{xp} XP")

            else:

                loss = random.randint(6,18)

                profile["money"] = max(0, profile["money"] - loss)

                profile["xp"] += 2

                save_event(profile, f"Bescherming faalde: -€{loss}, +2 XP")

                st.warning(f"Fout — verlies €{loss} maar +2 XP")

 

        st.markdown("---")

        # Small jobs

        st.subheader("Kleine klusjes")

        st.caption("Meestal kleine opbrengst, soms niks.")

        if st.button("Doe klusje"):

            if random.random() < 0.72:

                gain = random.randint(4,9)

                xp = random.randint(1,4)

                profile["money"] += gain

                profile["xp"] += xp

                save_event(profile, f"Klusje: +€{gain}, +{xp} XP")

                st.success(f"+€{gain}, +{xp} XP")

            else:

                save_event(profile, "Klusje mislukt: geen opbrengst")

                st.info("Geen opbrengst deze keer.")

 

        st.markdown("---")

        # Casino (risky)

        st.subheader("Gokken (gevaarlijk)")

        st.caption("Inzet €10 — vaak verlies, soms grote winst.")

        if st.button("Waag gok (inzet €10)"):

            if profile["money"] < 10:

                st.error("Niet genoeg geld voor inzet.")

            else:

                profile["money"] -= 10

                r = random.random()

                if r > 0.98:

                    win = 140; xp = 22

                    profile["money"] += win; profile["xp"] += xp

                    save_event(profile, f"Casino jackpot: +€{win}, +{xp} XP")

                    st.success(f"Jackpot! +€{win}, +{xp} XP")

                elif r > 0.87:

                    win = 40; xp = 8

                    profile["money"] += win; profile["xp"] += xp

                    save_event(profile, f"Casino winst: +€{win}, +{xp} XP")

                    st.info(f"Kleine winst +€{win}")

                else:

                    save_event(profile, "Casino verlies: -€10")

                    st.warning("Verloren -€10")

 

        # update level and save

profile["level"] = 1 + profile["xp"] // 200

 

# --- update speciale rangen ---

def update_special_ranks(profiles):

    sorted_profiles = sorted(profiles.values(), key=lambda x: x["xp"], reverse=True)

    for p in sorted_profiles:

        p["special_rank"] = None

    if len(sorted_profiles) > 0:

        sorted_profiles[0]["special_rank"] = "Capo di Tutti Capi"

    if len(sorted_profiles) > 1:

        sorted_profiles[1]["special_rank"] = "Sottocapo"

update_special_ranks(st.session_state["profiles"])

 

autosave()

 

# -----------------------

# Tab: Daily mission (random mini-games)

# -----------------------

with tab_mission:

    st.header("Dagelijkse missie (1× per dag — random mini-game)")

    if not st.session_state["logged_in"]:

        st.info("Log in om je dagelijkse missie te spelen.")

    else:

        profile = st.session_state["profiles"][st.session_state["username"]]

        today = date.today().isoformat()

        already = profile.get("last_mission_date") == today

        st.write("Je kunt één echte missie per dag doen. Oefenen is mogelijk, maar geeft weinig/niets.")

        if already:

            st.info("Je hebt vandaag al een missie gedaan. Je kunt oefenen (geen echte beloning).")

        st.markdown("---")

 

        # choose a random mission type for today (deterministic per-profile-per-day)

        seed = profile["name"] + today

        rng = random.Random(seed)

        mission_type = rng.choice(["guess_box", "dice_bet", "quick_quiz"])

        st.write("Missie van vandaag:", mission_type.replace("_"," ").title())

 

        # MISSION: guess_box (choose 1 of 3 boxes)

        if mission_type == "guess_box":

            st.subheader("Koffertjes-raadspel")

            st.write("Er zijn 3 koffertjes. Eén bevat geld, de anderen zijn leeg (of met tegenslag).")

            choice = st.radio("Welk koffertje open je?", ["1","2","3"], index=0, key=f"box_{profile['name']}")

            if st.button("Open koffertje"):

                correct = rng.randint(1,3)

                if int(choice) == correct:

                    # win

                    if already:

                        gain = int(rng.uniform(5,12) * 0.3)

                        xp = int(rng.uniform(2,6) * 0.3)

                        save_event(profile, f"Missie-oefening: koffertje (training) +€{gain}, +{xp} XP")

                        st.success(f"Training: +€{gain}, +{xp} XP (reduced)")

                    else:

                        gain = rng.randint(12, 32)

                        xp = rng.randint(6, 14)

                        profile["money"] += gain; profile["xp"] += xp

                        profile["last_mission_date"] = today

                        save_event(profile, f"Missie (koffertje) geslaagd: +€{gain}, +{xp} XP")

                        st.success(f"Goed geraden! +€{gain}, +{xp} XP")

                else:

                    # wrong -> penalty (small)

                    if already:

                        st.info("Training: fout, geen straf.")

                        save_event(profile, "Missie-oefening: koffertje fout (training)")

                    else:

                        loss = rng.randint(6, 18)

                        profile["money"] = max(0, profile["money"] - loss)

                        profile["last_mission_date"] = today

                        save_event(profile, f"Missie (koffertje) mislukt: -€{loss}")

                        st.error(f"Fout. Je verliest €{loss}")

 

        # MISSION: dice_bet

        elif mission_type == "dice_bet":

            st.subheader("Dobbelweddenschap")

            st.write("Raad of dobbelsteen hoog (4-6) of laag (1-3). Inzet €5.")

            bet = st.radio("Kies", ["Laag (1-3)", "Hoog (4-6)"], index=0, key=f"dice_{profile['name']}")

            if st.button("Werp dobbelsteen"):

                if profile["money"] < 5:

                    st.error("Je hebt geen €5 inzet.")

                else:

                    profile["money"] -= 5

                    roll = rng.randint(1,6)

                    st.write(f"Rol: {roll}")

                    pick_high = (bet.startswith("Hoog"))

                    won = (roll >=4) if pick_high else (roll <=3)

                    if already:

                        # training: small/no rewards

                        if won:

                            gain = 3; xp = 2

                            profile["money"] += gain; profile["xp"] += xp

                            save_event(profile, f"Missie-oefening dobbel: +€{gain}, +{xp} XP")

                            st.success(f"Training: +€{gain}, +{xp} XP")

                        else:

                            save_event(profile, "Missie-oefening dobbel: verloren")

                            st.info("Training: verloren, geen echte straf.")

                    else:

                        if won:

                            gain = rng.randint(15, 45); xp = rng.randint(6, 16)

                            profile["money"] += gain; profile["xp"] += xp

                            profile["last_mission_date"] = today

                            save_event(profile, f"Missie dobbel gewonnen: +€{gain}, +{xp} XP (roll {roll})")

                            st.success(f"Gewonnen! +€{gain}, +{xp} XP")

                        else:

                            loss = rng.randint(6,18)

                            profile["money"] = max(0, profile["money"] - loss)

                            profile["last_mission_date"] = today

                            save_event(profile, f"Missie dobbel verloren: -€{loss} (roll {roll})")

                            st.error(f"Verloren: -€{loss}")

 

        # MISSION: quick_quiz

        elif mission_type == "quick_quiz":

            st.subheader("Snelle kennisquiz")

            q_list = [

                ("Wat hoort niet in klassieke carbonara?", ["Room","Eieren","Pancetta"], "Room"),

                ("Welke stad staat bekend om pizza?", ["Napels","Milaan","Verona"], "Napels"),

                ("Hoe zeg je 'familie' in het Italiaans?", ["Famiglia","Familia","Familie"], "Famiglia")

            ]

            q = rng.choice(q_list)

            ans = st.radio(q[0], q[1], key=f"qq_{profile['name']}")

            if st.button("Antwoord versturen"):

                if ans == q[2]:

                    if already:

                        gain = int(rng.uniform(6,14)*0.3); xp = int(rng.uniform(3,8)*0.3)

                        profile["money"] += gain; profile["xp"] += xp

                        save_event(profile, f"Missie-oefening quiz: +€{gain}, +{xp} XP")

                        st.success(f"Training: +€{gain}, +{xp} XP")

                    else:

                        gain = rng.randint(14, 40); xp = rng.randint(8, 18)

                        profile["money"] += gain; profile["xp"] += xp

                        profile["last_mission_date"] = today

                        save_event(profile, f"Missie quiz geslaagd: +€{gain}, +{xp} XP")

                        st.success(f"Correct! +€{gain}, +{xp} XP")

                else:

                    if already:

                        st.info("Training: fout, geen straf.")

                        save_event(profile, "Missie-oefening quiz fout")

                    else:

                        loss = rng.randint(5,15)

                        profile["money"] = max(0, profile["money"] - loss)

                        profile["last_mission_date"] = today

                        save_event(profile, f"Missie quiz fout: -€{loss}")

                        st.error(f"Fout: -€{loss}")

 

        autosave()

 

# -----------------------

# Tab: Shop & Avatar

# -----------------------

with tab_shop:

    st.header("Shop & Avatar")

    if not st.session_state["logged_in"]:

        st.info("Log in om de shop te gebruiken.")

    else:

        profile = st.session_state["profiles"][st.session_state["username"]]

        c1, c2 = st.columns([1,2])

        with c1:

            st.subheader("Avatar")

            st.markdown(f"<div style='font-size:96px; white-space:pre'>{render_avatar(profile)}</div>", unsafe_allow_html=True)

            st.write("Gekocht:", ", ".join(profile["items"]) if profile["items"] else "Geen")

            st.markdown("---")

            new_base = st.selectbox("Basis avatar", options=BASE_AVATARS, index=BASE_AVATARS.index(profile["avatar"].get("base", BASE_AVATARS[0])))

            if st.button("Stel basis in"):

                profile["avatar"]["base"] = new_base

                save_event(profile, f"Basis avatar ingesteld op {new_base}")

                autosave()

                st.success("Basis avatar aangepast")

        with c2:

            st.subheader("Items te koop")

            st.write(f"Je geld: €{profile['money']}")

            for item, info in SHOP_ITEMS.items():

                cols = st.columns([3,1,1])

                with cols[0]:

                    st.write(f"{info['emoji']} **{item}** — €{info['price']} (+{info['xp']} XP)")

                with cols[1]:

                    st.write("✅" if item in profile["items"] else "❌")

                with cols[2]:

                    if item not in profile["items"]:

                        if st.button(f"Koop {item}", key=f"buy_{item}"):

                            if profile["money"] >= info["price"]:

                                profile["money"] -= info["price"]

                                profile["items"].append(item)

                                profile["avatar"][info["pos"]] = info["emoji"]

                                profile["xp"] += info["xp"]

                                save_event(profile, f"Gekocht {item}")

                                autosave()

                                st.success(f"{item} gekocht!")

                            else:

                                st.error("Niet genoeg geld")

 

# -----------------------

# Tab: Rank & History

# -----------------------

with tab_rank:

    st.header("Rang & Historie")

    if not st.session_state["logged_in"]:

        st.info("Log in of maak een account.")

    else:

        profile = st.session_state["profiles"][st.session_state["username"]]

        st.subheader(f"{profile['name']} — {get_rank(profile['xp'])} — Level {profile['level']}")

        st.markdown(f"<div style='font-size:72px; white-space:pre'>{render_avatar(profile)}</div>", unsafe_allow_html=True)

        st.write(f"Stad: {profile.get('city','-')} | Geld: €{profile['money']} | XP: {profile['xp']}")

        st.markdown("### Laatste acties (laatste 30)")

        for ev in list(reversed(profile.get("history", [])))[:30]:

            st.write(f"{ev['time']} — {ev['text']}")

 

# Final save

autosave()
