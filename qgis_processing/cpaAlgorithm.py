import sys

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessingParameterExtent,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsProcessingParameterFeatureSink,
    QgsProcessing,
    QgsWkbTypes,
    QgsField,
    QgsFeatureSink,
    QgsFields,
)

sys.path.append("..")
from .trajectoriesAlgorithm import TrajectoriesAlgorithm


class CPAAlgorithm(TrajectoriesAlgorithm):
    CLOSEST_POINT_OF_APPROACH = "CLOSEST_POINT_OF_APPROACH"
    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.CLOSEST_POINT_OF_APPROACH,
                description=self.tr("Closest Point of Approach"),
                type=QgsProcessing.TypeVectorPoint,
            )
        )

    def group(self):
        return self.tr("Event extraction")

    def groupId(self):
        return "TrajectoryEventExtraction"

    def name(self):
        return "extract_cpa"

    def displayName(self):
        return self.tr("Extract Closest Point of Approach")

    def shortHelpString(self):
        return self.tr("<p>Extracts Closest Point of Approach from trajectories.</p>")

    def processAlgorithm(self, parameters, context, feedback):
        tc, crs = self.create_tc(parameters, context)

        self.fields_pts = QgsFields()
        self.fields_pts.append(QgsField("time", QVariant.String))  # .DateTime))
        self.fields_pts.append(QgsField("traj_a", QVariant.String))
        self.fields_pts.append(QgsField("traj_b", QVariant.String))

        (self.sink, self.closest_point_of_approach) = self.parameterAsSink(
            parameters,
            self.CLOSEST_POINT_OF_APPROACH,
            context,
            self.fields_pts,
            QgsWkbTypes.Point,
            crs,
        )

        self.processTc(tc, parameters, context)

        return {self.CLOSEST_POINT_OF_APPROACH: self.closest_point_of_approach}

    def processTc(self, tc, parameters, context):
        traj_a = tc.trajectories[0]
        traj_b = tc.trajectories[1]
