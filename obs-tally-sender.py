# Автор данного произведения Frexirus. :)

import obspython as obs
import requests
from threading import Thread
import re

# IP адрес приёмника по умолчанию
target_ip_property = '192.168.25.55'
# Префикс имени сцен
target_scene_name_property = 'TL'

# Цвета в HEX
RED_HEX = 'FF0000'
GREEN_HEX = '00FF00'
WHITE_HEX = 'FFFFFF'

def script_description():
	return """
	Передача HTTP GET запроса на TALLY приёмник.
	Для тестирования подключения используйте журнал скрипта. 
	В случае, если у вас появляется ошибка при закрытии OBS, 
	попробуйте удалить из имён сцен все пробелы.
	"""


def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, target_ip_property, "IP адрес приёмника TALLY", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_button(props, "", "Проверить подключение", test_connect)
    obs.obs_properties_add_text(props, target_scene_name_property, "Префикс имени сцены для которой предназначен сигнал", obs.OBS_TEXT_DEFAULT)

    return props

def script_update(settings):
    global target_ip
    global target_scene_name

    target_ip = obs.obs_data_get_string(settings, target_ip_property)
    target_scene_name = obs.obs_data_get_string(settings, target_scene_name_property)

def script_defaults(settings):
    obs.obs_data_set_default_string(settings, target_ip_property, '192.168.25.55')
    obs.obs_data_set_default_string(settings, target_scene_name_property, 'TL')

def script_load(settings):
    obs.obs_frontend_add_event_callback(handle_event)

def handle_event(event):
    if event is obs.OBS_FRONTEND_EVENT_PREVIEW_SCENE_CHANGED:
        global color
        # Получение информации о текущей сцене
        get_current_scene = obs.obs_frontend_get_current_scene()
        current_scene = obs.obs_source_get_name(get_current_scene)
        # Получение информации о сцене в окне превью
        get_preview_scene = obs.obs_frontend_get_current_preview_scene()
        preview_scene = obs.obs_source_get_name(get_preview_scene)
        # Проверка на наличие префикса в имени сцены
        #if TARGET_SCENE_NAME in current_scene:
        if re.search(f"^{target_scene_name}*", current_scene):
            # Присваивание переменной color красного цвета
            color = RED_HEX
            #send_color(RED_HEX)
        #elif TARGET_SCENE_NAME in preview_scene:
        elif re.search(f"^{target_scene_name}*", preview_scene):
            # Присваивание переменной color зелёного цвета
            color = GREEN_HEX
            #send_color(GREEN_HEX)
        else:
            # Присваивание переменной color белого цвета
            color = WHITE_HEX
            #send_color(WHITE_HEX)

        # Выделенный поток для отправки GET запроса (Что бы не зависал OBS на время выполнения)
        th = Thread(target=send_color, args=(color,))
        th.start()
        # Просто дебагинг (Логирование)
        obs.script_log(obs.LOG_INFO, 'CURRENT: ' + current_scene)
        obs.script_log(obs.LOG_INFO, 'PREVIEW: ' + preview_scene)

    elif event is obs.OBS_FRONTEND_EVENT_SCRIPTING_SHUTDOWN:
        # Выполнить при завершении работы скрипта (Закрытие OBS)
        th = Thread(target=send_color, args=('000000',))
        th.start()


def test_connect(props, prop):
    th = Thread(target=send_color, args=(color,))
    th.start()

def send_color(hex_color):
    """Посылка GET запроса с заданным цветом."""
    url = f'http://{target_ip}/set?color={hex_color}'
    obs.script_log(obs.LOG_INFO, url)
    try:
        requests.get(url, timeout=2)
    except:
        obs.script_log(obs.LOG_INFO, f'Нет связи с приёмником {target_ip}...')
    else:
        obs.script_log(obs.LOG_INFO, f'Связь с приёмником {target_ip} установлена...')
