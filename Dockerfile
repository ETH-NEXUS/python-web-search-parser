FROM python:3.9.1

WORKDIR /
COPY . /

RUN adduser user
USER user
ENV PATH="$PATH:/home/user/.local/bin"

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --skip-lock

RUN pip install gunicorn[gevent]
ENTRYPOINT [ "/entrypoint.sh" ]
