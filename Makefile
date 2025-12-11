# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

STATIC_DIR := static
BUNDLE_DIR := $(STATIC_DIR)/bundle

INPUT_CSS := frontend/input.css
COMPILED_CSS := frontend/compiled.css

SOURCE_DIRS := frontend capella_model_explorer
CSS_FILES := $(shell find $(SOURCE_DIRS) -name '*.css')
JS_FILES := $(shell find $(SOURCE_DIRS) -name '*.js')
PY_FILES := $(shell find $(SOURCE_DIRS) -name '*.py')

export CME_MODEL ?= $(CAPELLA_MODEL)
CME_HOST ?=
CME_PORT ?=
CME_TEMPLATES_DIR ?=
CME_ROUTE_PREFIX ?=
CME_WATCH_BUNDLE ?=
CME_DEBUG_SPINNER ?=

.PHONY: bundle
bundle: $(BUNDLE_DIR) #: Build the app bundle

.PHONY: serve
serve: .venv bundle #: Run the server locally
	.venv/bin/cme run --skip-rebuild --model "$${CME_MODEL:?}"

.PHONY: dev
dev: .venv bundle #: Run a local development server
	.venv/bin/cme dev --model "$${CME_MODEL:?}"

$(BUNDLE_DIR): node_modules $(COMPILED_CSS) $(CSS_FILES) $(JS_FILES) $(PY_FILES)
	rm -rf $@
	pnpm exec tailwindcss --input frontend/input.css --output frontend/compiled.css
	pnpm exec parcel build frontend/app.js --dist-dir $@

node_modules: package.json pnpm-lock.yaml
	pnpm install --frozen-lockfile
	touch -c $@

.venv: pyproject.toml uv.lock
	uv sync --inexact
	touch -c $@

.PHONY: pretty format
format: pretty
pretty: .venv node_modules #: Run code auto-formatters
	.venv/bin/pre-commit run --all-files prettier ||:
	.venv/bin/pre-commit run --all-files ruff-format ||:

.PHONY: lint
lint: node_modules .venv #: Run all formatters and linters
	.venv/bin/pre-commit run --all-files

.PHONY: clean
clean: #: Remove build artifacts
	rm -rf $(COMPILED_CSS) $(BUNDLE_DIR)

.PHONY: really-clean
really-clean: clean #: Remove build artifacts, tools and all data
	rm -rf node_modules .venv

.PHONY: help
help: #: Show this help
	@echo Available make targets:
	@awk '{ if (match($$0, /^([A-Za-z-]+): .*?#: (.*)/, m)) { printf "    %-15s  %s\n", m[1], m[2] } }' Makefile
