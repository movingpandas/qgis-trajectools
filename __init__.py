# -*- coding: utf-8 -*-

"""
***************************************************************************
    trajectoolsProviderPlugin.py
    ---------------------
    Date                 : September 2025
    Copyright            : (C) 2025 by Anita Graser
    Email                : anitagraser@gmx.at
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Anita Graser'
__date__ = 'Sep 2025'
__copyright__ = '(c) 2025, Anita Graser'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'



from packaging.version import Version
from movingpandas import __version__ as mpd_version

MIN_MPD_VERSION = '0.22.3'
if Version(mpd_version) < Version(MIN_MPD_VERSION):
    raise(RuntimeError(f'Please update MovingPandas to >={MIN_MPD_VERSION}'))

from .qgis_processing.trajectoolsProviderPlugin import TrajectoryProviderPlugin

def classFactory(iface):
    return TrajectoryProviderPlugin()
