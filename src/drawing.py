from multiprocessing.dummy import Manager
from settings import *
from src.camera import Camera
from src.humanoids import *
from src.font_engine import FontEngine
from src.timer import Timer
from src.sounds import Sounds

import pygame as pg
import random


class Animation:

    def __init__(self, sprites: list, speed) -> None:

        self.sprites = sprites

        self.iter = iter(self.sprites)
        self.cur_sprite = next(self.iter)
        self.speed = speed
        
        self.new_timer()

    def new_timer(self) -> None:
        self.timer = Timer(self.speed)

    def get_sprite(self) -> None:

        if self.timer.done:

            try:
                self.cur_sprite = next(self.iter)
            except StopIteration:
                self.iter = iter(self.sprites)
                self.cur_sprite = next(self.iter)
            
            self.new_timer()
        
        return self.cur_sprite


class Drawing:

    def __init__(self, sc: pg.Surface, camera: Camera) -> None:

        self.sc = sc
        self.width = sc.get_width()
        self.height = sc.get_height()

        self.camera = camera
        
        self.fill_each_frame = True
        self.background_color = BLACK

        self.sprites = {
            'wall_base': pg.transform.scale(pg.image.load('static/wall_base.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_exit': pg.transform.scale(pg.image.load('static/wall_exit.png').convert_alpha(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_exit_open': pg.transform.scale(pg.image.load('static/wall_exit_open.png').convert_alpha(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_image': pg.transform.scale(pg.image.load('static/wall_image.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_image2': pg.transform.scale(pg.image.load('static/wall_image2.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_door': pg.transform.scale(pg.image.load('static/wall_door.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_room_base': pg.transform.scale(pg.image.load('static/wall_room_base.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_room_bed': pg.transform.scale(pg.image.load('static/wall_room_bed.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_room_book': pg.transform.scale(pg.image.load('static/wall_room_book.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_room_book_open': pg.transform.scale(pg.image.load('static/wall_room_book_open.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_room_closet': pg.transform.scale(pg.image.load('static/wall_room_closet.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_room_closet_open': pg.transform.scale(pg.image.load('static/wall_room_closet_open.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_room_door': pg.transform.scale(pg.image.load('static/wall_room_door.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'blood': pg.transform.scale(pg.image.load('static/blood.png').convert_alpha(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'closet_f': pg.transform.scale(pg.image.load('static/wall_closet_f.png').convert_alpha(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_window1': pg.transform.scale(pg.image.load('static/wall_window1.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_window2': pg.transform.scale(pg.image.load('static/wall_window2.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_window3': pg.transform.scale(pg.image.load('static/wall_window3.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'wall_window4': pg.transform.scale(pg.image.load('static/wall_window4.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'cecil_base': pg.transform.scale(pg.image.load('static/cecil_base.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)),
            'cecil_dead': pg.transform.scale(pg.image.load('static/cecil_dead.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)),
            'cecil_dead1': pg.transform.scale(pg.image.load('static/cecil_dead1.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)),
            'batia': pg.transform.scale(pg.image.load('static/batia.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)),
            'cecil_walk_right1': pg.transform.scale(pg.image.load('static/cecil_walk1.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)),
            'cecil_walk_right2': pg.transform.scale(pg.image.load('static/cecil_walk2.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)),
            'cecil_walk_right3': pg.transform.scale(pg.image.load('static/cecil_walk3.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)),
            'cecil_walk_left1': pg.transform.flip(pg.transform.scale(pg.image.load('static/cecil_walk1.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)), True, False),
            'cecil_walk_left2': pg.transform.flip(pg.transform.scale(pg.image.load('static/cecil_walk2.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)), True, False),
            'cecil_walk_left3': pg.transform.flip(pg.transform.scale(pg.image.load('static/cecil_walk3.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)), True, False),
            'cecil_crawl_right': pg.transform.scale(pg.image.load('static/cecil_crawl.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)),
            'cecil_crawl_left': pg.transform.flip(pg.transform.scale(pg.image.load('static/cecil_crawl.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)), True, False),
        }

        self.part_height = self.sprites['wall_base'].get_height()
        self.part_width = self.sprites['wall_base'].get_width()

        self.sprites['paralyze1'] = pg.transform.scale(pg.image.load('static/paralyze1.png').convert_alpha(), (self.part_width / 2, self.height - self.height / HALLWAY_HEIGHT_RATIO * 1.8))
        self.sprites['paralyze2'] = pg.transform.scale(pg.image.load('static/paralyze2.png').convert_alpha(), (self.part_width / 2, self.height - self.height / HALLWAY_HEIGHT_RATIO * 1.8))

        self.sprites['fisherman'] = pg.transform.scale(pg.image.load('static/fisherman.png').convert_alpha(), (self.part_width, self.height - self.height / HALLWAY_HEIGHT_RATIO * 1.5))

        self.sprites['mimic'] = pg.transform.scale(pg.image.load('static/mimic.png').convert_alpha(), (self.part_width / 1, self.height - self.height / HALLWAY_HEIGHT_RATIO * 1.5))

        self.sprites['marathoner1'] = pg.transform.scale(pg.image.load('static/marathoner_run1.png').convert_alpha(), (self.part_width * 2, self.height - self.height / HALLWAY_HEIGHT_RATIO * 1.1))
        self.sprites['marathoner2'] = pg.transform.scale(pg.image.load('static/marathoner_run2.png').convert_alpha(), (self.part_width * 2, self.height - self.height / HALLWAY_HEIGHT_RATIO * 1.1))
        self.sprites['marathoner3'] = pg.transform.scale(pg.image.load('static/marathoner_run3.png').convert_alpha(), (self.part_width * 2, self.height - self.height / HALLWAY_HEIGHT_RATIO * 1.1))
        self.sprites['marathoner_kill'] = pg.transform.scale(pg.image.load('static/marathoner_kill.png').convert_alpha(), (self.part_width * 2, self.height - self.height / HALLWAY_HEIGHT_RATIO * 1.1))

        self.to_say = None
        self.to_say_timer = None
        self.to_say_progress = None
        self.next_letter_timer = None
        self.evil = False
        self.is_credits = False

        self.font_engine = FontEngine(self.height // 30)

        self.cecil_right_animation = Animation(
            [self.sprites['cecil_walk_right1'], self.sprites['cecil_walk_right2'], self.sprites['cecil_walk_right3']], CECIL_ANIMATION_SPEED
        )
        self.cecil_left_animation = Animation(
            [self.sprites['cecil_walk_left1'], self.sprites['cecil_walk_left2'], self.sprites['cecil_walk_left3']], CECIL_ANIMATION_SPEED
        )

        self.window_animation = Animation(
            [self.sprites['wall_window1'], self.sprites['wall_window2'], self.sprites['wall_window3'], self.sprites['wall_window4']], WINDOW_ANIMATION_SPEED
        )

        self.marathoner_animation = Animation(
            [self.sprites['marathoner1'], self.sprites['marathoner2'], self.sprites['marathoner3']], MARATHONER_ANIMATION_SPEED
        )

        self.letter_add_speed = 0
        self.letter_color = 0

    def check_visibility(self, x: any, manager: Manager) -> any:

        part_x = x // self.part_width * self.part_width

        for part in manager.parts:

            if not part_x == part.x:
                continue

            if part.x >= self.camera.offset.x - self.part_width and part.x <= self.camera.offset.x + self.width:
                
                if part.transparency <= VISIBILE_TRANSPARENCY:
                    return True
                else:
                    return False
            
            return False

        return False

    def draw_marathoner(self, marathoner: Marathoner, dead: bool = False) -> None:

        if not dead:
            self.sc.blit(self.marathoner_animation.get_sprite(), (marathoner.position.x - self.camera.offset.x, marathoner.position.y - self.camera.offset.y))
        else:
            self.sc.blit(self.sprites['marathoner_kill'], (marathoner.position.x - self.camera.offset.x, marathoner.position.y - self.camera.offset.y))

    def draw_mimic(self, mimic: Mimic, cecil: Player) -> None:

        if not mimic:
            return

        if mimic.trigered:
            self.sc.blit(self.sprites['mimic'], (mimic.position.x - self.camera.offset.x, mimic.position.y - self.camera.offset.y))
        else:
            self.sc.blit(self.sprites['cecil_base'], (mimic.position.x + self.sprites['cecil_base'].get_width() - self.camera.offset.x, cecil.position.y - self.camera.offset.y))

    def draw_paralyze(self, paralyze: Paralyze) -> None:

        if paralyze.killed == False:
            self.sc.blit(self.sprites['paralyze1'], (paralyze.position.x - self.camera.offset.x, paralyze.position.y - self.camera.offset.y))
        else:
            self.sc.blit(self.sprites['paralyze2'], (paralyze.position.x - self.camera.offset.x, paralyze.position.y - self.camera.offset.y))

    def draw_fisherman(self, fisherman: Fisherman) -> None:

        self.sc.blit(self.sprites['fisherman'], (fisherman.position.x - self.camera.offset.x, fisherman.position.y - self.camera.offset.y))

    def draw_bars(self) -> None:
        
        if not self.background_color == DARK_RED:
            pg.draw.rect(self.sc, self.background_color, (0, 0, self.width, self.height / HALLWAY_HEIGHT_RATIO))
            pg.draw.rect(self.sc, self.background_color, (0, self.height - self.height / HALLWAY_HEIGHT_RATIO, self.width, self.height / HALLWAY_HEIGHT_RATIO))
        else:
            pg.draw.rect(self.sc, (random.randint(10, 60), 0, 0), (0, 0, self.width, self.height / HALLWAY_HEIGHT_RATIO))
            pg.draw.rect(self.sc, (random.randint(10, 60), 0, 0), (0, self.height - self.height / HALLWAY_HEIGHT_RATIO, self.width, self.height / HALLWAY_HEIGHT_RATIO))

    def draw_parts(self, parts, position) -> None:

        rain_visible = False
        rain_distance = 999999999999999999
        in_part = None

        for part in parts:

            if part.x == (position.x + self.sprites['cecil_base'].get_width() / 2) // self.part_width * self.part_width:
                in_part = part

            if part.x >= self.camera.offset.x - self.part_width and part.x <= self.camera.offset.x + self.width:

                if part.type == WALL_BASE:
                    image = self.sprites['wall_base']
                elif part.type == WALL_WINDOW:
                    image = self.window_animation.get_sprite()
                    rain_visible = True
                    if position.x > part.x + self.part_width // 2:
                        new_rain_distance = position.x - (part.x + self.part_width // 2)
                    else:
                        new_rain_distance = (part.x + self.part_width // 2) - position.x
                    if new_rain_distance <= rain_distance:
                        rain_distance = new_rain_distance
                elif part.type == WALL_DOOR:
                    image = self.sprites['wall_door']
                elif part.type == WALL_IMAGE_ONE:
                    image = self.sprites['wall_image']
                elif part.type == WALL_IMAGE_TWO:
                    image = self.sprites['wall_image2']
                elif part.type == WALL_ROOM_BED:
                    image = self.sprites['wall_room_bed']
                elif part.type == WALL_ROOM_BOOK:
                    if part.open == False:
                        image = self.sprites['wall_room_book']
                    else:
                        image = self.sprites['wall_room_book_open']
                elif part.type == WALL_ROOM_CLOSET:
                    if part.open == False:
                        image = self.sprites['wall_room_closet']
                    else:
                        image = self.sprites['wall_room_closet_open']
                elif part.type == WALL_ROOM_BASE:
                    image = self.sprites['wall_room_base']
                elif part.type == WALL_ROOM_DOOR:
                    image = self.sprites['wall_room_door']
                elif part.type == WALL_CLOSET_F:
                    image = self.sprites['wall_base']
                elif part.type == WALL_EXIT:
                    self.sc.blit(self.sprites['wall_base'], (part.x - self.camera.offset.x, self.height / HALLWAY_HEIGHT_RATIO - self.camera.offset.y))
                    if part.open == False:
                        image = self.sprites['wall_exit']
                    else:
                        image = self.sprites['wall_exit_open']

                self.sc.blit(image, (part.x - self.camera.offset.x, self.height / HALLWAY_HEIGHT_RATIO - self.camera.offset.y))

                if part.blood == True:
                    self.sc.blit(self.sprites['blood'], (part.x - self.camera.offset.x, self.height / HALLWAY_HEIGHT_RATIO - self.camera.offset.y))
                if part.type == WALL_CLOSET_F:
                    self.sc.blit(self.sprites['closet_f'], (part.x - self.camera.offset.x, self.height / HALLWAY_HEIGHT_RATIO - self.camera.offset.y))

                if part.type == WALL_EXIT:
                    if part.open:
                        self.sc.blit(self.sprites['batia'], (part.x + self.sprites['batia'].get_width() - self.camera.offset.x, self.height - self.sprites['batia'].get_height() - self.height / HALLWAY_HEIGHT_RATIO - self.camera.offset.y))

        return rain_visible, rain_distance, in_part
    
    def draw_parts_transparency(self, parts, blink: bool = False, dead: bool = False, boost = None, debuff = None) -> None:

        for part in parts:

            if part.x >= self.camera.offset.x - self.part_width and part.x <= self.camera.offset.x + self.width:

                # 32 is a number used by pygame
                surface = pg.Surface((self.part_width, self.part_height), pg.SRCALPHA, 32)
                surface = surface.convert_alpha()
    
                if not dead:
                    if not blink:
                        if not boost and not debuff:
                            surface.fill((0, 0, 0, part.transparency))
                        elif not boost and debuff:
                            if part.transparency < 200:
                                part.transparency = 200
                            surface.fill((0, 0, 0, part.transparency))
                        elif boost and not debuff:
                            surface.fill((0, 0, 0, part.transparency / 5))
                    else:
                        surface.fill((255, 255, 255, 100))
                else:
                    surface.fill((0, 0, 0, 200))


                self.sc.blit(surface, (part.x - self.camera.offset.x, self.height / HALLWAY_HEIGHT_RATIO - self.camera.offset.y))

    def draw_stamina_bar(self, cecil: Player) -> None:

        amount = cecil.stamina / CECIL_STAMINA_MAX
        length = self.width * amount

        pg.draw.rect(self.sc, (30, 30, 30), (self.width / 2 - length / 2, self.height / (HALLWAY_HEIGHT_RATIO * 2), length, self.height / (HALLWAY_HEIGHT_RATIO * 10)))
    
    def draw_cecil(self, cecil: Player, dead: bool = False, outro: bool = False) -> None:

        state = cecil.direction

        if not dead:
            if state == Humanoid.STATIC:
                image = self.sprites['cecil_base']
            else:
                if not cecil.crawling:
                    if state == Humanoid.RIGHT:
                        image = self.cecil_right_animation.get_sprite()
                    else:
                        image = self.cecil_left_animation.get_sprite()
                else:
                    if state == Humanoid.RIGHT:
                        image = self.sprites['cecil_crawl_right']
                    else:
                        image = self.sprites['cecil_crawl_left']
        else:
            image = self.sprites['cecil_base']

        if outro:
            if cecil.cecil_state == Player.DEAD_STANDING:
                image = self.sprites['cecil_dead']
            elif cecil.cecil_state == Player.DEAD_LAYING:
                image = self.sprites['cecil_dead1']
        
        if not image == self.sprites['cecil_dead1']:
            self.sc.blit(image, (cecil.position.x - self.camera.offset.x, cecil.position.y - self.camera.offset.y))
        else:
            self.sc.blit(image, (cecil.position.x - self.camera.offset.x, cecil.position.y + self.height / HALLWAY_HEIGHT_RATIO / 5 - self.camera.offset.y))
    
    def say(self, text, letter_add_speed, letter_color, evil: bool = False, is_credits: bool = False) -> None:

        self.to_say = text
        self.to_say_progress = ''
        self.next_letter_timer = Timer(letter_add_speed)

        self.evil = evil
        self.letter_add_speed = letter_add_speed
        self.letter_color = letter_color
        self.is_credits = is_credits

    def draw_say_update(self, sounds: Sounds, credits_up: bool = False, shake: bool = False) -> None:

        if self.to_say == None:
            return

        if self.to_say == self.to_say_progress and self.to_say_timer == None:
            if not self.is_credits:
                self.to_say_timer = Timer(TEXT_DISSAPEAR_TIME)
            else:
                self.to_say_timer = Timer(1)

        if self.to_say_timer != None:
            if self.to_say_timer.done == True:
                
                self.to_say = None
                self.to_say_progress = None
                self.to_say_timer = None
        
        if self.to_say != self.to_say_progress:

            if self.next_letter_timer != None:
                if self.next_letter_timer.done:
                    letter = self.to_say[len(self.to_say_progress)]
                    self.to_say_progress += letter
                    self.next_letter_timer = Timer(self.letter_add_speed)
                    if letter != ' ':
                        if not self.evil:
                            sounds.play('blip')
                        else:
                            sounds.play('evil_blip')
        
        new_text = self.to_say_progress

        if self.to_say_progress:
            if self.evil:
                shake = True
                new_text = ''
                for letter in self.to_say_progress:
                    if random.randint(1, 5) == 1:
                        new_text += '?'
                    else:
                        new_text += letter

        rendered_text = self.font_engine.render(new_text, self.letter_color)
        
        if shake:

            rotated_image = pg.transform.rotate(rendered_text, random.randint(-4, 4))
            new_rect = rotated_image.get_rect(center = rendered_text.get_rect(center = (self.width / 2 - rendered_text.get_width() / 2, self.height - self.height / HALLWAY_HEIGHT_RATIO + (self.height / HALLWAY_HEIGHT_RATIO // 2) - self.font_engine.font.get_height() // 2)).center)
            self.sc.blit(rendered_text, (new_rect.x, new_rect.y))
        
        else:

            
            if credits_up:
                self.sc.blit(rendered_text, (self.width / 2 - rendered_text.get_width() / 2, self.height / 2))
            else:
                self.sc.blit(rendered_text, (self.width / 2 - rendered_text.get_width() / 2, self.height - self.height / HALLWAY_HEIGHT_RATIO + (self.height / HALLWAY_HEIGHT_RATIO // 2) - self.font_engine.font.get_height() // 2))
            

        
