
## Тестовое задание  
[Описание](https://unwinddigital.notion.site/Python-1fdcee22ef5345cf82b058c333818c08)  


## Описание  
[Ссылка на google таблицу](https://docs.google.com/spreadsheets/d/12tn4_zbwp7IrdHNRyeoqaqg0E_d8q6CqF5icuGkPhjo/edit#gid=0)  



### Запуск проекта

- Переход в папку с файлом docker-compose.yml
```
cd deploy
```

- Создание образов
```
docker-compose build
```

- Запуск контейнеров
```
docker-compose up -d
```

- Подключение к запущенному контейнеру
```
docker exec -it test_kanalservis_service_1 /bin/bash
```

- Создание таблицы в БД
```
cd /test_kanalservis/shared/database
python db_engine.py
```

- Запуск скрипта загрузки данных
```
cd /test_kanalservis
python main.py
```

### Проверка данных, хранящихся в БД  

- Подключение к запущенному контейнеру с БД
```
docker exec -it test_kanalservis_db_1 /bin/bash
```
- Подключение к БД
```
psql -U postgres
\c test_kanalservis
```
- Выполнение запроса получения данных
```
SELECT * FROM public.order;
```