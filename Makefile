VENV=.deploy-venv
PYTHON_FOLDER=$(shell python3 --version | awk '{print tolower($$1$$2)}' | awk 'BEGIN{FS=OFS="."} NF--')
SITE_PACKAGES=$(VENV)/lib/$(PYTHON_FOLDER)/site-packages/
LAMBDA_FUNCTION_NAME=GPXify

# Default target: Display help
help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Targets

build: .clean .venv_setup .install_dependencies .package_files ## Build the project by setting up the environment, installing dependencies, and packaging files.

deploy: ## Deploy the zip file build to AWS.
	aws lambda update-function-code --function-name $(LAMBDA_FUNCTION_NAME) --zip-file fileb://$(LAMBDA_FUNCTION_NAME).zip

.clean: ## Remove existing virtual environments and deployment packages.
	rm -rf $(VENV)
	rm -f $(LAMBDA_FUNCTION_NAME).zip
.venv_setup: ## Set up the virtual environment.
	python3 -m venv $(VENV)

.install_dependencies: ## Install Python dependencies from requirements.txt.
	. $(VENV)/bin/activate; pip install -r requirements.txt

.package_files: ## Package the Python files and dependencies into a deployment package.
	(cd $(SITE_PACKAGES) && zip -r $(LAMBDA_FUNCTION_NAME).zip .)
	mv $(SITE_PACKAGES)/$(LAMBDA_FUNCTION_NAME).zip .
	zip $(LAMBDA_FUNCTION_NAME).zip main.py
