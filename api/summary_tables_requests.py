from pprint import pprint

from api.api import Api
from api.test_data.districts import *
from api.test_data.cities import *
from api.test_data.blocks import *
from api.test_data.municipalities import *
from api.test_data.houses import *
from typing import Dict, List

'''
Possible table names:

    Общий контекст – общая таблица-сводка по городу
    Территориальный контекст сводка по выбранному району или МО
    Территориальный контекст сводка по выбранному кварталу
    Отраслевой контекст – образование
    Отраслевой контекст - здравоохранение
    Отраслевой контекст – Культура и досуг
    Отраслевой контекст – Физическая культура и спорт
    Отраслевой контекст – Обслуживание населения
    
    Отраслевой контекст - транспорт
    Отраслевой контекст – Рекреация
    Объекты контекст сводка по выбранному объекту
'''


def get_summary_table(table: str, name_id: str = None, type: str = None, coordinates: List = None) -> Dict:
    return Api.EndpointsSummaryTables.get_summary_table(
        table=table,
        territory_name_id=name_id,
        territory_type=type,
        selection_zone=coordinates
    )


# def get_summary_table_by_territory_id(table: str, territory_name_id: str, territory_type: str) -> Dict:
#     return Api.EndpointsSummaryTables.get_table_by_geometry(
#         table=table,
#         territory_name_id=territory_name_id,
#         territory_type=territory_type
#     )


# Individual table functions
def get_general_stats_city(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_summary_table(
        table='Общий контекст – общая таблица-сводка по городу',
        territory_name_id=None,
        territory_type=None,
        selection_zone=coordinates
    )


def get_general_stats_districts_mo(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_summary_table(
        table='Территориальный контекст сводка по выбранному району или МО',
        territory_name_id=None,
        territory_type=None,
        selection_zone=coordinates
    )


def get_general_stats_block(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_summary_table(
        table='Территориальный контекст сводка по выбранному кварталу',
        territory_name_id=None,
        territory_type=None,
        selection_zone=coordinates
    )


def get_general_stats_education(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_summary_table(
        table='Отраслевой контекст – образование',
        territory_name_id=None,
        territory_type=None,
        selection_zone=coordinates
    )


def get_general_stats_healthcare(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_summary_table(
        table='Отраслевой контекст - здравоохранение',
        territory_name_id=None,
        territory_type=None,
        selection_zone=coordinates
    )


def get_general_stats_culture(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_summary_table(
        table='Отраслевой контекст – Культура и досуг',
        territory_name_id=None,
        territory_type=None,
        selection_zone=coordinates
    )


def get_general_stats_sports(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_summary_table(
        table='Отраслевой контекст – Физическая культура и спорт',
        territory_name_id=None,
        territory_type=None,
        selection_zone=coordinates
    )


def get_general_stats_services(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_summary_table(
        table='Отраслевой контекст – Обслуживание населения',
        territory_name_id=None,
        territory_type=None,
        selection_zone=coordinates
    )


def get_general_stats_demography(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_summary_table(
        table='Отраслевой контекст – демография',
        territory_name_id=None,
        territory_type=None,
        selection_zone=coordinates
    )


def get_general_stats_housing_and_communal_services(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_summary_table(
        table='Отраслевой контекст – Жилье и жилищно-коммунальное хозяйство',
        territory_name_id=None,
        territory_type=None,
        selection_zone=coordinates
    )


def get_general_stats_object(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_summary_table(
        table='Объекты контекст сводка по выбранному объекту',
        territory_name_id=None,
        territory_type=None,
        selection_zone=coordinates
    )


if __name__ == "__main__":
    tables = [
        'Общий контекст – общая таблица-сводка по городу',
        'Территориальный контекст сводка по выбранному району или МО',
        'Территориальный контекст сводка по выбранному кварталу',
        'Отраслевой контекст – образование',
        'Отраслевой контекст - здравоохранение',
        'Отраслевой контекст – Культура и досуг',
        'Отраслевой контекст – Физическая культура и спорт',
        'Отраслевой контекст – Обслуживание населения',
        'Отраслевой контекст – демография',
        'Отраслевой контекст – Жилье и жилищно-коммунальное хозяйство',
        'Объекты контекст сводка по выбранному объекту'
    ]

    coords = [{'t': 'city', 'coords': spb_coords, 'type': 'MultiPolygon'},
              {'t': 'district', 'coords': vuborg_district_coords, 'type': 'Polygon'},
              {'t': 'municipality', 'coords': krasnoe_selo_mo_coords, 'type': 'MultiPolygon'},
              {'t': 'block', 'coords': block2_coords, 'type': 'Polygon'},
              {'t': 'house', 'coords': house1_coords, 'type': 'Point'}]

    # coords = {'blocks': block2_coords}

    for table in tables:
        for element in coords:
            try:
                input_data = {"coordinates": element['coords'], "type": element['type']}
                res = get_summary_table(table, coordinates=input_data)
                print(f'{table} works well with {(element.get("t"))} data')
                # pprint(res)
            except Exception as e:
                pass
                print(f'ERROR: {table} has issues with {(element.get("t"))} data')
                print(e)
        print('-------------------------------------------------')
