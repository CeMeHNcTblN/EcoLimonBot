import logging
import telebot
from telebot import apihelper

from config import BOT_TOKEN, OBSERVE_SECONDS
from detector import process_camera
from storage import get_cameras, add_camera, remove_camera

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN)

HELP_TEXT = (
    "🌱 *EcoLIMON* — расчёт углеродного следа по камерам\n\n"
    "Я подключаюсь к видеопотокам (RTSP / MP4 / HTTP), распознаю "
    "транспорт с помощью YOLO11 + ByteTrack и оцениваю выброс CO₂.\n\n"
    "*Команды:*\n"
    "`/addcam <имя> <url>` — добавить камеру\n"
    "`/listcams` — список камер\n"
    "`/removecam <имя>` — удалить камеру\n"
    "`/co2` — запустить анализ по всем камерам\n"
    "`/help` — это сообщение\n\n"
    "*Примеры URL:*\n"
    "• `rtsp://user:pass@192.168.1.10:554/stream`\n"
    "• `https://example.com/traffic.m3u8`\n"
    "• `/content/test.mp4` (локальный файл)\n"
)


@bot.message_handler(commands=["start", "help"])
def cmd_start(message):
    bot.send_message(message.chat.id, HELP_TEXT, parse_mode="Markdown")


@bot.message_handler(commands=["addcam"])
def cmd_addcam(message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "Формат: `/addcam <имя> <url>`", parse_mode="Markdown")
        return

    _, name, url = parts
    name = name.strip()
    url = url.strip()

    if not name or not url:
        bot.reply_to(message, "Имя и URL не могут быть пустыми.")
        return

    add_camera(message.chat.id, name, url)
    bot.reply_to(message, f"✅ Камера `{name}` добавлена.", parse_mode="Markdown")


@bot.message_handler(commands=["listcams"])
def cmd_listcams(message):
    cams = get_cameras(message.chat.id)
    if not cams:
        bot.reply_to(message, "Список пуст. Добавь камеру: `/addcam <имя> <url>`", parse_mode="Markdown")
        return

    lines = ["📷 *Твои камеры:*", ""]
    for name, url in cams.items():
        # Прячем учётные данные, если они есть в URL
        safe_url = url
        if "@" in url and "://" in url:
            scheme, rest = url.split("://", 1)
            safe_url = f"{scheme}://***@{rest.split('@', 1)[1]}"
        lines.append(f"• `{name}` — {safe_url}")
    bot.reply_to(message, "\n".join(lines), parse_mode="Markdown")


@bot.message_handler(commands=["removecam"])
def cmd_removecam(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Формат: `/removecam <имя>`", parse_mode="Markdown")
        return

    name = parts[1].strip()
    if remove_camera(message.chat.id, name):
        bot.reply_to(message, f"🗑 Камера `{name}` удалена.", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"Камера `{name}` не найдена.", parse_mode="Markdown")


@bot.message_handler(commands=["co2"])
def cmd_co2(message):
    cams = get_cameras(message.chat.id)
    if not cams:
        bot.reply_to(message, "Сначала добавь хотя бы одну камеру: `/addcam <имя> <url>`", parse_mode="Markdown")
        return

    total = len(cams)
    eta = total * OBSERVE_SECONDS
    bot.send_message(
        message.chat.id,
        f"🔍 Запускаю анализ {total} камер(ы). Примерное время: ~{eta} сек.",
    )

    results = []
    for i, (name, url) in enumerate(cams.items(), 1):
        bot.send_message(
            message.chat.id,
            f"📷 Камера {i}/{total}: `{name}`…",
            parse_mode="Markdown",
        )
        results.append(process_camera(name, url, OBSERVE_SECONDS))

    bot.send_message(message.chat.id, _format_report(results), parse_mode="Markdown")


def _format_report(results) -> str:
    lines = ["📊 *Отчёт по камерам*", ""]
    grand_total = 0.0
    grand_counts = {"car": 0, "truck": 0, "bus": 0, "motorbike": 0}

    for r in results:
        if r.error:
            lines.append(f"*{r.name}*: ⚠️ {r.error}")
            continue

        co2 = r.total_co2_g
        grand_total += co2
        for k in grand_counts:
            grand_counts[k] += r.counts.get(k, 0)

        lines.append(
            f"*{r.name}*: 🚗 {r.counts.get('car',0)} | "
            f"🚚 {r.counts.get('truck',0)} | "
            f"🚌 {r.counts.get('bus',0)} | "
            f"🏍 {r.counts.get('motorbike',0)} "
            f"→ ~{co2/1000:.1f} кг CO₂"
        )

    lines.append("")
    lines.append(
        f"🌍 *Итого:* 🚗 {grand_counts['car']} | "
        f"🚚 {grand_counts['truck']} | "
        f"🚌 {grand_counts['bus']} | "
        f"🏍 {grand_counts['motorbike']}"
    )
    lines.append(f"💨 *Общий выброс:* ~{grand_total/1000:.1f} кг CO₂")
    lines.append("")
    lines.append("_Учтены уникальные машины (ByteTrack). Оценка приблизительная._")
    return "\n".join(lines)


if __name__ == "__main__":
    log.info("Бот запущен")
    bot.infinity_polling()
