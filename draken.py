import json

import os

import math

import pgzrun

from pgzero.actor import Actor

from random import randint
from pgzero.clock import clock

import random
eieren_origineel = []  
eieren_nieuw = []      
EI_DOEL = 20

WIDTH = 800
eieren_speler1 = 100
eieren_speler2 = 100
HEIGHT = 600

MIDDEN_X = WIDTH / 2

MIDDEN_Y = HEIGHT / 2

MIDDEN = (MIDDEN_X, MIDDEN_Y)

FONT_KLEUR = (0, 0, 0)

EIEREN_DOEL = 20

HELD_START = (200, 300)
onzichtbaar_tijd = 0  
onzichtbaar = False  

HELD2_START = (200, 350)

AANVAL_AFSTAND = 200

DRAAK_WEKTIJD= 2

EIEREN_VERBERGTIJD = 2

BEWEGEN_AFSTAND = 5

actieve_wereld = "origineel"
huidig_slot = "slot1"  
huidige_scherm = "start" 

def get_bestandsnaam(slot):
    return f"game_data_{slot}.json"

def laad_save_slot(nummer):
    global huidig_slot, eieren_verzameld, levens, wereld_ontgrendeld, schild, BEWEGEN_AFSTAND
    huidig_slot = f"slot{nummer}"
    bestand = get_bestandsnaam(huidig_slot)  # Bestandsnaam wordt nu goed ingesteld
    if os.path.exists(bestand):
        with open(bestand, 'r') as f:
            data = json.load(f)
            eieren_verzameld = data.get('eieren_verzameld', 0)
            levens = data.get('levens', 3)
            wereld_ontgrendeld = data.get('wereld_ontgrendeld', False)
            schild = data.get('schild', False)
            BEWEGEN_AFSTAND = data.get('BEWEGEN_AFSTAND', 5)
        print(f"Gegevens geladen uit {bestand}.")
    else:
        print(f"Geen opgeslagen gegevens voor {bestand}.")

def opslaan(pos):
    if huidig_slot is None:
        print("Geen slot gekozen!")
        return
    bestand = get_bestandsnaam(huidig_slot)  # Bestandsnaam wordt nu goed ingesteld
    with open(bestand, 'w') as f:
        json.dump({
            'eieren_speler1': eieren_speler1,
            'eieren_speler2': eieren_speler2,
            'wereld_ontgrendeld': wereld_ontgrendeld,
            'levens': levens,
            'eieren_verzameld': eieren_verzameld,
            'schild': schild,
            'BEWEGEN_AFSTAND': BEWEGEN_AFSTAND,
        }, f)
    print(f"Spel opgeslagen in {bestand}.")



levens = 3

eieren_verzameld = 100

game_over = False

game_complete = False

reset_vereist = False

shop_open = False

schild = False

wereld_ontgrendeld = False
 
shop_items = [
    {'naam': 'Extra Leven', 'prijs': 5},
    {'naam': 'Schild', 'prijs': 7},
    {'naam': 'Nieuwe Wereld', 'prijs': 100},  
]


BESTAND = "save_data.json"
 

def teken_shop():
    screen.draw.text("WINKEL", center=(400, 50), fontsize=60, color=(255, 255, 255))
    screen.draw.text("1. Extra Leven (5 eieren)", center=(400, 150), fontsize=40)
    screen.draw.text("2. Schild (7 eieren)", center=(400, 200), fontsize=40)
    screen.draw.text("3. Nieuwe Wereld (100 eieren)", center=(400, 250), fontsize=40)
    screen.draw.text("4. Onzichtbaarheid (10 eieren)", center=(400, 300), fontsize=40)
        

