import sys
from io import BytesIO
import requests
from PIL import Image


def find_parameters_for_map(json_resp, l='map'):
    # Получаем первый топоним из ответа геокодера.
    toponym = json_resp["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_latitude = toponym_coodrinates.split(" ")
    # Протяженность объекта в градусах
    lowerCorner = [float(x) for x in toponym["boundedBy"]["Envelope"]["lowerCorner"].split(" ")]
    upperCorner = [float(x) for x in toponym["boundedBy"]["Envelope"]["upperCorner"].split(" ")]
    longitude_corner = upperCorner[0] - lowerCorner[0]
    latitude_corner = upperCorner[1] - lowerCorner[1]

    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        "ll": ",".join([toponym_longitude, toponym_latitude]),
        "spn": ",".join([str(longitude_corner), str(latitude_corner)]),
        "l": l
    }
    return map_params


toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    print('Ошибка выполнения запроса:')
    print(response.url)
    print('Http статус:', response.status_code, '(' + response.reason + ')')
    sys.exit(1)

# Преобразуем ответ в json-объект
json_response = response.json()

# Создаём словарь с параметрами
map_params = find_parameters_for_map(json_response)
map_params['pt'] = map_params['ll'] + ",pm2ntm45",

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)

Image.open(BytesIO(
    response.content)).show()
# Создадим картинку
# и тут же ее покажем встроенным просмотрщиком операционной системы
