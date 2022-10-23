from multiprocessing.dummy import Manager
from settings import *
from src.camera import Camera
from src.humanoids import Humanoid, Player, Paralyze
from src.font_engine import FontEngine
from src.timer import Timer
from src.sounds import Sounds

import pygame as pg


class Animation:

    def __init__(self, sprites: list) -> None:

        self.sprites = sprites

        self.iter = iter(self.sprites)
        self.cur_sprite = next(self.iter)
        
        self.new_timer()

    def new_timer(self) -> None:
        self.timer = Timer(CECIL_ANIMATION_SPEED)

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
            'wall_window': pg.transform.scale(pg.image.load('static/wall_window.jpg').convert(), (self.width / 5, self.height - self.height / HALLWAY_HEIGHT_RATIO * 2)),
            'cecil_base': pg.transform.scale(pg.image.load('static/cecil_base.png').convert_alpha(), (self.width / 15, self.height - self.height / HALLWAY_HEIGHT_RATIO * 3.8)),
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

        self.to_say = None
        self.to_say_timer = None
        self.to_say_progress = None
        self.next_letter_timer = None
        self.evil = False

        self.font_engine = FontEngine(self.height // 30)

        self.cecil_right_animation = Animation(
            [self.sprites['cecil_walk_right1'], self.sprites['cecil_walk_right2'], self.sprites['cecil_walk_right3']]
        )
        self.cecil_left_animation = Animation(
            [self.sprites['cecil_walk_left1'], self.sprites['cecil_walk_left2'], self.sprites['cecil_walk_left3']]
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

    def draw_paralyze(self, paralyze: Paralyze) -> None:

        if paralyze.killed == False:
            self.sc.blit(self.sprites['paralyze1'], (paralyze.position.x - self.camera.offset.x, paralyze.position.y - self.camera.offset.y))
        else:
            self.sc.blit(self.sprites['paralyze2'], (paralyze.position.x - self.camera.offset.x, paralyze.position.y - self.camera.offset.y))

    def draw_bars(self) -> None:

        pg.draw.rect(self.sc, self.background_color, (0, 0, self.width, self.height / HALLWAY_HEIGHT_RATIO))
        pg.draw.rect(self.sc, self.background_color, (0, self.height - self.height / HALLWAY_HEIGHT_RATIO, self.width, self.height / HALLWAY_HEIGHT_RATIO))

    def draw_parts(self, parts, position) -> None:

        rain_visible = False
        rain_distance = 999999999999999999

        for part in parts:

            if part.x >= self.camera.offset.x - self.part_width and part.x <= self.camera.offset.x + self.width:

                if part.type == WALL_BASE:
                    image = self.sprites['wall_base']
                elif part.type == WALL_WINDOW:
                    image = self.sprites['wall_window']
                    rain_visible = True
                    if position.x > part.x + self.part_width // 2:
                        new_rain_distance = position.x - (part.x + self.part_width // 2)
                    else:
                        new_rain_distance = (part.x + self.part_width // 2) - position.x
                    if new_rain_distance <= rain_distance:
                        rain_distance = new_rain_distance
                    

                self.sc.blit(image, (part.x - self.camera.offset.x, self.height / HALLWAY_HEIGHT_RATIO - self.camera.offset.y))
        
        return rain_visible, rain_distance
    
    def draw_parts_transparency(self, parts, blink: bool = False, dead: bool = False) -> None:

        for part in parts:

            if part.x >= self.camera.offset.x - self.part_width and part.x <= self.camera.offset.x + self.width:

                # 32 is a number used by pygame
                surface = pg.Surface((self.part_width, self.part_height), pg.SRCALPHA, 32)
                surface = surface.convert_alpha()

                if not dead:
                    if not blink:
                        surface.fill((0, 0, 0, part.transparency))
                    else:
                        surface.fill((255, 255, 255, 100))
                else:
                    surface.fill((0, 0, 0, 200))


                self.sc.blit(surface, (part.x - self.camera.offset.x, self.height / HALLWAY_HEIGHT_RATIO - self.camera.offset.y))
    
    def draw_cecil(self, cecil: Player, dead: bool = False) -> None:

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
    
        self.sc.blit(image, (cecil.position.x - self.camera.offset.x, cecil.position.y - self.camera.offset.y))
    
    def say(self, text, letter_add_speed, letter_color, evil: bool = False) -> None:

        self.to_say = text
        self.to_say_progress = ''
        self.next_letter_timer = Timer(LETTER_ADD_SPEED)

        self.evil = evil
        self.letter_add_speed = letter_add_speed
        self.letter_color = letter_color

    def draw_say_update(self, sounds: Sounds) -> None:

        if self.to_say == None:
            return

        if self.to_say == self.to_say_progress and self.to_say_timer == None:
            self.to_say_timer = Timer(TEXT_DISSAPEAR_TIME)
        
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
        
        rendered_text = self.font_engine.render(self.to_say_progress, self.letter_color)

        self.sc.blit(rendered_text, (self.width // 300, self.height - self.height / HALLWAY_HEIGHT_RATIO + (self.height / HALLWAY_HEIGHT_RATIO // 2) - self.font_engine.font.get_height() // 2))
        
