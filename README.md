# LLM Agents for Smart City Management: Enhancing Decision Support through Multi-Agent AI Systems

The repository contains code and data for the LLM-based city management research.

## Build an image for the Pipeline with RAG and start the container:

Create the `$NSS_NPA_TOKEN` environment variable on the server

Pull changes:

```
cd /var/essdata/llm/project/BIAM-Urb
git checkout <required_branch>
git pull
```

Create `config.env` in the root of the project:

```
LLAMA_URL=<url>
LLAMA_FC_URL=<url>
ENDPOINT_LISTINGS_URL=<url>
ENDPOINT_CITY_URL=<url>
ENDPOINT_METRICS_URL=<url>
ENDPOINT_PROVISION_URL=<url>
ENDPOINT_TABLES_URL=<url>
```

Rebuild the image and run the container

```
docker container stop llm_city_app-container
docker container rm llm_city_app-container

# use --no-cache key if the entire image needs to be rebuilt (e.g. dependencies changed)
docker build -t llm_city_app --build-arg NSS_NPA_TOKEN=$NSS_NPA_TOKEN -f docker/app/Dockerfile --no-cache .
 
docker run -d --restart always -p <port>:80 --name llm_city_app-container llm_city_app
```

## Test the Pipeline on the server:

In the terminal, send a request:
```
curl -v POST http://<ip>:<port>/question -H 'Content-Type: application/json' -d '{"question_body": "What are the problems of demographic development of St. Petersburg?"}'
```

In the browser:

```
http://<ip>:<port>/docs/
```

The application logs can be checked on the server:

```
docker logs --follow --timestamps llm_city_app-container
```

## Test api locally:

Start the server (from the project root):

```
fastapi run main.py --proxy-headers --port 80
```

In the terminal, send a query:

```
curl -v POST http://0.0.0.0:80/question -H ‘Content-Type: application/json’ -d ‘{’question_body‘: “What are the problems of demographic development of St. Petersburg?”}’
```

In the browser:

```
http://localhost/docs#/
```

## Run ChromaDB and the embedding model on the server

Copy [compose.yaml](docker/chroma/compose.yaml) to the server

Execute the command:

```
docker compose up
```