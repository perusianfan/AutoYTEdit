import os
import random

INPUT_DIR = "input"
OUTPUT_DIR = "output"
TEMP_DIR = "temp"

FONTS = ["Arial", "Impact", "Helvetica", "Verdana"]
COLORS = [(255, 255, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (0, 255, 0)]
SHADOW_COLORS = [(0, 0, 0), (50, 50, 50), (30, 30, 30)]

CAPTIONS = [
    "WAIT FOR IT...", "NO WAY!", "LOOK AT THIS!", "INSANE!", "OMG!",
    "EPIC MOMENT", "LEGENDARY", "UNBELIEVABLE", "CRAZY!", "WOW!",
    "WATCH THIS", "HERE IT COMES", "BOOM!", "LET'S GO!", "FIRE!",
    "SHEESH!", "GOATED", "W MOMENT", "PEAK CONTENT", "VIBES"
]

INTRO_TEXTS = [
    "POV:", "WHEN YOU", "ME WHEN", "THAT MOMENT WHEN", "NOBODY:",
    "LITERALLY ME:", "REAL ONES KNOW", "FACTS:", "BE LIKE:"
]

ZOOM_INTENSITY = (1.05, 1.3)
SHAKE_INTENSITY = (2, 8)
SPEED_VARIATIONS = [0.5, 0.75, 1.0, 1.25, 1.5]

DETECTION_CONFIDENCE = 0.5
PERSON_CLASS_ID = 0

USE_GPU = True

def get_random_caption():
    return random.choice(CAPTIONS)

def get_random_intro():
    return random.choice(INTRO_TEXTS)

def get_random_color():
    return random.choice(COLORS)

def get_random_font():
    return random.choice(FONTS)

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)