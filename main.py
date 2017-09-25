# A rhythm-based coding Game
# Have fun in there :)

import pygame
import numpy as np
import random as rd
import time
from math import sin
from constants import *
from code import *

#   Keep it up!

class Game():
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        pygame.mixer.music.load('mus.wav')
        pygame.mixer.music.play(-1)

        self.screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
        pygame.display.set_caption("Command Prompt")
        self.screen.fill((0, 0, 0))
        self.framerate = 50

        #   This just got a little too meta.

        self.beat_length = 500
        self.current_color = 0
        self.multiplier = 1.0
        self.health = 100.0
        self.healthbar_health = 100.0
        self.healthbar_color = [255, 255, 255]

        self.time_offset = 0

        self.goal_pos = (60, WINDOW_HEIGHT-55)

        self.code_font = pygame.font.SysFont("monospace", 20)
        self.multiplier_font = pygame.font.SysFont("monospace", 50)
        self.win_font = pygame.font.SysFont("monospace", 35)
        self.clock = pygame.time.Clock()

        self.key_list = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r,
            pygame.K_t, pygame.K_y, pygame.K_u, pygame.K_i, pygame.K_o,
            pygame.K_p, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f,
            pygame.K_g, pygame.K_h, pygame.K_j, pygame.K_k, pygame.K_l,
            pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v, pygame.K_b,
            pygame.K_n, pygame.K_m, pygame.K_RETURN]
        self.last_presses = self.determine_keypresses()

        self.code = CODE
        self.lines = self.code.split("\n")
        for idx, item in enumerate(self.lines):
            if len(item) > 50:
                self.lines[idx] = item[0:50]
        i = 0
        while i < len(self.lines):
            if not len(self.lines[i]):
                self.lines.pop(i)
            else:
                i += 1
        self.line_idx = 0

        self.bang_list = []
        self.flash_list = []

        self.lines_to_render = []
        self.max_lines_rendered = 12
        self.yoffset = 25
        self.additional_offset = self.yoffset
        self.shock_offset = 0

        self.score = 0

        self.success_sound = pygame.mixer.Sound('success.wav')
        self.success_sound.set_volume(0.4)
        self.failure_sound = pygame.mixer.Sound('failure.wav')
        self.failure_sound.set_volume(0.7)

        self.beat_list = [8, 16,
                            24, 28,
                            #   First chorus
                            32, 36,
                            40, 44, 48, 52,
                            56, 60, 64, 68,
                            72, 76,
                            80, 82, 84,
                            88, 90, 92,
                            #   Second chorus
                            96, 98, 100,
                            104, 106, 108,
                            112, 114, 116,
                            120, 123, 125,
                            128, 130, 132,
                            136, 139, 142,
                            144, 148, 150,
                            152, 156, 158,
                            160, 162, 164,
                            168, 170, 172,
                            176, 178, 180, 182,
                            184, 186, 188,
                            #   Third chorus
                            192, 194, 195,
                            200, 204, 207,
                            208, 212,
                            216, 217, 218,
                            224, 226, 228,
                            232, 233, 234, 235,
                            236, 239,
                            241, 243,
                            244, 246,
                            248, 249, 250, 251,
                            252,
                            256, 258, 260, 262,
                            264, 265, 266, 267,
                            268, 270, 271,
                            272,
                            276]

    def render_score(self, pos):
        a = 10 - len(str(self.score))
        if pos == 0:
            string = game.code_font.render("Score: %s%s  Juice:" % ("0" * a, self.score), 1, (255, 255, 255))
            self.screen.blit(string,
                        (120 + self.shock_offset,
                        50 + self.shock_offset))
        elif pos == 1:
            string = game.code_font.render("Score: %s" % (self.score), 1, (255, 255, 255))
            self.screen.blit(string,
                        (300 + self.shock_offset,
                        260 + self.shock_offset))

    def render_goal(self, size):
        self.goal_size = (size, size)
        self.goal_surface = pygame.Surface(self.goal_size)
        self.goal_surface.set_colorkey((0, 0, 0))
        self.goal_color = (200, 200, 200)
        pygame.draw.circle(self.goal_surface, self.goal_color,
            (self.goal_size[0]/2, self.goal_size[0]/2),
            self.goal_size[0]/2, 2)
        half = self.goal_size[0]/2
        self.screen.blit(self.goal_surface,
            (self.goal_pos[0] - half, self.goal_pos[1] - half))

    def render_bangs(self, size):
        size = (size + 30)/2
        for bang in self.bang_list:
            bang_size = (size, size)
            bang_surface = pygame.Surface(bang_size)
            ypos = self.goal_pos[1] - bang.beats_away(self.time_ms) * 100.0
            lightness = max(200 - abs(self.goal_pos[1] - ypos), 120)
            bang_surface.set_colorkey((0, 0, 0))
            bang_color = (lightness, lightness, lightness)
            half = bang_size[0]/2
            pygame.draw.circle(bang_surface, bang_color, (half, half), half, 0)
            half = bang_size[0]/2
            self.screen.blit(bang_surface, (self.goal_pos[0] - half, ypos - half))

    def render_flashes(self):
        for prop in self.flash_list:
            if prop > 1:
                prop = 1
            size = 30 + 120*prop
            surf = pygame.Surface((size, size))
            surf.set_colorkey((0, 0, 0))
            shade = 255 - 255*prop**0.5
            xpos, ypos = self.goal_pos[0], self.goal_pos[1]
            half = int(size/2)
            color = [shade/1.2, shade/1.2, shade/1.2]
            color[self.current_color] *= 1.2
            color = [int(i) for i in color]
            pygame.draw.circle(surf, (color[2], color[1], color[0]), (half, half), half, 0)
            self.screen.blit(surf, (xpos - half, ypos - half))

    def make_flash(self):
        self.flash_list.append(0.0)

    def get_next_line(self):
        if self.line_idx >= len(self.lines):
            self.line_idx = 0
        res = self.line_idx
        self.line_idx += 1
        return self.lines[res]

    def render_lines(self):
        yoffset, xoffset, yspacing = 90, 120, self.yoffset
        start_position = (xoffset, WINDOW_HEIGHT - yoffset)
        current_y_position = start_position[1]

        for line in self.lines_to_render:
            t = OLD_FONT_TRANSPARENCY
            if line[0] == "!":
                hack = game.code_font.render(line, 1, (t/2+128, t/2, t/2))
            elif line[:7] == "Current":
                hack = game.code_font.render(line, 1, (t/2, t/2+128, t/2))
            elif line[0] == "#":
                hack = game.code_font.render(line, 1, (t/2+32, t/2+96, t/2+128))
            else:
                hack = game.code_font.render(line, 1, (t, t, t))
            self.screen.blit(hack,
                            (start_position[0] + self.shock_offset,
                            current_y_position + self.additional_offset + self.shock_offset))
            current_y_position -= yspacing

    def update_lines(self, line):
        self.additional_offset = self.yoffset
        if len(self.lines_to_render) < self.max_lines_rendered:
            self.lines_to_render = [line] + self.lines_to_render
        else:
            self.lines_to_render = [line] + self.lines_to_render[:-1]

    def get_warning_message(self):
        message_list = ["!ERROR! : Out of mayonnaise.",
            "!WARNING! : Hacking too much time.",
            "!ERROR! : Speed has not reached 88mph.",
            "!CAUTION! : Ground approaching rapidly.",
            "!DANGER! : Troll in the dungeon.",
            "!WARNING! : Maximum recursion depth of 1 exceeded.",
            "!ERROR! : What the hell is even going on.",
            "!ERROR! : Improbability drive produced rats."]
        a = rd.choice(message_list)
        if self.health <= 20:
            a = "!DANGER! : Juice levels critical!"
        return a

    def loop(self):
        self.clock.tick()
        self.time_ms = self.time_offset
        time_since_semicolon = 0
        speed = 1000
        progress = 0
        press_tolerance = 0.2
        multiplier_mentioned = 0
        flashy = 0
        self.last_error = self.time_ms
        beat = 0
        won = 0
        while True:
            pygame.event.pump()
            pressed = self.presses_since_last()

            time_diff = self.clock.tick(self.framerate)
            prev_time = self.time_ms
            self.time_ms += time_diff
            if prev_time % self.beat_length > self.time_ms % self.beat_length:
                beat += 1
                self.current_color += 1
                if self.current_color >= 3:
                    self.current_color = 0
                if beat + 4 in self.beat_list:
                    self.bang_list.append(Bang(self.time_ms + self.beat_length * 4,
                        self.beat_length))
            time_since_semicolon += time_diff
            for key in pressed[0:-1]:
                if key == 1:
                    progress = min(progress + 0.15, 1.0)
            if pressed[-1]==1 and time_since_semicolon > 0.05 and progress == 1:
                for item in self.bang_list:
                    if abs(item.beats_away(self.time_ms)) <= press_tolerance:
                        self.multiplier += 1
                        flashy = 1
                        if self.multiplier % 5 == 0:
                            self.update_lines("Current multiplier: %s" % self.multiplier)
                        self.success_sound.play()
                        self.update_lines(self.get_next_line()+"")
                        time_since_semicolon = 0
                        progress = 0
                        self.destroy_bang(item)
                        self.make_flash()
                        self.shock_offset = 5

            for item in self.bang_list:
                if item.beats_away(self.time_ms) < -press_tolerance:
                    self.failure_sound.play()
                    self.health = max(0, self.health - 30)
                    self.destroy_bang(item)
                    self.shock_offset = 50
                    self.update_lines(self.get_warning_message())
                    self.update_lines("Multiplier reset.")
                    self.last_error = self.time_ms
                    self.multiplier = 1.0

            dif = (self.time_ms % self.beat_length)*1.0/self.beat_length
            self.render_background(dif)
            if flashy:
                flashy = 0
                self.screen.fill((150, 150, 150))
            num_over_one = 0
            for idx, item in enumerate(self.flash_list):
                self.flash_list[idx] = item + dif/8
                if item > 1:
                    num_over_one += 1
            self.flash_list = self.flash_list[num_over_one:]

            self.render_flashes()
            min_rad = 0.3
            goal_size = max(dif, 1-dif)**4
            goal_size = int((min_rad + goal_size*(1-min_rad))*50)
            self.render_health()
            self.render_bangs(goal_size)
            self.render_goal(goal_size)
            self.render_lines()
            self.render_current_line(progress)
            self.additional_offset -= self.additional_offset * time_diff/100.0
            self.shock_offset *= -0.6
            self.score += int(self.multiplier * time_diff)
            if self.health != 0:
                self.health = min(self.health + time_diff/200.0, 100)
            self.render_score(0)
            if abs(self.shock_offset) <= 1:
                self.shock_offset = 0

            if beat > 280 or self.health == 0:
                won = self.health > 0
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()

        while 1:
            time_diff = self.clock.tick(self.framerate)
            prev_time = self.time_ms
            self.time_ms += time_diff

            if prev_time % self.beat_length > self.time_ms % self.beat_length:
                self.current_color = (self.current_color + 1)%3
                self.shock_offset += 12

            dif = (self.time_ms % self.beat_length)*1.0/self.beat_length
            self.render_background(dif)
            self.render_you_win(won)
            self.render_score(1)

            self.shock_offset *= -0.6
            if abs(self.shock_offset) <= 1:
                self.shock_offset = 0
            pygame.display.flip()

    def render_health(self):
        surf = pygame.Surface((300, 16))
        surf.set_colorkey((0, 0, 0))
        if self.health == 100:
            aim_color = (200, 200, 200)
        elif self.health >= 50:
            aim_color = (80, 110, 150)
        elif self.health >= 20:
            aim_color = (150, 140, 60)
            self.shock_offset += rd.choice([-1, 0, 1])
        else:
            aim_color = (130, 50, 40)
            self.shock_offset += rd.choice([-2, 0, 2])
        self.healthbar_color = [self.healthbar_color[i] + 5*(aim_color[i] - \
            self.healthbar_color[i])/self.framerate for i in range(0, 3)]
        color = (self.healthbar_color[0],
            self.healthbar_color[1],
            self.healthbar_color[2])
        self.healthbar_health += 3*(self.health - self.healthbar_health)/self.framerate
        pygame.draw.rect(surf, color, (0, 0, 3*self.healthbar_health, 16))
        self.screen.blit(surf, (432 + self.shock_offset, 52 + self.shock_offset))

    def render_you_win(self, won):
        if won:
            text = "Task completed."
        else:
            text = "Task failed."
        text_obj = self.win_font.render(text, 1, (255, 255, 255))
        self.screen.blit(text_obj, (255 + self.shock_offset, 200 + self.shock_offset))

    def render_background(self, dif):
        self.screen.fill((10, 10, 10))
        if dif < 0.5:
            if self.current_color == 0:
                self.screen.fill((35 - dif*50, 35 - dif*50, 70 - dif*120))
            elif self.current_color == 1:
                self.screen.fill((35 - dif*50, 55 - dif*90, 35 - dif*50))
            elif self.current_color == 2:
                self.screen.fill((80 - dif*140, 35 - dif*50, 35 - dif*50))

    def render_current_line(self, progress):
        line = self.lines[self.line_idx]
        num_letters = int(progress * len(line))
        new_line = line[0:num_letters]

        color = (155 + 100*progress, 155 + 100*progress, 155 + 100*progress)
        # if progress == 1.0:
        #     color = (150, 255, 180)
        hack = self.code_font.render(new_line, 1, color)

        self.screen.blit(hack,(120 + self.shock_offset,
            WINDOW_HEIGHT - 90 + self.yoffset + self.shock_offset))

    def determine_keypresses(self):
        pressed = pygame.key.get_pressed()
        self.last_keypresses = [pressed[key] for key in self.key_list]
        return self.last_keypresses

    def presses_since_last(self):
        #   -1 means key release
        a = self.last_keypresses
        b = self.determine_keypresses()
        c = [b[i] - a[i] for i in range(len(a))]
        return c

    def make_bang(self, beats_from_now):
        new_bang = Bang(self.time_ms + beats_from_now * self.beat_length)
        self.bang_list.append(new_bang)

    def destroy_bang(self, bang):
        self.bang_list.remove(bang)

class Bang():
    def __init__(self, pop_time, beat_length):
        self.pop_time = pop_time
        self.beat_length = beat_length

    def beats_away(self, cur_time):
        return (float(self.pop_time - cur_time))/self.beat_length

if __name__ == '__main__':
    game = Game()
    game.loop()
