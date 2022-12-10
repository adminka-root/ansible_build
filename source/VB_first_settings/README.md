# VirtualBox first settings

Подготовительный этап к тестированию ansible на виртуалке.

## Локальная сеть

Первым делом в систему следует установить виртуальный адаптер для сети. Перед этим желательно отключить все активные виртуалки. В VB *Файл* --> *Менеджер сетей хоста* (Ctrl+H) --> *Создать*. DHCP сервер стоит отключить. Во вкладке "*адаптер*" необходимо назначить адрес адаптера. Например, 192.168.56.1.

Помимо *NAT* сети, в настройках конкретной машинки необходимо включить подключение типа "Виртуальный адаптер хоста" и указать созданный на предыдущем шаге адаптер. 

Следующий шаг - назначение статики виртуалке. Т.к. это Linux Mint:

1. Смотрим имя адаптера, которому не назначены настройки сети `ifconfig`. В моем случае - *enp0s8*.

2. `sudo nano /etc/network/interfaces`

   Добавляем строки:

   ```ini
   # The host-only network interface
   auto enp0s8
   iface enp0s8 inet static
   address 192.168.56.100
   netmask 255.255.255.0
   network 192.168.56.1
   broadcast 192.168.56.255
   ```

3. Поднимаем сеть `sudo ifup enp0s8` или просто `reboot`.

После генерации ключа утилитой `ssh-keygen`, необходимо отправить публичный ключ на целевой сервер (виртуалку). Например:

```bash
ssh-copy-id -i ~/.ssh/asus_x751_ln.pub -p 22 adminka@192.168.56.100
```

И произвести подключение:

```bash
ssh -p '22' 'adminka@192.168.56.100'
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

Также установим pip:

```bash
sudo apt install python3-pip  # системный

# ---------- pip для python3.8 ----------
sudo apt install python3.8-distutils
cd /tmp
wget https://bootstrap.pypa.io/get-pip.py
python3.8 get-pip.py

# добавить путь в PATH, если нужно
add_to_PATH=("$HOME/.local/bin")
for path_i in "${add_to_PATH[@]}"; do case ":$PATH:" in *:$path_i:*) echo -e "\nskeep: $path_i already defined";; *) if [[ -d "$path_i" ]]; then echo 'PATH="${PATH:+${PATH}:}'"$path_i"\" >> "$HOME/.profile"; else echo -e "\nskeep: $path_i don't exist"; fi ;; esac; done
source ~/.profile
# ---------------------------------------

# --- Делаем pip3.10 по умолчанию в т.ч. и для нашего юзера ---
whereis pip3  # /usr/bin/pip3 /home/adminka/.local/bin/pip3
whereis pip3.10 # /usr/bin/pip3.10
mv "$HOME/.local/bin/pip3" "$HOME/.local/bin/pip3.backup"

alias update-my-alternatives='update-alternatives --altdir ~/.local/etc/alternatives --admindir ~/.local/var/lib/alternatives'
mkdir -p ~/.local/var/lib/alternatives ~/.local/etc/alternatives
update-my-alternatives --force --install "$HOME/.local/bin/pip3" pip3 "$HOME/.local/bin/pip3.8" 10
update-my-alternatives --install "$HOME/.local/bin/pip3" pip3 /usr/bin/pip3.10  20
update-my-alternatives --query pip3
pip3 -V  # pip 22.0.2 from /usr/lib/python3/dist-packages/pip (python 3.10)

# Примечание: очень даже можно на будущее 
# занести данный алиас в ~/.bashrc
# ---------------------------------------

sys_python="python3.10"
depends="/tmp/system-python-freeze.txt"
python3.10 -m pip list -v | grep -v "$HOME" | grep /usr/lib/python3/dist-packages | awk -F' ' '{ printf "%s==%s\n", $1, $2 }' | tee "$depends"
python3.8 -m pip install --upgrade pip
pip3.8 install -r "$depends"

```

Мало просто установить python3.8. В такой поставке не существует системных модулей, необходимых ansible.  Например, этого

```bash
$ apt content python3-apt | grep /usr/lib/python3/dist-packages/
```

Я столкнулся с проблемой установки python3-apt для python3.8. Далее мои умозоключения (ни факт, что верные). Судя по всему, нужен системный python3.8. Ведь, хоть мы и логинимся под конкретным пользователем, выполняются become команды от root. Соответственно, не подхватываются  dist-packages уровня пользователя. И второе но: даже если удастся писать в системную папку python3.8/dist-packages/ - как доставить python3-apt туда, откуда его взять для python3.8 и будет ли ansible туда заглядывать (вероятно будет)?! Словом, отпуская с чистой совестью эти вопросы, я заключаю, что текущий подход начал смахивать на костыльный. Нужен иной. Мне не нужно менять системы на host-е, устанавливая python3.8 и борясь с проблемами, чтобы ansible завелся. Но и управляющую систему с LM 19.3 на борту менять не хочу. Поэтому в планах - создание docker контейнера, в котором будет ansible с версией, способной управлять машинкой, на которой установлен python3.10. Я просто смонтирую репку в docker-контейнер, а команды буду выполнять, подключившись по ssh.

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
              ansible_host: 192.168.56.100
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

В таком случаи, возможно, будет удобно просто подключаться к виртуалке через ssh ( `ssh -p 22 adminka@192.168.56.100` ) и стартовать графику, когда нужно, простым `switch_tty`.

