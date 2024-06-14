FROM python:3.10

WORKDIR /code
ARG NSS_NPA_TOKEN

COPY ./requirements.txt /code/requirements.txt
RUN git config --global url."https://$NSS_NPA_TOKEN@github".insteadOf https://github && \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /code/

CMD ["fastapi", "run", "/code/main.py", "--proxy-headers", "--port", "80"]