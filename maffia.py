# la_famiglia_full.py
# Complete Streamlit "La Famiglia (parody) game" in één file.
# - Persistentie via profiles.json
# - Uitgebreide sollicitatie met beoordeling (kan afgewezen worden)
# - Avatar tonen & aanpassen
# - Moeilijkere beloningen en risico's
# - Shop & historie
#
# Vereisten: streamlit (pip install streamlit)
# Run: streamlit run la_famiglia_full.py

import streamlit as st
import json
import random
from datetime import datetime
from pathlib import Path

# ------------------------
# Config / Data
# ------------------------
DATA_FILE = Path("profiles.json")
st.set_page_config(page_title="La Famiglia – Full Parody Game", page_icon="🍝", layout="wide")

SHOP_ITEMS = {
    "Fedora": {"price": 150, "emoji": "🎩", "xp": 12},
    "Sunglasses": {"price": 200, "emoji": "🕶️", "xp": 18},
    "Gold Chain": {"price": 400, "emoji": "📿", "xp": 40},
    "Fancy Suit": {"price": 700, "emoji": "🤵", "xp": 70},
    "Black Boots": {"price": 180, "emoji": "👞", "xp": 18},
    "Nonna's Recipe": {"price": 250, "emoji": "📜", "xp": 25},
    "Motorcycle": {"price": 1200, "emoji": "🏍️", "xp": 120}
}

RANKS = [
    (0, "Rookie"),
    (120, "Associate"),
    (360, "Caporegime"),
    (840, "Consigliere"),
    (1800, "Underboss"),
    (3600, "Boss")
]

BASE_AVATARS = ["😎", "🕵️", "👨‍🍳", "🧑‍💼", "🧑‍🏭", "👴", "👩‍🦳"]

# ------------------------
# Helpers: load/save
# ------------------------
def load_profiles():
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # If JSON corrupted, back it up and start fresh
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

# ------------------------
# Session initialization
# ------------------------
if "profiles" not in st.session_state:
    st.session_state["profiles"] = load_profiles()  # dict: name -> profile dict

if "current_profile" not in st.session_state:
    st.session_state["current_profile"] = None

# autosave helper
def autosave():
    save_profiles(st.session_state["profiles"])

# ------------------------
# Profile model helpers
# ------------------------
def new_profile_struct(name, age, bio):
    return {
        "name": name,
        "age": age,
        "bio": bio,
        "created": datetime.now().isoformat(timespec="seconds"),
        "money": 150,   # starting lower so earning is harder
        "xp": 0,
        "level": 1,
        "items": [],
        "history": [],
        "avatar": {"base": random.choice(BASE_AVATARS), "extras": []},
        "application": None,  # store last application fields & status
    }

def save_event(profile, text):
    entry = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text": text}
    profile["history"].append(entry)
    autosave()

def get_rank(xp):
    rank = RANKS[0][1]
    for req, title in RANKS:
        if xp >= req:
            rank = title
    return rank

def render_avatar(profile):
    base = profile["avatar"].get("base", "😎")
    extras = "".join(profile["avatar"].get("extras", []))
    return f"{base} {extras}"

# ------------------------
# Application evaluation (realistic/parody)
# returns score (int) and status str
# ------------------------
def evaluate_application(form):
    # form: dict containing fields from form
    score = 0

    # Basic checks
    age = form.get("age", 0)
    if age >= 18 and age <= 80:
        score += 2
    else:
        score -= 2

    # Motivation: longer motivations give extra but with diminishing returns
    mot = form.get("motivation", "")
    if len(mot) > 100:
        score += 3
    elif len(mot) > 40:
        score += 2
    elif len(mot) > 10:
        score += 1

    # Experience tags: some are valuable, some penalize
    experience = form.get("experience", [])
    # value map (parody-safe)
    value_map = {
        "Pizzabakken": 2,
        "Logistiek": 3,
        "Onderhandelen": 3,
        "Discretie": 4,
        "PR": 1,
        "Technische hulp (IT)": 2,
        "Financieel inzicht": 3,
        "Kok / keuken": 1
    }
    for e in experience:
        score += value_map.get(e, 0)

    # Specialiteiten (from choices): some yield XP potential in game
    specials = form.get("specialties", [])
    for s in specials:
        if s in ["Discretie", "Financieel inzicht"]:
            score += 2
        elif s in ["Pizzabakken", "Kok / keuken"]:
            score += 1
        else:
            score += 0

    # Realistic test: short arithmetic and logic
    try:
        if int(form.get("calc", -999)) == 17 + 23:
            score += 2
        else:
            score -= 1
    except Exception:
        score -= 1

    # Loyalty checkbox
    if form.get("loyal"):
        score += 3
    else:
        score -= 2

    # Introduce some randomness (interview panel judgement)
    judge = random.random()
    if judge < 0.05:
        # rare immediate reject due to "bad vibes"
        score -= 5
    elif judge > 0.95:
        score += 3

    # Determine final status
    if score >= 10:
        status = "Aangenomen"
    elif score >= 5:
        status = "Op proef"
    else:
        status = "Afgewezen"

    return score, status

