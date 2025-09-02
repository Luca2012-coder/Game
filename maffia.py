# la_famiglia_full_jobs.py
# Full Streamlit parody game: secure accounts, extended application, cities,
# avatar/shop, and five jobs (minigames) to earn money & XP — no click-for-cash.
#
# Run:
#   pip install streamlit
#   streamlit run la_famiglia_full_jobs.py

import streamlit as st
import json
import random
import hashlib
from datetime import date, datetime, timedelta
from pathlib import Path

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="La Famiglia — Jobs & Minigames", page_icon="🍕", layout="wide")
DATA_FILE = Path("profiles.json")

CITIES = [
    "Florence", "Bologna", "Milaan", "Sicilië", "Sardinië", "Rome", "Palermo",
    "Bari", "Turijn", "Lombardo", "Venetië", "Empoli", "Napels", "Genua",
    "Verona", "Parma", "Calabrië"
]

BASE_AVATARS = ["😎", "🕵️", "👨‍🍳", "🧑‍💼", "🧑‍🏭", "👴", "👩‍🦳"]

SHOP_ITEMS = {
    "Fedora": {"price": 400, "emoji": "🎩", "pos": "top", "xp": 30},
    "Sunglasses": {"price": 420, "emoji": "🕶️", "pos": "eyes", "xp": 35},
    "Gold Chain": {"price": 800, "emoji": "📿", "pos": "neck", "xp": 60},
    "Fancy Suit": {"price": 1600, "emoji": "🤵", "pos": "torso", "xp": 120},
    "Black Boots": {"price": 520, "emoji": "👞", "pos": "feet", "xp": 36},
    "Motorcycle": {"price": 3000, "emoji": "🏍️", "pos": "side", "xp": 200},
}

# Levels per your spec (1..8 fixed). 9 & 10 assigned by leaderboard
LEVEL_THRESHOLDS = [
    (0, 100, "Groentje"),        # Level 1
    (100, 200, "Rekruut"),      # Level 2
    (200, 400, "Piccioto"),     # Level 3
    (400, 800, "Soldato"),      # Level 4
    (800, 1600, "Capodecino"),  # Level 5
    (1600, 3200, "Capo"),       # Level 6
    (3200, 6400, "Don"),        # Level 7
    (6400, 12800, "Consiglieri")# Level 8
]

# -----------------------
# Persistence
# -----------------------
def load_profiles():
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
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
# Security helpers (simple hashed passwords)
# -----------------------
def make_salt(name: str) -> str:
    return hashlib.sha256(("salt:" + name).encode("utf-8")).hexdigest()[:16]

def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

def verify_login(profiles, name, password):
    prof = profiles.get(name)
    if not prof: return False
    salt = prof.get("salt", make_salt(name))
    return prof.get("password_hash") == hash_password(password, salt)

# -----------------------
# Model helpers
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
        "admitted": False,
        "last_application_dt": None,
        "money": 80,  # small start
        "xp": 0,
        "level": 1,
        "items": [],
        "avatar": {"base": random.choice(BASE_AVATARS), "top":"", "eyes":"", "neck":"", "torso":"", "feet":"", "side":""},
        "history": [],
        "last_daily_dt": None
    }

def save_event(profile, text):
    profile.setdefault("history", []).append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text": text})
    autosave()

# -----------------------
# Ranking logic including unique top 2
# -----------------------
def compute_base_level(xp):
    for i, (lo, hi, title) in enumerate(LEVEL_THRESHOLDS, start=1):
        if lo <= xp < hi:
            return i, title
    return len(LEVEL_THRESHOLDS), LEVEL_THRESHOLDS[-1][2]

def assign_dynamic_ranks(profiles):
    # return dict name->(level,title) with top1=Capo di Tutti Capi, top2=Sottocapo
    items = list(profiles.values())
    # sort by xp desc then created asc
    items.sort(key=lambda p: (-p.get("xp",0), p.get("created","")))
    rank_map = {}
    for p in items:
        lvl, title = compute_base_level(p.get("xp",0))
        rank_map[p["name"]] = [lvl, title]
    if len(items) >= 1:
        rank_map[items[0]["name"]] = [10, "Capo di Tutti Capi"]
    if len(items) >= 2:
        rank_map[items[1]["name"]] = [9, "Sottocapo"]
    return rank_map

