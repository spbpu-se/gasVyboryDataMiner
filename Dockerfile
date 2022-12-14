FROM python:3.9

ARG start_date
ARG end_date
ARG level
ARG kafka_ip
ARG kafka_port

ENV start_date=$start_date
ENV end_date=$end_date
ENV level=$level
ENV kafka_ip=$kafka_ip
ENV kafka_port=$kafka_port

COPY . .
RUN  apt-get install tesseract-ocr && apt-get install chromium && pip install -r ./requirements.txt

ENTRYPOINT ["python", "main.py"]
