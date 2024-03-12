FROM ubuntu:latest
LABEL authors="Vadym"

ENTRYPOINT ["top", "-b"]