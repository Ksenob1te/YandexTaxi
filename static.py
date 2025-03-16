import osmnx as ox
import geopandas as gpd

WIDTH, HEIGHT = 400, 600

WHITE = (255, 255, 255)
ROAD_COLOR = (50, 50, 50)
GREEN_OUTLINE = (0, 150, 0)
GREEN_HATCH = (180, 230, 180)
BUILDING_OUTLINE = (100, 100, 100)
BUILDING_HATCH = (180, 180, 180)
BIG_MAP_WIDTH = 4000
BIG_MAP_HEIGHT = 4000

global_candy_counter = 0

graph = ox.load_graphml("moscow_roads_tverskoy.graphml")
buildings = gpd.read_file("moscow_buildings_tverskoy.geojson")
green_areas = gpd.read_file("moscow_green_tverskoy.geojson")