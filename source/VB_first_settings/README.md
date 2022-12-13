# VirtualBox first settings

Подготовительный этап к тестированию ansible на виртуалке.

<< НАПИШИ РОЛЬ ДЛЯ ОТПРАВКИ КЛЮЧА, ВКЛ/ВЫКЛ lightdm >>

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
      vars:
        ansible_user: adminka
        ansible_port: 22
        orig_private_key: "~/.ssh/asus_x751_ln"
        orig_public_key: "~/.ssh/asus_x751_ln.pub"
        ansible_ssh_private_key_file: "~/.ssh/asus_x751_ln"
        ansible_python_interpreter: /usr/bin/python3
        ansible_become_pass: 'pass'
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

