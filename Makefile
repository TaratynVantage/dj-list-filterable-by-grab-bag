
.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'

.PHONY: dc-down-delete-volumes
dc-down-delete-volumes:  ## docker compose down and delete any docker volumes used to persist the DB
	docker compose down -v

.PHONY: dc-down
dc-down: ## docker compose down (leave volumes alone)
	docker compose down

.PHONY: dc-up
dc-up:  ## docker compose up (detached)
	docker compose up -d

.PHONY: dc-full-reset
dc-full-reset: dc-down-delete-volumes dc-up  ## Fully reset the system with a fresh
	echo "System restored."

.PHONY: container-migrate
container-migrate: dc-up  ## Run the migration inside the app container
	docker compose exec web uv run manage.py migrate

.PHONY: container-shell
container-shell: dc-up
	docker compose exec web bash

.PHONY: container-generate-test-file
container-generate-test-file: dc-up
	docker compose exec web uv run manage.py generate_property_csv --properties 10 --columns 10_000 --output generated_data.ignore.csv

.PHONY: container-import-test-file
container-import-test-file: container-migrate container-generate-test-file
	echo "This can take a while..."
	docker compose exec web uv run manage.py import_property_csv generated_data.ignore.csv
	echo "Finally."
