from random import random
from settings import *
from src.drawing import Drawing
from src.camera import Camera
from src.manager import Manager
from src.humanoids import *
from src.sounds import Sounds
from src.timer import Timer

import pygame as pg
import random


pg.init()
pg.mixer.init()
pg.mixer.set_num_channels(8)

sc = pg.display.set_mode(flags=pg.FULLSCREEN)
sc_width, sc_height = sc.get_size()
clock = pg.time.Clock()
camera = Camera(-sc_width // 2 + sc_width / 15 // 2, 0)
drawing = Drawing(sc, camera)
manager = Manager()
sounds = Sounds()

player = Player(0, sc_height - sc_height / HALLWAY_HEIGHT_RATIO - drawing.sprites['cecil_base'].get_height())

lights_out = True
rain = True
thunder = True

set_time_thunder = random.randint(THUNDER_COOLDOWN[0], THUNDER_COOLDOWN[1])
next_thunder = Timer(set_time_thunder)
next_thunder_blink = Timer(set_time_thunder - 2)
thunder_blink_duration =  None

game_state = TUTORIAL_BEGINING
delta = 0

manager.generate_rooms(player.position, drawing.part_width)

drawing.say(' [CECIL] Why am i in my hallway? I feel like i should get outside of the house', CECIL_LETTER_ADD_SPEECH, WHITE)

rain_visible = False
rain_distance = 0

dead = False
paralyze = None

def spawn_paralyze() -> None:

    global paralyze

    side = random.randint(1, 2)

    if side == 1:
        x = player.position.x + drawing.sprites['cecil_base'].get_width() / 2 - random.randint(drawing.part_width, drawing.part_width * 2)
    else:
        x = player.position.x + drawing.sprites['cecil_base'].get_width() / 2 + random.randint(drawing.part_width, drawing.part_width * 2)

    y = drawing.height / HALLWAY_HEIGHT_RATIO + (drawing.height - drawing.height / HALLWAY_HEIGHT_RATIO * 2) - drawing.sprites['paralyze1'].get_height()

    paralyze = Paralyze(x, y)


spawn_paralyze()

running = True
while running:

    for ev in pg.event.get():

        if ev.type == pg.QUIT:
            pg.quit()
            quit()
    
    keys = pg.key.get_pressed()

    player.walk(keys, delta)
    if not dead:
        player.update_position(camera, delta)
        camera.update_offset(delta, sc_width)
    manager.update_used_parts(delta)

    if player.crawling == False:
        if player.velocity.x != 0:
            sounds.unpause_cecil_footsteps()
            if not sounds.playing_cecil_footsteps():
                sounds.play_cecil_footsteps()
        else:
            sounds.pause_cecil_footsteps()
    else:
        sounds.pause_cecil_footsteps()

    if rain == True and rain_visible == True:
        sounds.loaded_sounds['rain'].set_volume((sc_width - rain_distance) / sc_width * 0.5)
        if not sounds.playing_rain():
            sounds.play_rain()
    else:
        if sounds.playing_rain():
            sounds.stop_rain()

    if thunder:
        if next_thunder_blink:
            if next_thunder_blink.done:
                next_thunder_blink = None
                thunder_blink_duration = Timer(THUNDER_BLINK_LENGTH)

        if next_thunder.done:
            set_time_thunder = random.randint(THUNDER_COOLDOWN[0], THUNDER_COOLDOWN[1])
            next_thunder = Timer(set_time_thunder)
            next_thunder_blink = Timer(set_time_thunder - 2)
            sounds.play('thunder')

    if lights_out == True:

        if keys[pg.K_LEFT]:
            x1 = player.position.x // drawing.part_width * drawing.part_width - drawing.part_width
            x2 = player.position.x // drawing.part_width * drawing.part_width
            x3 = player.position.x // drawing.part_width * drawing.part_width + drawing.part_width
            manager.change_trasnsparency(x1, -SCAN_SPEED * delta, sounds)
            manager.change_trasnsparency(x2, -SCAN_SPEED / 2 * delta, sounds)
        if keys[pg.K_DOWN]:
            x1 = player.position.x // drawing.part_width * drawing.part_width - drawing.part_width
            x2 = player.position.x // drawing.part_width * drawing.part_width
            x3 = player.position.x // drawing.part_width * drawing.part_width + drawing.part_width
            manager.change_trasnsparency(x1, -SCAN_SPEED / 2 * delta, sounds)
            manager.change_trasnsparency(x2, -SCAN_SPEED * delta, sounds)
            manager.change_trasnsparency(x3, -SCAN_SPEED / 2 * delta, sounds)
        if keys[pg.K_RIGHT]:
            x1 = player.position.x // drawing.part_width * drawing.part_width - drawing.part_width
            x2 = player.position.x // drawing.part_width * drawing.part_width
            x3 = player.position.x // drawing.part_width * drawing.part_width + drawing.part_width
            manager.change_trasnsparency(x2, -SCAN_SPEED / 2 * delta, sounds)
            manager.change_trasnsparency(x3, -SCAN_SPEED * delta, sounds)

    if player.next_speech.done:
        if drawing.to_say == None:
            drawing.say(random.choice(Player.speeches), CECIL_LETTER_ADD_SPEECH, WHITE)
            player.next_speech = Timer(random.randint(CECIL_SPEECH_DELAY[0], CECIL_SPEECH_DELAY[1]))

    if drawing.fill_each_frame:
        sc.fill(BLACK)

    rain_visible, rain_distance = drawing.draw_parts(manager.parts, player.position)
    
    drawing.draw_cecil(player, dead)
    
    if paralyze:
        drawing.draw_paralyze(paralyze)
        if paralyze.seen == False:
            if drawing.check_visibility(paralyze.position.x, manager) or drawing.check_visibility(paralyze.position.x + drawing.sprites['paralyze1'].get_width(), manager):
                paralyze.seen = True
                paralyze.before_kill_timer = Timer(PARALYZE_BEFORE_KILL_WAIT)
                drawing.say(PARALYZE_SPEECH, PARALYZE_LETTER_ADD_SPEED, RED, True)
        
        if paralyze.seen == True:

            if not paralyze.kill_timer:

                if paralyze.before_kill_timer.done:
                    paralyze.kill_timer = Timer(PARALYZE_KILL_WAIT)
            
            else:

                if paralyze.kill_timer.done and not paralyze.dissapear_timer:
                    paralyze.dissapear_timer = Timer(PARALYZE_DISSAPEAR_TIME)
                else:
                    if player.velocity.x != 0:
                        paralyze.kill_position = player.position
                        paralyze.killed = True
                        sounds.play('paralyze_jumpscare')
                        dead = True
                        drawing.background_color = DARK_RED
        
        if paralyze.dissapear_timer:

            if paralyze.killed == False:
                if paralyze.dissapear_timer.done:
                    paralyze = None
                sc.fill(BLACK)
            else:
                if paralyze.dissapear_timer.done:
                    quit()

    if thunder_blink_duration:
        drawing.draw_parts_transparency(manager.parts, True, dead)
        if thunder_blink_duration.done:
            thunder_blink_duration = None
    else:
        drawing.draw_parts_transparency(manager.parts, False, dead)

    drawing.draw_bars()
    drawing.draw_say_update(sounds)

    pg.display.flip()
    delta = clock.tick(FPS)

pg.quit()