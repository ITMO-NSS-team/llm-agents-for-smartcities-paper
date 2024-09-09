FROM python:3.10

WORKDIR /code
ARG NSS_NPA_TOKEN
ARG LOG_PATH=/var/essdata/llm/log/biam-urb/:/var/log/biam_urb/
ENV LOG_PATH=$LOG_PATH

COPY ./requirements.txt /code/requirements.txt
RUN git config --global url."https://$NSS_NPA_TOKEN@github".insteadOf https://github && \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /code/

VOLUME $LOG_PATH

CMD ["fastapi", "run", "/code/main.py", "--proxy-headers", "--port", "80"]