import osmnx as ox
import geopandas as gpd
from tqdm import tqdm

# -------------------------------
# 1. DEFINE SPECIFIC REGION IN MOSCOW (Tverskoy District)
# -------------------------------
# Approximate coordinates of Tverskoy District
# Note: Normally latitude ~55 and longitude ~37 in Moscow.
# Ensure your order of values is as expected by the functions.
north, south, east, west = 37.60, 55.70, 37.64, 55.77  # (north, south, east, west)

# -------------------------------
# 2. DOWNLOAD & SAVE ROAD NETWORK, BUILDINGS, AND GREEN AREAS
# -------------------------------
try:
    # Download road network within the specified bounding box.
    # For OSMnx v2, graph_from_bbox expects a bbox tuple.
    graph = ox.graph_from_bbox((north, south, east, west), network_type='drive', simplify=False)
    ox.save_graphml(graph, "moscow_roads_tverskoy.graphml")

    # Download building footprints within the specified bounding box.
    buildings = ox.features_from_bbox((north, south, east, west), tags={"building": True})
    buildings.to_file("moscow_buildings_tverskoy.geojson", driver="GeoJSON")

    # Define tags for green areas (parks, grass, forest, etc.)
    green_tags = {
        "leisure": "park",
        "landuse": ["grass", "forest", "recreation_ground", "village_green"]
    }
    # Download green areas within the same bounding box.
    green_areas = ox.features_from_bbox((north, south, east, west), tags=green_tags)
    green_areas.to_file("moscow_green_tverskoy.geojson", driver="GeoJSON")

except Exception as e:
    print(f"❌ Download failed: {e}")
