FROM debian:stretch-slim

WORKDIR /home/flagification

RUN apt-get update && \
    apt-get -y install socat python3 python3-pip

COPY app/requirements.txt .
RUN pip3 install -r /home/flagification/requirements.txt

CMD python3 ./main.py