makkelijke_grot = {
    'draak': Actor('dragon-asleep', pos=(550, 100)),
    'eieren': Actor('one-egg', pos=(400, 100)),
    'ei_tellen': 1,
    'ei_verborgen':False,
    'ei_verberg_teller': 0,
    'slaap_lengte': 10,
    'slaap_teller': 0,
    'wekken_teller': 0
}
medium_grot = {
    'draak': Actor('dragon-asleep', pos=(550, 300)),
    'eieren': Actor('two-eggs', pos=(400, 300)),
    'ei_tellen': 2,
    'ei_verborgen':False,
    'ei_verberg_teller': 0,
    'slaap_lengte': 7,
    'slaap_teller': 0,
    'wekken_teller': 0
}
moeilijke_grot = {
    'draak': Actor('dragon-asleep', pos=(550, 500)),
    'eieren': Actor('three-eggs', pos=(400, 500)),
    'ei_tellen': 3,
    'ei_verborgen':False,
    'ei_verberg_teller': 0,
    'slaap_lengte': 4,
    'slaap_teller': 0,
    'wekken_teller': 0
}
grotten = [makkelijke_grot, medium_grot, moeilijke_grot]
held = Actor('hero', pos=HELD_START)
held2 = Actor('hero2', pos=HELD2_START)
 
 
def draw():
    screen.clear()

    if huidige_scherm == "start":
        screen.draw.text("Kies een save-slot:", center=(400, 100), fontsize=50)
        screen.draw.text("1. Slot 1", center=(400, 200), fontsize=40)
        screen.draw.text("2. Slot 2", center=(400, 300), fontsize=40)
        screen.draw.text("3. Slot 3", center=(400, 400), fontsize=40)
        return

    elif huidige_scherm == "wereld_kiezen":
        screen.draw.text("Kies een wereld:", center=(400, 100), fontsize=50)
        screen.draw.text("1. Wereld 1", center=(400, 200), fontsize=40)
        if wereld_ontgrendeld:
            screen.draw.text("2. Nieuwe Wereld", center=(400, 300), fontsize=40)
        return

    if shop_open:
        screen.blit('dungeon', (0, 0))
        teken_shop()
        return

    if game_over:
        screen.blit('dungeon', (0, 0))
        screen.draw.text('GAME OVER!', fontsize=60, center=MIDDEN, color=FONT_KLEUR)
        return

    # Achtergrond + grotten per wereld
    if actieve_wereld == "nieuw" and wereld_ontgrendeld:
        screen.blit('new-world-background', (0, 0))
        teken_grotten(nieuwe_wereld_grotten)
    else:
        screen.blit('dungeon', (0, 0))
        teken_grotten(grotten)

    held.draw()
    held2.draw()
    teken_tellers(eieren_verzameld, levens)
    screen.draw.text(f"Slot: {huidig_slot}", topleft=(10, 90), fontsize=30, color=(255, 255, 255))

 
    
 
def teken_grotten(grotten_te_tekenen):
 
    for grot in grotten_te_tekenen:
        grot['draak'].draw()
        if grot['ei_verborgen'] is False:
            grot['eieren'].draw()
def teken_tellers(eieren_verzameld, levens):
    screen.blit('egg-count', (0, HEIGHT - 30))
    screen.draw.text(str(eieren_verzameld),
                     fontsize=40,
                     pos=(30, HEIGHT - 30),
                     color=(255, 0, 0))  # Dit is rood
 

    screen.blit('life-count', (60, HEIGHT - 30))
    screen.draw.text(str(levens),
                     fontsize=40,
                     pos=(90, HEIGHT - 30),
                     color= (255, 0, 0))  # Dit is rood
 

def update():
    global onzichtbaar, onzichtbaar_tijd
    global shop_open
    if onzichtbaar:
        onzichtbaar_tijd -= 1  # Verlaag de tijd elke frame
        if onzichtbaar_tijd <= 0:
            onzichtbaar = False  # Maak de speler weer zichtbaar na de tijd
            onzichtbaar_tijd = 0  # Reset de timer

    
 
    # Open de winkel als spatie wordt ingedrukt, ongeacht in welke wereld je bent
    if keyboard.space:
        shop_open = True
        return  # Zorg ervoor dat je geen beweging uitvoert als de winkel open is
 
    # Sluit de winkel als ESC wordt ingedrukt
    if keyboard.escape:
        shop_open = False
        return  # Stop de winkel zonder dat beweging wordt uitgevoerd
 
    # Als de winkel open is, voer geen beweging uit
    if shop_open:
        return  
 
    # Beweging van de helden als de winkel niet open is
    if keyboard.right:
        held.x += BEWEGEN_AFSTAND
        if held.x > WIDTH:
            held.x = WIDTH
    elif keyboard.left:
        held.x -= BEWEGEN_AFSTAND
        if held.x < 0:
            held.x = 0
    elif keyboard.down:
        held.y += BEWEGEN_AFSTAND
        if held.y > HEIGHT:
            held.y = HEIGHT
    elif keyboard.up:
        held.y -= BEWEGEN_AFSTAND
        if held.y < 0:
            held.y = 0
 
    if keyboard.d:
        held2.x += BEWEGEN_AFSTAND
        if held2.x > WIDTH:
            held2.x = WIDTH
    elif keyboard.a:
        held2.x -= BEWEGEN_AFSTAND
        if held2.x < 0:
            held2.x = 0
    elif keyboard.s:
        held2.y += BEWEGEN_AFSTAND
        if held2.y > HEIGHT:
            held2.y = HEIGHT
    elif keyboard.w:
        held2.y -= BEWEGEN_AFSTAND
        if held2.y < 0:
            held2.y = 0
 
    check_voor_raken()
 
 

