# 냉장고 AI — API + UI 공용 이미지
FROM python:3.11-slim-bookworm

WORKDIR /app

# ultralytics(OpenCV) 런타임 의존성
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ api/
COPY core/ core/
COPY ui/ ui/
COPY data/ data/
COPY scripts/ scripts/
COPY best.pt best.pt

ENV PYTHONUNBUFFERED=1 \
    YOLO_WEIGHTS=/app/best.pt

EXPOSE 8000 8501
