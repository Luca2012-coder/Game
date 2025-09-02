# la_famiglia_jobs_game.py
# Streamlit parody game: secure accounts, expanded application with acceptance,
# cities, jobs with mini-games (Pizzabakker/Clubeigenaar/Chauffeur/Corrupte Politie),
# persistent storage, leaderboard, and custom rank system with unique Level 9/10.
#
# Run:
#   pip install streamlit
#   streamlit run la_famiglia_jobs_game.py

import streamlit as st
import json
import random
import hashlib
from datetime import date, datetime, timedelta
from pathlib import Path

# -----------------------
# App config
# -----------------------
st.set_page_config(page_title="La Famiglia — Jobs & Ranks", page_icon="🍕", layout="wide")
DATA_FILE = Path("profiles.json")

CITIES = [
    "Florence", "Bologna", "Milaan", "Sicilië", "Sardinië", "Rome", "Palermo",
    "Bari", "Turijn", "Lombardo", "Venetië", "Empoli", "Napels", "Genua",
    "Verona", "Parma", "Calabrië"
]

BASE_AVATARS = ["😎", "🕵️", "👨‍🍳", "🧑‍💼", "🧑‍🏭", "👴", "👩‍🦳"]
SHOP_ITEMS = {
    "Fedora": {"price": 300, "emoji": "🎩", "pos": "top", "xp": 18},
    "Sunglasses": {"price": 350, "emoji": "🕶️", "pos": "eyes", "xp": 22},
    "Gold Chain": {"price": 600, "emoji": "📿", "pos": "neck", "xp": 44},
    "Fancy Suit": {"price": 1200, "emoji": "🤵", "pos": "torso", "xp": 90},
    "Black Boots": {"price": 420, "emoji": "👞", "pos": "feet", "xp": 24},
    "Motorcycle": {"price": 2200, "emoji": "🏍️", "pos": "side", "xp": 150},
}

