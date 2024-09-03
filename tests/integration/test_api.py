import json
from test.test_data.api_objects_examples import coordinates
from test.test_data.api_objects_examples import possible_name_ids

import pytest

from api.summary_tables_requests import get_summary_table
from api.summary_tables_requests import possible_tables
from api.utils.coords_typer import prepare_typed_coords


# Test getting info from table by coordinates
@pytest.mark.parametrize("table", possible_tables.values())
@pytest.mark.parametrize("coord", coordinates)
def test_get_general_stats_via_coords(table, coord):
    # get coords in format: {'coords': [..., ...], 'type':Literal['Point', 'Polygon', 'Multipolygon']]}
    coord = prepare_typed_coords(coord["coords"])
    try:
        res = get_summary_table(table, None, None, coord)
        json.dumps(res)
    except Exception as e:
        print(f'Error: {e} from table: {table} and coord: {coord["type"]}')
        assert False
    assert res


# Test getting info from table by name of territory and its type
@pytest.mark.parametrize("table", possible_tables.values())
@pytest.mark.parametrize("name_and_type", possible_name_ids)
def test_get_general_stats_via_name_id(table, name_and_type):
    # unpack name and territory
    name_id, territory_type = name_and_type
    try:
        res = get_summary_table(table, name_id, territory_type, None)
        json.dumps(res)
    except Exception as e:
        print(
            f"Error: {e} from table: {table} and name_id: {name_id} and territory_type: {territory_type}"
        )
        assert False
    assert res
