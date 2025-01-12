import os
import pygame

pygame.mixer.init()

def load_sounds():
    sounds = {
        'start': pygame.mixer.Sound(os.path.abspath('sounds/gamestart-272829.mp3')),
        'game_loop': pygame.mixer.Sound(os.path.abspath('sounds/8-bit-game-music-122259.mp3')),
        'collision': pygame.mixer.Sound(os.path.abspath('sounds/retro-explode-1-236678.mp3')),
        'special_item': pygame.mixer.Sound(os.path.abspath('sounds/8-bit-game-6-188105.mp3')),
        'game_over': pygame.mixer.Sound(os.path.abspath('sounds/videogame-death-sound-43894.mp3')),
        'new_record': pygame.mixer.Sound(os.path.abspath('sounds/win-sfx-38507.mp3'))
    }
    return sounds

def play_sound(sound_name, sounds, loop=False):
    sound = sounds.get(sound_name)
    if sound:
        if loop:
            sound.play(loops=-1, maxtime=0)
        else:
            sound.play()

def stop_sound(sound_name, sounds):
    sound = sounds.get(sound_name)
    if sound:
        sound.stop()
