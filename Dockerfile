FROM python:3.10-bullseye
ENV TOKEN ${TOKEN}

# RUN apt-get install -y python3 python3-pip python-dev build-essential python3-venv
ARG DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
WORKDIR /app/
RUN pip3 install -r requirements.txt

COPY . .
CMD python3 ./bot.py
