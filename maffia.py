# la_famiglia_turnbased.py
# Streamlit app — La Famiglia parody game with turn-based PacMan-style daily mission
# Single-file app, persists profiles to profiles.json
#
# Run:
#   pip install streamlit
#   streamlit run la_famiglia_turnbased.py

import streamlit as st
import json
import random
from datetime import date, datetime
from pathlib import Path

# ---------- Config ----------
DATA_FILE = Path("profiles.json")
st.set_page_config(page_title="La Famiglia — Turn-based Mission", page_icon="🍝", layout="wide")

# Avatar/shop config (emoji layers)
SHOP_ITEMS = {
    "Fedora": {"price": 300, "emoji": "🎩", "pos": "top", "xp": 18},
    "Sunglasses": {"price": 350, "emoji": "🕶️", "pos": "eyes", "xp": 22},
    "Gold Chain": {"price": 600, "emoji": "📿", "pos": "neck", "xp": 44},
    "Fancy Suit": {"price": 1200, "emoji": "🤵", "pos": "torso", "xp": 90},
    "Black Boots": {"price": 420, "emoji": "👞", "pos": "feet", "xp": 24},
    "Motorcycle": {"price": 2200, "emoji": "🏍️", "pos": "side", "xp": 150},
}
BASE_AVATARS = ["😎", "🕵️", "👨‍🍳", "🧑‍💼", "🧑‍🏭", "👴", "👩‍🦳"]

# mission grid
GRID_W = 11
GRID_H = 9
MAX_TURNS = 60  # max moves in mission
COINS_TARGET = 8  # coins to collect to win faster

# ---------- Persistence ----------
def load_profiles():
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # backup and start fresh
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

# ---------- Session init ----------
if "profiles" not in st.session_state:
    st.session_state["profiles"] = load_profiles()

if "current_profile" not in st.session_state:
    st.session_state["current_profile"] = None

# ---------- Profile helpers ----------
def new_profile(name):
    return {
        "name": name,
        "created": datetime.now().isoformat(timespec="seconds"),
        "money": 120,
        "xp": 0,
        "level": 1,
        "items": [],
        "avatar": {"base": random.choice(BASE_AVATARS), "top":"", "eyes":"", "neck":"", "torso":"", "feet":"", "side":""},
        "history": [],
        "last_mission_date": None,
    }

def save_event(profile, text):
    profile.setdefault("history", []).append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text": text})
    autosave()

def get_rank(xp):
    if xp >= 7000: return "capo di capi"
    if xp >= 3001: return "Boss"
    if xp >= 1501: return "Underboss"
    if xp >= 701: return "Consigliere"
    if xp >= 301: return "Capo"
    if xp >= 101: return "Soldato"
    if xp >= 50: return "Tip de mogool"
    return "Rekruut"

def render_avatar(profile):
    a = profile["avatar"]
    # top, eyes, neck, torso, feet, side
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

