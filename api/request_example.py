from datetime import datetime
from api import Api


def school_demand_example():
    """Какой на данный момент дефицит школьных мест в муниципалитете Волковское?"""

    # Определяем категорию вопроса (вопрос по городским сервисам)
    # ...
    #
    # Определяем текущий год
    current_datetime = datetime.now()
    year = current_datetime.year
    # Вместо циклов здесь и далее гораздо лучше бы справился, например, запрос в MongoDB.
    # Определяем id необходимого типа сервиса (2)
    city_service_types = Api.EndpointsListings.city_service_types()
    for service_type in city_service_types:
        if service_type['name'] == 'Школа':
            service_type_id = service_type['id']
            service_type_code = service_type['code']
            break
    # Определяем id и имя города (1, 'saint-petersburg')
    cities = Api.EndpointsListings.cities(centers_only=True)
    for city in cities:
        if city['name'] == 'Санкт-Петербург':
            city_id = city['id']
            city_code = city['code']
    # Определяем координаты района
    municipalities = Api.EndpointsCity.municipalities(
        city=city_id, centers_only=False)
    for municipality in municipalities:
        if municipality['name'] == 'Волковское':
            # ['coordinates']
            municipality_coordinates = municipality['geometry']
            break
    # Запрашиваем расчёт обеспеченности сервисом по домам
    provision_result = Api.EndpointsProvision.get_provision(
        city=city_code,
        service_types=[service_type_code],
        user_selection_zone=municipality_coordinates,
        year=year,
        calculation_type='linear',  # TODO: remove hardcoded
        valuation_type='normative',  # TODO: remove hardcoded
        service_impotancy=[1],  # TODO: remove deprecated
    )
    houses = provision_result['houses']['features']
    # Вручную суммируем по домам, скольким людям не хватает школьных мест
    demand_left = round(
        sum(map(lambda house: house['properties']['demand_left'], houses)))
    # Формируем текст ответа
    print(
        f"В муниципалитете Волковское не хватает {demand_left} мест в школах.")


if __name__ == "__main__":
    school_demand_example()
