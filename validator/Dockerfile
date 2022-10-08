FROM ubuntu:18.04

RUN apt-get update --fix-missing
RUN apt-get install -y gnupg \
    software-properties-common \
RUN echo "deb http://repo.sawtooth.me/ubuntu/nightly bionic universe" >> /etc/apt/sources.list \
&& (apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 44FC67F19B2466EA \
|| apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 44FC67F19B2466EA) \
&& apt-get update \

#RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD
#RUN add-apt-repository 'deb [arch=amd64] <http://repo.sawtooth.me/ubuntu/chime/stable> bionic universe'
#RUN apt-get update
#RUN apt-get install -y sawtooth \
#    git
#
#COPY requirements.txt /
#RUN apt-get -y install python3 \
#    install python3-distutils

## For ubuntu 20.04
#RUN apt-get -y install wget
#RUN wget "https://bootstrap.pypa.io/get-pip.py" -O "install-pip3-ubuntu.py"
#RUN python3 install-pip3-ubuntu.py

# For ubuntu 18.04
#RUN apt-get -y install python3-pip
#RUN python3 -m pip install -U pip
#RUN python3 -m pip install -U setuptools
#
#RUN pip install -r requirements.txt.txt



#RUN git clone --depth 1 --branch v1.2.5 https://github.com/hyperledger/sawtooth-sdk-python.git
#RUN python3 sawtooth-sdk-python/bin/protogen
#RUN python3 -m pip install sawtooth-sdk-python/
#RUN rm -rf sawtooth-sdk-python

#COPY transaction_processor.py /
#COPY transaction_family.py /
#COPY constants.py /
#COPY util.py /
