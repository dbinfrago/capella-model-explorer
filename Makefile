# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

STATIC_DIR := static
BUNDLE_DIR := $(STATIC_DIR)/bundle

INPUT_CSS := frontend/input.css
COMPILED_CSS := frontend/compiled.css

CME_MODEL ?=
CME_HOST ?=
CME_PORT ?=
CME_TEMPLATES_DIR ?=
CME_LIVE_MODE ?=
CME_ROUTE_PREFIX ?=
CME_DEBUG_SPINNER ?=

.PHONY: bundle
bundle: $(BUNDLE_DIR) #: Build the app bundle

.PHONY: serve
serve: .venv bundle #: Run a local development server
	.venv/bin/cme run --skip-rebuild --model "$${CME_MODEL:?}"

$(BUNDLE_DIR): node_modules $(COMPILED_CSS) $(shell find frontend -name '*.js' -o -name '*.css')
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
	rm -rf $(BUNDLE_DIR)

.PHONY: really-clean
really-clean: clean #: Remove build artifacts, tools and all data
	rm -rf node_modules .venv

.PHONY: help
help: #: Show this help
	@echo Available make targets:
	@awk '{ if (match($$0, /^([A-Za-z-]+): .*?#: (.*)/, m)) { printf "    %-15s  %s\n", m[1], m[2] } }' Makefile
