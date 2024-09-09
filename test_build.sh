#!/bin/bash

function clear_host_machine() {
  docker stop test_llm_city_app_container
  docker rm test_llm_city_app_container
  docker rmi test_llm_city_app
}

docker build \
  -t test_llm_city_app \
  --build-arg NSS_NPA_TOKEN=$NSS_NPA_TOKEN \
  --build-arg LOG_PATH=logs_biam_urb:/var/log/biam_urb/ \
  -f docker/app/Dockerfile \
  --no-cache .

if [ $? -ne 0 ]; then
  echo "Error: Docker container build failed."
  exit 1
fi

docker run -d --restart always -p 5000:80 --name test_llm_city_app_container test_llm_city_app

sleep 30

curl -f http://localhost:5000/build_test -H "Content-Type:application/json" || {
  echo "Error: The application did not start correctly."
  docker logs test_llm_city_app_container
  clear_host_machine
  exit 1
}

echo "The application has been successfully launched and is available."
clear_host_machine