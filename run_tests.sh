#!/bin/bash

pytest --cov=plane_spotter ./tests/
black . --check
mypy .
coverage report 
