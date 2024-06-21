import obspython as obs
import requests
from threading import Thread

# IP адрес приёмника
TARGET_IP = '192.168.25.55'

# Цвета в HEX
RED_HEX = '#FF0000'
GREEN_HEX = '#00FF00'
WHITE_HEX = '#FFFFFF'

def handle_event(event):
    if event is obs.OBS_FRONTEND_EVENT_SCENE_CHANGED:
        # Получение информации о текущей сцене
        get_current_scene = obs.obs_frontend_get_current_scene()
        current_scene = obs.obs_source_get_name(get_current_scene)
        # Получение информации о сцене в окне превью
        get_preview_scene = obs.obs_frontend_get_current_preview_scene()
        preview_scene = obs.obs_source_get_name(get_preview_scene)
        # Проверка на наличие слова HANDYCAM
        if 'HANDYCAM' in current_scene:
            # Присваивание переменной color красного цвета
            color = RED_HEX
            #send_color(RED_HEX)
        elif 'HANDYCAM' in preview_scene:
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

def send_color(hex_color):
    """Посылка GET запроса с заданным цветом."""
    url = f'http://{TARGET_IP}/set?color={hex_color}'
    obs.script_log(obs.LOG_INFO, url)
    try:
        requests.get(url, timeout=2)
    except:
        obs.script_log(obs.LOG_INFO, 'Нет связи с приёмником...')

obs.obs_frontend_add_event_callback(handle_event)
