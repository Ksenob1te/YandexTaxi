from map_drawer import render_entire_map, create_path
from menu import HandDrawnMenu
from candy_display import HandDrawnCandyDisplay
from static import *
from user import User
from markers import Marker, generate_random_markers
import time
import math

import networkx as nx
import pygame


def open_marker_menu(marker):
    print(f"Opened menu for marker: {marker}")


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pre-render + Zoom & Pan with Invalid Polygon Fix")

    zoom = 1.0
    pan_x, pan_y = 0, 0
    pan_speed = 20
    user_circle = User()
    surface_array = []

    menu = HandDrawnMenu(WIDTH, HEIGHT)
    candy_menu = HandDrawnCandyDisplay(WIDTH, HEIGHT)

    # -------------------------------
    # MAP RENDER
    # -------------------------------
    print("Rendering map. Please wait...")
    counter = 0
    start_t = time.perf_counter()
    big_map_surface = render_entire_map()
    surface_array.append(big_map_surface)
    path_surf = None
    path_positions = None
    while path_surf is None:
        try:
            path_surf, pan_x, pan_y, path_positions = create_path()
            surface_array.append(path_surf)
        except nx.NetworkXNoPath:
            print("No path found. Retry")
    end_t = time.perf_counter()
    print(f"Map rendered in {end_t - start_t:.2f} seconds.")

    clock = pygame.time.Clock()
    running = True
    surface_array.append(user_circle.surface)
    markers = generate_random_markers()
    surface_array.append(Marker.surface)
    for marker in markers:
        marker.draw_marker()

    while running:
        # print(pan_x, pan_y, zoom)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pan_x += pan_speed
                elif event.key == pygame.K_RIGHT:
                    pan_x -= pan_speed
                elif event.key == pygame.K_UP:
                    pan_y += pan_speed
                elif event.key == pygame.K_DOWN:
                    pan_y -= pan_speed
            elif menu.visible:
                counter = menu.handle_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                for marker in Marker.active:
                    marker_screen_x = (marker.marker_x - user_circle.circle_x) + WIDTH // 2
                    marker_screen_y = (marker.marker_y - user_circle.circle_y) + HEIGHT // 2

                    dist = math.hypot(mx - marker_screen_x, my - marker_screen_y)
                    if dist < marker.radius and not marker.used:
                        menu.box_clicked = False
                        menu.show_candy = False
                        menu.open()
                        marker.make_used()
                        break

        scaled_w = int(BIG_MAP_WIDTH * zoom)
        scaled_h = int(BIG_MAP_HEIGHT * zoom)

        user_circle.draw_user(path_positions)
        user_circle.draw_empty_circle(path_surf, 9)
        for marker in markers:
            marker.update_marker(user_circle.circle_x, user_circle.circle_y, user_circle.user_radius)

        screen.fill(WHITE)
        pan_x = -user_circle.circle_x + WIDTH // 2
        pan_y = -user_circle.circle_y + HEIGHT // 2

        for surface in surface_array:
            surface_map = pygame.transform.smoothscale(surface, (scaled_w, scaled_h))
            screen.blit(surface_map, (pan_x, pan_y))

        menu.draw(screen)
        candy_menu.draw(screen, counter)
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()


if __name__ == "__main__":
    main()