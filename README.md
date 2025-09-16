# WP4 Emerald: T4.1 - Trajectory Data / Travel Time Analysis -- Trajectools

<a href="https://codeberg.org/movingpandas/trajectools">
    <img alt="Get it on Codeberg" src="https://get-it-on.codeberg.org/get-it-on-blue-on-white.png" height="60" align="right">
</a>

[![QGIS Plugin Repo](https://img.shields.io/badge/QGIS-Plugin%20repo-green.svg)](https://plugins.qgis.org/plugins/processing_trajectory/)
[![Issue Tracker](https://img.shields.io/badge/Issue_tracker-Codeberg-blue.svg)](https://codeberg.org/movingpandas/trajectools/issues) 
[![Zenodo badge](https://zenodo.org/badge/DOI/10.5281/zenodo.13847642.svg)](https://doi.org/10.5281/zenodo.13847642)

## Description

This repository contains the first version of QGIS Processing Trajectools plugin for the Trajectory Data / Travel Time Analysis Emerald, developed as part of T4.1 of WP4 within EMERALDS project. 
The Trajectools plugin adds trajectory analysis algorithms to the QGIS Processing toolbox. 
This README provides essential information for setting up this Emerald.

Related repositories include:
* [T4.1 - Trajectory Data / Travel Time Analysis -- No-code Model](https://github.com/emeralds-horizon/UC3-traveltime-analytics)
* [T4.1 - Trajectory Data / Travel Time Analysis -- Cartoblog Post](https://github.com/emeralds-horizon/Cartoblog)


## Table of Contents

* [Requirements](#requirements)
* [Examples](#examples)
* [Authors](#authors)
  

## Requirements
Running these models requires QGIS (a popular open source geographic information system) with MovingPandas (a Python library for movement data analysis) and the QGIS Trajectools plugin.

Trajectools requires [MovingPandas](https://github.com/movingpandas/movingpandas) >= 0.22.3 and optionally integrates [scikit-mobility](https://scikit-mobility.github.io/scikit-mobility/) (for privacy tests), [stonesoup](https://stonesoup.readthedocs.io/) (for smoothing), and [gtfs_functions](https://github.com/Bondify/gtfs_functions) (for GTFS data support). 

The recommended way to install these dependencies is through conda/mamba:

```
(base) conda create -n qgis -c conda-forge python=3.11 
(base) conda activate qgis
(qgis) mamba install -c conda-forge qgis movingpandas scikit-mobility stonesoup
(qgis) pip install gtfs_functions h3
```

(More details: https://anitagraser.com/2023/01/21/pyqgis-jupyter-notebooks-on-windows-using-conda/)

### Pip install

If you cannot use conda, you may try installing from the QGIS Python Console:

```
import pip
pip.main(['install', 'movingpandas'])
pip.main(['install', 'scikit-mobility'])
pip.main(['install', 'stonesoup'])
pip.main(['install', 'gtfs_functions'])
```

## Plugin installation

The Trajectools plugin can be installed directly in QGIS using the built-in Plugin Manager:

![plugin manager](https://github.com/movingpandas/qgis-processing-trajectory/assets/590385/edd86ed3-8118-4163-bfe5-993b533e455c)
**Figure 1: QGIS Plugin Manager with Trajectools plugin installed.**

![Trajectools Toolbox](screenshots/toolbox.PNG)
**Figure 2: Trajectools (v2.4) algorithms in the QGIS Processing toolbox**


## Examples
The Trajectools plugin is used in EMERALDS Use Case 3 to analyze travel time on public transport network segments, as documented in [the corresponding repo](https://github.com/emeralds-horizon/UC3-traveltime-analytics).

The individual Trajectools algorithms are flexible and modular and can therefore be used on a wide array on input datasets, including, for example, the open [Microsoft Geolife dataset](http://research.microsoft.com/en-us/downloads/b16d359d-d164-469e-9fd4-daa38f2b2e13/) a [sample](https://github.com/emeralds-horizon/trajectools-qgis/tree/main/sample_data) of which is included in the plugin repo:

![Trajectools Create Trajectory](https://github.com/movingpandas/qgis-processing-trajectory/assets/590385/3040ce90-552e-43a5-8660-17628f9b813a)

![Trajectools Clip Trajectory](screenshots/trajectools2.PNG)

![Trajectools Kalman Filter Smoothing](https://github.com/user-attachments/assets/e3bbf2e5-e551-4f3e-bd29-8d19bdc33137)

![Trajectools GTFS Extract Segments](https://github.com/user-attachments/assets/62a6e60c-dedc-4e90-8059-2679302346db)


## Presentations

[**Trajectools: analyzing anything that moves.** QGIS User Conference 2025, 2-3 June 2025, Norrköping, Sweden.](https://youtu.be/T7haF1DPy2U)

[![Trajectools presentation at QGISUC2025](screenshots/trajectoos-qgisuc25.png)](https://youtu.be/T7haF1DPy2U)


## Authors
AIT

## Citation information

Please cite [0] when using Trajectools in your research and reference the appropriate release version using the Zenodo DOI: https://doi.org/10.5281/zenodo.13847642

[0] [Graser, A., & Dragaschnig, M. (2024, June). Trajectools Demo: Towards No-Code Solutions for Movement Data Analytics. In 2024 25th IEEE International Conference on Mobile Data Management (MDM) (pp. 235-238). IEEE.](https://ieeexplore.ieee.org/abstract/document/10591660)

```
@inproceedings{graser2024trajectools,
  title = {Trajectools Demo: Towards No-Code Solutions for Movement Data Analytics},
  author = {Graser, Anita and Dragaschnig, Melitta},
  booktitle = {2024 25th IEEE International Conference on Mobile Data Management (MDM)},
  pages = {235--238},
  year = {2024},
  organization = {IEEE},
  doi = {10.1109/MDM61037.2024.00048},
}
```
