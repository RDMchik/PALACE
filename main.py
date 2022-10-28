from logging import exception
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
pg.mouse.set_visible(False)
pg.display.set_caption('PA?ACE')
pg.display.set_icon(pg.image.load('static/icon1.jpg'))

sc = pg.display.set_mode(flags=pg.FULLSCREEN)
sc_width, sc_height = sc.get_size()
clock = pg.time.Clock()
camera = Camera(0, 0)
drawing = Drawing(sc, camera)
manager = Manager()
sounds = Sounds()

player = Player(drawing.sprites['cecil_base'].get_width(), sc_height - sc_height / HALLWAY_HEIGHT_RATIO - drawing.sprites['cecil_base'].get_height())

lights_out = True
rain = True
thunder = True
room = False

set_time_thunder = random.randint(THUNDER_COOLDOWN[0], THUNDER_COOLDOWN[1])
next_thunder = Timer(set_time_thunder)
next_thunder_blink = Timer(set_time_thunder - 2)
thunder_blink_duration =  None

game_state = RUNNING
delta = 0

exit_key_found = False
shoot_timer = None
outro_timer = None
shoot_black_timer = None
cecil_dead_laying_timer = None

manager.generate_rooms(player.position, drawing.part_width)

drawing.say('Why am i in my hallway? I feel like i need to find exit key and get out', CECIL_LETTER_ADD_SPEECH, WHITE)

rain_visible = False
rain_distance = 0

dead = False
outro = False

paralyze = None
fisherman = None
mimic = None
marathoner = None

first_time_see_door = True

credits_text_iter = iter(CREDITS_TEXT)

camera.original_offset.x = -sc_width // 2 + sc_width / 15 // 2 + drawing.sprites['cecil_base'].get_width()
camera.offset.x = camera.original_offset.x

def spawn_paralyze() -> None:

    global paralyze

    if player.velocity.x < 0:
        x = player.position.x + drawing.sprites['cecil_base'].get_width() / 2 - drawing.part_width * 4
    else:
        x = player.position.x + drawing.sprites['cecil_base'].get_width() / 2 + drawing.part_width * 4

    y = drawing.height / HALLWAY_HEIGHT_RATIO + (drawing.height - drawing.height / HALLWAY_HEIGHT_RATIO * 2) - drawing.sprites['paralyze1'].get_height()

    paralyze = Paralyze(x, y)

def spawn_fisherman() -> None:

    global fisherman

    if player.velocity.x < 0:
        x = (player.position.x + drawing.sprites['cecil_base'].get_width() / 2 - drawing.part_width * 4) // drawing.part_width * drawing.part_width
    else:
        x = (player.position.x + drawing.sprites['cecil_base'].get_width() / 2 + drawing.part_width * 4) // drawing.part_width * drawing.part_width
    
    y = drawing.height / HALLWAY_HEIGHT_RATIO

    for part in manager.parts:
        if part.x == x:
            part.blood = False
            part.type = WALL_CLOSET_F

    fisherman = Fisherman(x, y)

def spawn_mimic() -> None:

    global mimic

    if player.velocity.x < 0:
        x = player.position.x + drawing.sprites['cecil_base'].get_width() / 2 - drawing.part_width * 4
    else:
        x = player.position.x + drawing.sprites['cecil_base'].get_width() / 2 + drawing.part_width * 4

    y = drawing.height - drawing.height / HALLWAY_HEIGHT_RATIO - drawing.sprites['mimic'].get_height()

    mimic = Mimic(x, y)

def spawn_marathoner() -> None:

    global marathoner

    x = player.position.x - drawing.part_width * 999
    y = drawing.height / HALLWAY_HEIGHT_RATIO

    marathoner = Marathoner(x, y)

    sounds.play('marathoner_run1')
    sounds.play('marathoner_run2')

def reset_monsters() -> None:

    global paralyze
    global fisherman
    global mimic
    global marathoner

    sounds.stop('mimic_run1')
    sounds.stop('mimic_run2')

    sounds.stop('marathoner_run1')
    sounds.stop('marathoner_run2')

    marathoner = None
    paralyze = None
    fisherman = None
    mimic = None

