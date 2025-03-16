import pygame
import random


class HandDrawnCandyDisplay:
    def __init__(self, screen_width, screen_height, position=(50, 10)):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.position = position

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)

    def draw(self, surface, counter):
        box_width = 150
        box_height = 50
        box_x, box_y = self.position
        box_coords = [
            (box_x, box_y),
            (box_x + box_width, box_y),
            (box_x + box_width, box_y + box_height),
            (box_x, box_y + box_height)
        ]
        self._draw_hand_drawn_polygon(surface, box_coords)
        text = f"Candy: {counter}"
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(box_x + box_width // 2, box_y + box_height // 2))
        surface.blit(text_surface, text_rect)

    def _draw_hand_drawn_polygon(self, surface, coords):
        for i in range(len(coords)):
            start_pt = coords[i]
            end_pt = coords[(i + 1) % len(coords)]
            self._draw_sketch_line(surface, (0, 0, 0), start_pt, end_pt)

    def _draw_sketch_line(self, surface, color, start_pos, end_pos, roughness=2, iterations=2):
        for _ in range(iterations):
            sx = start_pos[0] + random.randint(-roughness, roughness)
            sy = start_pos[1] + random.randint(-roughness, roughness)
            ex = end_pos[0] + random.randint(-roughness, roughness)
            ey = end_pos[1] + random.randint(-roughness, roughness)
            pygame.draw.aaline(surface, color, (sx, sy), (ex, ey))
