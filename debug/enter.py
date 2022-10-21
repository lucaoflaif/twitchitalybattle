from pynput.keyboard import Key, Controller
import time
import random

regions = ['abruzzo', 'basilicata', 'calabria', 'campania', 'emilia romagna', 'friuli venezia giulia',
'lazio', 'liguria', 'lombardia', 'marche', 'molise', 'piemonte', 'puglia','sardegna', 'sicilia',
'toscana', 'trentino alto adige', 'umbria', "valle d'aosta", 'veneto']
time.sleep(4)

def write(text):
    for word in text:
        keyboard.press(word)
        keyboard.release(word)

keyboard = Controller()

for _ in range(800):
    write(random.choice(regions))
    time.sleep(0.4)
    keyboard.press(Key.enter)

    keyboard.release(Key.enter)