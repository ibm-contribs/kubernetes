FROM debian:jessie

ADD join_cluster.py /
RUN chmod +x join_cluster.py

RUN apt-get update \
    && apt-get -y install python python-pip dnsutils \
    && apt-get autoclean \
    && apt-get autoremove

RUN pip install requests

WORKDIR /

ENTRYPOINT ["/bin/bash",  "-c",  "trap : TERM INT; sleep infinity & wait"]