def update_grotten():
    global grotten, nieuwe_wereld_grotten, held, held2, levens
 
    grotten_te_gebruiken = nieuwe_wereld_grotten if actieve_wereld == "nieuw" else grotten
 
    for grot in grotten_te_gebruiken:
        if grot['draak'].image == 'dragon-asleep':
            update_slapende_draak(grot)
        elif grot['draak'].image == 'dragon-awake':
            update_wekken_draak(grot)
        update_ei(grot)
 
 

clock.schedule_interval(update_grotten, 1)
def update_slapende_draak(grot):
    if onzichtbaar:  # Als de speler onzichtbaar is, kan hij niet geraakt worden
        return 

    elif grot['slaap_teller'] >= grot['slaap_lengte']:
        if random.choice([True, False]):
            grot['draak'].image = 'dragon-awake'
            grot['slaap_teller'] = 0
    else:
        grot['slaap_teller'] +=1

 

def update_wekken_draak(grot):
    if grot['wekken_teller'] >= DRAAK_WEKTIJD:
        grot['draak'].image = 'dragon-asleep'
        grot['wekken_teller'] = 0
    else:
        grot['wekken_teller'] +=1
 
 

def update_ei(grot):
    if grot['ei_verborgen'] is True:
        if grot['ei_verberg_teller'] >= EIEREN_VERBERGTIJD:
            grot['ei_verborgen'] = False
            grot['ei_verberg_teller'] = 0
        else:
            grot['ei_verberg_teller'] += 1
def check_voor_raken():
    global grotten, nieuwe_wereld_grotten, eieren_verzameld, levens, reset_vereist, game_complete
    grotten_te_controleren = nieuwe_wereld_grotten if actieve_wereld == "nieuw" else grotten
 
    for grot in grotten_te_controleren:
        if grot['ei_verborgen'] is False:
            check_voor_ei_raken(grot)
            if grot['draak'].image == 'dragon-awake' and reset_vereist is False:
                check_voor_draak_raken(grot)
 

def check_voor_draak_raken(grot):
    for h in [held, held2]:
        x_afstand = h.x - grot['draak'].x
        y_afstand = h.y - grot['draak'].y
        afstand = math.hypot(x_afstand, y_afstand)
        if afstand < AANVAL_AFSTAND:
            handle_draak_raken(h)
 
def handle_draak_raken(h):
    global reset_vereist
    reset_vereist = True
    animate(h, pos=HELD_START if h == held else HELD2_START, on_finished=verminder_leven)
 

def check_voor_ei_raken(grot):
    global eieren_verzameld, game_complete
    for h in [held, held2]:
        if h.colliderect(grot['eieren']):
            grot['ei_verborgen'] = True
            eieren_verzameld += grot['ei_tellen']
            opslaan(huidig_slot)
            if eieren_verzameld >= EI_DOEL:
                game_complete = True
 
