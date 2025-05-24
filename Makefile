# Improved Makefile for running pytest with QGIS environment and packaging plugin

# --- Configuration: Define Python Paths ---
# These paths are based on your original Makefile.
# Modify them if your QGIS installation or Python environment differs.

# Path to the QGIS application resources
QGIS_APP_RESOURCES_PATH := /Applications/MacPorts/QGIS3.app/Contents/Resources
# System Python site-packages (ensure this matches your Python version)
# Example: /opt/local/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages
# Or for a virtual environment: /path/to/your/venv/lib/pythonX.Y/site-packages
SYSTEM_SITE_PACKAGES := /opt/local/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages


# QGIS core Python libraries
QGIS_PYTHON_DIR := $(QGIS_APP_RESOURCES_PATH)/python

# QGIS plugins directory (often needed for processing tools)
QGIS_PLUGINS_DIR := $(QGIS_APP_RESOURCES_PATH)/python/plugins


# --- Plugin Configuration ---
PLUGIN_NAME := trajectools
# Assuming PLUGIN_SRC_DIR contains metadata.txt
PLUGIN_SRC_DIR := .
_METADATA_FILE := $(PLUGIN_SRC_DIR)/metadata.txt

# Robustly extract version from metadata.txt, remove quotes and whitespace
_RAW_VERSION := $(shell if [ -f "$(_METADATA_FILE)" ]; then grep -m1 -E "version\s*=" "$(_METADATA_FILE)" 2>/dev/null | sed -e 's/.*version\s*=\s*//' -e 's/"//g' -e "s/'//g" | tr -d '[:space:]\r\n' ; fi)
ifeq ($(_RAW_VERSION),)
    PLUGIN_VERSION := dev
else
    PLUGIN_VERSION := $(_RAW_VERSION)
endif


REQUIREMENTS_FILE := $(PLUGIN_SRC_DIR)/requirements.txt

# --- Build Configuration ---
BUILD_DIR := ./build
PACKAGE_TEMP_DIR := $(BUILD_DIR)/$(PLUGIN_NAME)_package_temp
# Ensure ZIP_FILE uses PLUGIN_NAME and PLUGIN_VERSION if available
ifeq ($(PLUGIN_VERSION),dev)
	ZIP_FILE_NAME := $(PLUGIN_NAME).zip
else
	ZIP_FILE_NAME := $(PLUGIN_NAME)_v$(PLUGIN_VERSION).zip
endif
ZIP_FILE := ./$(ZIP_FILE_NAME)


# --- PYTHONPATH Construction ---
# This section constructs the PYTHONPATH string for testing.
# It will include QGIS Python dir, QGIS plugins dir, and system site-packages.
# It also appends these to any existing PYTHONPATH from your environment.

ADDITIONAL_PYTHONPATH := $(QGIS_PYTHON_DIR)
ADDITIONAL_PYTHONPATH := $(ADDITIONAL_PYTHONPATH):$(QGIS_PLUGINS_DIR)
ADDITIONAL_PYTHONPATH := $(ADDITIONAL_PYTHONPATH):$(SYSTEM_SITE_PACKAGES)

ifeq ($(strip $(PYTHONPATH)),)
  export PYTHONPATH := $(ADDITIONAL_PYTHONPATH)
else
  export PYTHONPATH := $(PYTHONPATH):$(ADDITIONAL_PYTHONPATH)
endif


# --- Phony Targets ---
# Declare targets that are not actual files.
.PHONY: all test package clean clean_pycache help


# --- Main Targets ---

# Default target: running 'make' without arguments will execute 'make all'
all: test

# Test target: runs pytest
test:
	@echo "Setting up Python environment for QGIS..."
	@echo "PYTHONPATH is being set to:"
	@echo "$$PYTHONPATH" # Use $$PYTHONPATH to print the environment variable value in the shell
	@echo "Running tests..."
	pytest

