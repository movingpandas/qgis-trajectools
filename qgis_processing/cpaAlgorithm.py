# -*- coding: utf-8 -*-

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFeatureSink,
    QgsProcessingException,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsWkbTypes,
    QgsPoint,
    QgsGeometry,
    QgsLineString,
    QgsMessageLog,
    Qgis,
)
from qgis.PyQt.QtCore import QCoreApplication, QVariant, QDateTime
import pandas as pd
from .qgisUtils import tc_from_pt_layer
from .cpa import CPACalculator


def tr(string):
    """
    Gets a translated string to the current locale.
    """
    return QCoreApplication.translate("CpaAlgorithm", string)


class CpaAlgorithm(QgsProcessingAlgorithm):
    # Define constants for parameter names to avoid typos
    INPUT_A = "INPUT_A"
    TRAJ_ID_FIELD_A = "TRAJ_ID_FIELD_A"
    TIME_FIELD_A = "TIME_FIELD_A"
    INPUT_B = "INPUT_B"
    TRAJ_ID_FIELD_B = "TRAJ_ID_FIELD_B"
    TIME_FIELD_B = "TIME_FIELD_B"
    OUTPUT = "OUTPUT"

    def log(self, message):
        """Helper for logging"""
        QgsMessageLog.logMessage(str(message), "Trajectools", level=Qgis.Info)

    def createInstance(self):
        """
        Must return a new copy of this algorithm.
        """
        return CpaAlgorithm()

    def name(self):
        """
        Returns the unique algorithm name.
        """
        return "cpa"

    def displayName(self):
        """
        Returns the translated algorithm name.
        """
        return tr("Closest Point of Approach")

    def group(self):
        """
        Returns the name of the group this algorithm belongs to.
        """
        return tr("Event extraction")

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to.
        """
        return "TrajectoryEventExtraction"

    def shortHelpString(self):
        """
        Returns a brief description of the algorithm.
        """
        return tr(
            "Calculates the Closest Point of Approach (CPA) between trajectories from two layers."
        )

    def onParameterChanged(self, parameters, name, context):
        """
        Dynamically update the trajectory ID and time field parameters
        with the most likely fields from the selected input layer.
        """
        if name == self.INPUT_A or name == self.INPUT_B:
            input_param_name = name
            id_field_param_name = (
                self.TRAJ_ID_FIELD_A if name == self.INPUT_A else self.TRAJ_ID_FIELD_B
            )
            time_field_param_name = (
                self.TIME_FIELD_A if name == self.INPUT_A else self.TIME_FIELD_B
            )

            source = self.parameterAsSource(parameters, input_param_name, context)
            if source:
                id_field_candidates = ["traj_id", "mmsi", "id"]  # Prioritize traj_id
                best_id_field = ""
                for candidate in id_field_candidates:
                    if source.fields().lookupField(candidate) != -1:
                        best_id_field = candidate
                        break
                parameters[id_field_param_name].setValue(best_id_field)

                best_time_field = ""
                for field in source.fields():
                    if field.type() == QVariant.DateTime:
                        best_time_field = field.name()
                        break
                parameters[time_field_param_name].setValue(best_time_field)

        return super().onParameterChanged(parameters, name, context)

    def initAlgorithm(self, config=None):
        """
        Defines the input and output parameters of the algorithm.
        """
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_A,
                tr("Input layer A"),
                [QgsProcessing.TypeVectorPoint],
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.TRAJ_ID_FIELD_A,
                tr("Trajectory ID field A"),
                parentLayerParameterName=self.INPUT_A,
                type=QgsProcessingParameterField.Any,
                defaultValue="traj_id",
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.TIME_FIELD_A,
                tr("Time field A"),
                parentLayerParameterName=self.INPUT_A,
                type=QgsProcessingParameterField.Any,
                defaultValue="t",
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_B,
                tr("Input layer B"),
                [QgsProcessing.TypeVectorPoint],
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.TRAJ_ID_FIELD_B,
                tr("Trajectory ID field B"),
                parentLayerParameterName=self.INPUT_B,
                type=QgsProcessingParameterField.Any,
                defaultValue="traj_id",
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.TIME_FIELD_B,
                tr("Time field B"),
                parentLayerParameterName=self.INPUT_B,
                type=QgsProcessingParameterField.Any,
                defaultValue="t",
            )
        )
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, tr("CPA")))

    def processAlgorithm(self, parameters, context, feedback):
        """
        The main logic of the algorithm.
        """
        self.log("--- Starting processAlgorithm ---")
        source_a = self.parameterAsSource(parameters, self.INPUT_A, context)
        id_field_a = self.parameterAsString(parameters, self.TRAJ_ID_FIELD_A, context)
        time_field_a = self.parameterAsString(parameters, self.TIME_FIELD_A, context)
        source_b = self.parameterAsSource(parameters, self.INPUT_B, context)
        id_field_b = self.parameterAsString(parameters, self.TRAJ_ID_FIELD_B, context)
        time_field_b = self.parameterAsString(parameters, self.TIME_FIELD_B, context)

        self.log(f"Received parameters: ID_A='{id_field_a}', TIME_A='{time_field_a}'")
        self.log(f"Received parameters: ID_B='{id_field_b}', TIME_B='{time_field_b}'")

        if source_a.sourceCrs().isGeographic() or source_b.sourceCrs().isGeographic():
            raise QgsProcessingException(tr("Input layers must have a projected CRS."))

        if source_a.fields().lookupField(id_field_a) == -1:
            raise QgsProcessingException(
                tr(f"Trajectory ID field '{id_field_a}' not found in Input Layer A.")
            )
        if source_a.fields().lookupField(time_field_a) == -1:
            raise QgsProcessingException(
                tr(f"Time field '{time_field_a}' not found in Input Layer A.")
            )
        if source_b.fields().lookupField(id_field_b) == -1:
            raise QgsProcessingException(
                tr(f"Trajectory ID field '{id_field_b}' not found in Input Layer B.")
            )
        if source_b.fields().lookupField(time_field_b) == -1:
            raise QgsProcessingException(
                tr(f"Time field '{time_field_b}' not found in Input Layer B.")
            )

        tc_a = tc_from_pt_layer(source_a, time_field_a, id_field_a)
        tc_b = tc_from_pt_layer(source_b, time_field_b, id_field_b)

        if not tc_a or not tc_b:
            raise QgsProcessingException(tr("One or both input layers are empty."))

        fields = QgsFields()
        fields.append(QgsField("traj_id_a", QVariant.String))
        fields.append(QgsField("traj_id_b", QVariant.String))
        fields.append(QgsField("cpa_time", QVariant.DateTime))
        fields.append(QgsField("cpa_distance", QVariant.Double))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.LineString,
            source_a.sourceCrs(),
        )

        total_calculations = len(tc_a) * len(tc_b)
        progress = 0

        for traj_a in tc_a:
            for traj_b in tc_b:
                if feedback.isCanceled():
                    return {}

                if traj_a.id == traj_b.id:
                    total_calculations -= 1
                    continue

                cpa_calc = CPACalculator(traj_a, traj_b)
                cpa_result = cpa_calc.min()

                self.log(f"CPA result for {traj_a.id} vs {traj_b.id}: {type(cpa_result)}")
                self.log(f"CPA result value: {cpa_result}")

                if cpa_result is not None and not pd.isna(cpa_result["dist"]):
                    feat = QgsFeature(fields)

                    line_geom = cpa_result["geometry"]
                    p_a_coords = line_geom.coords[0]
                    p_b_coords = line_geom.coords[1]

                    p_a = QgsPoint(p_a_coords[0], p_a_coords[1])
                    p_b = QgsPoint(p_b_coords[0], p_b_coords[1])

                    line = QgsLineString([p_a, p_b])
                    feat.setGeometry(QgsGeometry(line))

                    # Convert pandas Timestamp to a QDateTime object for QGIS
                    cpa_time_val = cpa_result["t_at"]
                    if isinstance(cpa_time_val, pd.Timestamp):
                        # First convert to standard Python datetime
                        py_datetime = cpa_time_val.to_pydatetime()
                        # Then convert to QDateTime
                        cpa_time_val = QDateTime(py_datetime)

                    self.log(f"Setting attributes: time type={type(cpa_time_val)}")

                    feat.setAttributes(
                        [
                            str(traj_a.id),
                            str(traj_b.id),
                            cpa_time_val,
                            cpa_result["dist"],
                        ]
                    )
                    sink.addFeature(feat)
                    self.log("--> Feature added.")
                else:
                    self.log("--> No feature added.")

                progress += 1
                if total_calculations > 0:
                    feedback.setProgress(int(progress * 100 / total_calculations))

        self.log("--- Finished processAlgorithm ---")
        return {self.OUTPUT: dest_id}
