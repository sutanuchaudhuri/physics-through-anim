SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help setup sync health list render render-rolling stitch-rolling render-rod \
        stitch-rod render-lesson stitch-lesson compile stitch-compilation \
        list-compilations publish-prepare publish-complete list-publications \
        test check clean

# ---------------------------------------------------------------------------
# Self-documenting help: every target with a `## description` is listed below.
# Override variables on the command line, e.g.
#   make render-rolling SCENE=III QUALITY=high NARRATION=auto
# Variables (with defaults): QUALITY=low  NARRATION=auto  SCENE=all
# ---------------------------------------------------------------------------
help: ## Show this help (all targets and their descriptions)
	@echo "physics-through-anim — make targets"
	@echo "Usage: make <target> [VAR=value ...]"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Common variables: QUALITY={low|medium|high}  NARRATION={off|auto|required}  SCENE=<id|chapter|all>"

setup: ## Install Python 3.12 and sync dependencies (first-time setup)
	uv python install 3.12
	uv sync --extra dev

sync: ## Sync dependencies from uv.lock
	uv sync --extra dev

health: ## Verify Manim + LaTeX + dvisvgm are working
	uv run manim checkhealth

list: ## List planned topics and their scene names
	@uv run python main.py list

render: ## Render a foundations topic (TOPIC=vectors QUALITY= NARRATION=)
	uv run python main.py render $(TOPIC) --quality $(or $(QUALITY),low) --narration $(or $(NARRATION),auto)

render-rolling: ## Render the rolling/slipping lesson (SCENE=all|<id>|<chapter>)
	uv run python main.py render-rolling $(or $(SCENE),all) --quality $(or $(QUALITY),low) --narration $(or $(NARRATION),auto)

stitch-rolling: ## Stitch rendered rolling/slipping scenes into the final video
	uv run python main.py stitch-rolling --quality $(or $(QUALITY),low)

render-rod: ## Render the rod-slipping lesson (SCENE=all|<id>|<chapter>)
	uv run python main.py render-rod $(or $(SCENE),all) --quality $(or $(QUALITY),low) --narration $(or $(NARRATION),auto)

stitch-rod: ## Stitch rendered rod-slipping scenes into the final video
	uv run python main.py stitch-rod --quality $(or $(QUALITY),low)

render-lesson: ## Render any lesson in lessons.toml (LESSON=<name> SCENE=all|<id>)
	uv run python main.py render-lesson $(LESSON) $(or $(SCENE),all) --quality $(or $(QUALITY),low) --narration $(or $(NARRATION),auto)

stitch-lesson: ## Stitch any lesson in lessons.toml (LESSON=<name>)
	uv run python main.py stitch-lesson $(LESSON) --quality $(or $(QUALITY),low)

compile: ## Build a named, arbitrary-order compilation (LESSON= SCENES= NAME=)
	uv run python main.py compile $(LESSON) $(SCENES) --name $(NAME) --quality $(or $(QUALITY),low) --narration $(or $(NARRATION),auto)

stitch-compilation: ## Rebuild a defined compilation from compilations.toml (NAME=<name>)
	uv run python main.py stitch-compilation $(NAME) --quality $(or $(QUALITY),low)

list-compilations: ## List all defined compilations and their scenes
	@uv run python main.py list-compilations

publish-prepare: ## Persist a pending publish record (SOURCE= TITLE= DESCRIPTION=)
	uv run python main.py publish-prepare $(SOURCE) --title "$(TITLE)" --description "$(DESCRIPTION)" --tags "$(or $(TAGS),)" --visibility $(or $(VISIBILITY),unlisted) --slug "$(or $(SLUG),)" --quality $(or $(QUALITY),high)

publish-complete: ## Record a completed upload's video id/URL (SLUG= VIDEO_ID= URL=)
	uv run python main.py publish-complete $(SLUG) --video-id $(VIDEO_ID) --url $(URL)

list-publications: ## List all publish records and their status
	@uv run python main.py list-publications

test: ## Run the test suite
	uv run pytest -q

check: ## Lint (ruff) and run tests
	uv run ruff check .
	uv run pytest -q

clean: ## Remove rendered media, caches, and draft audio
	rm -rf media .pytest_cache .ruff_cache .mypy_cache assets/audio/*.wav
