#!/bin/bash

pytest --cov=plane_spotter ./tests/
black . --check
coverage report --fail-under=100