# Package target: creates a zip file of the plugin with dependencies
package:
	@echo "Packaging plugin: $(PLUGIN_NAME)..."
	# Clean up previous package attempts
	rm -rf $(PACKAGE_TEMP_DIR) "$(ZIP_FILE)" # Quote ZIP_FILE in case version creates tricky names
	# Create temporary structure for packaging
	mkdir -p "$(PACKAGE_TEMP_DIR)/$(PLUGIN_NAME)" # Quote paths

	# Copy plugin source code from PLUGIN_SRC_DIR.
	# If PLUGIN_SRC_DIR is ".", this copies files from the current directory.
	@echo "Copying plugin source files from $(PLUGIN_SRC_DIR) to $(PACKAGE_TEMP_DIR)/$(PLUGIN_NAME)/"
	# Using rsync for more control over exclusions
	# Add more exclusions if needed (e.g., .venv/, README.md)
	rsync -a \
		--exclude='.git*' \
		--exclude='__pycache__' \
		--exclude='*.pyc' \
		--exclude='*.pyo' \
		--exclude='.pytest_cache' \
		--exclude='build/' \
		--exclude='*.zip' \
		--exclude='Makefile' \
		"$(PLUGIN_SRC_DIR)/" "$(PACKAGE_TEMP_DIR)/$(PLUGIN_NAME)/" # Quote source/dest

	# Install dependencies from requirements.txt if it exists, using a shell conditional
	# Removing @ from echos below for debugging the shell error
	if [ -f "$(REQUIREMENTS_FILE)" ]; then \
		echo "Found $(REQUIREMENTS_FILE), installing dependencies with --no-deps..."; \
		mkdir -p "$(PACKAGE_TEMP_DIR)/$(PLUGIN_NAME)/libs"; \
		pip install --no-cache-dir --no-deps -r "$(REQUIREMENTS_FILE)" \
			-t "$(PACKAGE_TEMP_DIR)/$(PLUGIN_NAME)/libs" --upgrade; \
		echo "Dependencies installed into $(PACKAGE_TEMP_DIR)/$(PLUGIN_NAME)/libs/"; \
	else \
		echo "No $(REQUIREMENTS_FILE) found, skipping dependency installation."; \
	fi

	# Create the zip file
	@echo "Creating zip file: $(ZIP_FILE)..."
	cd "$(PACKAGE_TEMP_DIR)" && zip -rq "../../$(ZIP_FILE_NAME)" "$(PLUGIN_NAME)" # Quote paths/names

	# Clean up temporary packaging directory
	rm -rf "$(PACKAGE_TEMP_DIR)" # Quote path
	@echo "Plugin packaged successfully: $(ZIP_FILE)"

# Clean target: removes Python cache files, pytest cache, build artifacts, and zip files
clean: clean_pycache
	@echo "Cleaning build directory and zip files..."
	rm -rf "$(BUILD_DIR)" # Quote path
	rm -f ./*.zip # Removes zip files in the current directory
	@echo "Build directory and zip files cleaned."

clean_pycache:
	@echo "Cleaning Python cache files (__pycache__, *.pyc, *.pyo)..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	@echo "Cleaning pytest cache (.pytest_cache)..."
	rm -rf .pytest_cache
	@echo "Cleaning coverage data (.coverage)..."
	rm -rf .coverage
	@echo "Cache cleaning complete."

# Help target: displays useful information about the Makefile targets
help:
	@echo "Available targets:"
	@echo "  all           - Runs the default target (test)."
	@echo "  test          - Sets up PYTHONPATH and runs pytest."
	@echo "  package       - Packages the '$(PLUGIN_NAME)' plugin into '$(ZIP_FILE_NAME)'."
	@echo "                  Dependencies from '$(REQUIREMENTS_FILE)' (if found) will be included in a 'libs' folder using --no-deps."
	@echo "                  Plugin source is taken from '$(PLUGIN_SRC_DIR)'."
	@echo "  clean         - Removes Python cache, pytest cache, build artifacts, and .zip files."
	@echo "  clean_pycache - Removes Python cache files, pytest cache, and coverage data."
	@echo "  help          - Displays this help message."
	@echo ""
	@echo "Configuration for Testing:"
	@echo "  QGIS_PYTHON_DIR       : $(QGIS_PYTHON_DIR)"
	@echo "  QGIS_PLUGINS_DIR      : $(QGIS_PLUGINS_DIR)"
	@echo "  SYSTEM_SITE_PACKAGES  : $(SYSTEM_SITE_PACKAGES)"
	@echo "  Current PYTHONPATH will be: [Existing PYTHONPATH (if any)]$(if $(PYTHONPATH),:)$(ADDITIONAL_PYTHONPATH)"
	@echo ""
	@echo "Configuration for Packaging:"
	@echo "  PLUGIN_NAME           : $(PLUGIN_NAME)"
	@echo "  PLUGIN_VERSION        : $(PLUGIN_VERSION) (extracted from $(_METADATA_FILE), defaults to 'dev')"
	@echo "  PLUGIN_SRC_DIR        : $(PLUGIN_SRC_DIR)"
	@echo "  REQUIREMENTS_FILE     : $(REQUIREMENTS_FILE)"
	@echo "  ZIP_FILE              : $(ZIP_FILE)"
	@echo "  BUILD_DIR             : $(BUILD_DIR)"
