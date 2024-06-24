from pprint import pprint

from api import Api
from test_data.districts import *
from test_data.cities import *
from test_data.blocks import *
from test_data.municipalities import *
from test_data.houses import *
from typing import Dict

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
def get_summary_table_by_geometry(table: str, user_selection_zone: Dict) -> Dict:
    return Api.EndpointsSummaryTables.get_table_by_geometry(
        table=table,
        user_selection_zone=user_selection_zone
    )

def get_summary_table_by_territory_id(table: str, territory_name_id: str, territory_type: str) -> Dict:
    return Api.EndpointsSummaryTables.get_table_by_geometry(
        table=table,
        territory_name_id=territory_name_id,
        territory_type=territory_type
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
              'block': block1_coords,
              'house': house1_coords}

    coords = {'blocks': block2_coords}

    for table in tables:
        for type, coord in coords.items():
            try:
                input_data = {"coordinates": coord}
                res = get_summary_table_by_geometry(table, input_data)
                print(f'{table} works well with {type} data')
                pprint(res)
            except Exception as e:
                pass
                # print(f'ERROR: {table} has issues with {type} data')
                # print(e)
        print('-------------------------------------------------')
