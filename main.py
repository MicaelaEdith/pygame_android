import pygame, time
import csv
from settings import *
from game_logic import Game
from sound import load_sounds, play_sound, stop_sound

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    SCREEN_SIZE = screen.get_size()
    clock = pygame.time.Clock() 
    sound_on = True
    game = Game(screen, SCREEN_SIZE, sound_on)

    best_score = load_best_score()
    new_record = False

    running = True
    start_screen = True

    sounds = load_sounds()
    if sound_on:
        play_sound('start', sounds)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if start_screen and event.type == pygame.MOUSEBUTTONDOWN:
                if not check_sound_button(event, screen):
                    game.reset()
                    start_screen = False
                    new_record = False
            if event.type == pygame.MOUSEBUTTONDOWN and check_sound_button(event, screen):
                sound_on = not sound_on
                if sound_on:
                    play_sound('start', sounds)
                else:
                    stop_sound('start', sounds)

        if start_screen:
            screen.fill(BACKGROUND_COLOR)
            display_start_screen(screen, best_score, new_record, sound_on)
            pygame.display.flip()
        else:
            screen.fill(BACKGROUND_COLOR)
            game.update(sound_on)
            pygame.display.flip()
            clock.tick(FPS)

            if not pygame.mixer.music.get_busy() and sound_on:
                stop_sound('start', sounds)
                pygame.mixer.music.load('sounds/8-bit-game-music-122259.mp3')
                pygame.mixer.music.play(loops=-1)

            if game.game_over:
                pygame.mixer.music.stop()

                if game.score > best_score:
                    new_record = True
                if sound_on:
                    if new_record:
                        play_sound('new_record', sounds)
                    else:
                        play_sound('game_over', sounds)

                if game.score > best_score:
                    save_best_score(game.score)
                    best_score = game.score

                time.sleep(2)
                game.reset()
                start_screen = True
                stop_sound('start', sounds)


    pygame.quit()

def load_best_score():
    try:
        with open('best_score.csv', 'r') as file:
            reader = csv.reader(file)
            return int(next(reader)[0])
    except (FileNotFoundError, ValueError):
        return 0

def save_best_score(score):
    with open('best_score.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([score])

def check_sound_button(event, screen):
    button_rect = pygame.Rect(screen.get_width() - 220, 10, 100, 50)
    return button_rect.collidepoint(event.pos)

def display_start_screen(screen, best_score, new_record, sound_on):
    font = pygame.font.Font(FONT_PATH,58)
    font1 = pygame.font.SysFont(None,58)

    start_text = font.render("Tap to Start", True, (255, 255, 255))
    best_score_text = font.render(f"Best Score: {best_score}" if not new_record else f"New Record: {best_score}", True, (255, 255, 255))
    
    game_name_text = font.render("The Angle Hunter", True, (255, 255, 255))
    
    move_text = font.render("touch screen for moves", True, (255, 255, 255))
    
    sound_text = font1.render("Sound On" if sound_on else "Sound Off", True, (255, 255, 255))
    
    screen.blit(start_text, (screen.get_width() // 2 - start_text.get_width() // 2, screen.get_height() // 3))
    screen.blit(best_score_text, (screen.get_width() // 2 - best_score_text.get_width() // 2, screen.get_height() // 2))
    screen.blit(game_name_text, (screen.get_width() // 2 - game_name_text.get_width() // 2, screen.get_height() // 4))
    screen.blit(move_text, (screen.get_width() // 2 - move_text.get_width() // 2, screen.get_height() - 60))
    screen.blit(sound_text, (screen.get_width() - 220, 10))

if __name__ == "__main__":
    main()