def on_key_down(key):
    global levens, BEWEGEN_AFSTAND, eieren_verzameld, schild
    global wereld_ontgrendeld, actieve_wereld, huidig_slot, huidige_scherm
    global onzichtbaar, onzichtbaar_tijd  # <-- deze 2 toegevoegd!


    # === RESET ===
    if key == keys.R:
        reset_spel()  # Reset alles naar de beginstatus
        opslaan(huidig_slot)
    # Rest van de code...

    # === SHOP ===
    if shop_open:
        if key == keys.K_1 and eieren_verzameld >= 5:
            levens += 1
            eieren_verzameld -= 5
            opslaan(huidig_slot)

        elif key == keys.K_2 and eieren_verzameld >= 7:
            schild = True
            eieren_verzameld -= 7
            opslaan(huidig_slot)

        elif key == keys.K_3:
            prijs = shop_items[2]['prijs']
            if eieren_verzameld >= prijs and not wereld_ontgrendeld:
                wereld_ontgrendeld = True
                eieren_verzameld -= prijs
                opslaan(huidig_slot)

        elif key == keys.K_4 and eieren_verzameld >= 10:
            onzichtbaar = True
            onzichtbaar_tijd = 10  # seconden
            eieren_verzameld -= 10
            opslaan(huidig_slot)

    # === STARTSCHERM: kies save-slot ===
    elif huidige_scherm == "start":
        if key == keys.K_1:
            laad_save_slot(1)
            huidige_scherm = "wereld_kiezen"
        elif key == keys.K_2:
            laad_save_slot(2)
            huidige_scherm = "wereld_kiezen"
        elif key == keys.K_3:
            laad_save_slot(3)
            huidige_scherm = "wereld_kiezen"

    # === WERELD KIEZEN ===
    elif huidige_scherm == "wereld_kiezen":
        if key == keys.K_1:
            actieve_wereld = "origineel"
            huidige_scherm = "spel"
        elif key == keys.K_2 and wereld_ontgrendeld:
            actieve_wereld = "nieuw"
            huidige_scherm = "spel"



   
    

    
    
    elif key == keys.ESCAPE and huidige_scherm == "spel":
        huidige_scherm = "start"

                
 
nieuwe_wereld_grotten = [
    {
        'draak': Actor('dragon-asleep', pos=(550, 100)),
        'eieren': Actor('one-egg', pos=(400, 100)),
        'ei_tellen': 4,
        'ei_verborgen': False,
        'ei_verberg_teller': 0,
        'slaap_lengte': 3,
        'slaap_teller': 0,
        'wekken_teller': 0
    },
    {
        'draak': Actor('dragon-asleep', pos=(550, 300)),
        'eieren': Actor('two-eggs', pos=(400, 300)),
        'ei_tellen': 5,
        'ei_verborgen': False,
        'ei_verberg_teller': 0,
        'slaap_lengte': 2,
        'slaap_teller': 0,
        'wekken_teller': 0
    },
    {
        'draak': Actor('dragon-asleep', pos=(550, 500)),
        'eieren': Actor('three-eggs', pos=(400, 500)),
        'ei_tellen': 6,
        'ei_verborgen': False,
        'ei_verberg_teller': 0,
        'slaap_lengte': 1,
        'slaap_teller': 0,
        'wekken_teller': 0
    }
]

def reset_spel():
    global levens, eieren_verzameld, wereld_ontgrendeld, schild, actieve_wereld, huidig_slot

    # Reset waarden naar de beginstatus
    levens = 3
    eieren_verzameld = 0
    wereld_ontgrendeld = False
    schild = False
    actieve_wereld = "origineel"

    # Reset de save-bestanden
    opslaan(huidig_slot)


def verminder_leven():
    global levens, reset_vereist, game_over, schild

    if schild:
        schild = False  # Schild breekt, geen leven verliezen
    else:
        levens -= 1  # Geen schild? Dan leven verliezen
        if levens <= 0:
            game_over = True  # Geen levens meer? Game over!

    reset_vereist = False  # Speler is weer veilig na reset

    opslaan(huidig_slot)
def reset_slot(slot):
    global levens, eieren_verzameld, wereld_ontgrendeld, schild, actieve_wereld
    levens = 3
    eieren_verzameld = 0
    wereld_ontgrendeld = False
    actieve_wereld = "origineel"
    schild = False
    opslaan()
 
import atexit
atexit.register(opslaan)
 
laad_save_slot(huidig_slot)
pgzrun.go()            
 

 
