# game.py
import random

def get_random_prize():
    prizes = [0, 20, 50, 100, 200, 500]
    weights = [40, 25, 15, 10, 7, 3]
    return random.choices(prizes, weights=weights)[0]
