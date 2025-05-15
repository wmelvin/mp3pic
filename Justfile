@default:
  @just --list

@build: test lint check
  echo 'Run pyproject-build'
  uv build

@check:
  echo 'Run ruff format --check'
  uv run ruff format --check

@clean:
  rm dist/*
  rmdir dist
  rm mp3pic.egg-info/*
  rmdir mp3pic.egg-info

@format:
  echo 'Run ruff format'
  uv run ruff format

@lint:
  echo 'Run ruff check'
  uv run ruff check

@test:
  echo 'Run pytest'
  uv run pytest -vv
