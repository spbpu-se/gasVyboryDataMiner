FROM joyzoursky/python-chromedriver:3.9

ARG start_date
ARG end_date
ARG level
ARG mongo_ip
ARG mongo_port
ARG mongo_usr
ARG mongo_pwd

ENV start_date=$start_date
ENV end_date=$end_date
ENV level=$level
ENV mongo_ip=$mongo_ip
ENV mongo_port=$mongo_port
ENV mongo_usr=$mongo_usr
ENV mongo_pwd=$mongo_pwd

COPY . .
RUN  apt-get -y update && apt-get -y install tesseract-ocr && pip install -r ./requirements.txt

ENTRYPOINT ["python", "main.py"]
