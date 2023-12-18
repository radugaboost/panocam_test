FROM python:3.10.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /panocam

COPY requirements.txt .
COPY packages .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install rknn_*.whl

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY . .