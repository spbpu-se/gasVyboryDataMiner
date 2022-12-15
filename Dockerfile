FROM python:3.9

ARG start_date
ARG end_date
ARG level
ARG mongo_ip
ARG mongo_port

ENV start_date=$start_date
ENV end_date=$end_date
ENV level=$level
ENV kafka_ip=$kafka_ip
ENV kafka_port=$kafka_port

COPY . .
RUN  apt-get -y update && apt-get -y install tesseract-ocr && apt-get -y install chromium && pip install -r ./requirements.txt

ENTRYPOINT ["python", "main.py"]
