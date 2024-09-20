#!/bin/bash

pushd "${VIRTUAL_ENV}/.." > /dev/null

source "${VIRTUAL_ENV}/bin/activate"

python -m black --line-length 100 urlkit tests

python -m pylint --rcfile=pylintrc urlkit tests

python -m mypy --ignore-missing-imports urlkit/ tests/

popd > /dev/null