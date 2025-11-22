import os

from qgis.PyQt.QtGui import QIcon
from qgis.core import Qgis, QgsProcessingProvider, QgsMessageLog

from qgis_processing.createTrajectoriesAlgorithm import CreateTrajectoriesAlgorithm
from qgis_processing.splitTrajectoriesAlgorithm import (
    ObservationGapSplitterAlgorithm,
    TemporalSplitterAlgorithm,
    StopSplitterAlgorithm,
    ValueChangeSplitterAlgorithm,
)
from qgis_processing.overlayAlgorithm import (
    ClipTrajectoriesByExtentAlgorithm,
    ClipTrajectoriesByPolygonLayerAlgorithm,
    IntersectWithPolygonLayerAlgorithm,
)
from qgis_processing.extractPtsAlgorithm import (
    ExtractODPtsAlgorithm,
    ExtractStopsAlgorithm,
)
from qgis_processing.generalizationAlgorithm import (
    DouglasPeuckerGeneralizerAlgorithm,
    MinDistanceGeneralizerAlgorithm,
    MinTimeDeltaGeneralizerAlgorithm,
    TopDownTimeRatioGeneralizerAlgorithm,
)
from qgis_processing.cleaningAlgorithm import (
    OutlierCleanerAlgorithm,
)

try:  # skmob-based algs
    from qgis_processing.privacyAttackAlgorithm import HomeWorkAttack
except ImportError as e:
    QgsMessageLog.logMessage(e.msg, "Trajectools", level=Qgis.Info)

try:  # gtfs_functions-based algs
    from qgis_processing.gtfsAlgorithm import (
        GtfsStopsAlgorithm,
        GtfsShapesAlgorithm,
        GtfsSegmentsAlgorithm,
    )
except ImportError as e:
    QgsMessageLog.logMessage(e.msg, "Trajectools", level=Qgis.Info)

try:  # stonesoup-based algs
    from qgis_processing.smoothingAlgorithm import KalmanSmootherAlgorithm
except ImportError as e:
    QgsMessageLog.logMessage(e.msg, "Trajectools", level=Qgis.Info)


pluginPath = os.path.dirname(__file__)


class TrajectoolsProvider(QgsProcessingProvider):
    def __init__(self):
        super().__init__()
        self.algs = []

    def id(self):
        return "Trajectory"

    def name(self):
        return "Trajectools"

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "icon.png"))

    def load(self):
        self.refreshAlgorithms()
        return True

    def unload(self):
        pass

    def isActive(self):
        return True

    def setActive(self, active):
        pass

    def getAlgs(self):
        algs = [
            CreateTrajectoriesAlgorithm(),
            ObservationGapSplitterAlgorithm(),
            TemporalSplitterAlgorithm(),
            StopSplitterAlgorithm(),
            ValueChangeSplitterAlgorithm(),
            ClipTrajectoriesByExtentAlgorithm(),
            ClipTrajectoriesByPolygonLayerAlgorithm(),
            IntersectWithPolygonLayerAlgorithm(),
            ExtractODPtsAlgorithm(),
            ExtractStopsAlgorithm(),
            DouglasPeuckerGeneralizerAlgorithm(),
            MinDistanceGeneralizerAlgorithm(),
            MinTimeDeltaGeneralizerAlgorithm(),
            TopDownTimeRatioGeneralizerAlgorithm(),
            OutlierCleanerAlgorithm(),
        ]
        try:  # skmob-based algs
            algs.append(HomeWorkAttack())
        except NameError:
            pass
        try:  # gtfs_functions-based algs
            algs.append(GtfsStopsAlgorithm())
            algs.append(GtfsShapesAlgorithm())
            algs.append(GtfsSegmentsAlgorithm())
        except NameError:
            pass
        try:  # stonesoup-based algs
            algs.append(KalmanSmootherAlgorithm())
        except NameError:
            pass
        return algs

    def loadAlgorithms(self):
        self.algs = self.getAlgs()
        for a in self.algs:
            self.addAlgorithm(a)

    def tr(self, string, context=""):
        pass
