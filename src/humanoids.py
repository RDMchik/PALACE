from settings import *
from src.timer import Timer

import pygame as pg
import random


class Humanoid:
    
    RIGHT = 1
    LEFT = 2
    STATIC = 3

    def __init__(self, x, y) -> None:
        
        self.position = pg.Vector2(x, y)
        self.velocity = pg.Vector2(0, 0)

        self.acceleration = 0
        self.friction = 0
    
    @property
    def walking(self) -> bool:

        if self.velocity.x != 0:
            return True
        else:
            return False

    @property
    def direction(self) -> bool:

        if self.walking:
            if self.velocity.x < 0:
                return Humanoid.LEFT
            elif self.velocity.x > 0:
                return Humanoid.RIGHT
        else:
            return Humanoid.STATIC

    
    def update_position(self, delta) -> None:

        self.position.x += self.velocity.x * delta
        self.position.y += self.velocity.y * delta

        if self.velocity.x != 0:

            if self.velocity.x < 0:
                self.velocity.x += self.friction * delta
                if self.velocity.x >= 0:
                    self.velocity.x = 0
            else:
                self.velocity.x -= self.friction * delta
                if self.velocity.x <= 0:
                    self.velocity.x = 0

        if self.velocity.y != 0:

            if self.velocity.y < 0:
                self.velocity.y += self.friction * delta
                if self.velocity.y >= 0:
                    self.velocity.y = 0
            else:
                self.velocity.y -= self.friction * delta
                if self.velocity.y <= 0:
                    self.velocity.y = 0
    

class Player(Humanoid):

    speeches = [
        ' [CECIL] Why do i feel so wrong...',
        ' [CECIL] I hate my brother...',
        ' [CECIL] How is my dad is so smart...',
        ' [CECIL] I saw my mom die in a nightmare today...',
        ' [CECIL] Did i nightwalk again...?',
        ' [CECIL] I really should get out of my house fast...',
        ' [CECIL] Am i a psychopath? My dad said it can\'t be...',
        ' [CECIL] Dad hates mom...',
        ' [CECIL] I wish i was as kind as my mom...',
        ' [CECIL] I wonder how is my dad so rich...',
        ' [CECIL] I love my doggy so much, i hope he is alright...',
        ' [CECIL] How am i going to go to school tomorrow...'
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.acceleration = CECIL_ACCELERATION
        self.friction = CECIL_FRICTION
        self.crawling = False

        self.next_speech = Timer(random.randint(CECIL_SPEECH_DELAY[0], CECIL_SPEECH_DELAY[1]))
    
    @property
    def terminal_velocity(self) -> float:
        if self.crawling:
            return CECIL_TERMINAL_VELOCITY / 5
        else:
            return CECIL_TERMINAL_VELOCITY

    def walk(self, keys, delta) -> None:

        if keys[pg.K_a]:
            
            self.velocity.x -= self.acceleration * delta
            if self.velocity.x <= -self.terminal_velocity:
                self.velocity.x = -self.terminal_velocity

        if keys[pg.K_d]:
            
            self.velocity.x += self.acceleration * delta
            if self.velocity.x >= self.terminal_velocity:
                self.velocity.x = self.terminal_velocity

        if keys[pg.K_s]:
            self.crawling = True
        else:
            self.crawling = False
    
    def update_position(self, camera, delta) -> None:

        self.position.x += self.velocity.x * delta
        self.position.y += self.velocity.y * delta

        camera.original_offset.x += self.velocity.x * delta
        camera.original_offset.y += self.velocity.y * delta

        if self.velocity.x != 0:

            if self.velocity.x < 0:
                self.velocity.x += self.friction * delta
                if self.velocity.x >= 0:
                    self.velocity.x = 0
            else:
                self.velocity.x -= self.friction * delta
                if self.velocity.x <= 0:
                    self.velocity.x = 0

        if self.velocity.y != 0:

            if self.velocity.y < 0:
                self.velocity.y += self.friction * delta
                if self.velocity.y >= 0:
                    self.velocity.y = 0
            else:
                self.velocity.y -= self.friction * delta
                if self.velocity.y <= 0:
                    self.velocity.y = 0
                
class Paralyze(Humanoid):

    STABLE = 1
    UNSTABLE = 2

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.state = Paralyze.STABLE
        self.seen = False
        self.killed = False

        self.before_kill_timer = None
        self.kill_timer = None
        self.kill_timer_completed_safe = None
        self.dissapear_timer = None
        self.kill_position = None