FROM ubuntu:jammy AS ubuntu-base
MAINTAINER Adminka-Root <https://github.com/adminka-root>
EXPOSE 22

RUN apt-get update && \
    apt-get install -y --no-install-suggests --no-install-recommends \
      supervisor \
      openssh-server \
      python3 \
      python3-apt \
      sudo \
      passwd  \
      ansible && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    mkdir -p /run/sshd && \
    apt-get clean && \
    rm -rvf /var/lib/apt/lists/* && \
    rm -vf /etc/ssh/ssh_host_*

ADD entrypoint.sh /entrypoint.sh
RUN useradd -s /bin/sh adminka -d /home/adminka -m && \
    mkdir -p /home/adminka/.ssh && \
    chown adminka:adminka /home/adminka/.ssh && \
    chmod +x entrypoint.sh

ADD supervisord.conf /etc/supervisor/supervisord.conf


ENTRYPOINT ["/entrypoint.sh"]

