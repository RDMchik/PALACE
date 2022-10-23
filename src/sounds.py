import pygame as pg


class Sounds:

    def __init__(self) -> None:

        self.channel = pg.mixer.Channel(5)
        self.cecil_footsteps_channel = pg.mixer.Channel(6)
        self.rain_channel = pg.mixer.Channel(7)

        self.loaded_sounds = {
            'blip': pg.mixer.Sound('static/sounds/blip.wav'),
            'evil_blip': pg.mixer.Sound('static/sounds/evil_blip.wav'),
            'scan': pg.mixer.Sound('static/sounds/scan.wav'),
            'rain': pg.mixer.Sound('static/sounds/rain.wav'),
            'thunder': pg.mixer.Sound('static/sounds/thunder.wav'),
            'paralyze_jumpscare': pg.mixer.Sound('static/sounds/paralyze_jumpscare.wav'),
            'cicil_footsteps': pg.mixer.Sound('static/sounds/light_footsteps.wav')
        }

        self.loaded_sounds['blip'].set_volume(0.05)
        self.loaded_sounds['evil_blip'].set_volume(0.05)
        self.loaded_sounds['scan'].set_volume(0.05)
        self.loaded_sounds['rain'].set_volume(0.5)
        self.loaded_sounds['paralyze_jumpscare'].set_volume(2)
        self.loaded_sounds['thunder'].set_volume(20)
        self.loaded_sounds['cicil_footsteps'].set_volume(1.5)

    def play(self, name: str) -> None:
        self.loaded_sounds[name].play()

    def pause(self, name: str) -> None:
        self.loaded_sounds[name].pause()
    
    def stop(self, name: str) -> None:
        self.loaded_sounds[name].stop()

    def play_cecil_footsteps(self) -> None:
        self.cecil_footsteps_channel.play(self.loaded_sounds['cicil_footsteps'])

    def pause_cecil_footsteps(self) -> None:
        self.cecil_footsteps_channel.pause()
    
    def unpause_cecil_footsteps(self) -> None:
        self.cecil_footsteps_channel.unpause()

    def play_rain(self) -> None:
        self.rain_channel.play(self.loaded_sounds['rain'])

    def playing_rain(self) -> None:
        return self.rain_channel.get_busy()
    
    def stop_rain(self) -> None:
        self.rain_channel.stop()

    def playing_cecil_footsteps(self) -> bool:
        return self.cecil_footsteps_channel.get_busy()