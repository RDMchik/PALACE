from settings import *
from src.sounds import Sounds

import pygame as pg
import random


class Room:

    def __init__(self, x, room_type) -> None:

        self.x = x
        self.type = room_type
        self.transparency = 255


class Manager:

    def __init__(self) -> None:

        self.parts = []
        self.used_parts = []

    def generate_rooms(self, player_position: pg.Vector2, part_width) -> None:

        for i in range(-HALLWAY_LOAD_LENGTH, HALLWAY_LOAD_LENGTH+1):
            
            try:
                x = part_width * i
                x = (x + player_position.x) // part_width * part_width 
            except ZeroDivisionError:
                continue

            found = False
            for part in self.parts:
                if part.x == x:
                    found = True
                    break

            if found:
                continue

            room_type = random.randint(1, 3)

            if room_type == 3:
                room_type = WALL_WINDOW
            else:
                room_type = WALL_BASE

            room = Room(
                x, room_type
            )

            self.parts.append(room)

    def change_trasnsparency(self, x: any, change: any, sounds: Sounds) -> None:

        for part in self.parts:
            if part.x == x:
                if part.transparency + change >= MIN_DARKNESS and part.transparency <= MAX_DARKNESS:
                    if not part in self.used_parts:
                        self.used_parts.append(part)
                        sounds.play('scan')
                    part.transparency += change

    def update_used_parts(self, delta) -> None:

        to_remove = []

        for part in self.used_parts:
            if part.transparency + BLACKOUT_SPEED * delta <= MAX_DARKNESS:
                part.transparency += BLACKOUT_SPEED * delta
            else:
                part.transparency = MAX_DARKNESS
                to_remove.append(part)
        for part in to_remove:
            self.used_parts.remove(part)
