#!/usr/bin/env bash

if [ ${DEBUG} ]; then
  ./pwsp.py
else
  gunicorn --worker-class gevent --workers 8 --bind ${PWSP_HOST}:${PWSP_PORT} "pwsp:gunicorn()" --max-requests 10000 --timeout 30 --keep-alive 5 --log-level info --log-file -
fi