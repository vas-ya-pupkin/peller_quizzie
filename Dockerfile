FROM python:3.7-alpine

RUN apk add build-base libffi-dev
RUN apk add --virtual build-deps musl-dev && \
    apk add --no-cache --update postgresql-dev

RUN pip3 install -U setuptools

ARG APP_DIR=quiz
WORKDIR ${APP_DIR}

COPY requirements.txt /${APP_DIR}/
RUN pip3 install -r requirements.txt

COPY run.py /${APP_DIR}/
RUN mkdir -p app/
COPY ./app/ /${APP_DIR}/app/

EXPOSE 8000

# CMD ["pytest", "app/tests.py"]
CMD ["python3", "run.py"]
