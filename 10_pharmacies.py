import requests
from io import BytesIO
import sys
from PIL import Image
from json import dump


search_api_server = "https://search-maps.yandex.ru/v1/"  # запрос API Поиска по организациям
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"  # ключ API Поиска по организациям


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
    "type": "biz",
    "results": 10
}

response = requests.get(search_api_server, params=search_params)
if not response:
    if_not_response(response)

json_response = response.json()
with open('search.json', 'w', encoding='utf-8') as jsn:
    dump(json_response, jsn, ensure_ascii=False)

points_list = []
organizations_list = json_response["features"]
for organization in organizations_list:
    # Получаем координаты ответа.
    point = organization["geometry"]["coordinates"]
    org_point = "{0},{1}".format(point[0], point[1])
    # График работы организации
    org_hours = organization["properties"]["CompanyMetaData"]
    if org_hours.get("Hours"):
        if org_hours["Hours"]["Availabilities"][0].get("TwentyFourHours") is True:
            points_list.append(('pm2dgl', org_point))
        else:
            points_list.append(('pm2dbl', org_point))
    else:
        points_list.append(('pm2grl', org_point))

points_list.append(('pm2rdl', address_coordinates))

# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    # позиционируем карту центром на наш исходный адрес
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": "~".join([f"{x[1]},{x[0]}" for x in points_list])
}

map_api_server = "http://static-maps.yandex.ru/1.x/"  # запрос Static API
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

Image.open(BytesIO(response.content)).show()
