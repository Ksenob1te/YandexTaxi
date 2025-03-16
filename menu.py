import random
import pygame
import math
from shapely.geometry import Polygon, LineString


class HandDrawnMenu:
    polygon = None
    dot_array = None

    def __init__(self, screen_width, screen_height, corner_radius=40):
        self.counter = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.corner_radius = corner_radius

        self.visible = False
        self.text = "Hello from the bottom half!"
        self.fill_color = (255, 255, 255)
        self.outline_color = (0, 0, 0)
        self.text_color = (0, 0, 0)
        self.marker_color = (255, 0, 0)
        self.cross_color = (255, 0, 0)

        self.x = 0
        self.y = self.screen_height // 2
        self.w = self.screen_width
        self.h = self.screen_height // 2

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)

        self.cross_offset = 40
        self.cross_size = 15

        self.box_width = 200
        self.box_height = 100
        self.box_x = (self.screen_width - self.box_width) // 2
        self.box_y = self.y + 50
        self.box_clicked = False
        self.show_candy = False

    def open(self, text="Hello from the bottom half!"):
        self.visible = True
        self.text = text

    def close(self):
        self.visible = False

    def draw(self, surface):
        if not self.visible:
            return

        shape_points = self._build_rounded_top_polygon(self.x, self.y, self.w, self.h, self.corner_radius)
        pygame.draw.polygon(surface, self.fill_color, shape_points)

        outline_passes = 2
        roughness = 2
        for _ in range(outline_passes):
            for i in range(len(shape_points)):
                p1 = shape_points[i]
                p2 = shape_points[(i + 1) % len(shape_points)]
                sx1 = p1[0] + random.randint(-roughness, roughness)
                sy1 = p1[1] + random.randint(-roughness, roughness)
                sx2 = p2[0] + random.randint(-roughness, roughness)
                sy2 = p2[1] + random.randint(-roughness, roughness)
                pygame.draw.aaline(surface, self.outline_color, (sx1, sy1), (sx2, sy2))

        # text_surf = self.font.render(self.text, True, self.text_color)
        # text_rect = text_surf.get_rect(
        #     center=(self.screen_width // 2, self.y + self.h // 2)
        # )
        # surface.blit(text_surf, text_rect)

        self._draw_marker(surface)
        self._draw_red_cross(surface)

        if self.show_candy:
            self._draw_hand_drawn_candy(surface)
        else:
            self._draw_hand_drawn_box(surface)

    def _build_rounded_top_polygon(self, x, y, w, h, r, segments=8):
        points = []
        points.append((x, y + h))
        points.append((x + w, y + h))

        cx_right = x + w - r
        cy_right = y + r
        for i in range(segments + 1):
            theta_deg = (90 * i / segments)
            theta = math.radians(theta_deg)
            px = cx_right + r * math.cos(theta)
            py = cy_right - r * math.sin(theta)
            points.append((px, py))

        cx_left = x + r
        cy_left = y + r
        for i in range(segments + 1):
            theta_deg = 90 + (90 * i / segments)
            theta = math.radians(theta_deg)
            px = cx_left + r * math.cos(theta)
            py = cy_left - r * math.sin(theta)
            points.append((px, py))

        points.append((x, y + h))
        return points

    def _draw_red_cross(self, surface):
        cx = self.x + self.w - self.cross_offset
        cy = self.y + self.cross_offset

        arm_len = self.cross_size
        passes = 2
        jitter = 2
        for _ in range(passes):
            x1 = cx - arm_len + random.randint(-jitter, jitter)
            y1 = cy - arm_len + random.randint(-jitter, jitter)
            x2 = cx + arm_len + random.randint(-jitter, jitter)
            y2 = cy + arm_len + random.randint(-jitter, jitter)
            pygame.draw.aaline(surface, self.cross_color, (x1, y1), (x2, y2))

            x3 = cx - arm_len + random.randint(-jitter, jitter)
            y3 = cy + arm_len + random.randint(-jitter, jitter)
            x4 = cx + arm_len + random.randint(-jitter, jitter)
            y4 = cy - arm_len + random.randint(-jitter, jitter)
            pygame.draw.aaline(surface, self.cross_color, (x3, y3), (x4, y4))

    def draw_hatch_lines(self, surface, hatch_spacing, hatch_angle, color):
        theta = math.radians(hatch_angle)
        nx = -math.sin(theta)
        ny = math.cos(theta)
        min_x, min_y, max_x, max_y = self.polygon.bounds
        corners = [(min_x, min_y), (min_x, max_y), (max_x, min_y), (max_x, max_y)]
        c_values = [nx * x + ny * y for (x, y) in corners]
        c_min, c_max = min(c_values), max(c_values)

        center = ((min_x + max_x) / 2, (min_y + max_y) / 2)
        dx = math.cos(theta)
        dy = math.sin(theta)
        L = math.sqrt((max_x - min_x) ** 2 + (max_y - min_y) ** 2) * 1.5

        c = c_min - hatch_spacing
        while c < c_max + hatch_spacing:
            center_proj = nx * center[0] + ny * center[1]
            d = c - center_proj
            p0 = (center[0] + d * nx, center[1] + d * ny)
            p1 = (p0[0] - L * dx, p0[1] - L * dy)
            p2 = (p0[0] + L * dx, p0[1] + L * dy)
            line = LineString([p1, p2])
            if self.polygon.is_valid:
                inter = self.polygon.intersection(line)
                if not inter.is_empty:
                    if inter.geom_type == "LineString":
                        coords = list(inter.coords)
                        if len(coords) >= 2:
                            pygame.draw.line(surface, color,
                                             (coords[0][0], coords[0][1]),
                                             (coords[-1][0], coords[-1][1]), width=2)
                    elif inter.geom_type == "MultiLineString":
                        for seg in inter.geoms:
                            coords = list(seg.coords)
                            if len(coords) >= 2:
                                pygame.draw.line(surface, color,
                                                 (coords[0][0], coords[0][1]),
                                                 (coords[-1][0], coords[-1][1]), width=2)
            c += hatch_spacing

    def crosshatch_polygon(self, surface, color=(100, 100, 100), spacing=8):
        self.draw_hatch_lines(surface, spacing, 45, color)
        self.draw_hatch_lines(surface, spacing, -45, color)

    def draw_sketch_outline(self, surface, color=(0, 0, 0),
                            roughness=1, iterations=2):
        for i in range(len(self.dot_array)):
            start = self.dot_array[i]
            end = self.dot_array[(i + 1) % len(self.dot_array)]
            for _ in range(iterations):
                sx = start[0] + random.randint(-roughness, roughness)
                sy = start[1] + random.randint(-roughness, roughness)
                ex = end[0] + random.randint(-roughness, roughness)
                ey = end[1] + random.randint(-roughness, roughness)
                pygame.draw.aaline(surface, color, (sx, sy), (ex, ey))

    def build_marker_shape(self, radius=20, tip_height=30, segments=12):
        shape_points = []
        for i in range(segments + 1):
            angle = math.pi + (i * (math.pi / segments))
            x = self.screen_width // 2 + radius * math.cos(angle)
            y = self.screen_height // 2 - tip_height // 2 + radius * math.sin(angle)
            shape_points.append((x, y))

        bottom_tip = (self.screen_width // 2, self.screen_height // 2 + tip_height // 2)
        shape_points.append(bottom_tip)
        return shape_points

    def _draw_marker(self, surface, radius=60, tip_height=90, refresh=True):
        if self.polygon is None or refresh:
            self.dot_array = self.build_marker_shape(radius=radius,
                                                     tip_height=tip_height,
                                                     segments=12)
            self.polygon = Polygon(self.dot_array)
        self.crosshatch_polygon(surface, color=(187, 150, 0), spacing=6)
        self.draw_sketch_outline(surface, color=(102, 82, 0), roughness=2, iterations=2)

    def _draw_hand_drawn_box(self, surface):
        box_coords = [
            (self.box_x, self.box_y),
            (self.box_x + self.box_width, self.box_y),
            (self.box_x + self.box_width, self.box_y + self.box_height),
            (self.box_x, self.box_y + self.box_height)
        ]
        self._draw_hand_drawn_polygon(surface, box_coords)
        box_text = "Click to open box"
        box_color = (0, 0, 255)
        box_surf = self.font.render(box_text, True, box_color)
        box_rect = box_surf.get_rect(center=(self.screen_width // 2, self.box_y + self.box_height // 2))
        surface.blit(box_surf, box_rect)

    def _draw_hand_drawn_candy(self, surface):
        candy_coords = self._get_candy_shape_coords()
        self._draw_hand_drawn_polygon(surface, candy_coords)
        candy_text = "Candy!"
        candy_color = (255, 0, 255)
        candy_surf = self.font.render(candy_text, True, candy_color)
        candy_rect = candy_surf.get_rect(center=(self.screen_width // 2, self.y + 85))
        surface.blit(candy_surf, candy_rect)

    def _get_candy_shape_coords(self):
        candy_width = 100
        candy_height = 50
        candy_x = (self.screen_width - candy_width) // 2
        candy_y = self.y + 60
        return [
            (candy_x, candy_y),
            (candy_x + candy_width, candy_y),
            (candy_x + candy_width, candy_y + candy_height),
            (candy_x, candy_y + candy_height)
        ]

    def _draw_hand_drawn_polygon(self, surface, coords):
        for i in range(len(coords)):
            start_pt = coords[i]
            end_pt = coords[(i + 1) % len(coords)]
            self._draw_sketch_line(surface, self.outline_color, start_pt, end_pt)

    def _draw_sketch_line(self, surface, color, start_pos, end_pos, roughness=2, iterations=2):
        for _ in range(iterations):
            sx = start_pos[0] + random.randint(-roughness, roughness)
            sy = start_pos[1] + random.randint(-roughness, roughness)
            ex = end_pos[0] + random.randint(-roughness, roughness)
            ey = end_pos[1] + random.randint(-roughness, roughness)
            pygame.draw.aaline(surface, color, (sx, sy), (ex, ey))

    def handle_event(self, event):
        if not self.visible:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            cross_center = (self.x + self.w - self.cross_offset, self.y + self.cross_offset)
            dist = math.hypot(mx - cross_center[0], my - cross_center[1])
            if dist < self.cross_size:
                self.close()
            box_rect = pygame.Rect(self.box_x, self.box_y, self.box_width, self.box_height)
            if box_rect.collidepoint(mx, my) and not self.box_clicked:
                self.box_clicked = True
                self.counter += 1
                self.show_candy = not self.show_candy
        return self.counter

