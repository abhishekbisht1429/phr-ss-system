FROM ubuntu:20.04

RUN apt-get update
RUN apt-get -y install git

COPY requirements.txt /
RUN apt-get -y install python3
RUN apt-get -y install python3-distutils

# For ubuntu 20.04
RUN apt-get -y install wget
RUN wget "https://bootstrap.pypa.io/get-pip.py" -O "install-pip3-ubuntu.py"
RUN python3 install-pip3-ubuntu.py

## For ubuntu 18.04
#RUN apt-get -y install python3-pip
#RUN python3 -m pip install -U pip
#RUN python3 -m pip install -U setuptools

RUN pip3 install -r requirements.txt


#RUN git clone --depth 1 --branch v1.2.5 https://github.com/hyperledger/sawtooth-sdk-python.git
#RUN python3 sawtooth-sdk-python/bin/protogen
#RUN python3 -m pip install sawtooth-sdk-python/
#RUN rm -rf sawtooth-sdk-python

COPY transaction_processor.py /
COPY transaction_family.py /
COPY constants.py /
COPY util.py /
