# Репозиторий Ansible_build

Этот репозиторий создан не для массового пользователя, а для моих личных нужд. Почему он оказался в публичном доступе?! Не вижу в этом ничего плохого.

## Проблематика

Миграция со старой уже не поддерживаемой версии ОС (в моем случаи, LM 19.3, который умрет примерно в апреле 2023) на новую версию несет в себе много боли. За 5 лет использования моя система обросла рядом особенностей, которые с одной стороны, хотелось бы сохранить, но проблематично. Ведь обновление LM на пару мажорных версий несет в себе кучу головной боли, которая ни факт, что закончится приемлемо. Кроме того, хотелось бы точно знать: а чем моя система отличается от базового образа? При классической разработке программисты используют систему контроля версий, а когда речь заходит об ОС - как контролировать и запомнить действительно важные удобные изменения?

## Цель

Цель данного репозитория состоит в документировании изменений в системе через средства автоматизации. Я буду использовать *bash*, *python* и *ansible*. В конечном счете я хочу получить модульный продукт, который будет автоматически применять настройки, устанавливать нужные программы, редактировать конфиги и т.п. Таким образом, скачав и установив базовый образ ОС LM, я смогу быстро его настроить до идеального по-моему мнению состояния.