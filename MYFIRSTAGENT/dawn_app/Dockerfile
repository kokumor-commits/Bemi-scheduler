FROM python:3.11-slim

# ffmpeg + fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000
CMD ["python", "main.py"]
