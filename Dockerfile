FROM python:3.9.1

WORKDIR /
COPY . /

RUN pip install --disable-pip-version-check --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --skip-lock

RUN pip install gunicorn[gevent]

ENTRYPOINT [ "/entrypoint.sh" ]
