# WP4: T4.1 - Trajectory Data / Travel Time Analysis -- Trajectools

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

The recommended way to install these dependencies is through conda/mamba:

```
(base) conda create -n qgis -c conda-forge python=3.9 
(base) conda activate qgis
(qgis) mamba install -c conda-forge qgis movingpandas
```

(More details: https://anitagraser.com/2023/01/21/pyqgis-jupyter-notebooks-on-windows-using-conda/)

The Trajectools plugin can be installed directly in QGIS using the built-in Plugin Manager:

![image](https://github.com/emeralds-horizon/UC3-traveltime-analytics/assets/590385/9f6cdb53-f2b3-4f2f-82cf-923d3b61341f)

**Figure 1: QGIS Plugin Manager with Trajectools plugin installed.**


## Examples
The Trajectools plugin is used in EMERALDS Use Case 3 to analyze travel time on public transport network segments, as documented in [the corresponding repo](https://github.com/emeralds-horizon/UC3-traveltime-analytics).

The individual Trajectools algorithms are flexible and modular and can therefore be used on a wide array on input datasets, including, for example, the open [Microsoft Geolife dataset](http://research.microsoft.com/en-us/downloads/b16d359d-d164-469e-9fd4-daa38f2b2e13/) a [sample](https://github.com/emeralds-horizon/trajectools-qgis/tree/main/sample_data) of which is included in the plugin repo:

![Trajectools screenshot](screenshots/trajectools.PNG)
![Trajectools clipping screenshot](screenshots/trajectools2.PNG)


## Authors
AIT

