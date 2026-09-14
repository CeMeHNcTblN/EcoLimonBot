# 🌱 EcoLIMON — Universal CO₂ Estimator for Traffic Cameras

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![YOLO](https://img.shields.io/badge/Ultralytics-YOLO11-orange)
![Tracker](https://img.shields.io/badge/Tracker-ByteTrack-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A Telegram bot that estimates CO₂ emissions from road traffic by analyzing **any camera stream you give it** — RTSP, HTTP, HLS, or a local video file. Powered by **YOLO11** object detection and **ByteTrack** multi-object tracking.

> ⚠️ **Disclaimer:** rough estimation, not a scientific measurement. See [Limitations](#-limitations).

---

## ✨ Features

- 📹 **Bring your own cameras** — add RTSP / HTTP / HLS streams or local files via the bot
- 🎯 **YOLO11 detection** — only vehicle classes (car, motorbike, bus, truck)
- 🔁 **ByteTrack tracking** — counts *unique* vehicles, not frame-by-frame detections
- 🌍 **CO₂ estimation** — per-class emission coefficients
- 🤖 **Telegram interface** — add, list, remove cameras and run analysis without editing code
- 💾 **Per-user storage** — each user has their own camera list (`cameras.json`)
- ⚙️ **Config-driven** — thresholds and coefficients live in `config.py`

---

## 🏗️ Architecture

```
Telegram user
     │  /addcam, /listcams, /co2
     ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   bot.py     │──▶│ detector.py  │──▶│  config.py   │
│  (Telebot)   │   │ YOLO+ByteTrack│   │ thresholds   │
└──────┬───────┘   └──────────────┘   └──────────────┘
       │
       ▼
┌──────────────┐
│ storage.py   │  cameras.json (per chat_id)
└──────────────┘
```

**Pipeline per camera:**
1. Open the stream with OpenCV (`cv2.VideoCapture`)
2. Run `YOLO11.track()` with ByteTrack for N seconds
3. Collect unique `track_id` → vehicle class
4. Multiply by coefficients → estimated grams of CO₂
5. Return per-camera and grand totals to Telegram

---

## 🚀 Quick Start

### 1. Clone

```bash
git clone https://github.com/<your-username>/eco-limon.git
cd eco-limon
```

### 2. Virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate     # Linux / macOS
# .venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get a Telegram bot token

- Open [@BotFather](https://t.me/BotFather)
- `/newbot` → copy the token

### 5. Configure `.env`

```bash
cp .env.example .env
```

Edit `.env`:

```env
BOT_TOKEN=your_bot_token_here
```

### 6. Run

```bash
python bot.py
```

Open your bot in Telegram and send `/start`.

---

## 🤖 Bot Commands

| Command | Description |
|---|---|
| `/start` `/help` | Show help and examples |
| `/addcam <name> <url>` | Add a camera |
| `/listcams` | List your cameras (credentials are hidden) |
| `/removecam <name>` | Remove a camera |
| `/co2` | Run analysis over all your cameras |

### Supported URL formats

- `rtsp://user:pass@192.168.1.10:554/stream`
- `http://example.com/traffic.m3u8` (HLS)
- `https://example.com/video.mp4`
- `/absolute/path/to/local.mp4` (local file)

### Example session

```
/addcam highway https://example.com/highway.m3u8
/addcam parking rtsp://admin:pass@192.168.1.5:554/Streaming/Channels/101
/co2
```

---

## 📂 Project Structure

```
eco-limon/
├── .env                 # BOT_TOKEN (gitignored)
├── .env.example
├── .gitignore
├── requirements.txt
├── config.py            # thresholds, coefficients
├── storage.py           # per-user camera storage
├── detector.py          # YOLO + ByteTrack wrapper
├── bot.py               # Telegram entrypoint
├── cameras.json         # auto-created, gitignored
└── README.md
```

---

## ⚙️ Configuration

| Variable | Description | Default |
|---|---|---|
| `OBSERVE_SECONDS` | how long to watch each camera | `15` |
| `CONF_THRESHOLD` | YOLO confidence threshold | `0.25` |
| `MODEL_PATH` | Ultralytics weights | `yolo11n.pt` |
| `CO2_PER_VEHICLE_G` | grams of CO₂ per unique vehicle | see `config.py` |

---

## 🧪 How CO₂ Is Calculated

```
total_co2 = Σ (unique_vehicles[class] × CO2_PER_VEHICLE_G[class])
```

**Linear approximation.** Real emissions depend on fuel type, engine size, speed, idle time, and time-on-camera.

---

## ⚠️ Limitations

- **Not scientifically accurate.** Coefficients are rough averages.
- **Stream availability** depends on the source; geoblocked or expired streams will fail gracefully.
- **Weather & lighting** reduce YOLO accuracy (rain, night, glare).
- **Occlusion** may cause ByteTrack to lose a vehicle and create a new `track_id`, slightly over-counting.
- **No ROI masking** — vehicles outside the road (parking lots, side streets) are also counted.
- **Short streams** (`< OBSERVE_SECONDS`) produce lower counts.

---

## 🛣️ Roadmap

- [ ] ROI polygon per camera
- [ ] SQLite storage for historical analytics
- [ ] Per-camera custom CO₂ coefficients
- [ ] Web dashboard (FastAPI + Chart.js)
- [ ] Docker image
- [ ] Optional screenshot with bounding boxes returned to Telegram

---

## 🧰 Tech Stack

- [Ultralytics YOLO11](https://github.com/ultralytics/ultralytics) — detection
- [ByteTrack](https://github.com/ifzhang/ByteTrack) — multi-object tracking (built into Ultralytics)
- [OpenCV](https://opencv.org/) — stream capture
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) — Telegram interface
- [python-dotenv](https://github.com/theskumar/python-dotenv) — secrets management

---

## 📜 License

MIT — see [LICENSE](LICENSE).

---
---

# 🌱 EcoLIMON — универсальный расчёт CO₂ по камерам

Telegram-бот, который оценивает выбросы CO₂ от дорожного трафика, анализируя **любой видеопоток, который вы ему дадите** — RTSP, HTTP, HLS или локальный файл. Работает на **YOLO11** и трекере **ByteTrack**.

> ⚠️ **Дисклеймер:** это грубая оценка, а не научное измерение. Подробности — в разделе [Ограничения](#-ограничения-1).

---

## ✨ Возможности

- 📹 **Свои камеры** — добавляй RTSP / HTTP / HLS потоки или локальные файлы прямо через бота
- 🎯 **Детекция YOLO11** — только классы транспорта (car, motorbike, bus, truck)
- 🔁 **Трекинг ByteTrack** — считаются *уникальные* машины, а не детекции по кадрам
- 🌍 **Оценка CO₂** — коэффициенты выбросов по классам
- 🤖 **Telegram-интерфейс** — добавляй, смотри и удаляй камеры без редактирования кода
- 💾 **Хранилище по пользователям** — у каждого свой список камер (`cameras.json`)
- ⚙️ **Конфиг вместо хардкода** — пороги и коэффициенты в `config.py`

---

## 🏗️ Архитектура

```
Пользователь Telegram
     │  /addcam, /listcams, /co2
     ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   bot.py     │──▶│ detector.py  │──▶│  config.py   │
│  (Telebot)   │   │ YOLO+ByteTrack│   │ пороги, CO₂  │
└──────┬───────┘   └──────────────┘   └──────────────┘
       │
       ▼
┌──────────────┐
│ storage.py   │  cameras.json (по chat_id)
└──────────────┘
```

**Пайплайн для каждой камеры:**
1. Открываем поток через OpenCV
2. Крутим `YOLO11.track()` с ByteTrack N секунд
3. Собираем уникальные `track_id` → класс
4. Умножаем на коэффициенты → граммы CO₂
5. Отправляем отчёт в Telegram

---

## 🚀 Быстрый старт

### 1. Клонировать

```bash
git clone https://github.com/<твой-ник>/eco-limon.git
cd eco-limon
```

### 2. Виртуальное окружение

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Получить токен бота

- [@BotFather](https://t.me/BotFather) → `/newbot` → скопировать токен

### 5. Создать `.env`

```bash
cp .env.example .env
```

И вписать токен:

```env
BOT_TOKEN=твой_токен
```

### 6. Запустить

```bash
python bot.py
```

Открой бота в Telegram и отправь `/start`.

---

## 🤖 Команды бота

| Команда | Описание |
|---|---|
| `/start` `/help` | Помощь и примеры |
| `/addcam <имя> <url>` | Добавить камеру |
| `/listcams` | Список камер (креды скрыты) |
| `/removecam <имя>` | Удалить камеру |
| `/co2` | Запустить анализ по всем камерам |

### Поддерживаемые форматы URL

- `rtsp://user:pass@192.168.1.10:554/stream`
- `http://example.com/traffic.m3u8` (HLS)
- `https://example.com/video.mp4`
- `/абсолютный/путь/к/файлу.mp4`

### Пример сессии

```
/addcam highway https://example.com/highway.m3u8
/addcam parking rtsp://admin:pass@192.168.1.5:554/Streaming/Channels/101
/co2
```

---

## 📂 Структура проекта

```
eco-limon/
├── .env                 # BOT_TOKEN (в .gitignore)
├── .env.example
├── .gitignore
├── requirements.txt
├── config.py
├── storage.py
├── detector.py
├── bot.py
├── cameras.json         # создаётся сам, в .gitignore
└── README.md
```

---

## ⚙️ Конфигурация

| Переменная | Описание | По умолчанию |
|---|---|---|
| `OBSERVE_SECONDS` | сколько секунд смотреть камеру | `15` |
| `CONF_THRESHOLD` | порог уверенности YOLO | `0.25` |
| `MODEL_PATH` | веса Ultralytics | `yolo11n.pt` |
| `CO2_PER_VEHICLE_G` | граммы CO₂ на уникальный транспорт | см. `config.py` |

---

## 🧪 Как считается CO₂

```
total_co2 = Σ (уникальные_машины[класс] × CO2_PER_VEHICLE_G[класс])
```

**Линейная аппроксимация.** Реальные выбросы зависят от типа топлива, объёма двигателя, скорости и времени простоя.

---

## ⚠️ Ограничения

- **Не научно точно.** Коэффициенты — средние.
- **Доступность потока** зависит от источника; геоблокированные или устаревшие ссылки корректно обрабатываются с ошибкой.
- **Погода и освещение** снижают точность YOLO.
- **Перекрытия** могут приводить к потере трека и небольшому завышению счёта.
- **Нет ROI-маски** — машины вне дороги тоже считаются.
- **Короткие потоки** (< `OBSERVE_SECONDS`) дают заниженный счёт.

---

## 🛣️ Планы

- [ ] ROI-полигон для каждой камеры
- [ ] SQLite для исторической аналитики
- [ ] Отдельные коэффициенты CO₂ для каждой камеры
- [ ] Веб-дашборд (FastAPI + Chart.js)
- [ ] Docker-образ
- [ ] Отправка скриншота с bbox в Telegram

---

## 🧰 Стек

- [Ultralytics YOLO11](https://github.com/ultralytics/ultralytics) — детекция
- [ByteTrack](https://github.com/ifzhang/ByteTrack) — трекинг (встроен в Ultralytics)
- [OpenCV](https://opencv.org/) — захват потока
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) — Telegram
- [python-dotenv](https://github.com/theskumar/python-dotenv) — секреты

---

## 📜 Лицензия

MIT — см. [LICENSE](LICENSE).