# ------------------------
# UI: Sidebar profile management
# ------------------------
st.sidebar.title("La Famiglia — Profielen")
if st.sidebar.button("Nieuw profiel"):
    st.session_state["creating_new"] = True

profiles_list = list(st.session_state["profiles"].keys())
selected = st.sidebar.selectbox("Selecteer profiel", options=["--nieuw--"] + profiles_list)
if selected and selected != "--nieuw--":
    st.session_state["current_profile"] = selected
    st.session_state["creating_new"] = False

if "creating_new" not in st.session_state:
    st.session_state["creating_new"] = False

if st.sidebar.button("Verwijder huidig profiel"):
    cur = st.session_state["current_profile"]
    if cur and cur in st.session_state["profiles"]:
        del st.session_state["profiles"][cur]
        st.session_state["current_profile"] = None
        autosave()
        st.sidebar.success("Profiel verwijderd")

st.sidebar.markdown("---")
st.sidebar.markdown("**Gebruikstips**: Maak een profiel, vul de sollicitatie volledig in voor de beste kans. Verdien voorzichtig geld via minigames en investeer in cosmetische items.")

# ------------------------
# Main layout: tabs
# ------------------------
tab_profile, tab_play, tab_shop, tab_rank = st.tabs(["📝 Sollicitatie & Profiel", "🎮 Spelen", "🛍️ Shop & Avatar", "📜 Rang & Historie"])

# ------------------------
# Tab: Sollicitatie & Profiel
# ------------------------
with tab_profile:
    st.header("📝 Sollicitatieformulier (uitgebreid)")
    st.caption("Vul de sollicitatie volledig in. De beoordeling is streng; niet iedereen wordt aangenomen.")

    # Create or edit profile area
    colL, colR = st.columns([2, 1])
    with colL:
        if st.session_state["current_profile"] is None:
            st.info("Maak eerst een profiel of kies een bestaand profiel in de sidebar.")
        else:
            profile = st.session_state["profiles"][st.session_state["current_profile"]]
            st.subheader(f"Actief: {profile['name']} ({profile['age']})")
            st.write("Bio:", profile.get("bio", ""))
            st.write("Avatar:", render_avatar(profile))
            st.write(f"💰 Geld: €{profile['money']}   |   ⭐ XP: {profile['xp']}   |   Rang: {get_rank(profile['xp'])}")
            st.write("---")

    # The extended application form (always editable even if profile exists)
    with st.form("application_form", clear_on_submit=False):
        st.markdown("### Persoonlijke gegevens")
        name = st.text_input("Volledige naam", value=(st.session_state["current_profile"] or ""))
        age = st.number_input("Leeftijd", min_value=16, max_value=99, value=25)
        bio = st.text_area("Korte introductie / bio", value="Ik wil meedoen omdat...")

        st.markdown("### Achtergrond & Ervaring")
        experience = st.multiselect("Ervaring (meerdere kiezen mogelijk)",
                                    ["Pizzabakken", "Logistiek", "Onderhandelen", "Discretie", "PR", "Technische hulp (IT)", "Financieel inzicht", "Kok / keuken"])

        st.markdown("### Specialiteiten")
        specialties = st.multiselect("Specialiteiten (tong-in-cheek, parodie)",
                                     ["Pizzabakken", "Discretie", "Netwerken", "Financieel inzicht", "PR", "Onderhandelen"])

        st.markdown("### Testjes")
        calc = st.number_input("Rekentest: hoeveel is 17 + 23 ?", value=0)
        loyal = st.checkbox("Ik ga professioneel en discreet om met opdrachten (loyale verklaring)")

        st.markdown("### Motivatie")
        motivation = st.text_area("Waarom wil je bij La Famiglia? (hoe uitgebreider, hoe beter)")

        submitted = st.form_submit_button("Verstuur sollicitatie")

    if submitted:
        # Create temp form structure
        form = {"name": name.strip(), "age": int(age), "bio": bio.strip(),
                "experience": experience, "specialties": specialties,
                "calc": int(calc), "loyal": bool(loyal), "motivation": motivation.strip()}
        score, status = evaluate_application(form)

        # If profile doesn't exist yet, create and attach application
        if name.strip() not in st.session_state["profiles"]:
            prof = new_profile_struct(name.strip(), age, bio.strip())
            st.session_state["profiles"][name.strip()] = prof
        profile = st.session_state["profiles"][name.strip()]

        profile["application"] = {"form": form, "score": score, "status": status, "when": datetime.now().isoformat(timespec="seconds")}
        save_event(profile, f"Sollicitatie ingediend — status: {status} (score {score})")
        autosave()

        # Show result
        if status == "Aangenomen":
            # small starting bonus but not huge
            add_amt = 50
            profile["money"] += add_amt
            add_xp = 20
            profile["xp"] += add_xp
            save_event(profile, f"Aangenomen: +€{add_amt}, +{add_xp} XP")
            st.success(f"Gefeliciteerd — je bent **{status}**! Je ontvangt €{add_amt} en {add_xp} XP.")
        elif status == "Op proef":
            # small trial resources
            profile["money"] += 20
            profile["xp"] += 8
            save_event(profile, f"Op proef geplaatst: +€20, +8 XP")
            st.warning("Je staat op proef. Presteer goed in mini-games om je status te verbeteren.")
        else:
            # Rejected: they still have a profile but no resources
            save_event(profile, "Afgewezen bij sollicitatie")
            st.error("Helaas — je sollicitatie is afgewezen. Je kunt het later opnieuw proberen.")

        st.session_state["current_profile"] = name.strip()
        autosave()

