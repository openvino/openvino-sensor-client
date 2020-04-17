FROM python:3.8.2

WORKDIR openvino-client/

COPY weather-station .
COPY forwarder.py .

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python-pip libi2c-dev python-dev python-smbus i2c-tools
RUN python2 -m pip install tentacle_pi RPi.GPIO

RUN python3 -m pip install pyserial
#RUN python3 -m pip install requirements.txt

CMD python3 -u forwarder.py





