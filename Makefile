# Improved Makefile for running pytest with QGIS environment

# --- Configuration: Define Python Paths ---
# These paths are based on your original Makefile.
# Modify them if your QGIS installation or Python environment differs.

# Path to the QGIS application resources
QGIS_APP_RESOURCES_PATH := /Applications/MacPorts/QGIS3.app/Contents/Resources

# QGIS core Python libraries
QGIS_PYTHON_DIR := $(QGIS_APP_RESOURCES_PATH)/python

# QGIS plugins directory (often needed for processing tools)
QGIS_PLUGINS_DIR := $(QGIS_APP_RESOURCES_PATH)/python/plugins

# System Python site-packages (ensure this matches your Python version)
# Example: /opt/local/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages
# Or for a virtual environment: /path/to/your/venv/lib/pythonX.Y/site-packages
SYSTEM_SITE_PACKAGES := /opt/local/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages


# --- PYTHONPATH Construction ---
# This section constructs the PYTHONPATH string.
# It will include QGIS Python dir, QGIS plugins dir, and system site-packages.
# It also appends these to any existing PYTHONPATH from your environment.

# Concatenate the paths to be added
# The order is: QGIS Python, QGIS Plugins, System Site Packages.
# This order ensures that QGIS's Python environment is prioritized if there are conflicts,
# followed by plugins, and then general site-packages.
ADDITIONAL_PYTHONPATH := $(QGIS_PYTHON_DIR)
ADDITIONAL_PYTHONPATH := $(ADDITIONAL_PYTHONPATH):$(QGIS_PLUGINS_DIR)
ADDITIONAL_PYTHONPATH := $(ADDITIONAL_PYTHONPATH):$(SYSTEM_SITE_PACKAGES)

# Export the full PYTHONPATH.
# If the environment's PYTHONPATH is currently empty, use our ADDITIONAL_PYTHONPATH directly.
# Otherwise, append ADDITIONAL_PYTHONPATH to the existing PYTHONPATH, separated by a colon.
ifeq ($(strip $(PYTHONPATH)),)
  export PYTHONPATH := $(ADDITIONAL_PYTHONPATH)
else
  export PYTHONPATH := $(PYTHONPATH):$(ADDITIONAL_PYTHONPATH)
endif


# --- Phony Targets ---
# Declare targets that are not actual files. This prevents conflicts if a file
# with the same name as a target (e.g., "test") exists.
.PHONY: all test clean clean_pycache help


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

# Clean target: removes Python cache files and pytest cache
# Useful for ensuring a clean test run.
clean_pycache:
	@echo "Cleaning Python cache files (__pycache__, *.pyc)..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete # Also remove optimized .pyo files
	@echo "Cleaning pytest cache (.pytest_cache)..."
	rm -rf .pytest_cache
	@echo "Cleaning coverage data (.coverage)..."
	rm -rf .coverage
	@echo "Cache cleaning complete."

# Alias 'clean' to 'clean_pycache' for convenience
clean: clean_pycache

# Help target: displays useful information about the Makefile targets
help:
	@echo "Available targets:"
	@echo "  all           - Runs the default target (test)."
	@echo "  test          - Sets up PYTHONPATH and runs pytest."
	@echo "  clean         - Removes Python cache files, pytest cache, and coverage data."
	@echo "  clean_pycache - Alias for clean."
	@echo "  help          - Displays this help message."
	@echo ""
	@echo "Configuration:"
	@echo "  QGIS_PYTHON_DIR       : $(QGIS_PYTHON_DIR)"
	@echo "  QGIS_PLUGINS_DIR      : $(QGIS_PLUGINS_DIR)"
	@echo "  SYSTEM_SITE_PACKAGES  : $(SYSTEM_SITE_PACKAGES)"
	@echo "  Current PYTHONPATH will be: [Existing PYTHONPATH (if any)]$(if $(PYTHONPATH),:)$(ADDITIONAL_PYTHONPATH)"
