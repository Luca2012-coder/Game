import streamlit as st
import json
import random
import os

# --- Helper functies ---
SAVE_FILE = "profiles.json"

def load_profiles():
    if not os.path.exists(SAVE_FILE):
        return []
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_profiles(profiles):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)

def save_event(player, event):
    if "history" not in player:
        player["history"] = []
    player["history"].append(event)
    save_profiles(profiles)

def update_special_ranks(profiles):
    sorted_profiles = sorted(profiles, key=lambda x: x["xp"], reverse=True)
    for p in sorted_profiles:
        p["special_rank"] = None
    if len(sorted_profiles) > 0:
        sorted_profiles[0]["special_rank"] = "Capo di Tutti Capi"
    if len(sorted_profiles) > 1:
        sorted_profiles[1]["special_rank"] = "Sottocapo"
    return profiles

def get_rank(xp):
    if xp < 100:
        return "Groentje"
    elif xp < 200:
        return "Rekruut"
    elif xp < 400:
        return "Piccioto"
    elif xp < 800:
        return "Soldato"
    elif xp < 1600:
        return "Capodecino"
    elif xp < 3200:
        return "Capo"
    elif xp < 6400:
        return "Don"
    elif xp < 12800:
        return "Consiglieri"
    else:
        return "Legende"

# --- Main ---
st.title("🕴️ Maffia Game")

# Laad profielen
profiles = load_profiles()

# Login of nieuw profiel
st.subheader("Login of maak een nieuw account")
username = st.text_input("Gebruikersnaam")
password = st.text_input("Wachtwoord (optioneel)", type="password")
if st.button("Login / Maak account"):
    p = None
    for prof in profiles:
        if prof["username"] == username:
            p = prof
            st.success(f"Welkom terug, {username}!")
            break
    if not p:
        p = {"username": username, "password": password, "money": 100, "xp": 0, "job": None, "history": [], "city": None}
        profiles.append(p)
        st.success(f"Account aangemaakt voor {username}")
    save_profiles(profiles)

    # Stad kiezen
    city_list = ["Florence","Bologna","Milaan","Sicilië","Sardinië","Rome","Palermo","Bari","Turijn","Lombardo","Venetië","Empoli","Napels","Genua","Verona","Parma","Calabrië"]
    city = st.selectbox("Kies een stad", city_list, index=0)
    p["city"] = city

    # Kies job
    job_list = ["Pizzabakker","Chauffeur","Clubeigenaar","Corrupte Politie","Sollicitatieafnemer"]
    job = st.selectbox("Kies een baan", job_list)
    p["job"] = job
    save_profiles(profiles)

    st.write(f"Je huidige geld: €{p['money']}, XP: {p['xp']}, Stad: {p['city']}")

    # --- Pizzabakker minigame ---
    if job == "Pizzabakker":
        st.subheader("🍕 Pizzabakker — maak en verkoop pizza's")
        st.write("Kies de juiste ingrediënten voor elke bestelling. Fout ingrediënt kan je XP en geld kosten!")

        PIZZAS = {
            "Margherita": {"need": {"Tomaat","Mozzarella","Basilicum"}, "opts": {"Olijfolie"}},
            "Pepperoni": {"need": {"Tomaat","Mozzarella","Pepperoni"}, "opts": {"Olijfolie","Oregano"}},
            "Quattro Formaggi": {"need": {"Mozzarella","Gorgonzola","Parmezaan","Fontina"}, "opts": set()},
            "Vegetariana": {"need": {"Tomaat","Mozzarella","Paprika","Champignons","Ui"}, "opts": {"Rucola"}}
        }

        pantry = sorted(list(set().union(*[v["need"]|v["opts"] for v in PIZZAS.values()]) | {"Ananas","Tonijn","Olijven","Chili-olie"}))
        orders_count = st.number_input("Aantal bestellingen (1-4)", min_value=1, max_value=4, value=1)
        order_choices = st.multiselect("Kies pizza's voor de bestelling (laat leeg voor random selectie)", list(PIZZAS.keys()), default=None)
        if not order_choices:
            order_choices = random.choices(list(PIZZAS.keys()), k=orders_count)
        else:
            order_choices = (order_choices * ((orders_count//len(order_choices))+1))[:orders_count]

        st.write("Bestellingen:", ", ".join(order_choices))

        results = {}
        total_correct = 0
        total_wrong = 0
        total_need = 0

        for i, pizza in enumerate(order_choices, start=1):
            st.markdown(f"**Bestelling {i}: {pizza}**")
            chosen = st.multiselect(f"Ingrediënten voor {pizza}", options=pantry, key=f"pz_{i}")

            # --- ananas-check ---
            if "Ananas" in chosen:
                st.error("Maledetto idiota, una vergogna per la famiglia.\nMuori het dag erna en ti becchi una pallottola.")
                p["xp"] = max(0, p["xp"] - 50)
                p["money"] = max(0, p["money"] - 20)
                save_event(p, "Pizzabakker: Ananas gebruikt → straf XP & geld")
                continue

            results[pizza + f"#{i}"] = set(chosen)

        if st.button("Bak en verkoop"):
            for key, chosen in results.items():
                pizza_name = key.split("#")[0]
                spec = PIZZAS[pizza_name]
                need = spec["need"]
                correct = len(chosen & need)
                wrong = len(chosen - (need | spec["opts"]))
                total_correct += correct
                total_wrong += wrong
                total_need += len(need)

            score = max(0, total_correct - total_wrong)
            money = score * 5
            xp = score * 4
            if total_correct == total_need and total_wrong == 0:
                money += 10
                xp += 6

            if score == 0:
                st.error("Klanten boos: je hebt niks goed gedaan. Geen verkoop.")
                save_event(p, "Pizzabakker: gefaald (geen correcte ingrediënten)")
            else:
                p["money"] += money
                p["xp"] += xp
                save_event(p, f"Pizzabakker: score {score} → +€{money}, +{xp} XP")
                st.success(f"Verkocht! +€{money}, +{xp} XP (score {score})")

            save_profiles(profiles)

    # --- Rang updates ---
    profiles = update_special_ranks(profiles)

    # --- Toon alle spelers ---
    st.subheader("👥 Alle spelers")
    for prof in profiles:
        rang = get_rank(prof["xp"])
        if prof.get("special_rank"):
            rang = prof["special_rank"]
        st.write(f"{prof['username']} | Geld: €{prof['money']} | XP: {prof['xp']} | Rang: {rang} | Stad: {prof['city']}")
