from datetime import datetime
from api import Api
from typing import List, Tuple, Any


def get_service_code(service_name: str) -> int:
    city_service_types = Api.EndpointsListings.city_service_types()
    for service_type in city_service_types:
        if service_type['name'] == service_name:
            service_type_id = service_type['code']
            return service_type_id


def get_city_code_and_id(city_name: str) -> Tuple[Any, Any]:
    cities = Api.EndpointsListings.cities(centers_only=True)
    for city in cities:
        if city['name'] == city_name:
            return (city['code'], city['id'])


def get_district_coordinates(city_id: int, district_name: str) -> List:
    districts = Api.EndpointsCity.districts(city=city_id, centers_only=False)
    for district in districts:
        if district['name'] == district_name:
            return district['geometry']


def get_house_coordinates(city_id: int, address: str) -> List:
    houses = Api.EndpointsCity.houses(city=city_id, geometryAsCenter=False, livingOnly=True, requiredProperties='')
    houses = houses['features']
    for house in houses:
        if house['properties']['address'] == address:
            return house['geometry']


def get_municipalities_coordinates(city: str, mun_name: str) -> List:
    municipalities = Api.EndpointsCity.municipalities(city=city, centers_only=False)
    for municipality in municipalities:
        if municipality['name'] == mun_name:
            return municipality['geometry']


def get_provision_data(city: str, service_id: int, area_coordinates: List, year: int):
    return Api.EndpointsProvision.get_provision(
        city=city,
        service_types=[service_id],
        user_selection_zone=area_coordinates,
        year=year,
        calculation_type='linear',  # TODO: define properly for all usecases
        valuation_type='normative',  # TODO: define properly for all usecases
        service_impotancy=[1],  # TODO: define properly for all usecases
    )


def get_houses_provision_data(city: str, service_id: int, area_coordinates: List, year: int) -> List:
    provision_result = get_provision_data(city, service_id, area_coordinates, year)
    return provision_result['houses']['features']


def get_services_provision_data(city: str, service_id: int, area_coordinates: List, year: int) -> List:
    provision_result = get_provision_data(city, service_id, area_coordinates, year)
    return provision_result['services']['features']

# Methods for buildings
def get_general_demand(city, service_id, area_coordinates, year):
    houses = get_houses_provision_data(city, service_id, area_coordinates, year)
    length = len(houses)
    sum = round(sum(map(lambda house: house['properties']['demand'], houses)))
    avg = sum / length
    return f'Всего для этого района необходимо {sum} мест, в среднем на один дом необходимо {avg} мест.'


def get_demand_left(city, service_id, area_coordinates, year):
    houses = get_houses_provision_data(city, service_id, area_coordinates, year)
    len = len(houses)
    sum = round(sum(map(lambda house: house['properties']['demand_left'], houses)))
    avg = sum / len
    return f'Всего в этой местности не хватает {sum} мест, в среднем в каждом доме не хватает {avg} мест.'


def get_provison_value(city, service_id, area_coordinates, year):
    houses = get_houses_provision_data(city, service_id, area_coordinates, year)
    len = len(houses)
    sum = round(sum(map(lambda house: house['properties']['provison_value'], houses)))
    avg_percentage = sum / len * 100
    return f'Обеспеченность сервисом в этой местности составляет {avg_percentage} процентов.'


def get_demand_within(city, service_id, area_coordinates, year):
    houses = get_houses_provision_data(city, service_id, area_coordinates, year)
    len = len(houses)
    sum = round(sum(map(lambda house: house['properties']['supplyed_demands_within'], houses)))
    avg = sum / len
    return f'Количество человек, обеспеченных сервисом в заданном диапазоне доступности: {sum},' \
           f'среднее количество человек в каждом доме, обеспеченных сервисом в заданном диапазоне доступности: {avg}'


def get_demand_without(city, service_id, area_coordinates, year):
    houses = get_houses_provision_data(city, service_id, area_coordinates, year)
    len = len(houses)
    sum = round(sum(map(lambda house: house['properties']['supplyed_demands_without'], houses)))
    avg = sum / len
    return f'Количество человек, обеспеченных сервисом вне заданного диапазона доступности: {sum},' \
           f'среднее количество человек в каждом доме, обеспеченных сервисом вне заданного диапазона доступности: {avg}'


# Methods for services
def get_capacity(city, service_id, area_coordinates, year):
    houses = get_services_provision_data(city, service_id, area_coordinates, year)
    len = len(houses)
    sum = round(sum(map(lambda house: house['properties']['capacity'], houses)))
    avg = sum / len
    return f'Всего в заданной местности доступно {sum} мест,' \
           f'в среднем в каждом сервисе в заданной местности доступно: {avg} мест.'


def get_capacity_left(city, service_id, area_coordinates, year):
    houses = get_services_provision_data(city, service_id, area_coordinates, year)
    len = len(houses)
    sum = round(sum(map(lambda house: house['properties']['capacity_left'], houses)))
    avg = sum / len
    return f'На данный момент в заданной местности свободно {sum} мест,' \
           f'в среднем в каждом сервисе в заданной местности свободно: {avg} мест.'


def get_capacity_within(city, service_id, area_coordinates, year):
    houses = get_services_provision_data(city, service_id, area_coordinates, year)
    len = len(houses)
    sum = round(sum(map(lambda house: house['properties']['carried_capacity_within'], houses)))
    avg = sum / len
    return f'Количество мест, занятых людьми из заданного диапазона доступности: {sum},' \
           f'среднее количество мест в каждом сервисе, занятых людьми из заданного диапазона доступности: {avg}'


def get_capacity_without(city, service_id, area_coordinates, year):
    houses = get_services_provision_data(city, service_id, area_coordinates, year)
    len = len(houses)
    sum = round(sum(map(lambda house: house['properties']['carried_capacity_without'], houses)))
    avg = sum / len
    return f'Количество мест, занятых людьми не из заданного диапазона доступности: {sum},' \
           f'среднее количество мест в каждом сервисе, занятых людьми не из заданного диапазона доступности: {avg}'


def get_service_load(city, service_id, area_coordinates, year):
    houses = get_services_provision_data(city, service_id, area_coordinates, year)
    len = len(houses)
    sum = round(sum(map(lambda house: house['properties']['service_load'], houses)))
    avg = sum / len
    return f'На данный момент в заданной местности занято {sum} мест,' \
           f'в среднем в каждом сервисе в заданной местности занято: {avg} мест.'


city = 'Санкт-Петербург'
district = 'Выборгский район'
municipality = 'Волковское'
type = 'муниципальный округ'
service = 'Школа'
address = 'Санкт-Петербург, Московский проспект, 73к5'
current_datetime = datetime.now()
year = current_datetime.year

city_code, city_id = get_city_code_and_id(city)
service_code = get_service_code(service)
# print(get_district_coordinates(city, district))
# area_coordinates = get_municipalities_coordinates(city_code, municipality) # just city will work (name of the city in russian)
#
# res = get_general_demand(city_code, service_code, area_coordinates, year)


house_coords = get_house_coordinates(city_id, address)
# res = get_general_demand(city_code, service_code, house_coords, year) -> has issues
# print(res)
