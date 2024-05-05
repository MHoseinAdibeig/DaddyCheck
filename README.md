[![pipeline status](https://gitlab.etcuniverse.com/seporia/daddy-check/badges/renew/pipeline.svg)](https://gitlab.etcuniverse.com/seporia/daddy-check/-/commits/renew)

[![coverage report](https://gitlab.etcuniverse.com/seporia/daddy-check/badges/renew/coverage.svg)](https://gitlab.etcuniverse.com/seporia/daddy-check/-/commits/renew)

This contains the main code to launch daddy-check server.

Entry point is `/BIM/wsgi.py`.

`daddy_care_server.sock` is the route from nginx to gunicorn service.

flower.sh runs a celery monitoring server
