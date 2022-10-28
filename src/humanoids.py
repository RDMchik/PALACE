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

        self.delete_time = Timer(30)
    
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
        'Why do i feel so wrong...',
        'I hate my brother...',
        'How is my dad is so smart...',
        'I saw my mom die in a nightmare today...',
        'Did i nightwalk again...?',
        'I really should get out of my house fast...',
        'Am i a psychopath? My dad said it can\'t be...',
        'Dad hates mom...',
        'I wish i was as kind as my mom...',
        'I wonder how is my dad so rich...',
        'I love my doggy so much, i hope he is alright...',
        'How am i going to go to school tomorrow...'
    ]

    ACCELERATION_BOOST = 'acceleration'
    CRAWLING_BOOST = 'crawling'
    STAMINA_BOOST = 'stamina'
    VISION_BOOST = 'vision'

    ACCELERATION_DEBUFF = 'acceleration_d'
    CRAWLING_DEBUFF = 'crawling_d'
    STAMINA_DEBUFF = 'stamina_d'
    VISION_DEBUFF = 'vision_d'

    STANDING = 1
    DEAD_STANDING = 2
    DEAD_LAYING = 3

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.acceleration = CECIL_ACCELERATION
        self.friction = CECIL_FRICTION
        self.crawling = False
        self.sprinting = False
        self.stamina = CECIL_STAMINA_MAX
        self.tired = False

        self.cecil_state = Player.STANDING

        self.boosts = {}

        self.next_speech = Timer(random.randint(CECIL_SPEECH_DELAY[0], CECIL_SPEECH_DELAY[1]))
    
    def add_boost(self, of_type, length) -> None:

        self.boosts[of_type] = Timer(length)

    @property
    def terminal_velocity(self) -> float:
        if self.boosts.get(Player.ACCELERATION_BOOST) == None:
            if self.boosts.get(Player.ACCELERATION_DEBUFF):
                if not self.sprinting:
                    if self.crawling:
                        return CECIL_TERMINAL_VELOCITY / 10
                    else:
                        return CECIL_TERMINAL_VELOCITY * 0.5
                else:
                    return CECIL_TERMINAL_VELOCITY
            if not self.sprinting:
                if self.crawling:
                    return CECIL_TERMINAL_VELOCITY / 5
                else:
                    return CECIL_TERMINAL_VELOCITY
            else:
                return CECIL_TERMINAL_VELOCITY * 1.5
        else:
            if not self.sprinting:
                if self.crawling:
                    return CECIL_TERMINAL_VELOCITY / 1.5
                else:
                    return CECIL_TERMINAL_VELOCITY * 1.5
            else:
                return CECIL_TERMINAL_VELOCITY * 3
    
    @property
    def sprint_boost(self) -> int:
        if self.sprinting:
            return 2
        else:
            return 1

    def walk(self, keys, delta) -> None:

        acceleration = self.acceleration
        if self.boosts.get(Player.ACCELERATION_BOOST):
            acceleration *= 2
        elif self.boosts.get(Player.ACCELERATION_DEBUFF):
            acceleration *= 0.5

        if keys[pg.K_a]:
            
            self.velocity.x -= acceleration * delta * self.sprint_boost
            if self.velocity.x <= -self.terminal_velocity:
                self.velocity.x = -self.terminal_velocity

        if keys[pg.K_d]:
            
            self.velocity.x += acceleration * delta * self.sprint_boost
            if self.velocity.x >= self.terminal_velocity:
                self.velocity.x = self.terminal_velocity

        if not self.sprinting:
            if keys[pg.K_s]:
                self.crawling = True
            else:
                self.crawling = False
        
        if self.boosts.get(Player.STAMINA_BOOST):
            self.tired = False
            self.stamina = CECIL_STAMINA_MAX
        elif self.boosts.get(Player.STAMINA_DEBUFF):
            self.tired = True
            self.stamina = 0

        if keys[pg.K_LSHIFT]:
            if not self.tired:
                if self.stamina > 0:
                    if not self.crawling:
                        self.sprinting = True
                        self.stamina -= CECIL_STAMINA_DRAIN * delta
                        if self.stamina < 0:
                            self.sprinting = False
                            self.tired = True
                            self.stamina = 0
        else:
            self.sprinting = False
    
    def update_position(self, camera, delta, room, sc_width, cecil_width) -> None:

        to_remove = []
        for boost_type, boost_timer in self.boosts.items():
            if boost_timer.done:
                to_remove.append(boost_type) 
        for boost_type in to_remove:
            del self.boosts[boost_type]

        if room == False:
            self.position.x += self.velocity.x * delta
            self.position.y += self.velocity.y * delta
        else:
            if self.position.x + self.velocity.x * delta - camera.offset.x > 0 and self.position.x + self.velocity.x * delta - camera.offset.x < sc_width - cecil_width:
                self.position.x += self.velocity.x * delta
                

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

        self.stamina += CECIL_STAMINA_DRAIN / 5 * delta
        if self.stamina > CECIL_STAMINA_MAX:
            self.stamina = CECIL_STAMINA_MAX
            self.tired = False

                
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

class Fisherman(Humanoid):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.seen = False
        self.killed = False

        self.start_dissaper_timer = Timer(FISHERMAN_DISSAPEAR_TIME - FISHERMAN_FADING_TIME)
        self.dissapear_timer = Timer(FISHERMAN_DISSAPEAR_TIME)
        self.jumpscare_timer = None

class Mimic(Humanoid):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.seen = False
        self.killed = False
        self.trigered = False
        self.side = None

        self.chase_timer = None
        self.before_trigger_timer = None
        self.jumpscare_timer = None
        self.dissapear_timer = None

    def move(self, side, delta) -> None:

        if side == True:
            self.velocity.x += MIMIC_ACCELERATION * delta
            if self.velocity.x > self.terminal_velocity:
                self.velocity.x = self.terminal_velocity
        elif side == False:
            self.velocity.x -= MIMIC_ACCELERATION * delta
            if self.velocity.x < -self.terminal_velocity:
                self.velocity.x = -self.terminal_velocity

    def update_position(self, delta) -> None:

        if self.trigered:
            self.position.x += self.velocity.x * delta

    @property
    def terminal_velocity(self) -> float:
        return CECIL_TERMINAL_VELOCITY * 1.6

class Marathoner(Humanoid):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.seen = False
        self.killed = False

        # self.start_dissaper_timer = Timer(FISHERMAN_DISSAPEAR_TIME - FISHERMAN_FADING_TIME)
        # self.dissapear_timer = Timer(FISHERMAN_DISSAPEAR_TIME)
        self.jumpscare_timer = None
        self.trigered = False
        self.before_move_timer = Timer(MARATHONER_BEFORE_MOVE_TIME)
    
    @property
    def terminal_velocity(self) -> float:
        return CECIL_TERMINAL_VELOCITY * 15

    def move(self, delta) -> None:

        self.velocity.x += MARATHONER_ACCELERATION * delta
        if self.velocity.x > self.terminal_velocity:
            self.velocity.x = self.terminal_velocity

    def update_position(self, delta) -> None:

        self.position.x += self.velocity.x * delta