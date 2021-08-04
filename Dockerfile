FROM python:3.9.1
RUN pip install --upgrade pip
RUN pip install pipenv
WORKDIR /
COPY . /
RUN pipenv install --system --skip-lock
RUN pip install gunicorn[gevent]
ENTRYPOINT [ "/entrypoint.sh" ]
