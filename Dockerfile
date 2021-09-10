FROM python:3.8.2

WORKDIR openvino-client/

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python-pip libi2c-dev python-dev python-smbus i2c-tools
RUN python2 -m pip install tentacle_pi RPi.GPIO

RUN python3 -m pip install pyserial requests mysql-connector-python pycryptodome
RUN python3 -m pip --no-cache-dir install bloock==1.0.0

COPY weather-station .
COPY forwarder.py .
COPY wait-for-it.sh .

CMD ./wait-for-it.sh -t 0 database:3306 -- python3 -u forwarder.py
