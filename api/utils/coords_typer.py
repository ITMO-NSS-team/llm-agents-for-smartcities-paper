from typing import Dict, List


def get_dimensions(lst: list | float):
    if isinstance(lst, list):
        return 1 + max(get_dimensions(item) for item in lst)
    else:
        return 0


def get_territory_coordinate_type(coords: List) -> str:
    n_dims = get_dimensions(coords)
    if n_dims == 4:
        return "MultiPolygon"
    elif n_dims == 3:
        return "Polygon"
    elif n_dims == 2:
        return "LineString"
    elif n_dims == 1:
        return "Point"
    else:
        raise Exception(f"Unexpected coordinates dims: {n_dims}")


def prepare_typed_coords(coords: List) -> Dict:
    return {
        "coordinates": coords,
        "type": get_territory_coordinate_type(coords),
    }
