#!/usr/bin/env bash

set -euo pipefail

SSH_HOST_RSA_KEY=${SSH_HOST_RSA_KEY:-}
SSH_HOST_RSA_PUBLIC_KEY=${SSH_HOST_RSA_PUBLIC_KEY:-}
SSH_AUTHORIZED_KEY=${SSH_AUTHORIZED_KEY:-}

if [[ -n "${SSH_HOST_RSA_KEY}" ]]; then
  echo "${SSH_HOST_RSA_KEY}" > /home/${USER_NAME}/.ssh/${SSH_HOST_RSA_KEY_NAME}
  chown -R ${USER_NAME}:${USER_NAME} /home/${USER_NAME}/.ssh
  chmod 600 /home/${USER_NAME}/.ssh/${SSH_HOST_RSA_KEY_NAME}
  unset SSH_HOST_RSA_KEY
fi

if [[ ! -f /etc/ssh/ssh_host_rsa_key ]]; then
  ssh-keygen -f /etc/ssh/ssh_host_rsa_key -N '' -t rsa
fi

if [[ -n "${SSH_HOST_RSA_PUBLIC_KEY}" ]]; then
  echo "${SSH_HOST_RSA_PUBLIC_KEY}" > /home/${USER_NAME}/.ssh/${SSH_HOST_RSA_PUBLIC_KEY_NAME}
  chown -R ${USER_NAME}:${USER_NAME} /home/${USER_NAME}/.ssh
  chmod 644 /home/${USER_NAME}/.ssh/${SSH_HOST_RSA_PUBLIC_KEY_NAME}
  unset SSH_HOST_RSA_PUBLIC_KEY
fi

if [[ -n "${SSH_AUTHORIZED_KEY}" ]]; then
  echo "${SSH_AUTHORIZED_KEY}" > /home/${USER_NAME}/.ssh/authorized_keys
  chown -R ${USER_NAME}:${USER_NAME} /home/${USER_NAME}/.ssh
  chmod 0400 /home/${USER_NAME}/.ssh/authorized_keys
  unset SSH_AUTHORIZED_KEY
fi

passwd -d ${USER_NAME}
echo "$(echo -e "${USER_PASSWORD}\n${USER_PASSWORD}")" | sudo passwd ${USER_NAME}
USER_PASSWORD=''

exec supervisord -n -c /etc/supervisor/supervisord.conf