# ------------------------
# Tab: Spelen (harder rewards)
# ------------------------
with tab_play:
    st.header("🎮 Spelen (verdien geld & XP — moeilijker!)")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer of maak eerst een profiel in de sidebar.")
    else:
        profile = st.session_state["profiles"][st.session_state["current_profile"]]
        st.subheader(f"Speler: {profile['name']} — Geld: €{profile['money']} — XP: {profile['xp']}")

        # Select activity
        activity = st.selectbox("Kies activiteit", ["Korte quiz (laag risico)", "Snelle levering (risico)", "Klik-challenge (lange termijn)", "Geluksrad (hoog risico)"])

        if activity == "Korte quiz (laag risico)":
            st.write("Moeilijkere vragen — beloning klein en kans op niets groter.")
            q = random.choice([
                ("Wat hoort traditioneel niet in carbonara?", ["Room", "Pancetta", "Eieren"], "Room"),
                ("Welke stad staat bekend om pizza?", ["Napels", "Turijn", "Parma"], "Napels"),
            ])
            ans = st.radio(q[0], q[1], key=f"quiz_{profile['name']}")
            if st.button("Indienen (quiz)"):
                if ans == q[2] and random.random() < 0.7:
                    reward = random.randint(15, 40)  # small reward
                    xp = random.randint(8, 18)
                    profile["money"] += reward
                    profile["xp"] += xp
                    save_event(profile, f"Quiz gewonnen: +€{reward}, +{xp} XP")
                    st.success(f"Goed! +€{reward}, +{xp} XP")
                else:
                    # often nothing
                    profile["xp"] += 3
                    save_event(profile, "Quiz poging zonder beloning")
                    st.info("Niet helemaal goed — je krijgt wel +3 XP voor de poging.")

        elif activity == "Snelle levering (risico)":
            st.write("Kies je route: riskant = hogere beloning maar kans op verliezen.")
            choice = st.radio("Route", ["Snelle route (risico)", "Veilige route (minder winst)"])
            if st.button("Start levering"):
                if choice.startswith("Snelle"):
                    success = random.random() < 0.5
                    if success:
                        reward = random.randint(80, 180)
                        xp = random.randint(20, 40)
                        profile["money"] += reward
                        profile["xp"] += xp
                        save_event(profile, f"Delivery success: +€{reward}, +{xp} XP")
                        st.success(f"Delivery geslaagd! +€{reward} en +{xp} XP")
                    else:
                        loss = random.randint(20, 80)
                        profile["money"] = max(0, profile["money"] - loss)
                        profile["xp"] += 5
                        save_event(profile, f"Delivery failed: -€{loss}")
                        st.error(f"Delivery mislukt — verlies €{loss}")
                else:
                    # safe route
                    success = random.random() < 0.85
                    if success:
                        reward = random.randint(30, 60)
                        xp = random.randint(8, 16)
                        profile["money"] += reward
                        profile["xp"] += xp
                        save_event(profile, f"Safe delivery: +€{reward}, +{xp} XP")
                        st.success(f"Veilige delivery geslaagd: +€{reward}, +{xp} XP")
                    else:
                        st.info("Kleine tegenslag, geen winst.")

        elif activity == "Klik-challenge (lange termijn)":
            st.write("Klik zo vaak je wilt. Elke X klikken levert kleine beloningen — geduld loont.")
            if "click_count" not in profile:
                profile["click_count"] = 0
            if st.button("Klik!"):
                profile["click_count"] = profile.get("click_count", 0) + 1
                if profile["click_count"] % 10 == 0:
                    reward = 15
                    xp = 6
                    profile["money"] += reward
                    profile["xp"] += xp
                    save_event(profile, f"Click milestone: +€{reward}, +{xp} XP")
                    st.success(f"Milestone! +€{reward} en +{xp} XP")
                else:
                    st.write("Klik geregistreerd. Tel op naar 10 voor kleine beloning.")
                st.write("Totaal klikken:", profile["click_count"])

        elif activity == "Geluksrad (hoog risico)":
            st.write("Het rad is wispelturig. Kans op jackpot heel klein.")
            if st.button("Draai rad (€10 inzet)"):
                if profile["money"] < 10:
                    st.error("Je hebt niet genoeg geld om te draaien.")
                else:
                    profile["money"] -= 10
                    r = random.random()
                    if r > 0.985:
                        # tiny jackpot
                        profile["money"] += 1000
                        profile["xp"] += 200
                        save_event(profile, "Geluksrad jackpot!")
                        st.success("Jackpot! +€1000 en +200 XP")
                    elif r > 0.90:
                        profile["money"] += 100
                        profile["xp"] += 30
                        save_event(profile, "Geluksrad winst")
                        st.success("Goed! +€100 en +30 XP")
                    else:
                        save_event(profile, "Geluksrad mis")
                        st.info("Helaas, je verliest de inzet.")

        # After any activity, update level and autosave
        profile["level"] = 1 + profile["xp"] // 120
        autosave()

