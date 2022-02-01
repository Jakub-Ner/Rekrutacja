FROM ubuntu

RUN apt-get update && apt-get -y install  \
    python3 \
    python3-pip

COPY . .
RUN pip install --requirement /requirements.txt

CMD ["python3", "backend/main.py"]
