import json

import pytest

from api.summary_tables_requests import get_summary_table
from api.summary_tables_requests import possible_tables
from api.utils.coords_typer import prepare_typed_coords
from tests.test_data.api_objects_examples import coordinates
from tests.test_data.api_objects_examples import possible_indicators
from tests.test_data.api_objects_examples import possible_name_ids


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


# Test getting info from table by the selection_zone and needed indicators
@pytest.mark.parametrize("indicators", possible_indicators)
@pytest.mark.parametrize("coord", coordinates)
def test_get_indicator_stats(indicators, coord):
    coord = prepare_typed_coords(coord["coords"])
    try:
        res = get_indicators([indicators], None, None, coord)
        json.dumps(res)
    except Exception as e:
        print(f"Error: {e} from indicators: {indicators} and coord: {coord['type']}")
        assert False
    assert res


# Test getting needed indicators with name_id and territory_type
@pytest.mark.parametrize("indicators", possible_indicators)
@pytest.mark.parametrize("name_and_type", possible_name_ids)
def test_get_indicators_via_name_id(indicators, name_and_type):
    # unpack name and territory
    name_id, territory_type = name_and_type
    try:
        res = get_indicators([indicators], name_id, territory_type, None)
        json.dumps(res)
    except Exception as e:
        print(
            f"Error: {e} from indicators: {indicators} and name_id: {name_id} and territory_type: {territory_type}"
        )
        assert False
    assert res