def reset_all(room: bool = False, keep_down: bool = False) -> None:

    reset_monsters()

    player.position.x = drawing.sprites['cecil_base'].get_width()
    camera.original_offset.x = -sc_width // 2 + sc_width / 15 // 2 + drawing.sprites['cecil_base'].get_width()
    camera.offset.x = camera.original_offset.x
    manager.parts.clear()
    if not keep_down:
        manager.generate_rooms(player.position, drawing.part_width, room)

def credits_start() -> None:

    global game_state 

    reset_monsters()

    game_state = CREDITS
    sounds.stop('paralyze_jumpscare')
    sounds.pause_cecil_footsteps()
    drawing.background_color = BLACK
    reset_all(False, True)
    drawing.say(next(credits_text_iter), CREDITS_LETTER_ADD_SPEED, WHITE, is_credits=True)
    sounds.play('ending')

pre_x = 0

running = True
while running:

    space_pressed = False

    for ev in pg.event.get():

        if ev.type == pg.QUIT:
            pg.quit()
            quit()

        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_SPACE:
                space_pressed = True
    
    if game_state == RUNNING:

        keys = pg.key.get_pressed()

        if not dead and not outro:
            player.walk(keys, delta)
            if not dead:
                player.update_position(camera, delta, room, sc_width, drawing.sprites['cecil_base'].get_width())
                camera.update_offset(delta, sc_width, room)
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

        if dead:
            sounds.pause_cecil_footsteps()

        if rain == True and rain_visible == True:
            sounds.loaded_sounds['rain'].set_volume((sc_width - rain_distance) / sc_width * 0.5)
            if not sounds.playing_rain():
                sounds.play_rain()
        else:
            if sounds.playing_rain():
                sounds.stop_rain()

        if player.sprinting:
            drawing.cecil_left_animation.speed = CECIL_ANIMATION_SPEED / 1.5
            drawing.cecil_right_animation.speed = CECIL_ANIMATION_SPEED / 1.5
        else:
            drawing.cecil_left_animation.speed = CECIL_ANIMATION_SPEED 
            drawing.cecil_right_animation.speed = CECIL_ANIMATION_SPEED 

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
            elif keys[pg.K_DOWN]:
                x1 = player.position.x // drawing.part_width * drawing.part_width - drawing.part_width
                x2 = player.position.x // drawing.part_width * drawing.part_width
                x3 = player.position.x // drawing.part_width * drawing.part_width + drawing.part_width
                manager.change_trasnsparency(x1, -SCAN_SPEED / 2 * delta, sounds)
                manager.change_trasnsparency(x2, -SCAN_SPEED * delta, sounds)
                manager.change_trasnsparency(x3, -SCAN_SPEED / 2 * delta, sounds)
            elif keys[pg.K_RIGHT]:
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

        rain_visible, rain_distance, part = drawing.draw_parts(manager.parts, player.position)

        if part.type == WALL_ROOM_DOOR or part.type == WALL_DOOR:
            if first_time_see_door:
                first_time_see_door = False
                drawing.say('*Here is a door! You should go in and check drawers and closets for a key*', NARRATOR_LETTER_ADD_SPEED, GRAY)
            if space_pressed:
                if room == False and part.used == False:
                    room = True
                    part.used = True
                    reset_all(True)
                else:
                    room = False
                    reset_all()
                sounds.play('door')
        
        if space_pressed:
            if part.type == WALL_ROOM_BOOK or part.type == WALL_ROOM_CLOSET:
                if part.open == False:
                    part.open = True
                    if part.type == WALL_ROOM_BOOK:
                        sounds.play('book')
                    elif part.type == WALL_ROOM_CLOSET:
                        sounds.play('closet')
                    if random.randint(1, FIND_OBJECT_CHANCE) == 1:
                        object_type = random.randint(1, 100)
                        if exit_key_found == False:
                            if object_type >= 1 and object_type <= 100:
                                drawing.say('*Exit key found! Now find the exit door and escape!*', NARRATOR_LETTER_ADD_SPEED, GOLD) 
                                exit_key_found = True
                        if object_type >= 1 and object_type <= 20:
                            time = random.randint(10, 20)
                            player.add_boost(Player.STAMINA_BOOST, time)
                            if player.boosts.get(Player.STAMINA_DEBUFF):
                                del player.boosts[Player.STAMINA_DEBUFF]
                            drawing.say('*Found stamina boost for %d seconds*' % time, NARRATOR_LETTER_ADD_SPEED, GRAY)
                        elif object_type >= 21 and object_type <= 30:
                            time = random.randint(10, 20)
                            player.add_boost(Player.CRAWLING_BOOST, time)
                            if player.boosts.get(Player.CRAWLING_DEBUFF):
                                del player.boosts[Player.CRAWLING_DEBUFF]
                            drawing.say('*Found crawling boost for %d seconds*' % time, NARRATOR_LETTER_ADD_SPEED, GRAY) 
                        elif object_type >= 31 and object_type <= 40:
                            time = random.randint(10, 20)
                            player.add_boost(Player.ACCELERATION_BOOST, time)
                            if player.boosts.get(Player.ACCELERATION_DEBUFF):
                                del player.boosts[Player.ACCELERATION_DEBUFF]
                            drawing.say('*Found acceleration boost for %d seconds*' % time, NARRATOR_LETTER_ADD_SPEED, GRAY)
                        elif object_type >= 41 and object_type <= 50:
                            time = random.randint(10, 20)
                            player.add_boost(Player.VISION_BOOST, time)
                            if player.boosts.get(Player.VISION_DEBUFF):
                                del player.boosts[Player.VISION_DEBUFF]
                            drawing.say('*Found vision boost for %d seconds*' % time, NARRATOR_LETTER_ADD_SPEED, GRAY)
                        elif object_type >= 51 and object_type <= 60:
                            time = random.randint(10, 20)
                            player.add_boost(Player.STAMINA_DEBUFF, time)
                            if player.boosts.get(Player.STAMINA_BOOST):
                                del player.boosts[Player.STAMINA_BOOST]
                            drawing.say('*Found stamina debuff for %d seconds*' % time, NARRATOR_LETTER_ADD_SPEED, GRAY_RED, True)
                        elif object_type >= 61 and object_type <= 70:
                            time = random.randint(10, 20)
                            player.add_boost(Player.CRAWLING_DEBUFF, time)
                            if player.boosts.get(Player.STAMINA_BOOST):
                                del player.boosts[Player.STAMINA_BOOST]
                            drawing.say('*Found crawling debuff for %d seconds*' % time, NARRATOR_LETTER_ADD_SPEED, GRAY_RED, True)
                        elif object_type >= 71 and object_type <= 80:
                            time = random.randint(10, 20)
                            player.add_boost(Player.ACCELERATION_DEBUFF, time)
                            if player.boosts.get(Player.ACCELERATION_BOOST):
                                del player.boosts[Player.ACCELERATION_BOOST]
                            drawing.say('*Found acceleration debuff for %d seconds*' % time, NARRATOR_LETTER_ADD_SPEED, GRAY_RED, True)
                        elif object_type >= 81 and object_type <= 90:
                            time = random.randint(10, 20)
                            player.add_boost(Player.VISION_DEBUFF, time)
                            if player.boosts.get(Player.VISION_BOOST):
                                del player.boosts[Player.VISION_BOOST]
                            drawing.say('*Found vision debuff for %d seconds*' % time, NARRATOR_LETTER_ADD_SPEED, GRAY_RED, True)
                    else:
                        drawing.say('*It\'s empty*', NARRATOR_LETTER_ADD_SPEED, GRAY)

        if space_pressed:
            if part.type == WALL_EXIT:
                if not part.open:
                    if exit_key_found:
                        part.open = True
                        outro = True
                        reset_monsters()
                        sounds.play('outro')
                        drawing.say('*Good Ending (Reunion with Father)*', NARRATOR_LETTER_ADD_SPEED, GOLD)
                        player.position.x = part.x
                    else:
                        drawing.say('*You don\'t have a key for an exit*', NARRATOR_LETTER_ADD_SPEED, GRAY)
                    
        if room == False:
            created = manager.update_needed(player, drawing.part_width * 5)

        if player.position.x // drawing.part_width * drawing.part_width != pre_x and room == False:
            monster_type = random.randint(1, 4)
            if monster_type == 1:
                if random.randint(1, PARALYZE_SPAWN_CHANCE) == 1:
                    if not paralyze and not mimic and not marathoner:
                        spawn_paralyze()
            elif monster_type == 2:
                if random.randint(1, FISHERMAN_SPAWN_CHANCE) == 1:
                    if not fisherman and not mimic and not marathoner:
                        spawn_fisherman()
            elif monster_type == 3:
                if random.randint(1, MIMIC_SPAWN_CHANCE) == 1:
                    if not mimic and not marathoner:
                        spawn_mimic()
            elif monster_type == 4:
                if random.randint(1, MARATHONER_SPAWN_CHANCE) == 1:
                    if not mimic and not marathoner:
                        spawn_marathoner()

        drawing.draw_cecil(player, dead, outro)

        if mimic:
            drawing.draw_mimic(mimic, player)
            if mimic.delete_time.done:
                sounds.stop('mimic_run1')
                sounds.stop('mimic_run2')
                mimic = None

            if dead == False:
                mimic.update_position(delta)
                if mimic.seen == False:
                    if drawing.check_visibility(mimic.position.x, manager) or drawing.check_visibility(mimic.position.x + drawing.sprites['cecil_base'].get_width(), manager):
                        mimic.seen = True
                        mimic.before_trigger_timer = Timer(MIMIC_BEFORE_TRIGGER_TIMER)
                else:
                    if mimic.before_trigger_timer:
                        if mimic.before_trigger_timer.done:
                            mimic.before_trigger_timer = None
                            mimic.trigered = True
                    else: 
                        if not mimic.chase_timer:
                            sounds.play('mimic_run1')
                            sounds.play('mimic_run2')
                            drawing.say(MIMIC_SPEECH, MIMIC_LETTER_ADD_SPEED, RED, True)
                            mimic.chase_timer = Timer(MIMIC_CHASE_LENGTH)
                        else:
                            mimic.move(True if player.position.x > mimic.position.x else False, delta)
                            if mimic.chase_timer.done:
                                if not mimic.dissapear_timer:
                                    mimic.dissapear_timer = Timer(MIMIC_FADING_TIME)
                                    mimic.trigered = False
                                else:
                                    sounds.stop('mimic_run1')
                                    sounds.stop('mimic_run2')
                                    sc.fill(BLACK)
                                    if mimic.dissapear_timer.done:
                                        mimic = None
                if mimic:
                    if mimic.trigered:
                        if player.position.x + drawing.sprites['cecil_base'].get_width() / 2 > mimic.position.x + drawing.sprites['mimic'].get_width() / 2:
                            distance = player.position.x + drawing.sprites['cecil_base'].get_width() / 2 - mimic.position.x + drawing.sprites['mimic'].get_width() / 2
                        else:
                            distance = mimic.position.x + drawing.sprites['mimic'].get_width() / 2 - player.position.x + drawing.sprites['cecil_base'].get_width() / 2 

                        if distance < drawing.sprites['mimic'].get_width() / 2:
                            mimic.jumpscare_timer = Timer(MIMIC_JUMPSCARE_LENGTH)
                            drawing.background_color = DARK_RED
                            dead = True
                            sounds.stop('mimic_run1')
                            sounds.stop('mimic_run2')
                            sounds.play('mimic_jumpscare')
            
            if mimic:
                if mimic.jumpscare_timer:
                    if mimic.jumpscare_timer.done:
                        sounds.stop('mimic_jumpscare')
                        credits_start()
                    else:
                        mimic.velocity.x = 0
        
        if marathoner:
            if marathoner.delete_time.done:
                marathoner = None
            if marathoner.before_move_timer.done:
                drawing.draw_marathoner(marathoner, dead)
                if marathoner.trigered == False:
                    marathoner.trigered = True
                    marathoner.position.x = player.position.x - drawing.part_width * 20
                if not dead:
                    marathoner.move(delta)
                    marathoner.update_position(delta)
                    if player.position.x + drawing.sprites['cecil_base'].get_width() / 2 > marathoner.position.x + drawing.sprites['marathoner1'].get_width() / 2:
                        distance = player.position.x + drawing.sprites['cecil_base'].get_width() / 2 - marathoner.position.x + drawing.sprites['marathoner1'].get_width() / 2
                    else:
                        distance = marathoner.position.x + drawing.sprites['marathoner1'].get_width() / 2 - player.position.x + drawing.sprites['cecil_base'].get_width() / 2 

                    if distance < drawing.sprites['marathoner1'].get_width() / 2:
                        dead = True
                        marathoner.jumpscare_timer = Timer(MIMIC_JUMPSCARE_LENGTH)
                        drawing.background_color = DARK_RED
                        sounds.stop('marathoner_run1')
                        sounds.stop('marathoner_run2')
                        sounds.play('marathoner_jumpscare')
                else:
                    if marathoner.jumpscare_timer.done:
                        sounds.stop('marathoner_jumpscare')
                        credits_start()

        if paralyze:
            if paralyze.delete_time.done:
                paralyze = None
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
                        credits_start()

        if fisherman:
            if fisherman.delete_time.done:
                fisherman = None
            drawing.draw_fisherman(fisherman)

            if fisherman.killed == False:

                if fisherman.seen == False:
                    if drawing.check_visibility(fisherman.position.x + drawing.part_width / 2, manager):
                        fisherman.seen = True
                        drawing.say(FISHERMAN_SPEECH, FISHERMAN_LETTER_ADD_SPEED, RED, True)
                
                if (player.position.x + drawing.sprites['cecil_base'].get_width() / 2) // drawing.part_width * drawing.part_width == fisherman.position.x:
                    if player.boosts.get(Player.CRAWLING_DEBUFF) == None:
                        if player.crawling == False and player.boosts.get(Player.CRAWLING_BOOST) == None:
                            fisherman.killed = True
                            fisherman.jumpscare_timer = Timer(FISHERMAN_JUMPSCARE_LENGTH)
                            sounds.play('fisherman_jumpscare')
                            dead = True
                    else:
                        fisherman.killed = True
                        fisherman.jumpscare_timer = Timer(FISHERMAN_JUMPSCARE_LENGTH)
                        sounds.play('fisherman_jumpscare')
                        dead = True

                if fisherman.start_dissaper_timer.done:
                    sc.fill(drawing.background_color)
                    if fisherman.dissapear_timer.done:
                        fisherman = None
            else:
                drawing.background_color = DARK_RED
                if fisherman.jumpscare_timer.done:
                    sounds.stop('fisherman_jumpscare')
                    credits_start()

        if thunder_blink_duration:
            drawing.draw_parts_transparency(manager.parts, True, dead)
            if thunder_blink_duration.done:
                thunder_blink_duration = None
        else:
            drawing.draw_parts_transparency(manager.parts, False, dead, player.boosts.get(player.VISION_BOOST), player.boosts.get(player.VISION_DEBUFF))

        if outro:
            drawing.draw_say_update(sounds)
            player.velocity.x = 0
            if not shoot_timer:
                shoot_timer = Timer(4)
            else:
                if shoot_timer.done:
                    if not shoot_black_timer:
                        sounds.play('gun')
                        player.cecil_state = Player.DEAD_STANDING
                        cecil_dead_laying_timer = Timer(3)
                        shoot_black_timer = Timer(1)
                    else:
                        if cecil_dead_laying_timer.done:
                            player.cecil_state = Player.DEAD_LAYING
                        else:
                            player.cecil_state = Player.DEAD_STANDING
                        if shoot_black_timer.done:
                            if not outro_timer:
                                sounds.stop('gun')
                                outro_timer = Timer(4)
                            else:
                                if outro_timer.done:
                                    credits_start()
                        else:
                            sc.fill(BLACK)

        drawing.draw_bars()
        # drawing.draw_stamina_bar(player)
        drawing.draw_say_update(sounds)
    
    elif game_state == CREDITS:
        sc.fill(drawing.background_color)
        if not sounds.playing_rain():
            sounds.play_rain()
        if drawing.to_say == None:
            try:
                drawing.say(next(credits_text_iter), CREDITS_LETTER_ADD_SPEED, WHITE, is_credits=True)
            except StopIteration:
                quit()
        drawing.draw_say_update(sounds, True)
    
    pre_x = player.position.x // drawing.part_width * drawing.part_width
    pg.display.flip()
    delta = clock.tick(FPS)

pg.quit()