import sys
import pandas as pd

from movingpandas import (
    OutlierCleaner
)

from qgis.core import (
    QgsProcessingParameterString,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
)

sys.path.append("..")

from .trajectoriesAlgorithm import TrajectoryManipulationAlgorithm, help_str_base, help_str_traj


class CleaningAlgorithm(TrajectoryManipulationAlgorithm):

    def __init__(self):
        super().__init__()

    def group(self):
        return self.tr("Trajectory cleaning")

    def groupId(self):
        return "TrajectoryCleaning"


class OutlierCleanerAlgorithm(CleaningAlgorithm):
    TOLERANCE = "TOLERANCE"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.TOLERANCE,
                description=self.tr("Speed threshold"),
                defaultValue=10.0,
                type=QgsProcessingParameterNumber.Double,
            )
        )

    def name(self):
        return "clean_vmax"

    def displayName(self):
        return self.tr("Remove speed above threshold")

    def shortHelpString(self):
        return self.tr(
            "<p>Speed-based outlier cleaner that cuts away spikes in the trajectory when "
            "the speed exceeds the provided <b>Speed threshold</b> value </p>"
            "<p>For more info see: "
            "https://movingpandas.readthedocs.io/en/main/api/trajectorycleaner.html</p>"
            ""+help_str_base+help_str_traj
        )

    def processTc(self, tc, parameters, context):
        v_max = self.parameterAsDouble(parameters, self.TOLERANCE, context)
        generalized = OutlierCleaner(tc).clean(v_max=v_max, units=tuple(self.speed_units))
        self.tc_to_sink(generalized)
        for traj in generalized:
            self.traj_to_sink(traj)
