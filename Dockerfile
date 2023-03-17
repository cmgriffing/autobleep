FROM python:3.10

RUN apt update && \
  apt install portaudio19-dev -y && \
  apt install ffmpeg -y

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "./main.py", "--input=/input/input.mkv", "--output=/output/output.mka" ]