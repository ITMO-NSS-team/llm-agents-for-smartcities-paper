# BIAM-Urb

## Собрать образ для пайплайна с RAG и запустить контейнер:

Создать на сервере переменную окружения `$NSS_NPA_TOKEN` (гитхаб токен для пользователя `nss-npa`)

Подтянуть изменения:
```
cd /var/essdata/llm/project-2/BIAM-Urb
git checkout <required_branch>
git pull
```

Создать `config.env` в корне проекта:
```
LLAMA_URL_8b=http://10.32.2.2:8671/v1/chat/completions
LLAMA_URL=http://10.32.15.21:6672/generate
```

Пересобрать образ и запустить контейнер
```
docker container stop llm_city_app-container-agent-checks
docker container rm llm_city_app-container-agent-checks

# use --no-cache key if the entire image needs to be rebuilt (e.g. dependencies changed)
docker build -t llm_city_app-agent-checks [--no-cache] --build-arg NSS_NPA_TOKEN=$NSS_NPA_TOKEN . 
 
docker run -d --restart always -p 9953:80 --name llm_city_app-container-agent-checks llm_city_app-agent-checks
```

## Тестировать пайплайн на сервере:

В терминале отправить запрос:
```
curl -v POST http://10.32.1.34:9951/question -H 'Content-Type: application/json' -d '{"question_body": "Какие проблемы демографического развития Санкт-Петербурга?"}'
```
В браузере:
```
http://10.32.1.34:9951/docs/ - первая версия, где только rag 
http://10.32.1.34:9952/docs/ - вторая версия с агентами
http://10.32.1.34:9953/docs/ - последняя версия с доработками агента
```

## Тестировать апи локально:

Запустить сервер (из корня проекта):
```
fastapi run main.py --proxy-headers --port 80
```

В терминале отправить запрос:
```
curl -v POST http://0.0.0.0:80/question -H 'Content-Type: application/json' -d '{"question_body": "Какие проблемы демографического развития Санкт-Петербурга?"}'
```
В браузере:
```
http://localhost/docs#/
```

## Запустить ChromaDB и модель эмбеддинга на сервере

Скопировать на сервер [compose.yaml](docker/chroma/compose.yaml)

Выполнить команду:
```
docker compose up
```

## Дополнительные материалы
[Task tracker](https://github.com/orgs/ITMO-NSS-team/projects/3)

[Пример для работы с ChromaDB](https://github.com/aimclub/stairs-rag)

[Таблицы с тестовыми вопросами](https://docs.google.com/spreadsheets/d/1FseP8q0kuRyUc4PJWUfR3yzFLmOi8bBplZRQ-H6F3WU/edit?gid=28598507)

[Документ с примерами всех тем/вопросов для сервиса](https://docs.google.com/document/d/1bZWENunwM2j2x67a4yRUagvw3-OiC4zz/edit?pli=1)

[Описание апи 1](https://docs.google.com/document/d/104Cznsoj9RL0iQsDFqz3RGIOYqQDEvZebI-ecmk0CpI/edit)

[Возможные роли с типовыми вопросами](https://docs.google.com/document/d/1DtBHCn04urr_7gJq_X0tQ-hD6yhVBdmj/edit)

[Основное API для доступа к данным по разным территориям](http://10.32.1.107:1244/swagger-ui/#/)

[Основное API для доступа к данным по разным территориям - альтернатива](https://main-api-new.idu.actcognitive.org/swagger-ui/#/)

[API с транспортной доступностью](http://10.32.1.65:5000/docs#/)

[Ещё API с транспортной доступностью](http://10.32.1.42:5000/docs#/)

[Новое API с таблицами](http://10.32.1.42/docs)

[Описание содержимого API с таблицами](https://niuitmo-my.sharepoint.com/:x:/g/personal/412499_niuitmo_ru/EcbagMIPX0BGoiPcPwXMJjsBnP1I0o4mndqqGVi54wmsoA?rtime=qcIb9LKZ3Eg)
