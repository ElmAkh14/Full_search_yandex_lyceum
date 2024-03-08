import requests
import sys


apikey = "40d1649f-0493-4b70-98ba-98533de7710b"
geocoder_template = "https://geocode-maps.yandex.ru/1.x/"


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

params = {
    'apikey': apikey,
    'geocode': address_coordinates,
    'kind': 'district',
    'result': 1,
    'format': 'json'
}

response = requests.get(geocoder_template, params)
if not response:
    if_not_response(response)

json_response = response.json()

geoobject = json_response['response']['GeoObjectCollection']['featureMember'][0]
address = geoobject['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']
for dct in address['Components']:
    if dct['kind'] == 'district':
        print(dct['name'])

