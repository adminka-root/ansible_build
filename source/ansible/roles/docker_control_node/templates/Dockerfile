FROM ubuntu:jammy AS ubuntu-base
MAINTAINER Adminka-Root <https://github.com/adminka-root>
EXPOSE 22

ARG USER_NAME={{ hostvars[cn_server]['ansible_user'] }}
ENV USER_NAME ${USER_NAME}
ARG USER_UID={{ hostvars[cn_server]['user']['uid'] }}
ARG USER_GID={{ hostvars[cn_server]['user']['gid'] }}
ARG GIT_REPO_DIR={{ hostvars[cn_server]['docker']['volume']['dest'] }}

RUN apt-get update && \
    apt-get install -y --no-install-suggests --no-install-recommends \
      supervisor \
      openssh-server \
      sshpass \
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
    --uid="${USER_UID}" \
    --groups=sudo \
    ${USER_NAME} && \
    groupmod -g ${USER_GID} ${USER_NAME} && \
    mkhomedir_helper ${USER_NAME} && \
    mkdir -p /home/${USER_NAME}/.ssh && \
    chown ${USER_NAME}:${USER_NAME} /home/${USER_NAME}/.ssh && \
    echo "cd \"${GIT_REPO_DIR}/source/ansible\"" >> /home/${USER_NAME}/.bashrc && \
    chmod +x entrypoint.sh

ADD supervisord.conf /etc/supervisor/supervisord.conf

ENTRYPOINT ["/entrypoint.sh"]

