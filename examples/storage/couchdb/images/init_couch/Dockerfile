FROM debian:jessie

ADD configer_couch.sh /
RUN chmod +x configer_couch.sh

WORKDIR /

ENTRYPOINT ["/bin/bash",  "-c",  "trap : TERM INT; sleep infinity & wait"]
