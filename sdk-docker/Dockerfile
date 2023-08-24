FROM python:3.9

WORKDIR /fabric

COPY install-fabric.sh install-fabric.sh
RUN ./install-fabric.sh --fabric-version 1.4.12 binary
ENV PATH=${PATH}:/fabric/bin

RUN pip install fabric-sdk-py==1.0.0
RUN pip install protobuf==3.20.0

ENV SETTINGS_DEFAULT "settings/config-docker.json"