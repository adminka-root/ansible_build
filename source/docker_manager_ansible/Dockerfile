FROM ubuntu:jammy AS ubuntu-base
MAINTAINER adminka-Root <https://github.com/adminka-root>
EXPOSE 22

ARG USER_NAME=ubuntu
ENV USER_NAME ${USER_NAME}

RUN apt-get update && \
    apt-get install -y --no-install-suggests --no-install-recommends \
      supervisor \
      openssh-server \
      python3 \
      sudo \
      passwd  \
      ansible && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    mkdir -p /run/sshd && \
    apt-get clean && \
    rm -rvf /var/lib/apt/lists/* && \
    rm -vf /etc/ssh/ssh_host_*

ADD entrypoint.sh /entrypoint.sh
RUN useradd \
    --shell=/bin/bash \
    --uid=1000 \
    --groups=sudo \
    ${USER_NAME} && \
    groupmod -g 1001 ${USER_NAME} && \
    mkhomedir_helper ${USER_NAME} && \
    mkdir -p /home/${USER_NAME}/.ssh && \
    chown ${USER_NAME}:${USER_NAME} /home/${USER_NAME}/.ssh && \
    chmod +x entrypoint.sh

ADD supervisord.conf /etc/supervisor/supervisord.conf

ENTRYPOINT ["/entrypoint.sh"]

