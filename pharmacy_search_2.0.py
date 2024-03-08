import requests
from io import BytesIO
import sys
from PIL import Image
from json import dump
import math


search_api_server = "https://search-maps.yandex.ru/v1/"  # запрос API Поиска по организациям
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"  # ключ API Поиска по организациям


def lonlat_distance(a, b):
    """Функция, считающая расстояние между двумя точками, заданными координатами"""
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_latitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_latitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


def if_not_response(resp: requests.Response) -> None:
    """Функция выполняется при неверном запросе"""
    print('Ошибка выполнения запроса:')
    print(resp.url)
    print('Http статус:', resp.status_code, '(' + resp.reason + ')')
    sys.exit(1)


def find_address_coordinates(addr: str) -> str:
    """Функция вычисляет координаты точки по адресу"""
    apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
    geocoder_template = "https://geocode-maps.yandex.ru/1.x/"
    params = {'apikey': apikey, 'geocode': addr, 'lang': 'ru_RU', 'format': 'json'}
    resp = requests.get(geocoder_template, params=params)
    if resp:
        jsn_response = resp.json()
        geoobject = jsn_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
        coordinates = geoobject['Point']['pos']
        return ','.join(coordinates.split(' '))
    else:
        if_not_response(resp)


# Вычисление координат введённого адреса
address = " ".join(sys.argv[1:])
address_coordinates = find_address_coordinates(address)

# Параметры для API Поиска по организациям
search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_coordinates,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    if_not_response(response)

json_response = response.json()
with open('search.json', 'w', encoding='utf-8') as jsn:
    dump(json_response, jsn, ensure_ascii=False)

# Получаем первую найденную организацию.
organization = json_response["features"][0]
# Название организации.
org_name = organization["properties"]["CompanyMetaData"]["name"]
print(org_name)
# Адрес организации.
org_address = organization["properties"]["CompanyMetaData"]["address"]
print(org_address)
# График работы организации
org_hours = organization["properties"]["CompanyMetaData"]["Hours"]["text"]
print(org_hours)

# Получаем координаты ответа.
point = organization["geometry"]["coordinates"]
org_point = "{0},{1}".format(point[0], point[1])
print('Расстояние -', round(lonlat_distance([float(x) for x in address_coordinates.split(',')],
                            [float(x) for x in org_point.split(',')])), 'метров')

# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    # позиционируем карту центром на наш исходный адрес
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": "{0},pm2dgl~{1},pm2dbl".format(org_point, address_coordinates)
}

map_api_server = "http://static-maps.yandex.ru/1.x/"  # запрос Static API
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

Image.open(BytesIO(response.content)).show()
