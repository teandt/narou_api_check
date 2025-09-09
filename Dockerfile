FROM python:3

ARG UID=1000
ARG GID=1000
ARG USERNAME=dev
ARG GROUPNAME=dev

USER root

RUN apt-get update && \
    apt-get -y --no-install-recommends install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8  

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

#RUN apt-get -y install libgl1-mesa-dev
RUN pip install --upgrade pip
RUN python3 -m pip install pymysql pandas matplotlib requests

RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -u $UID -g $GID $USERNAME

RUN mkdir /code
RUN chown ${UID}:${GID} /code

USER $USERNAME
WORKDIR /code
