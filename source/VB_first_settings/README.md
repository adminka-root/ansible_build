# VirtualBox first settings

Подготовительный этап к тестированию ansible на виртуалке.

## Локальная сеть

Помимо *NAT* сети, в VB необходимо включить подключение типа "*Сетевой мост*". Утилитой `ifconfig` на реальной машине можно посмотреть имя выбираемого адаптера. Ей же в виртуалке можно подсмотреть ip-шник виртуалки в локальной сети и добавить в **hosts.yml**.

> Примечание: на данном этапе я не рассматриваю вопрос статичного адреса. Возможно в будущем это может оказаться проблемой.

После генерации ключа утилитой `ssh-keygen`, необходимо отправить публичный ключ на целевой сервер (виртуалку). Например:

```bash
ssh-copy-id -i ~/.ssh/asus_x751_ln.pub -p 22 adminka@192.168.1.103
```

И произвести подключение:

```bash
ssh -p '22' 'adminka@192.168.1.103'
```

## SSH

Вероятно, эти пакеты будут полезны на виртуалке и в управляющей системе:

```bash
sudo apt install -y ssh openssh-server
```

## Ansible

Т.к. моя версия ansible [не удовлетворяла](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#node-requirement-summary) целевому python, на виртуалке доустановил python3.8:

```bash
sudo apt update
sudo apt install -y dirmngr ca-certificates software-properties-common gnupg gnupg2 apt-transport-https

sudo mkdir -p /root/.gnupg
sudo chmod 700 /root/.gnupg

sudo gpg --no-default-keyring --keyring /usr/share/keyrings/deadsnakes.gpg --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776

sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.8
```

В таком случаи можно указать явно используемый интерпретатор для всей группы *virtual_box* в файле *hosts.yml* :

```yaml
all:
  children:
    local:
      hosts:
        asus_x751_ln:  # alias
          ansible_host: 127.0.0.1
          ansible_port: 40002
      children:
        virtual_box:
          hosts:
            linux_mint_19_2_beta:
              ansible_host: 192.168.1.103
              ansible_port: 22
          vars:
            ansible_python_interpreter: /usr/bin/python3.8
      vars:
        ansible_ssh_private_key_file: /home/adminka/.ssh/asus_x751_ln
```

В *ansible.cfg*:

```ini
[defaults]
host_key_checking = false
inventory         = ./hosts.yml
```

И проверить:

```bash
$ ansible virtual_box -m ping
linux_mint_19_2_beta | SUCCESS => {
    "changed": false, 
    "ping": "pong"
}
```

## TTY (примечание)

Возможен вариант использования, при котором происходит отключение графического окружения. Например, скрипт **switch_tty.sh** для Linux Mint 21.1 :

```bash
if [[ "$(service lightdm status | grep Active | awk -F ' ' '{print $2}')" == "active" ]]; then
    sudo chvt 1
    sudo service lightdm stop
else
    sudo service lightdm start
fi
```

```bash
# Путь до скрипта
head="/home/adminka/Рабочий стол/ansible_build/source/VB_first_settings"
script="switch_tty.sh"  # Название скрипта
sub="/usr/local/bin/"  # Куда создаем симлинк

sudo chown root:root "$head/$script"
sudo ln -s "$head/$script" "$sub/${script%.*}"
source ~/.bashrc
```

Для полного отключения при загрузке:

```bash
sudo systemctl disable lightdm
```

В таком случаи, возможно, будет удобно просто подключаться к виртуалке через ssh ( `ssh -p 22 adminka@192.168.1.103` ) и стартовать графику, когда нужно, простым `switch_tty`.

