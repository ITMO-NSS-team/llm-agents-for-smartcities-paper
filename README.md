# BIAM-Urb

## Собрать образ для пайплайна с RAG и запустить контейнер:

Создать на сервере переменную окружения `$NSS_NPA_TOKEN`

Подтянуть изменения:

```
cd /var/essdata/llm/project/BIAM-Urb
git checkout <required_branch>
git pull
```

Создать `config.env` в корне проекта:

```
LLAMA_URL_8b=<url>
LLAMA_URL=<url>
```

Пересобрать образ и запустить контейнер

```
docker container stop llm_city_app-container
docker container rm llm_city_app-container

# use --no-cache key if the entire image needs to be rebuilt (e.g. dependencies changed)
docker build -t llm_city_app [--no-cache] --build-arg NSS_NPA_TOKEN=$NSS_NPA_TOKEN . 
 
docker run -d --restart always -p <port>:80 --name llm_city_app-container llm_city_app
```

## Тестировать пайплайн на сервере:

В терминале отправить запрос:

```
curl -v POST http://<ip>:<port>/question -H 'Content-Type: application/json' -d '{"question_body": "Какие проблемы демографического развития Санкт-Петербурга?"}'
```

В браузере:

```
http://<ip>:<port>/docs/
```

Логи приложения можно проверить на сервере:

```
docker logs --follow --timestamps llm_city_app-container
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

## Проверка линтером и форматтером `ruff`

Настроена проверка кода при каждом `push`. Если необходимо отключить проверку для отдельных строк кода, в конце каждой
такой строки необходимо добавить комментарий `# noqa`. Это отключит проверку всех правил. Если же нужно отклюить
конкретное, то нужно дописать его название после `# noqa`.

Доступные правила можно найти [здесь](https://docs.astral.sh/ruff/rules/)
