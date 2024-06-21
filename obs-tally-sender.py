import obspython as obs
import requests
from threading import Thread
import re

# IP адрес приёмника по умолчанию
TARGET_IP_PROPERTY = '192.168.25.55'

# Цвета в HEX
RED_HEX = 'FF0000'
GREEN_HEX = '00FF00'
WHITE_HEX = 'FFFFFF'

TARGET_SCENE_NAME_PROPERTY = 'HANDYCAM'

def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, TARGET_IP_PROPERTY, "IP адрес приёмника TALLY", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, TARGET_SCENE_NAME_PROPERTY, "Начало имени сцены для которой предназначен сигнал", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_button(props, "", "Проверить подключение", test_connect)

    return props

def script_update(settings):
    global TARGET_IP
    global TARGET_SCENE_NAME

    TARGET_IP = obs.obs_data_get_string(settings, TARGET_IP_PROPERTY)
    TARGET_SCENE_NAME = obs.obs_data_get_string(settings, TARGET_SCENE_NAME_PROPERTY)

def script_defaults(settings):
    obs.obs_data_set_default_string(settings, TARGET_IP_PROPERTY, '192.168.25.55')
    obs.obs_data_set_default_string(settings, TARGET_SCENE_NAME_PROPERTY, 'HANDYCAM')

def handle_event(event):
    global color
    if event is obs.OBS_FRONTEND_EVENT_SCENE_CHANGED:
        # Получение информации о текущей сцене
        get_current_scene = obs.obs_frontend_get_current_scene()
        current_scene = obs.obs_source_get_name(get_current_scene)
        # Получение информации о сцене в окне превью
        get_preview_scene = obs.obs_frontend_get_current_preview_scene()
        preview_scene = obs.obs_source_get_name(get_preview_scene)
        # Проверка на наличие слова HANDYCAM
        #if TARGET_SCENE_NAME in current_scene:
        if re.search(f"^{TARGET_SCENE_NAME}*", current_scene):
            # Присваивание переменной color красного цвета
            color = RED_HEX
            #send_color(RED_HEX)
        #elif TARGET_SCENE_NAME in preview_scene:
        elif re.search(f"^{TARGET_SCENE_NAME}*", preview_scene):
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

def test_connect(props, prop):
    #url = f'http://{TARGET_IP}/set?color={color}'
    #requests.get(url, timeout=2)
    th = Thread(target=send_color, args=(color,))
    th.start()

def send_color(hex_color):
    """Посылка GET запроса с заданным цветом."""
    url = f'http://{TARGET_IP}/set?color={hex_color}'
    obs.script_log(obs.LOG_INFO, url)
    try:
        requests.get(url, timeout=2)
    except:
        obs.script_log(obs.LOG_INFO, f'Нет связи с приёмником {TARGET_IP}...')
    else:
        obs.script_log(obs.LOG_INFO, f'Связь с приёмником {TARGET_IP} установлена...')

obs.obs_frontend_add_event_callback(handle_event)
