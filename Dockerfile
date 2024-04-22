FROM python:3.10.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /panocam

COPY requirements.txt .
COPY packages .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install rknn_toolkit_lite2-1.5.2-cp310-cp310-linux_aarch64.whl
RUN pip install rknn_toolkit2-1.6.0+81f21f4d-cp310-cp310-linux_x86_64.whl

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY . .