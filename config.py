import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в .env")

# --- Настройки обработки ---
OBSERVE_SECONDS = 15          # сколько секунд смотрим каждую камеру
CONF_THRESHOLD = 0.25         # порог уверенности YOLO
MODEL_PATH = "yolo11n.pt"     # веса, скачаются автоматически при первом запуске
CAMERAS_FILE = "cameras.json" # файл с пользовательскими камерами

# --- Классы COCO, которые нас интересуют ---
VEHICLE_CLASSES = {
    2: "car",
    3: "motorbike",
    5: "bus",
    7: "truck",
}

# --- Коэффициенты выбросов CO2 (граммы на один уникальный транспорт
#     за окно наблюдения OBSERVE_SECONDS).
#     ВАЖНО: очень грубая линейная аппроксимация, не научное измерение.
CO2_PER_VEHICLE_G = {
    "car":   5_440,
    "truck": 65_280,
    "bus":   13_600_000,
    "motorbike": 2_500,
}
