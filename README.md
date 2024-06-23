# BIAM-Urb

Нужен VPN!

## Собрать образ для пайплайна с RAG и запустить контейнер:

Создать `config.env` в корне проекта:
```
SAIGA_URL=http://10.32.2.2:8671/v1/chat/completions
```

Создать на сервере переменную окружения `$NSS_NPA_TOKEN` (гитхаб токен для пользователя `nss-npa`)

Обновить приложение
```
cd /var/essdata/llm/project/BIAM-Urb
git checkout <required_branch>
git pull

docker container stop llm_city_app-container
docker container rm llm_city_app-container

# use --no-cache key if the entire image needs to be rebuilt (e.g. dependencies changed)
docker build -t llm_city_app [--no-cache] --build-arg NSS_NPA_TOKEN=$NSS_NPA_TOKEN . 
 
docker run -d --restart always -p 9951:80 --name llm_city_app-container llm_city_app
```

## Тестировать пайплайн на сервере:

В терминале отправить запрос:
```
curl -v POST http://10.32.1.34:9951/question -H 'Content-Type: application/json' -d '{"question_body": "Какие проблемы демографического развития Санкт-Петербурга?"}'
```
В браузере:
```
http://10.32.1.34:9951/docs/
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
