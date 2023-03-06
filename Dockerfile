FROM python:3

RUN apt update && \
  apt install portaudio19-dev -y && \
  apt install ffmpeg -y

RUN groupadd -g 1024 python
RUN adduser --gid 1024 --disabled-password --gecos "" --force-badname python
USER python

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

CMD [ "python3", "./main.py", "--input=/input/input.mkv", "--output=/output/output.mka" ]