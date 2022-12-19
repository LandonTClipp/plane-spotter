#!/bin/bash

source ve/bin/activate
pytest --cov=plane_spotter ./tests/
black . --check