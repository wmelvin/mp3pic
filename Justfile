@default:
  @just --list

@build: test lint check
  echo 'Run pyproject-build'
  pipenv run pyproject-build

@check:
  echo 'Run ruff format --check'
  pipenv run ruff format --check

@clean:
  rm dist/*
  rmdir dist
  rm mp3pic.egg-info/*
  rmdir mp3pic.egg-info

@format:
  echo 'Run ruff format'
  pipenv run ruff format

@lint:
  echo 'Run ruff check'
  pipenv run ruff check

@test:
  echo 'Run pytest'
  pipenv run pytest -vv
