FROM python:3.10-bullseye
ENV TOKEN ${TOKEN}

# Even need theese?
RUN apt-get update -y && apt-get upgrade -y
# RUN apt-get install -y python3 python3-pip python-dev build-essential python3-venv
RUN apt-get install ffmpeg -y

COPY requirements.txt /app/
WORKDIR /app/
RUN pip install -r requirements.txt

COPY . .
CMD python3 ./bot.py
