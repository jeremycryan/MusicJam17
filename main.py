import pygame
import numpy as np
import random as rd
import time
from constants import *

class Game():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
        self.screen.fill((0, 0, 0))
        self.framerate = 50

        self.code_font = pygame.font.SysFont("monospace", 20)
        self.clock = pygame.time.Clock()

        self.code = CODE
        self.lines = self.code.split("\n")
        self.line_idx = -1

        self.lines_to_render = []
        self.max_lines_rendered = 10
        self.yoffset = 25
        self.additional_offset = self.yoffset

    def get_next_line(self):
        self.line_idx += 1
        if self.line_idx >= len(self.lines):
            self.line_idx = 0
        return self.lines[self.line_idx]

    def render_lines(self):
        yoffset, xoffset, yspacing = 100, 100, self.yoffset
        start_position = (xoffset, WINDOW_HEIGHT - yoffset)
        current_y_position = start_position[1]

        for line in self.lines_to_render:
            t = OLD_FONT_TRANSPARENCY
            if line[0] != "!":
                hack = game.code_font.render(line, 1, (t, t, t))
            else:
                hack = game.code_font.render(line, 1, (t/2+128, t/2, t/2))
            self.screen.blit(hack,
                            (start_position[0],
                            current_y_position + self.additional_offset))
            current_y_position -= yspacing
        self.additional_offset -= 0.25 * self.additional_offset

    def loop(self):
        self.clock.tick()
        self.time_ms = 0
        speed = 1000
        while True:

            time_diff = self.clock.tick(self.framerate)
            prev_time = self.time_ms
            self.time_ms += time_diff
            a = (self.time_ms % speed < prev_time % speed)
            if a:
                self.additional_offset = self.yoffset
                if len(self.lines_to_render) < self.max_lines_rendered:
                    self.lines_to_render = [self.get_next_line()] + self.lines_to_render
                else:
                    self.lines_to_render = [self.get_next_line()] + self.lines_to_render[:-1]

            self.screen.fill((0, 0, 0))
            self.render_lines()
            pygame.display.flip()

class Sequence():
    def __init__(self, measures = 1, pattern_dict = None):
        self.measures = measures

    def random_pattern_dict(self, valid_nums, granularity = 8, fullness = 0.3):
        d = {}
        for num in valid_nums:
            sequence_length = granularity * self.measures
            sequence = zeros(sequence_length)
            for idx in range(sequence_length):
                if rd.random < fullness:
                    sequence[idx] = 1



if __name__ == '__main__':
    game = Game()
    game.loop()