# Rank thresholds (Levels 1–8 are fixed; 9–10 are assigned by leaderboard)
LEVELS = [
    (0, 100, "Groentje"),            # Level 1
    (100, 200, "Rekruut"),           # Level 2
    (200, 400, "Piccioto"),          # Level 3
    (400, 800, "Soldato"),           # Level 4
    (800, 1600, "Capodecino"),       # Level 5
    (1600, 3200, "Capo"),            # Level 6
    (3200, 6400, "Don"),             # Level 7
    (6400, 12800, "Consiglieri"),    # Level 8
    # Level 9 & 10 below via leaderboard
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
            # backup corrupt file
            backup = DATA_FILE.with_suffix(".broken.json")
            DATA_FILE.replace(backup)
            return {}
    return {}

def save_profiles(profiles):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Opslaan mislukt: {e}")

def autosave():
    save_profiles(st.session_state["profiles"])

# -----------------------
# Security helpers
# -----------------------
def make_salt(name: str) -> str:
    return hashlib.sha256(("salt:" + name).encode("utf-8")).hexdigest()[:16]

def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

def verify_login(profiles, name, password):
    prof = profiles.get(name)
    if not prof:
        return False
    salt = prof.get("salt", make_salt(name))
    return prof.get("password_hash") == hash_password(password, salt)

# -----------------------
# Model helpers
# -----------------------
def new_profile_struct(name, password, city, age, bio, motivations, strengths, references):
    salt = make_salt(name)
    return {
        "name": name,
        "password_hash": hash_password(password, salt),
        "salt": salt,
        "city": city,
        "age": age,
        "bio": bio,
        "motivations": motivations,
        "strengths": strengths,
        "references": references,
        "created": datetime.now().isoformat(timespec="seconds"),

        # Application gate
        "admitted": False,
        "last_application_dt": None,

        # Progression
        "money": 80,   # heel bescheiden start
        "xp": 0,
        "level": 1,
        "items": [],
        "avatar": {"base": random.choice(BASE_AVATARS), "top":"", "eyes":"", "neck":"", "torso":"", "feet":"", "side":""},
        "history": [],
        "last_daily_dt": None
    }

def save_event(profile, text):
    profile.setdefault("history", []).append(
        {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text": text}
    )

def render_avatar(profile):
    a = profile["avatar"]
    lines = [
        a.get("top",""),
        f"{a.get('base','😎')}{a.get('eyes','')}",
        a.get("neck",""),
        a.get("torso",""),
        a.get("feet",""),
    ]
    side = a.get("side","")
    avatar_str = "\n".join(lines)
    if side:
        avatar_str = avatar_str.replace("\n", f" {side}\n")
    return avatar_str

# ----- Rank logic with unique Level 9 & 10 -----
def compute_base_level_and_title(xp: int):
    for i, (lo, hi, title) in enumerate(LEVELS, start=1):
        if lo <= xp < hi:
            return i, title
    # >= LEVELS[-1][1] => Level 8 by default, title "Consiglieri"
    return 8, "Consiglieri"

def assign_dynamic_ranks(profiles_dict):
    """Return mapping name -> (level, title) with unique Level 9 and 10."""
    # Sort by XP desc, then by created (older first breaks ties consistently)
    all_profiles = list(profiles_dict.values())
    all_profiles.sort(key=lambda p: (-p.get("xp",0), p.get("created","")))
    # Base rank first
    rank_map = {}
    for p in all_profiles:
        lvl, title = compute_base_level_and_title(p.get("xp",0))
        rank_map[p["name"]] = [lvl, title]
    # Top 2 override (if there are at least 2 players)
    if len(all_profiles) >= 1:
        top = all_profiles[0]["name"]
        rank_map[top] = [10, "Capo di Tutti Capi"]
    if len(all_profiles) >= 2:
        second = all_profiles[1]["name"]
        rank_map[second] = [9, "Sottocapo"]
    return rank_map

def update_profile_level_title(profile, rank_map):
    lvl, title = rank_map.get(profile["name"], compute_base_level_and_title(profile.get("xp",0)))
    profile["level"] = lvl
    # we show title dynamically in UI; no need to store permanent title

# -----------------------
# Session init
# -----------------------
if "profiles" not in st.session_state:
    st.session_state["profiles"] = load_profiles()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# -----------------------
# Sidebar: create + login
# -----------------------
st.sidebar.title("Account")
if not st.session_state["logged_in"]:
    st.sidebar.subheader("Sollicitatie (account aanmaken)")
    with st.sidebar.form("create"):
        new_name = st.text_input("Gebruikersnaam")
        new_pass = st.text_input("Wachtwoord", type="password")
        city = st.selectbox("Kies je stad", CITIES)
        age = st.number_input("Leeftijd", min_value=16, max_value=99, value=22)
        bio = st.text_area("Korte intro/bio")
        motivations = st.text_area("Motivatie: waarom wil je erbij?")
        strengths = st.text_area("Sterke punten / ervaring")
        references = st.text_input("Referentie (naam/telefoon — fictief mag)")
        submit = st.form_submit_button("Aanvragen")

    if submit:
        if not new_name.strip() or not new_pass:
            st.sidebar.error("Naam en wachtwoord verplicht.")
        elif new_name in st.session_state["profiles"]:
            st.sidebar.error("Gebruikersnaam bestaat al.")
        else:
            prof = new_profile_struct(new_name.strip(), new_pass, city, age, bio, motivations, strengths, references)
            # mark application time
            prof["last_application_dt"] = datetime.now().isoformat(timespec="seconds")
            # Evaluate admission (not always accepted) — score + randomness
            score = 0
            # longer motivations & strengths help
            score += min(len(motivations.strip()) // 40, 5)
            score += min(len(strengths.strip()) // 40, 5)
            # references give small boost
            if references.strip():
                score += 1
            # certain cities purely cosmetic but tiny flavor boost
            if city in ["Napels","Sicilië","Palermo"]:
                score += 1
            # randomness
            roll = random.randint(0, 6)
            admitted = (score + roll) >= 5  # ~niet altijd toegelaten
            prof["admitted"] = admitted
            st.session_state["profiles"][new_name.strip()] = prof
            autosave()
            if admitted:
                st.sidebar.success("Sollicitatie geaccepteerd! Log nu in hieronder.")
            else:
                st.sidebar.warning("Sollicitatie afgewezen. Probeer het opnieuw na 24 uur (verbeter je motivatie/sterke punten).")

    st.sidebar.subheader("Inloggen")
    with st.sidebar.form("login"):
        login_name = st.text_input("Naam")
        login_pass = st.text_input("Wachtwoord", type="password")
        login = st.form_submit_button("Login")
    if login:
        if verify_login(st.session_state["profiles"], login_name.strip(), login_pass):
            st.session_state["logged_in"] = True
            st.session_state["username"] = login_name.strip()
            st.sidebar.success("Ingelogd")
        else:
            st.sidebar.error("Login mislukt.")

else:
    st.sidebar.markdown(f"**Ingelogd als:** {st.session_state['username']}")
    if st.sidebar.button("Uitloggen"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None

st.sidebar.markdown("---")
st.sidebar.info("Wachtwoorden worden lokaal gehashed. Deel je wachtwoord niet.")

# -----------------------
# Rank map for this render (for unique Level 9/10)
# -----------------------
rank_map = assign_dynamic_ranks(st.session_state["profiles"])

# -----------------------
# Tabs
# -----------------------
tab_profile, tab_jobs, tab_mission, tab_shop, tab_board = st.tabs([
    "📝 Profiel", "🧰 Banen & Minigames", "🎯 Dagelijkse missie", "🛍️ Shop & Avatar", "🏆 Alle accounts"
])

# -----------------------
# Profile tab
# -----------------------
with tab_profile:
    st.header("Mijn profiel")
    if not st.session_state["logged_in"]:
        st.info("Log in of solliciteer via de zijbalk.")
    else:
        p = st.session_state["profiles"][st.session_state["username"]]
        # If not admitted, show re-apply gate with cooldown
        if not p.get("admitted", False):
            st.warning("Je sollicitatie is (nog) niet geaccepteerd. Je kunt (na 24 uur) opnieuw solliciteren met een verbeterde motivatie.")
            last_dt = p.get("last_application_dt")
            can_reapply = True
            if last_dt:
                last = datetime.fromisoformat(last_dt)
                can_reapply = datetime.now() - last >= timedelta(hours=24)
            with st.form("reapply"):
                st.subheader("Heraanvraag")
                motivations = st.text_area("Motivatie (uitgebreider is beter)")
                strengths = st.text_area("Sterke punten (ervaring, vaardigheden)")
                references = st.text_input("Referenties")
                resubmit = st.form_submit_button("Dien opnieuw in")
            if resubmit:
                if not can_reapply:
                    st.error("Je kunt pas na 24 uur opnieuw solliciteren.")
                else:
                    score = 0
                    score += min(len(motivations.strip()) // 40, 5)
                    score += min(len(strengths.strip()) // 40, 5)
                    if references.strip(): score += 1
                    roll = random.randint(0, 6)
                    admitted = (score + roll) >= 5
                    p["motivations"] = motivations
                    p["strengths"] = strengths
                    p["references"] = references
                    p["last_application_dt"] = datetime.now().isoformat(timespec="seconds")
                    p["admitted"] = admitted
                    save_event(p, "Heraanvraag verstuurd (geaccepteerd)" if admitted else "Heraanvraag verstuurd (afgewezen)")
                    autosave()
                    if admitted:
                        st.success("Gefeliciteerd! Je bent toegelaten.")
                    else:
                        st.warning("Helaas, nog niet toegelaten. Probeer later opnieuw.")
        # Show profile card
        update_profile_level_title(p, rank_map)
        col1, col2 = st.columns([1,2])
        with col1:
            st.markdown(f"<div style='font-size:96px; white-space:pre'>{render_avatar(p)}</div>", unsafe_allow_html=True)
            st.write("Stad:", p.get("city","-"))
            st.write("Geld: €", p.get("money",0))
            st.write("XP:", p.get("xp",0))
            st.write("Level:", p.get("level",1))
            st.write("Rang:", rank_map[p["name"]][1])
        with col2:
            st.subheader(p["name"])
            st.write("Bio:", p.get("bio",""))
            st.write("Motivatie:", p.get("motivations",""))
            st.write("Sterke punten:", p.get("strengths",""))
            st.write("Referenties:", p.get("references",""))
            st.markdown("### Laatste acties")
            for ev in list(reversed(p.get("history", [])))[:15]:
                st.write(f"{ev['time']} — {ev['text']}")

# -----------------------
# Jobs tab (minigames)
# -----------------------
with tab_jobs:
    st.header("Banen & Minigames")
    if not st.session_state["logged_in"]:
        st.info("Log in om te spelen.")
    else:
        p = st.session_state["profiles"][st.session_state["username"]]
        if not p.get("admitted", False):
            st.warning("Je bent nog niet toegelaten. Rond je sollicitatie af op het profiel-tab.")
        else:
            # Pizzabakker minigame: ingredient matching
            st.subheader("🍕 Pizzabakker — Ingrediëntenmatch")
            st.caption("Koppel per pizza de juiste ingrediënten. Hoe meer juist, hoe meer beloning.")
            pizzas = {
                "Margherita": {"must": {"Tomaat","Mozzarella","Basilicum"}, "opts": {"Olijfolie"}},
                "Marinara": {"must": {"Tomaat","Knoflook","Oregano"}, "opts": {"Olijfolie"}},
                "Quattro Formaggi": {"must": {"Mozzarella","Gorgonzola","Parmezaan","Fontina"}, "opts": set()},
                "Capricciosa": {"must": {"Tomaat","Mozzarella","Champignons","Artisjok","Ham","Olijven"}, "opts": set()},
                "Diavola": {"must": {"Tomaat","Mozzarella","Pikante salami"}, "opts": {"Chili-olie"}},
            }
            pantry = sorted(list(set().union(*[v["must"]|v["opts"] for v in pizzas.values()]) |
                                  {"Ui","Paprika","Ananas","Rucola"}))
            cols = st.columns(2)
            picks = {}
            with cols[0]:
                for name in list(pizzas.keys())[:3]:
                    picks[name] = st.multiselect(f"{name}", options=pantry, key=f"pz_{name}")
            with cols[1]:
                for name in list(pizzas.keys())[3:]:
                    picks[name] = st.multiselect(f"{name}", options=pantry, key=f"pz_{name}")

            if st.button("🍕 Bak pizza's"):
                correct = 0
                total_must = sum(len(v["must"]) for v in pizzas.values())
                penalties = 0
                for name, v in pizzas.items():
                    chosen = set(picks.get(name, []))
                    correct += len(chosen & v["must"])
                    penalties += len(chosen - (v["must"] | v["opts"]))
                # score: correct must - wrong extras
                score = max(0, correct - penalties)
                # rewards modest to keep leveling slow
                money = score * 3
                xp = score * 2
                p["money"] += money
                p["xp"] += xp
                save_event(p, f"Pizzabakker: score {score} (juist {correct}, fout {penalties}) → +€{money}, +{xp} XP")
                st.success(f"Resultaat: score {score} → +€{money}, +{xp} XP")
                autosave()

            st.markdown("---")

            # Clubeigenaar minigame: budget allocation & events
            st.subheader("🎧 Clubeigenaar — Nacht budgetteren")
            st.caption("Verdeel je budget over Security / Bar / Muziek. Random events bepalen de nacht.")
            budget = st.slider("Nachtbudget (€)", 50, 300, 120)
            colA, colB, colC = st.columns(3)
            with colA:
                sec = st.number_input("Security (€)", 0, budget, 40)
            with colB:
                bar = st.number_input("Bar (€)", 0, budget - sec, 50)
            with colC:
                music = st.number_input("Muziek (€)", 0, budget - sec - bar, 30)
            if st.button("🏁 Start clubnacht"):
                if sec + bar + music > budget:
                    st.error("Verdeling overschrijdt budget.")
                else:
                    # outcomes: compute satisfaction and risk
                    rng = random.Random(f"{p['name']}-{datetime.now().isoformat()}")
                    crowd = rng.uniform(0.8, 1.2) * (music/30 + bar/50 + 0.5)
                    safety = (sec/40) + rng.uniform(0.4, 1.0)
                    sales = crowd * (bar/40 + rng.uniform(0.5, 1.5))
                    incidents = 0 if safety > 1.2 else (1 if safety > 0.8 else 2)
                    income = int( sales * 25 - incidents * 15 )
                    xp = max(1, int(crowd*2 + (safety*1.5)))
                    if incidents >= 2:
                        income -= 10  # penalty
                    # modest rewards
                    income = max(-20, min(60, income))
                    p["money"] += income
                    p["xp"] += xp
                    save_event(p, f"Clubeigenaar: omzet {income}€, incidents {incidents}, xp +{xp}")
                    if income >= 0:
                        st.success(f"Nacht geslaagd: +€{income}, +{xp} XP (incidenten: {incidents})")
                    else:
                        st.warning(f"Mager: {income}€ (verlies), +{xp} XP (incidenten: {incidents})")
                    autosave()

            st.markdown("---")

            # Chauffeur minigame: route choice
            st.subheader("🚗 Chauffeur — Kies je route")
            st.caption("Elke route heeft risico op files/controles. Kies slim.")
            routes = [
                {"name":"Langs de kust", "dist": 18, "traffic":"middel", "risk":"laag"},
                {"name":"Door het centrum", "dist": 10, "traffic":"hoog", "risk":"middel"},
                {"name":"Snelweg omweg", "dist": 24, "traffic":"laag", "risk":"middel-hoog"},
            ]
            route_names = [r["name"] for r in routes]
            choice = st.radio("Route", route_names, index=0)
            if st.button("🏁 Vertrek"):
                r = next(x for x in routes if x["name"] == choice)
                rng = random.Random(f"{p['name']}-{datetime.now().isoformat()}-route")
                delay = 0
                # traffic effect
                delay += {"laag": rng.randint(0,3), "middel": rng.randint(2,7), "hoog": rng.randint(5,12)}.get(r["traffic"], 4)
                # risk effect
                mishap_roll = rng.random()
                mishap = False
                if r["risk"] == "middel-hoog":
                    mishap = mishap_roll < 0.35
                elif r["risk"] == "middel":
                    mishap = mishap_roll < 0.22
                else:
                    mishap = mishap_roll < 0.12
                if mishap:
                    delay += rng.randint(6,15)
                time_score = max(0, int(40 - (r["dist"] + delay)))
                money = max(-8, min(35, time_score // 2))
                xp = max(1, min(16, 8 + (15 - delay)//3))
                p["money"] += money
                p["xp"] += xp
                msg = f"Route '{r['name']}', vertraging {delay} min. Resultaat: €{money}, +{xp} XP."
                save_event(p, "Chauffeur: " + msg)
                st.success(msg if money>=0 else "Vertraging kost geld. " + msg)
                autosave()

            st.markdown("---")

            # Corrupte politie (parodie) — paperwork memory puzzle
            st.subheader("🗂️ 'Corrupte' Politie — Papierwerkpuzzel (parodie)")
            st.caption("Zoek de juiste formulierencombinatie. (Humoristisch/onschuldig, geen echte misdaad).")
            forms = ["A38", "B12", "C07", "D99", "E21"]
            rng_key = f"forms_{p['name']}"
            if rng_key not in st.session_state:
                st.session_state[rng_key] = random.sample(forms, 3)  # secret combo
            secret = st.session_state[rng_key]
            pick = st.multiselect("Kies 3 formulieren", options=forms, max_selections=3)
            if st.button("🔍 Controleer formulieren"):
                if len(pick) != 3:
                    st.error("Kies precies 3 formulieren.")
                else:
                    correct = len(set(pick) & set(secret))
                    money = correct * 4
                    xp = 2 + correct
                    # modest reward; if full match, reshuffle for next time
                    if correct == 3:
                        st.session_state[rng_key] = random.sample(forms, 3)
                        money += 6; xp += 3
                    p["money"] += money
                    p["xp"] += xp
                    save_event(p, f"Papierwerkpuzzel: {correct}/3 goed → +€{money}, +{xp} XP")
                    st.success(f"{correct}/3 goed → +€{money}, +{xp} XP")
                    autosave()

# -----------------------
# Daily mission (simple, optional)
# -----------------------
with tab_mission:
    st.header("Dagelijkse missie (1× per dag)")
    if not st.session_state["logged_in"]:
        st.info("Log in om je dagelijkse missie te doen.")
    else:
        p = st.session_state["profiles"][st.session_state["username"]]
        today = date.today().isoformat()
        done = p.get("last_daily_dt") == today
        if done:
            st.info("Je dagelijkse missie is vandaag al voltooid. Morgen weer! (Je kunt natuurlijk banen blijven doen.)")
        # Simple deterministic daily challenge (no quiz style on application; daily mission is fine)
        rng = random.Random(p["name"] + today)
        target = rng.randint(6, 15)
        st.write(f"Vandaag: verzamel **exact {target} punten** door max 3 beurten te kiezen (opties 1/2/3/4 punten per beurt).")
        if "daily_turns" not in st.session_state:
            st.session_state["daily_turns"] = 3
            st.session_state["daily_sum"] = 0
        colx = st.columns(4)
        moves = [1,2,3,4]
        pressed = None
        for i, c in enumerate(colx):
            with c:
                if st.button(f"+{moves[i]} punten", key=f"mv{i}"):
                    pressed = moves[i]
        if pressed is not None and not done:
            st.session_state["daily_sum"] += pressed
            st.session_state["daily_turns"] -= 1
            st.write(f"Totaal: {st.session_state['daily_sum']} (beurten over: {st.session_state['daily_turns']})")
            if st.session_state["daily_turns"] == 0:
                # evaluate
                if st.session_state["daily_sum"] == target:
                    gain = rng.randint(18, 42)
                    xp = rng.randint(10, 22)
                    p["money"] += gain
                    p["xp"] += xp
                    p["last_daily_dt"] = today
                    save_event(p, f"Dagmissie gelukt: +€{gain}, +{xp} XP")
                    st.success(f"Gelukt! +€{gain}, +{xp} XP")
                else:
                    # small consolation
                    p["money"] += 3
                    p["xp"] += 1
                    p["last_daily_dt"] = today
                    save_event(p, f"Dagmissie gemist: +€3, +1 XP (totaal {st.session_state['daily_sum']} != {target})")
                    st.info(f"Niet precies {target}. Je krijgt +€3 en +1 XP.")
                # reset local state
                st.session_state["daily_turns"] = 3
                st.session_state["daily_sum"] = 0
                autosave()

# -----------------------
# Shop & Avatar
# -----------------------
with tab_shop:
    st.header("Shop & Avatar")
    if not st.session_state["logged_in"]:
        st.info("Log in om de shop te gebruiken.")
    else:
        p = st.session_state["profiles"][st.session_state["username"]]
        update_profile_level_title(p, rank_map)
        c1, c2 = st.columns([1,2])
        with c1:
            st.subheader("Avatar")
            st.markdown(f"<div style='font-size:96px; white-space:pre'>{render_avatar(p)}</div>", unsafe_allow_html=True)
            st.write("Geld: €", p.get("money",0))
            new_base = st.selectbox("Basis avatar", options=BASE_AVATARS, index=BASE_AVATARS.index(p["avatar"].get("base", BASE_AVATARS[0])))
            if st.button("Stel basis in"):
                p["avatar"]["base"] = new_base
                save_event(p, f"Basis avatar → {new_base}")
                autosave()
                st.success("Basis ingesteld.")
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
                                save_event(p, f"Kocht {item}")
                                autosave()
                                st.success(f"{item} gekocht!")
                            else:
                                st.error("Niet genoeg geld")

# -----------------------
# Leaderboard tab (all accounts)
# -----------------------
with tab_board:
    st.header("Alle accounts & rangen")
    profiles = st.session_state["profiles"]
    # build table
    rows = []
    for name, prof in profiles.items():
        lvl, title = rank_map[name]
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
# Finalize
# -----------------------
autosave()
