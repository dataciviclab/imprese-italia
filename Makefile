# Imprese Italia — Makefile
TOOLKIT = toolkit
export TOOLKIT_ALLOW_SCRIPT_SOURCE = 1

DATASETS := $(shell find datasets -name dataset.yml 2>/dev/null | sort)

.PHONY: check run run-all clean test help

check:
	@for f in $(DATASETS); do \
		echo "→ $$f"; \
		$(TOOLKIT) run preflight --config "$$f" > /dev/null 2>&1 || exit 1; \
	done
	@echo "✅ All configs valid"

run:
	$(TOOLKIT) run

run-all:
	@find datasets -name dataset.yml | sort > batch.txt; \
	$(TOOLKIT) run --batch batch.txt

test:
	python3 -m pytest tests/ -v

clean:
	rm -rf out/data/_runs out/data/probe out/data/raw out/data/clean out/data/mart .tmp/ batch.txt

.PHONY: registry registry-write
registry:
	$(TOOLKIT) registry build --prefix imprese-italia

registry-write:
	$(TOOLKIT) registry build --prefix imprese-italia --write

help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sort
