FROM python:3.9

ARG start_date
ARG end_date
ARG level

ENV start_date=$start_date
ENV end_date=$end_date
ENV level=$level

COPY . .
RUN  apk -i add tesseract-ocr && apk -i add chromium && pip install -r ./requirements.txt

ENTRYPOINT ["python", "main.py"]
