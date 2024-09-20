#!/bin/bash

python -m pytest tests --cov=urlkit --cov-report html --cov-report xml --doctest-modules --junitxml=junit/test-results.xml