# Tek container: Python pipeline + Node/Remotion + ffmpeg + rhubarb
FROM node:20-bookworm

# System deps (includes Chromium shared libs required by Remotion headless)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip ffmpeg unzip wget ca-certificates \
    libgl1 libglib2.0-0 \
    libnspr4 libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Rhubarb lip-sync
ARG RHUBARB_VERSION=1.13.0
RUN wget -q "https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v${RHUBARB_VERSION}/Rhubarb-Lip-Sync-${RHUBARB_VERSION}-Linux.zip" -O /tmp/rh.zip \
 && unzip -q /tmp/rh.zip -d /opt \
 && ln -s "/opt/Rhubarb-Lip-Sync-${RHUBARB_VERSION}-Linux/rhubarb" /usr/local/bin/rhubarb \
 && rm /tmp/rh.zip

WORKDIR /app
COPY pipeline/requirements.txt pipeline/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r pipeline/requirements.txt

COPY renderer/package.json renderer/package.json
RUN cd renderer && npm install

COPY . .

# Remotion needs a headless Chromium for rendering; fetch it at build time.
RUN cd renderer && npx remotion browser ensure || true

ENTRYPOINT ["python3", "pipeline/run.py"]
CMD ["--auto"]
