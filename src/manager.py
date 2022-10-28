from settings import *
from src.sounds import Sounds
from src.humanoids import Player

import pygame as pg
import random


class Room:

    def __init__(self, x, room_type, blood: bool = False) -> None:

        self.x = x
        self.type = room_type
        self.blood = blood
        self.transparency = 255

        self.digit = random.randint(1, 10000)
        self.used = False
        self.open = False


class Manager:

    def __init__(self) -> None:

        self.parts = []
        self.used_parts = []
        self.part_width = None

    def _get_room_random(self, x, is_room: bool = False) -> Room:

        blood = False

        if not is_room:

            room_type = random.randint(1, 80)

            if room_type == 1:
                room_type = WALL_IMAGE_ONE
            elif room_type == 2:
                room_type = WALL_IMAGE_TWO
            elif room_type >= 3 and room_type <= 10:
                room_type = WALL_DOOR
            elif room_type >= 11 and room_type <= 15:
                room_type = WALL_CLOSET_F
            elif room_type >= 16 and room_type <= 40:
                room_type = WALL_WINDOW
                if random.randint(1, 8) == 1:
                    blood = True
            elif room_type >= 41 and room_type <= 41:
                room_type = WALL_EXIT
            else:
                room_type = WALL_BASE
                if random.randint(1, 8) == 1:
                    blood = True 
        
        else:

            room_type = random.randint(1, 5)

            if room_type == 3:
                room_type = WALL_ROOM_BED
            elif room_type == 4:
                room_type = WALL_ROOM_BOOK
            elif room_type == 5:
                room_type = WALL_ROOM_CLOSET
            else:
                room_type = WALL_ROOM_BASE
                if random.randint(1, 3) == 1:
                    blood = True

        room = Room(x, room_type, blood)

        return room

    def generate_rooms(self, player_position: pg.Vector2, part_width, room: bool = False) -> None:

        if not self.part_width:
            self.part_width = part_width

        if not room:

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

                room = self._get_room_random(x)

                self.parts.append(room)
        
        else:

            room_num = random.randint(-1, 1)

            for i in range(-3, 3):
                
                try:
                    x = part_width * i
                    x = x // part_width * part_width
                except ZeroDivisionError:
                    continue

                room = self._get_room_random(x, True)

                if room_num == i:
                    room = Room(x, WALL_ROOM_DOOR)

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

    def update_needed(self, player: Player, terminal_distance: any) -> bool:

        player_position = player.position
        
        right_block = self.parts[-1]
        left_block = self.parts[0]

        created = False

        if right_block.x > player_position.x:
            right_distance = right_block.x - player_position.x
        else:
            right_distance = player_position.x - right_block.x
        
        if left_block.x > player_position.x:
            left_distance = left_block.x - player_position.x
        else:
            left_distance = player_position.x - left_block.x

        if right_distance <= terminal_distance or left_distance <= terminal_distance:

            if right_distance < left_distance:
                room = self._get_room_random(right_block.x + self.part_width)
                self.parts.append(room)
                self.parts.pop(0)
            else:
                room = self._get_room_random(left_block.x - self.part_width)
                self.parts.insert(0, room)
                self.parts.pop(-1)
            
            created = True
        
        return created