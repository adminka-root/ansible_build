# docker_control_node

Роль применяет изменения к **real_system** для узла **cn_server**, переданного как параметр из основного playbook.

## Опции

Поддерживаемые опции (имя | значение по умолчанию):

1. **start** | false

   Запуск контейнера.

2. **stop** | false

   Остановка контейнера.

3. **restart** | false

   Перезапуск контейнера.

4. **rebuild** | false

   Удаление ранее построенных контейнеров, образа, привязки томов, построение, поднятие.

5. **drop_node** | false

   Удаление ранее построенных контейнеров, образа, привязки томов.

## Запуск

Для первого построения и поднятия пишем:

```bash
ansible-playbook <имя_playbook-а_реализующего роль> -e "rebuild=true"
```

Например,

```bash
ansible-playbook docker_control_node.yml -e "rebuild=true"
```

Тогда, для подключения по ssh к контейнеру:

```bash
# общий случай
# ssh ansible_user@ansible_host -p ansible_port

# control_node
ssh adminka@192.168.55.100 -p 22
```

И т.д.