# ---------- Mission (turn-based) helpers ----------
def make_mission_state(seed=None):
    """Create a mission state: walls, player, guards, coins, turns left."""
    rng = random.Random(seed)
    # simple walls: border + some inner blocks
    walls = set()
    for x in range(GRID_W):
        walls.add((x, 0)); walls.add((x, GRID_H-1))
    for y in range(GRID_H):
        walls.add((0, y)); walls.add((GRID_W-1, y))
    # add some random internal blocks
    for _ in range((GRID_W*GRID_H)//8):
        x = rng.randint(1, GRID_W-2); y = rng.randint(1, GRID_H-2)
        walls.add((x,y))
    # place player and guards and coins on empty cells
    def rnd_empty(exclude):
        while True:
            x = rng.randint(1, GRID_W-2); y = rng.randint(1, GRID_H-2)
            if (x,y) not in walls and (x,y) not in exclude:
                return (x,y)
    occupied = set()
    player = rnd_empty(occupied); occupied.add(player)
    guards = []
    for _ in range(3):
        g = rnd_empty(occupied); occupied.add(g); guards.append(g)
    coins = set()
    for _ in range(12):
        c = rnd_empty(occupied); occupied.add(c); coins.add(c)
    state = {
        "walls": list(walls),
        "player": player,
        "guards": guards,
        "coins": list(coins),
        "turns": MAX_TURNS,
        "seed": seed
    }
    return state

def move_pos(pos, dir):
    x,y = pos
    if dir == "up": return (x, y-1)
    if dir == "down": return (x, y+1)
    if dir == "left": return (x-1, y)
    if dir == "right": return (x+1, y)
    return pos

def in_bounds(pos):
    x,y = pos
    return 0 <= x < GRID_W and 0 <= y < GRID_H

def neighbors(pos):
    x,y = pos
    return [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]

def guard_move_simple(guard_pos, player_pos, walls):
    # simple behavior: try move towards player with random deviation
    gx,gy = guard_pos
    px,py = player_pos
    choices = []
    if px > gx: choices.append((gx+1,gy))
    if px < gx: choices.append((gx-1,gy))
    if py > gy: choices.append((gx,gy+1))
    if py < gy: choices.append((gx,gy-1))
    # add random neighbors
    choices += neighbors(guard_pos)
    random.shuffle(choices)
    for c in choices:
        if in_bounds(c) and c not in walls:
            return c
    return guard_pos

# ---------- UI: Sidebar profiles ----------
st.sidebar.title("Profielen")
if st.sidebar.button("Nieuw profiel"):
    st.session_state["creating_new"] = True

profiles_list = list(st.session_state["profiles"].keys())
selected = st.sidebar.selectbox("Selecteer profiel", options=["--nieuw--"] + profiles_list)
if selected != "--nieuw--":
    st.session_state["current_profile"] = selected; st.session_state["creating_new"] = False
if "creating_new" not in st.session_state:
    st.session_state["creating_new"] = False

if st.sidebar.button("Verwijder huidig profiel"):
    cur = st.session_state["current_profile"]
    if cur and cur in st.session_state["profiles"]:
        del st.session_state["profiles"][cur]; st.session_state["current_profile"]=None; autosave(); st.sidebar.success("Profiel verwijderd")

st.sidebar.markdown("---")
st.sidebar.write("Tip: upgrades zijn duur — spaar langzaam. Speel dagelijkse missie 1× per dag (turn-based).")

# ---------- Main tabs ----------
tab_profile, tab_earn, tab_mission, tab_shop, tab_rank = st.tabs(["📝 Profiel", "💼 Verdien (moeilijk)", "🎯 Dagelijkse missie", "🛍️ Shop", "📜 Rang & Historie"])

# ---------- Tab: Profile ----------
with tab_profile:
    st.header("Sollicitatie / Profiel")
    if st.session_state["current_profile"] is None:
        if st.session_state["creating_new"]:
            with st.form("create"):
                name = st.text_input("Naam")
                submitted = st.form_submit_button("Maak profiel")
            if submitted:
                if not name.strip(): st.error("Geef een naam")
                elif name.strip() in st.session_state["profiles"]: st.error("Naam bestaat")
                else:
                    st.session_state["profiles"][name.strip()] = new_profile(name.strip()); st.session_state["current_profile"] = name.strip(); autosave(); st.success("Profiel aangemaakt")
        else:
            st.info("Maak een nieuw profiel via de sidebar of klik 'Nieuw profiel' in de zijbalk.")
    else:
        p = st.session_state["profiles"][st.session_state["current_profile"]]
        st.subheader(f"{p['name']} — Rang: {get_rank(p['xp'])}")
        st.markdown(f"**Geld:** €{p['money']}    **XP:** {p['xp']}    **Level:** {p['level']}")
        st.markdown(f"<div style='font-size:72px; white-space:pre'>{render_avatar(p)}</div>", unsafe_allow_html=True)
        if st.button("Laat profiel exporteren (JSON)"):
            st.download_button("Download profiel JSON", data=json.dumps(p, ensure_ascii=False, indent=2), file_name=f"profile_{p['name']}.json")

# ---------- Tab: Always-available earning (hard) ----------
with tab_earn:
    st.header("Altijd geld verdienen (moeilijk en risicovol)")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer profiel in sidebar.")
    else:
        p = st.session_state["profiles"][st.session_state["current_profile"]]
        st.write("Acties zijn laag-winst of riskant. Herhaal veel om iets te bereiken.")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Bescherming innen")
            if st.button("Probeer innen"):
                r = random.random()
                if r < 0.48:
                    gain = random.randint(10, 22); xp = random.randint(3,8)
                    p["money"] += gain; p["xp"] += xp; save_event(p, f"Bescherming: +€{gain}, +{xp} XP"); st.success(f"+€{gain}, +{xp} XP")
                else:
                    loss = random.randint(6,16); p["money"] = max(0, p["money"]-loss); p["xp"] += 2; save_event(p, f"Bescherming mis: -€{loss}"); st.warning(f"Mis: -€{loss}")
        with col2:
            st.subheader("Kleine klus")
            if st.button("Doe klus"):
                if random.random() < 0.73:
                    gain = random.randint(4,8); xp = random.randint(1,4)
                    p["money"] += gain; p["xp"] += xp; save_event(p, f"Klus: +€{gain}, +{xp} XP"); st.success(f"+€{gain}, +{xp} XP")
                else:
                    save_event(p, "Klus mislukt"); st.info("Geen beloning")
        with col3:
            st.subheader("Gokken (gevaarlijk)")
            if st.button("Waag gok (€10)"):
                if p["money"] < 10: st.error("Niet genoeg geld")
                else:
                    p["money"] -= 10
                    r = random.random()
                    if r > 0.98:
                        win = 140; xp = 20; p["money"] += win; p["xp"] += xp; save_event(p, f"Jackpot: +€{win}, +{xp} XP"); st.success(f"Jackpot! +€{win}")
                    elif r > 0.88:
                        win = 40; xp = 8; p["money"] += win; p["xp"] += xp; save_event(p, f"Gok winst: +€{win}"); st.info(f"Kleine winst +€{win}")
                    else:
                        save_event(p, "Gok verlies -€10"); st.warning("Verloren -€10")
        p["level"] = 1 + p["xp"] // 200
        autosave()

# ---------- Tab: Turn-based Daily Mission ----------
with tab_mission:
    st.header("Dagelijkse missie (turn-based Pac-Man-achtig)")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer eerst een profiel.")
    else:
        p = st.session_state["profiles"][st.session_state["current_profile"]]
        today = date.today().isoformat()
        done_today = (p.get("last_mission_date") == today)

        st.write(f"Vandaag: {'al gedaan' if done_today else 'nog open'} — je kunt de missie *één keer per dag* spelen voor echte beloning.")
        st.write("Spelregels: je beweegt per beurt met de pijltjes. Verzamel munten (💰). Vermijd rivalen (👮).")
        st.write(f"Doel: verzamel minstens {COINS_TARGET} munten binnen {MAX_TURNS} beurten voor een goede beloning.")

        # initialize mission state in session_state keyed by profile
        key = f"mission_{p['name']}"
        if key not in st.session_state:
            # create a deterministic seed per day so layout is same for everyone that day
            seed = f"{p['name']}_{today}"
            st.session_state[key] = make_mission_state(seed=seed)

        state = st.session_state[key]
        walls = set(tuple(w) for w in state["walls"])
        player = tuple(state["player"])
        guards = [tuple(g) for g in state["guards"]]
        coins = set(tuple(c) for c in state["coins"])
        turns = state["turns"]

        # render grid as emojis
        def render_grid(player, guards, coins, walls):
            grid = []
            for y in range(GRID_H):
                row = []
                for x in range(GRID_W):
                    if (x,y) in walls:
                        row.append("⬛")
                    elif (x,y) == player:
                        row.append("😎")
                    elif (x,y) in guards:
                        row.append("👮")
                    elif (x,y) in coins:
                        row.append("💰")
                    else:
                        row.append("·")
                grid.append("".join(row))
            return "\n".join(grid)

        st.markdown(f"<pre style='font-size:20px'>{render_grid(player, guards, coins, walls)}</pre>", unsafe_allow_html=True)
        st.write(f"Munten verzameld: {len(state['coins']) and 0}  — beurten over: {turns}")

        # movement buttons
        col_u, col_m, col_d = st.columns([1,4,1])
        with col_m:
            up = st.button("⬆️")
        left_col, mid_col, right_col = st.columns([1,1,1])
        with left_col:
            left = st.button("⬅️")
        with mid_col:
            stay = st.button("•")
        with right_col:
            right = st.button("➡️")
        with col_d:
            down = st.button("⬇️")

        # handle move
        moved = False
        if any([up,left,down,right,stay]):
            dir = None
            if up: dir = "up"
            elif down: dir = "down"
            elif left: dir = "left"
            elif right: dir = "right"
            else: dir = "stay"
            # compute new player pos
            newpos = player if dir=="stay" else move_pos(player, dir)
            if not in_bounds(newpos) or newpos in walls:
                st.info("Je botst tegen een muur — zet gaat verloren maar telt als beurt.")
                newpos = player
            # collect coin?
            if newpos in coins:
                coins.remove(newpos)
                save_event(p, "Munten gepakt in missie (momentopname)")
            # update player
            player = newpos
            # guards move
            new_guards = []
            for g in guards:
                ng = guard_move_simple(g, player, walls)
                new_guards.append(ng)
            guards = new_guards
            # collision check
            if player in guards:
                st.error("Een rivaal heeft je gepakt! Missie mislukt.")
                # mission fails: small penalty or no reward
                p["money"] = max(0, p["money"] - 5)
                save_event(p, "Missie gefaald: gepakt door rivaal (-€5)")
                # mark mission done for today with tiny training reward
                p["last_mission_date"] = today
                autosave()
                # reset session mission (so next day will be new)
                del st.session_state[key]
            else:
                # reduce turns
                state["turns"] = max(0, state["turns"] - 1)
                state["player"] = player
                state["guards"] = list(guards)
                state["coins"] = list(coins)
                autosave()
                moved = True

        # check victory conditions
        coins_collected = 12 - len(coins)  # original count was 12
        # successful completion if coins_collected >= COINS_TARGET
        if coins_collected >= COINS_TARGET and not done_today:
            # reward: modest but meaningful
            reward_money = 8 * coins_collected  # small per coin
            reward_xp = 3 * coins_collected
            p["money"] += reward_money
            p["xp"] += reward_xp
            p["last_mission_date"] = today
            save_event(p, f"Dagelijkse missie geslaagd: +€{reward_money}, +{reward_xp} XP (munten: {coins_collected})")
            autosave()
            st.success(f"Missie voltooid! Je verdient €{reward_money} en {reward_xp} XP.")
            # clear mission state to get new layout next day
            del st.session_state[key]
        elif state["turns"] <= 0 and not done_today:
            st.info("Beurten op — missie voorbij. Je krijgt een kleine training beloning.")
            # small training reward (so practice is okay)
            p["money"] += 2
            p["xp"] += 1
            p["last_mission_date"] = today
            save_event(p, "Missie tijd op: training beloning +€2 +1 XP")
            autosave()
            del st.session_state[key]
        elif done_today:
            st.info("Je hebt vandaag al een missie voltooid — je kunt oefenen, maar echte beloning is al opgehaald.")
            # allow practice but low/no reward; don't modify profile significantly
            if moved:
                st.write("Training: je acties veranderen de grid maar geven geen echte beloning.")

# ---------- Tab: Shop ----------
with tab_shop:
    st.header("Shop & Avatar")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer eerst een profiel.")
    else:
        p = st.session_state["profiles"][st.session_state["current_profile"]]
        c1, c2 = st.columns([1,2])
        with c1:
            st.subheader("Avatar")
            st.markdown(f"<div style='font-size:80px; white-space:pre'>{render_avatar(p)}</div>", unsafe_allow_html=True)
            st.write("Items:", ", ".join(p["items"]) if p["items"] else "Geen")
            st.markdown("---")
            new_base = st.selectbox("Basis avatar", options=BASE_AVATARS, index=BASE_AVATARS.index(p["avatar"].get("base",BASE_AVATARS[0])))
            if st.button("Stel basis in"):
                p["avatar"]["base"] = new_base; save_event(p, f"Basis avatar ingesteld"); autosave(); st.success("Basis avatar ingesteld")
        with c2:
            st.subheader("Items te koop")
            st.write(f"Jouw geld: €{p['money']}")
            for item, info in SHOP_ITEMS.items():
                cols = st.columns([3,1,1])
                with cols[0]: st.write(f"{info['emoji']} **{item}** — €{info['price']} (+{info['xp']} XP)")
                with cols[1]: st.write("✅" if item in p["items"] else "❌")
                with cols[2]:
                    if item not in p["items"]:
                        if st.button(f"Koop {item}", key=f"buy_{item}"):
                            if p["money"] >= info["price"]:
                                p["money"] -= info["price"]; p["items"].append(item); p["avatar"][info["pos"]] = info["emoji"]; p["xp"] += info["xp"]; save_event(p, f"Gekocht {item}"); autosave(); st.success(f"{item} gekocht")
                            else:
                                st.error("Niet genoeg geld")

# ---------- Tab: Rank & History ----------
with tab_rank:
    st.header("Rang & Historie")
    if st.session_state["current_profile"] is None:
        st.info("Selecteer eerst een profiel.")
    else:
        p = st.session_state["profiles"][st.session_state["current_profile"]]
        st.subheader(f"{p['name']} — {get_rank(p['xp'])} — Level {p['level']}")
        st.markdown(f"<div style='font-size:64px; white-space:pre'>{render_avatar(p)}</div>", unsafe_allow_html=True)
        st.write(f"Geld: €{p['money']}  |  XP: {p['xp']}")
        st.markdown("### Historie (laatste 30)")
        for ev in list(reversed(p.get("history", [])))[:30]:
            st.write(f"{ev['time']} — {ev['text']}")

# ---------- final save ----------
autosave()