def update_profile_level(profile, rank_map):
    lvl, title = rank_map.get(profile["name"], compute_base_level(profile.get("xp",0)))
    profile["level"] = lvl

# -----------------------
# Game: Jobs / Minigames
# - Pizzabakker: order matching (skill) → reward scaled by accuracy
# - Chauffeur: route choice + small randomness, skill via choosing best route
# - Clubeigenaar: mixing orders quickly (turn-based choices)
# - Corrupte Politie (parody): negotiation puzzle (choose bribe value in range)
# - Sollicitatieafnemer: evaluate applicants (choose accept/reject based on clues)
# -----------------------

# Persistent state init
if "profiles" not in st.session_state:
    st.session_state["profiles"] = load_profiles()
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# -----------------------
# Sidebar: Registration / Login with extended application
# -----------------------
st.sidebar.title("La Famiglia — Account")

if not st.session_state["logged_in"]:
    st.sidebar.subheader("Solliciteer / Maak account")
    with st.sidebar.form("apply"):
        uname = st.text_input("Gebruikersnaam")
        pwd = st.text_input("Wachtwoord", type="password")
        city = st.selectbox("Stad", CITIES)
        age = st.number_input("Leeftijd", min_value=16, max_value=99, value=25)
        bio = st.text_area("Korte bio")
        specialities = st.multiselect("Specialiteiten", ["Pizzabakken","Chauffeur","Clubeigenaar","Corrupte Politie","Sollicitatieafnemer","Logistiek","Financieel inzicht"])
        # Extended application fields (not quiz style)
        employment_history = st.text_area("Werkervaring (korte omschrijving)")
        references = st.text_input("Referenties (fictief ok)")
        apply_submit = st.form_submit_button("Verstuur sollicitatie / maak account")
    if apply_submit:
        if not uname.strip() or not pwd:
            st.sidebar.error("Naam en wachtwoord verplicht.")
        elif uname in st.session_state["profiles"]:
            st.sidebar.error("Gebruikersnaam bestaat al.")
        else:
            prof = new_profile_struct(uname.strip(), pwd, city, age, bio, specialities)
            prof["employment_history"] = employment_history
            prof["references"] = references
            prof["last_application_dt"] = datetime.now().isoformat(timespec="seconds")
            # Evaluate acceptance: not always accepted
            score = 0
            score += min(len(employment_history)//40, 4)
            score += min(len(bio)//50, 3)
            score += min(len(specialities), 3)
            if references.strip(): score += 1
            # city flavor
            if city in ["Napels","Sicilië","Palermo"]: score += 1
            roll = random.randint(0,6)
            admitted = (score + roll) >= 5
            prof["admitted"] = admitted
            st.session_state["profiles"][uname.strip()] = prof
            autosave()
            if admitted:
                st.sidebar.success("Sollicitatie geaccepteerd — log nu in.")
            else:
                st.sidebar.warning("Afgekeurd — probeer later opnieuw met verbeterde motivatie/ervaring.")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Login")
    with st.sidebar.form("login"):
        login_name = st.text_input("Naam", key="login_name")
        login_pass = st.text_input("Wachtwoord", type="password", key="login_pass")
        login_btn = st.form_submit_button("Login")
    if login_btn:
        if verify_login(st.session_state["profiles"], login_name.strip(), login_pass):
            st.session_state["logged_in"] = True
            st.session_state["username"] = login_name.strip()
            st.sidebar.success("Ingelogd")
        else:
            st.sidebar.error("Login mislukt — controleer naam/wachtwoord.")
else:
    st.sidebar.markdown(f"**Ingelogd als:** {st.session_state['username']}")
    if st.sidebar.button("Uitloggen"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.sidebar.success("Uitgelogd")

st.sidebar.markdown("---")
st.sidebar.info("Wachtwoorden worden lokaal gehashed. Deel ze niet.")

# recompute ranks
rank_map = assign_dynamic_ranks(st.session_state["profiles"])

# -----------------------
# Main layout tabs
# -----------------------
tab_profile, tab_jobs, tab_daily, tab_shop, tab_board = st.tabs([
    "📝 Profiel", "🧰 Banen", "🎯 Dagelijkse missie", "🛍️ Shop & Avatar", "🏆 Leaderboard"
])

# -----------------------
# Helper: render avatar string
# -----------------------
def render_avatar(profile):
    a = profile["avatar"]
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
# PROFILE TAB
# -----------------------
with tab_profile:
    st.header("Mijn profiel")
    if not st.session_state["logged_in"]:
        st.info("Log in of solliciteer via de zijbalk.")
    else:
        p = st.session_state["profiles"][st.session_state["username"]]
        update_profile_level(p, rank_map)
        col1, col2 = st.columns([1,2])
        with col1:
            st.markdown(f"<div style='font-size:96px; white-space:pre'>{render_avatar(p)}</div>", unsafe_allow_html=True)
            st.write("Stad:", p.get("city","-"))
            st.write("Geld: €", p.get("money",0))
            st.write("XP:", p.get("xp",0))
            st.write("Level:", p.get("level",1))
            # dynamic title from rank_map
            title = rank_map.get(p["name"], [None, None])[1]
            st.write("Rang:", title)
        with col2:
            st.subheader(p["name"])
            st.write("Bio:", p.get("bio",""))
            st.write("Specialiteiten:", ", ".join(p.get("specialities",[])) or "-")
            st.markdown("### Laatste acties")
            for ev in list(reversed(p.get("history", [])))[:20]:
                st.write(f"{ev['time']} — {ev['text']}")

# -----------------------
# JOBS TAB (all minigames)
# -----------------------
with tab_jobs:
    st.header("Banen & Minigames — verdien door skill")
    if not st.session_state["logged_in"]:
        st.info("Log in om banen te spelen.")
    else:
        p = st.session_state["profiles"][st.session_state["username"]]
        if not p.get("admitted", False):
            st.warning("Je bent nog niet toegelaten — rond je sollicitatie af of wacht op toelating.")
        # show jobs selection
        job = st.selectbox("Kies baan", ["Pizzabakker","Chauffeur","Clubeigenaar","Corrupte Politie (parodie)","Sollicitatieafnemer"])
        st.markdown("---")

        # ---------- Pizzabakker ----------
        if job == "Pizzabakker":
            st.subheader("🍕 Pizzabakker — maak en verkoop pizza's")
            st.write("Je krijgt bestellingen. Kies de juiste ingrediënten. Meer correcte ingrediënten → hogere beloning.")
            # available pizzas
            PIZZAS = {
                "Margherita": {"need": {"Tomaat","Mozzarella","Basilicum"}, "opts": {"Olijfolie"}},
                "Pepperoni": {"need": {"Tomaat","Mozzarella","Pepperoni"}, "opts": {"Olijfolie","Oregano"}},
                "Quattro Formaggi": {"need": {"Mozzarella","Gorgonzola","Parmezaan","Fontina"}, "opts": set()},
                "Vegetariana": {"need": {"Tomaat","Mozzarella","Paprika","Champignons","Ui"}, "opts": {"Rucola"}}
            }
            pantry = sorted(list(set().union(*[v["need"]|v["opts"] for v in PIZZAS.values()]) | {"Ananas","Tonijn","Olijven","Chili-olie"}))
            # create order(s)
            orders_count = st.number_input("Aantal bestellingen (1-4)", min_value=1, max_value=4, value=1)
            order_choices = st.multiselect("Kies welke pizza's besteld worden (random selectie als je niets kiest)", list(PIZZAS.keys()), default=None)
            if not order_choices:
                # generate random
                order_choices = random.choices(list(PIZZAS.keys()), k=orders_count)
            else:
                # respect count
                order_choices = (order_choices * ((orders_count//len(order_choices))+1))[:orders_count]
            st.write("Bestellingen:", ", ".join(order_choices))
            # UI for ingredient selection per order
            results = {}
            for i, pizza in enumerate(order_choices, start=1):
                st.markdown(f"**Bestelling {i}: {pizza}**")
                chosen = st.multiselect(f"Ingrediënten voor {pizza}", options=pantry, key=f"pz_{i}")
                results[pizza + f"#{i}"] = set(chosen)
            if st.button("Bak en verkoop"):
                total_correct = 0
                total_wrong = 0
                total_need = 0
                for key, chosen in results.items():
                    pizza_name = key.split("#")[0]
                    spec = PIZZAS[pizza_name]
                    need = spec["need"]
                    correct = len(chosen & need)
                    wrong = len(chosen - (need | spec["opts"]))
                    total_correct += correct
                    total_wrong += wrong
                    total_need += len(need)
                # scoring: correct vs wrong, penalties for extras
                score = max(0, total_correct - total_wrong)
                # reward scales with score but modestly (avoid too fast leveling)
                money = score * 5
                xp = score * 4
                # small bonus if perfect all
                if total_correct == total_need and total_wrong == 0:
                    money += 10; xp += 6
                if score == 0:
                    st.error("Klanten boos: je hebt niks goed gedaan. Geen verkoop.")
                    save_event(p, "Pizzabakker: gefaald (geen correcte ingrediënten)")
                else:
                    p["money"] += money
                    p["xp"] += xp
                    save_event(p, f"Pizzabakker: score {score} → +€{money}, +{xp} XP")
                    st.success(f"Verkocht! +€{money}, +{xp} XP (score {score})")
                autosave()

        # ---------- Chauffeur ----------
        elif job == "Chauffeur":
            st.subheader("🚗 Chauffeur — route- & timing keuze (strategie)")
            st.write("Kies een route; elke route heeft risico (files, controles). Kies slim.")
            routes = [
                {"name":"Langzaam maar veilig (lange afstand)", "dist": 24, "traffic":"laag", "risk":"laag"},
                {"name":"Snel door centrum (korte afstand)", "dist": 10, "traffic":"hoog", "risk":"middel"},
                {"name":"Snelle ringweg (omweg)", "dist": 16, "traffic":"middel", "risk":"laag-middel"},
            ]
            choice = st.selectbox("Kies route", [r["name"] for r in routes])
            hurry = st.slider("Rij haastig? (meer snelheid = hoger risico)", 0, 2, 1)
            if st.button("Begin rit"):
                r = next(x for x in routes if x["name"] == choice)
                rng = random.Random(f"{p['name']}-{datetime.now().isoformat()}")
                base_time = r["dist"]
                traffic_pen = {"laag": rng.randint(0,2), "middel": rng.randint(2,6), "hoog": rng.randint(5,12)}.get(r["traffic"], 4)
                risk_factor = {"laag": 0.08, "laag-middel":0.15, "middel":0.25, "hoog":0.35}.get(r["risk"], 0.2)
                # hurry decreases time but increases mishap chance
                hurry_effect = (1 - 0.15*hurry)
                mishap = rng.random() < (risk_factor + 0.07*hurry)
                delay = int(base_time * (1 + traffic_pen/10) / hurry_effect)
                if mishap:
                    # mishap penalty: delay + possible fine
                    fine = rng.randint(5, 25)
                    p["money"] = max(0, p["money"] - fine)
                    msg = f"Politiecontrole / probleem: boete €{fine}, vertraging {delay}min."
                    p["xp"] += 2
                    save_event(p, "Chauffeur: " + msg)
                    st.warning(msg)
                else:
                    # good run
                    payout = max(6, int(40 - delay)//3)
                    xp = max(3, int(12 - delay//5))
                    p["money"] += payout
                    p["xp"] += xp
                    save_event(p, f"Chauffeur: route {choice} → +€{payout}, +{xp} XP (vertraging {delay})")
                    st.success(f"Rit geslaagd: +€{payout}, +{xp} XP (vertraging {delay}min)")
                autosave()

        # ---------- Clubeigenaar ----------
        elif job == "Clubeigenaar":
            st.subheader("🍸 Clubeigenaar — mixen en management (timed/turn-based)")
            st.write("Je ontvangt bestellingen (drinks). Kies de juiste combinatie per bestelling. Meer goede mixen → hogere omzet.")
            # recipes
            RECIPES = {
                "Vodka-Cola": {"need":["Vodka","Cola"]},
                "Mojito": {"need":["Rum","Lime","Mint","Soda"]},
                "Negroni": {"need":["Gin","Vermouth","Campari"]},
                "Spritz": {"need":["Prosecco","Aperol","Soda"]}
            }
            pantry = sorted(list(set().union(*[v["need"] for v in RECIPES.values()]) | {"Orange","Cherry","Ice"}))
            orders = random.choices(list(RECIPES.keys()), k=3)
            st.write("Bestellingen:", ", ".join(orders))
            choices = {}
            for i, ord_name in enumerate(orders, start=1):
                choices[ord_name+f"#{i}"] = st.multiselect(f"{ord_name} (bestelling {i})", options=pantry, key=f"club_{i}")
            if st.button("Serveer nacht"):
                correct = 0; wrong = 0
                for key, chosen in choices.items():
                    name = key.split("#")[0]
                    need = set(RECIPES[name]["need"])
                    chosen_set = set(chosen)
                    corr = len(chosen_set & need)
                    bad = len(chosen_set - need)
                    correct += corr
                    wrong += bad
                score = max(0, correct - wrong)
                money = score * 6
                xp = score * 3
                if score == 0:
                    st.error("Nacht flop: klanten ontevreden, geen inkomsten.")
                    save_event(p, "Clubeigenaar: Nacht flop")
                else:
                    p["money"] += money
                    p["xp"] += xp
                    save_event(p, f"Clubeigenaar: +€{money}, +{xp} XP (score {score})")
                    st.success(f"Nacht afgerond: +€{money}, +{xp} XP (score {score})")
                autosave()

        # ---------- Corrupte Politie (parodie puzzle) ----------
        elif job == "Corrupte Politie (parodie)":
            st.subheader("🗂️ Corrupte Politie (parodie) — onderhandelingspuzzel")
            st.write("Dit is een fictieve puzzel: kies een 'omkoopbedrag' netjes binnen een redelijke marge. Te laag = geweigerd, te hoog = verlies.")
            base_value = random.randint(40,160)
            st.write(f"Situatie-waarde (hint): tussen ~{int(base_value*0.6)} en {int(base_value*1.6)}")
            bid = st.number_input("Bied (€)", min_value=0, max_value=1000, value=int(base_value))
            if st.button("Onderhandel"):
                rng = random.Random(f"{p['name']}-{datetime.now().isoformat()}")
                acceptable_low = int(base_value * 0.7)
                acceptable_high = int(base_value * 1.3)
                if acceptable_low <= bid <= acceptable_high:
                    # success, profit margin (you get a cut)
                    cut = int(bid * 0.35)  # you keep a cut (fictional playful)
                    xp = rng.randint(6, 16)
                    p["money"] += cut
                    p["xp"] += xp
                    save_event(p, f"CorrPol: succesvolle onderhand: +€{cut}, +{xp} XP (bied {bid})")
                    st.success(f"Onderhandeling geslaagd: je neemt €{cut} mee, +{xp} XP (fictie/puzzel).")
                elif bid < acceptable_low:
                    # refused; no reward, small xp
                    p["xp"] += 1
                    save_event(p, f"CorrPol: geweigerd (bied te laag: {bid})")
                    st.warning("Weigering — bied te laag. Geen beloning.")
                else:
                    # bid too high: you lose money (overschot suspect)
                    loss = min(p["money"], int((bid - acceptable_high) * 0.5))
                    p["money"] -= loss
                    save_event(p, f"CorrPol: teveel betaald - verlies €{loss} (bied {bid})")
                    st.error(f"Je overbetaalde en verloor €{loss}.")
                autosave()

        # ---------- Sollicitatieafnemer ----------
        elif job == "Sollicitatieafnemer":
            st.subheader("📋 Sollicitatieafnemer — beoordeel kandidaten")
            st.write("Je krijgt 3 korte profielen. Kies wie je aanneemt. Goede keuze → XP; foute keuze → mogelijk verlies (reputatie).")
            # generate 3 candidate cards with hints (skill tags)
            CAND_SKILLS = ["Pizzabakken","Chauffeur","Clubeigenaar","Corrupte Politie","PR","Logistiek","Financieel inzicht"]
            candidates = []
            rng = random.Random(f"cand-{p['name']}-{datetime.now().isoformat()}")
            for i in range(3):
                name = f"Pers_{rng.randint(100,999)}"
                skills = rng.sample(CAND_SKILLS, k=rng.randint(1,3))
                years = rng.randint(0,12)
                cand = {"name": name, "skills": skills, "years": years}
                candidates.append(cand)
            picks = []
            for i, cnd in enumerate(candidates, start=1):
                st.markdown(f"**{cnd['name']}** — vaardigheden: {', '.join(cnd['skills'])} — {cnd['years']} jaar ervaring")
                acc = st.checkbox(f"Aanstellen {cnd['name']}", key=f"app_{i}")
                if acc:
                    picks.append(cnd)
            if st.button("Beoordeel en beslis"):
                # scoring: prefer candidates who match job specialties of your profile
                good = 0; bad = 0
                for c in picks:
                    match = len(set(c["skills"]) & set(p.get("specialities", [])))
                    if match > 0 or c["years"] >= 3:
                        good += 1
                    else:
                        bad += 1
                if good > bad:
                    xp = good * 8
                    p["xp"] += xp
                    save_event(p, f"Sollicitatieafnemer: juiste keuze → +{xp} XP")
                    st.success(f"Goede aanstellingen: +{xp} XP")
                else:
                    loss = min(20, max(0, bad*8))
                    p["money"] = max(0, p["money"] - loss)
                    save_event(p, f"Sollicitatieafnemer: slechte keuze → verlies €{loss}")
                    st.error(f"Slechte aanstellingen: je reputatie kost je €{loss} (fictief).")
                autosave()

        # update level from rank map
        update_profile_level(p, rank_map)

# -----------------------
# Daily mission (random mini-game, 1x/day)
# -----------------------
with tab_daily:
    st.header("Dagelijkse missie (1× per dag)")
    if not st.session_state["logged_in"]:
        st.info("Log in om je dagelijkse missie te spelen.")
    else:
        p = st.session_state["profiles"][st.session_state["username"]]
        today = date.today().isoformat()
        done = p.get("last_daily_dt") == today
        st.write("Elke dag 1 missie: variërend van gok/quiz tot mini-puzzels. Oefenen mag, echte beloning maar 1x per dag.")
        if done:
            st.info("Vandaag is al gedaan — oefenen is mogelijk maar levert weinig op.")
        # deterministic choice per-profile-per-day
        rng = random.Random(p["name"] + today)
        mission = rng.choice(["order_focus","timed_guess","combo_quiz"])
        st.write("Missie:", mission.replace("_"," ").title())
        if mission == "order_focus":
            st.write("Je moet een sequence van 4 items in de juiste volgorde kiezen (memory-like).")
            seq = rng.sample(["A","B","C","D","E","F"], 4)
            # show sequence briefly (we simulate: user must type exact sequence)
            st.write("Kijk goed naar de volgorde — onthoud deze:")
            st.write(" ".join(seq))
            guess = st.text_input("Typ de volgorde van letters (gescheiden met spaties)").strip().upper()
            if st.button("Verstuur volgorde"):
                if not done and guess == " ".join(seq):
                    gain = rng.randint(18, 36); xp = rng.randint(9, 18)
                    p["money"] += gain; p["xp"] += xp; p["last_daily_dt"] = today
                    save_event(p, f"Dagmissie volgorde gelukt: +€{gain}, +{xp} XP")
                    st.success(f"Goed onthouden! +€{gain}, +{xp} XP")
                else:
                    if not done:
                        p["last_daily_dt"] = today
                        p["money"] += 2; p["xp"] += 1
                        save_event(p, "Dagmissie volgorde gemist: training +€2 +1 XP")
                        st.info("Fout of oefenmodus: training reward +€2 +1XP")
                    else:
                        st.info("Training voltooid.")
                autosave()
        elif mission == "timed_guess":
            st.write("Kies welke 'case' (1..3) volgens jouw gevoel winstgevend is. Kans en beloning variëren.")
            opt = st.radio("Welke case kies je?", ["1","2","3"], index=0)
            if st.button("Voer missie uit"):
                if done:
                    st.info("Training: kleine beloning of niets.")
                    p["money"] += 2; p["xp"] += 1; save_event(p, "Dagmissie oefening (timed_guess)")
                else:
                    pick = rng.randint(1,3)
                    if int(opt) == pick:
                        gain = rng.randint(14, 38); xp = rng.randint(7, 16)
                        p["money"] += gain; p["xp"] += xp; p["last_daily_dt"] = today
                        save_event(p, f"Dagmissie case gewonnen: +€{gain}, +{xp} XP")
                        st.success(f"Goed gekozen! +€{gain}, +{xp} XP")
                    else:
                        loss = rng.randint(6, 18)
                        p["money"] = max(0, p["money"] - loss); p["last_daily_dt"] = today
                        save_event(p, f"Dagmissie case verloren: -€{loss}")
                        st.warning(f"Verloren: -€{loss}")
                autosave()
        elif mission == "combo_quiz":
            st.write("Een korte kennisvraag — goed = beloning, fout = kleine straf.")
            qs = [
                ("Welke stad is beroemd om pizza?", ["Napels","Milaan","Rome"], "Napels"),
                ("Wat hoort in Margherita?", ["Tomaat","Sushi","Banaan"], "Tomaat"),
            ]
            q, opts, ans = rng.choice(qs)
            pick = st.radio(q, opts, key=f"dq_{p['name']}")
            if st.button("Antwoord"):
                if done:
                    st.info("Training: geen echte beloning.")
                    p["xp"] += 1; save_event(p, "Dagmissie oefening quiz")
                else:
                    if pick == ans:
                        gain = rng.randint(12, 30); xp = rng.randint(6, 14)
                        p["money"] += gain; p["xp"] += xp; p["last_daily_dt"] = today
                        save_event(p, f"Dagmissie quiz goed: +€{gain}, +{xp} XP")
                        st.success(f"Goed! +€{gain}, +{xp} XP")
                    else:
                        loss = rng.randint(5, 15)
                        p["money"] = max(0, p["money"] - loss); p["last_daily_dt"] = today
                        save_event(p, f"Dagmissie quiz fout: -€{loss}")
                        st.error(f"Fout: -€{loss}")
                autosave()

# -----------------------
# SHOP & AVATAR
# -----------------------
with tab_shop:
    st.header("Shop & Avatar")
    if not st.session_state["logged_in"]:
        st.info("Log in om te shoppen.")
    else:
        p = st.session_state["profiles"][st.session_state["username"]]
        update_profile_level(p, rank_map)
        c1, c2 = st.columns([1,2])
        with c1:
            st.markdown(f"<div style='font-size:96px; white-space:pre'>{render_avatar(p)}</div>", unsafe_allow_html=True)
            st.write("Geld: €", p.get("money",0))
            new_base = st.selectbox("Basis avatar", options=BASE_AVATARS, index=BASE_AVATARS.index(p["avatar"].get("base", BASE_AVATARS[0])))
            if st.button("Stel basis in"):
                p["avatar"]["base"] = new_base
                save_event(p, f"Basis avatar ingesteld op {new_base}")
                autosave(); st.success("Basis avatar aangepast")
        with c2:
            st.subheader("Items te koop")
            for item, info in SHOP_ITEMS.items():
                cols = st.columns([3,1,1])
                with cols[0]: st.write(f"{info['emoji']} **{item}** — €{info['price']} (+{info['xp']} XP)")
                with cols[1]: st.write("✅" if item in p["items"] else "❌")
                with cols[2]:
                    if item not in p["items"]:
                        if st.button(f"Koop {item}", key=f"buy_{item}"):
                            if p["money"] >= info["price"]:
                                p["money"] -= info["price"]
                                p["items"].append(item)
                                p["avatar"][info["pos"]] = info["emoji"]
                                p["xp"] += info["xp"]
                                save_event(p, f"Gekocht {item}")
                                autosave(); st.success(f"{item} gekocht!")
                            else:
                                st.error("Niet genoeg geld")

# -----------------------
# LEADERBOARD / ALL ACCOUNTS
# -----------------------
with tab_board:
    st.header("Alle accounts & leaderboard")
    profiles = st.session_state["profiles"]
    # build rows sorted by xp desc
    rows = []
    for name, prof in profiles.items():
        lvl, title = rank_map.get(name, compute_base_level(prof.get("xp",0)))
        rows.append({
            "Naam": name,
            "Stad": prof.get("city","-"),
            "XP": prof.get("xp",0),
            "Level": lvl,
            "Rang": title,
            "Geld": prof.get("money",0),
            "Toegelaten": "Ja" if prof.get("admitted", False) else "Nee",
            "Aangemaakt": prof.get("created","")
        })
    rows.sort(key=lambda r: (-r["XP"], r["Aangemaakt"]))
    st.dataframe(rows, use_container_width=True)

# -----------------------
# Finalization
# -----------------------
# always update dynamic ranks & persist
for prof in st.session_state["profiles"].values():
    update_profile_level(prof, rank_map)
autosave()
