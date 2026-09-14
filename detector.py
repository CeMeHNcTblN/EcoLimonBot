import cv2
import time
import logging
from dataclasses import dataclass, field
from ultralytics import YOLO

from config import VEHICLE_CLASSES, CONF_THRESHOLD, MODEL_PATH, CO2_PER_VEHICLE_G

log = logging.getLogger(__name__)


@dataclass
class CameraResult:
    name: str
    counts: dict = field(default_factory=dict)
    error: str | None = None

    @property
    def total_co2_g(self) -> float:
        return sum(self.counts.get(k, 0) * v for k, v in CO2_PER_VEHICLE_G.items())


# Загружаем модель один раз при импорте
log.info("Загружаю модель %s…", MODEL_PATH)
_model = YOLO(MODEL_PATH)
log.info("Модель готова")


def process_camera(name: str, url: str, seconds: int) -> CameraResult:
    """Смотрит в камеру N секунд, считает УНИКАЛЬНЫЕ машины через ByteTrack."""
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        log.warning("Камера %s не открылась: %s", name, url)
        return CameraResult(name=name, error="поток недоступен")

    seen_ids: dict[int, str] = {}
    deadline = time.time() + seconds
    frames = 0

    try:
        while time.time() < deadline:
            ok, frame = cap.read()
            if not ok:
                log.warning("Камера %s: кадр не получен", name)
                break

            results = _model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                conf=CONF_THRESHOLD,
                classes=list(VEHICLE_CLASSES.keys()),
                verbose=False,
            )

            if results and results[0].boxes.id is not None:
                for box in results[0].boxes:
                    tid = int(box.id)
                    cls_id = int(box.cls)
                    seen_ids[tid] = VEHICLE_CLASSES.get(cls_id, "unknown")

            frames += 1
    finally:
        cap.release()

    counts: dict[str, int] = {}
    for label in seen_ids.values():
        counts[label] = counts.get(label, 0) + 1

    log.info("Камера %s: кадров=%d, уникальных=%s", name, frames, counts)
    return CameraResult(name=name, counts=counts)
