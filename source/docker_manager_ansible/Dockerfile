FROM ubuntu:jammy AS ubuntu-base
MAINTAINER adminka-Root <https://github.com/adminka-root>
EXPOSE 22

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
    ubuntu && \
    groupmod -g 1001 ubuntu && \
    mkhomedir_helper ubuntu && \
    mkdir -p /home/ubuntu/.ssh && \
    chown ubuntu:ubuntu /home/ubuntu/.ssh && \
    chmod +x entrypoint.sh

ADD supervisord.conf /etc/supervisor/supervisord.conf


ENTRYPOINT ["/entrypoint.sh"]

