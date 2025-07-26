#!/usr/bin/bash

alembic revision --autogenerate -m "Initial revision"
alembic upgrade head