# ------------------------
# Tab: Shop & Avatar customization
# ------------------------
with tab_shop:
    st.header("🛍️ Shop & Avatar aanpassen")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer of maak eerst een profiel.")
    else:
        profile = st.session_state["profiles"][st.session_state["current_profile"]]
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("Huidige avatar")
            st.markdown(f"<div style='font-size:80px'>{render_avatar(profile)}</div>", unsafe_allow_html=True)
            st.write("Items:", ", ".join(profile["items"]) if profile["items"] else "Geen")

            # basic avatar customization
            st.markdown("---")
            st.subheader("Avatar basis kiezen")
            new_base = st.selectbox("Kies basis avatar", options=BASE_AVATARS, index=BASE_AVATARS.index(profile["avatar"].get("base", BASE_AVATARS[0])))
            if st.button("Stel basis in"):
                profile["avatar"]["base"] = new_base
                save_event(profile, f"Avatar basis ingesteld op {new_base}")
                autosave()
                st.success("Avatar basis aangepast")

        with c2:
            st.subheader("Shop items")
            st.write(f"Jouw geld: €{profile['money']}")
            for item, info in SHOP_ITEMS.items():
                cols = st.columns([3,1,1])
                with cols[0]:
                    st.write(f"{info['emoji']} **{item}** — €{info['price']}  (+{info['xp']} XP)")
                with cols[1]:
                    owned = item in profile["items"]
                    st.write("✅" if owned else "❌")
                with cols[2]:
                    if not owned:
                        if st.button(f"Koop {item}", key=f"buy_{item}"):
                            if profile["money"] >= info["price"]:
                                profile["money"] -= info["price"]
                                profile["items"].append(item)
                                profile["avatar"]["extras"].append(info["emoji"])
                                profile["xp"] += info["xp"]
                                save_event(profile, f"Gekocht {item}")
                                autosave()
                                st.success(f"{item} gekocht!")
                            else:
                                st.error("Niet genoeg geld")

# ------------------------
# Tab: Rank & History
# ------------------------
with tab_rank:
    st.header("📜 Rang & Geschiedenis")
    if st.session_state["current_profile"] is None:
        st.info("Maak of kies eerst een profiel.")
    else:
        profile = st.session_state["profiles"][st.session_state["current_profile"]]
        st.subheader(f"{profile['name']} — Rang: {get_rank(profile['xp'])} — Level: {profile['level']}")
        st.markdown("### Avatar")
        st.markdown(f"<div style='font-size:64px'>{render_avatar(profile)}</div>", unsafe_allow_html=True)

        st.markdown("### Statistieken")
        st.write(f"• Geld: €{profile['money']}")
        st.write(f"• XP: {profile['xp']}")
        st.write(f"• Items: {', '.join(profile['items']) if profile['items'] else 'Geen'}")

        st.markdown("### Geschiedenis (laatste 30)")
        for ev in list(reversed(profile["history"]))[:30]:
            st.write(f"{ev['time']} — {ev['text']}")

# ------------------------
# End of file: ensure autosave on exit
# ------------------------
# Save when script finishes handling request (Streamlit runs multiple times)
autosave()
