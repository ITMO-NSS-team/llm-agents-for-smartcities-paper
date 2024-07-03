from pprint import pprint

from api import Api
from test_data.districts import *
from test_data.cities import *
from test_data.blocks import *
from test_data.municipalities import *
from test_data.houses import *
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
def get_summary_table_by_geometry(table: str, coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_table_by_geometry(
        table=table,
        user_selection_zone=coordinates
    )

def get_summary_table_by_territory_id(table: str, territory_name_id: str, territory_type: str) -> Dict:
    return Api.EndpointsSummaryTables.get_table_by_geometry(
        table=table,
        territory_name_id=territory_name_id,
        territory_type=territory_type
    )


# Individual table functions
def get_general_stats_city(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_table_by_geometry(
        table='Общий контекст – общая таблица-сводка по городу',
        user_selection_zone=coordinates
    )


def get_general_stats_districs_mo(coordinates: List) -> Dict:  #!!!!!!!!!!
    return Api.EndpointsSummaryTables.get_table_by_geometry(
        table='Территориальный контекст сводка по выбранному району или МО',
        user_selection_zone=coordinates
    )


def get_general_stats_block(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_table_by_geometry(
        table='Территориальный контекст сводка по выбранному кварталу',
        user_selection_zone=coordinates
    )


def get_general_stats_education(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_table_by_geometry(
        table='Отраслевой контекст – образование',
        user_selection_zone=coordinates
    )


def get_general_stats_healthcare(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_table_by_geometry(
        table='Отраслевой контекст - здравоохранение',
        user_selection_zone=coordinates
    )


def get_general_stats_culture(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_table_by_geometry(
        table='Отраслевой контекст – Культура и досуг',
        user_selection_zone=coordinates
    )



def get_general_stats_sports(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_table_by_geometry(
        table='Отраслевой контекст – Физическая культура и спорт',
        user_selection_zone=coordinates
    )



def get_general_stats_services(coordinates: List) -> Dict:
    return Api.EndpointsSummaryTables.get_table_by_geometry(
        table='Отраслевой контекст – Обслуживание населения',
        user_selection_zone=coordinates
    )


if __name__ == "__main__":
    tables = ['Общий контекст – общая таблица-сводка по городу',
              'Территориальный контекст сводка по выбранному району или МО',
              'Территориальный контекст сводка по выбранному кварталу',
              'Отраслевой контекст – образование',
              'Отраслевой контекст - здравоохранение',
              'Отраслевой контекст – Культура и досуг',
              'Отраслевой контекст – Физическая культура и спорт',
              'Отраслевой контекст – Обслуживание населения']

    coords = {'city': spb_coords,
              'district': vuborg_district_coords,
              'municipality': krasnoe_selo_mo_coords,
              'block': block2_coords,
              'house': house1_coords}

    # coords = {'blocks': block2_coords}

    for table in tables:
        for type, coord in coords.items():
            try:
                input_data = {"coordinates": coord}
                res = get_summary_table_by_geometry(table, input_data)
                print(f'{table} works well with {type} data')
                # pprint(res)
            except Exception as e:
                pass
                print(f'ERROR: {table} has issues with {type} data')
                print(e)
        print('-------------------------------------------------')
