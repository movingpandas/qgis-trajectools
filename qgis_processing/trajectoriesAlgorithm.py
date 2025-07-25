import os
import sys

from qgis.PyQt.QtCore import QCoreApplication, QVariant, QDateTime, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingUtils,
    QgsWkbTypes,
    QgsProcessingParameterString,
    QgsProcessingParameterNumber,
    QgsProcessingParameterBoolean,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsGeometry,
    QgsFeatureSink,
)

sys.path.append("..")

from .qgisUtils import (
    set_multiprocess_path,
    tc_from_pt_layer, 
    feature_from_gdf_row, 
    df_from_pt_layer, 
)

pluginPath = os.path.dirname(__file__)

TIME_FACTOR = {
    "s": 1,
    "min": 60,
    "h": 3600,
    "d": 3600 * 24,
    "a": 3600 * 24 * 365,
}

CPU_COUNT = os.cpu_count()


class TrajectoriesAlgorithm(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    TRAJ_ID_FIELD = "TRAJ_ID_FIELD"
    TIMESTAMP_FIELD = "TIME_FIELD"
    ADD_METRICS = "ADD_METRICS"
    SPEED_UNIT = "SPEED_UNIT"
    MIN_LENGTH = "MIN_LENGTH"

    def __init__(self):
        super().__init__()
        set_multiprocess_path()

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "mpd.png"))

    def tr(self, text):
        return QCoreApplication.translate("trajectools", text)

    def helpUrl(self):
        return "https://github.com/movingpandas/processing-trajectory"

    def createInstance(self):
        return type(self)()

    def flags(self):
        super().flags()
        return  QgsProcessingAlgorithm.FlagNoThreading

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                name=self.INPUT,
                description=self.tr("Input point layer"),
                types=[QgsProcessing.TypeVectorPoint],
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                name=self.TRAJ_ID_FIELD,
                description=self.tr("Trajectory ID field"),
                defaultValue="trajectory_id",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any,
                allowMultiple=False,
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                name=self.TIMESTAMP_FIELD,
                description=self.tr("Timestamp field"),
                defaultValue="t",
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any,
                allowMultiple=False,
                optional=False,
            )
        )


    def create_df(self, parameters, context):
        self.prepare_parameters(parameters, context)

        df = df_from_pt_layer(
            self.input_layer, self.timestamp_field, self.traj_id_field
        )

        return df

    def prepare_parameters(self, parameters, context):
        self.input_layer = self.parameterAsSource(parameters, self.INPUT, context)
        self.traj_id_field = self.parameterAsFields(
            parameters, self.TRAJ_ID_FIELD, context
        )[0]
        self.timestamp_field = self.parameterAsFields(
            parameters, self.TIMESTAMP_FIELD, context
        )[0]
        self.speed_units = self.parameterAsString(
            parameters, self.SPEED_UNIT, context
        ).split("/")
        self.min_length = self.parameterAsDouble(parameters, self.MIN_LENGTH, context)
        self.add_metrics = self.parameterAsBoolean(parameters, self.ADD_METRICS, context)

    def create_tc(self, parameters, context):
        self.prepare_parameters(parameters, context)
        crs = self.input_layer.sourceCrs()

        tc = tc_from_pt_layer(
            self.input_layer, self.timestamp_field, self.traj_id_field, self.min_length
        )

        if len(tc.trajectories) < 1:
            raise ValueError(
                "The resulting trajectory collection is empty. Check that the trajectory ID and timestamp fields have been configured correctly."
            )

        if self.add_metrics:
            tc.add_speed(units=tuple(self.speed_units), overwrite=True, n_processes=CPU_COUNT)
            tc.add_direction(overwrite=True, n_processes=CPU_COUNT)
        return tc, crs

    def get_pt_fields(self, fields_to_add=[]):
        fields = QgsFields()
        for field in self.input_layer.fields():
            if field.name() == "fid":
                continue
            elif field.name() == self.traj_id_field:
                # we need to make sure the ID field is String
                fields.append(QgsField(self.traj_id_field, QVariant.String))
            elif field.name() == self.timestamp_field:
                fields.append(QgsField(self.timestamp_field, QVariant.DateTime))
            else:
                fields.append(field)
        for field in fields_to_add:
            i = fields.indexFromName(field.name())
            if i < 0:
                fields.append(field)
        return fields


class TrajectoryManipulationAlgorithm(TrajectoriesAlgorithm):
    FIELDS_TO_ADD = "FIELDS_TO_ADD"
    OUTPUT_PTS = "OUTPUT_PTS"
    OUTPUT_SEGS = "OUTPUT_SEGS"
    OUTPUT_TRAJS = "OUTPUT_TRAJS"

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUTPUT_PTS,
                description=self.tr("Trajectory points"),
                type=QgsProcessing.TypeVectorPoint,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUTPUT_TRAJS,
                description=self.tr("Trajectories"),
                type=QgsProcessing.TypeVectorLine,
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                name=self.FIELDS_TO_ADD,
                description=self.tr("Fields to add to trajectories (line) layer"),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any,
                allowMultiple=True,
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.ADD_METRICS,
                description=self.tr("Add movement metrics (speed, direction)"),
                defaultValue=True,
                optional=False,
            )
        )        
        self.addParameter(
            QgsProcessingParameterString(
                name=self.SPEED_UNIT,
                description=self.tr("Speed units (e.g. km/h, m/s)"),
                defaultValue="km/h",
                optional=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.MIN_LENGTH,
                description=self.tr("Minimum trajectory length"),
                defaultValue=0,
                # optional=True,
                minValue=0,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        tc, crs = self.create_tc(parameters, context)
        self.setup_pt_sink(parameters, context, tc, crs)
        self.setup_traj_sink(parameters, context, crs)
        self.processTc(tc, parameters, context)
        return {self.OUTPUT_PTS: self.dest_pts, self.OUTPUT_TRAJS: self.dest_trajs}

    def setup_traj_sink(self, parameters, context, crs):
        self.fields_to_add = self.parameterAsFields(
            parameters, self.FIELDS_TO_ADD, context
        )
        self.fields_trajs = self.get_traj_fields(fields_to_add=self.fields_to_add)
        (self.sink_trajs, self.dest_trajs) = self.parameterAsSink(
            parameters,
            self.OUTPUT_TRAJS,
            context,
            self.fields_trajs,
            QgsWkbTypes.LineStringM,
            crs,
        )

    def setup_pt_sink(self, parameters, context, tc, crs):
        fields_to_add = []
        if self.add_metrics:
            fields_to_add = [
                QgsField(tc.get_speed_col(), QVariant.Double),
                QgsField(tc.get_direction_col(), QVariant.Double),
            ]
        self.fields_pts = self.get_pt_fields(fields_to_add)
        (self.sink_pts, self.dest_pts) = self.parameterAsSink(
            parameters,
            self.OUTPUT_PTS,
            context,
            self.fields_pts,
            QgsWkbTypes.Point,
            crs,
        )

    def processTc(self, tc, parameters, context):
        pass  # needs to be implemented by each splitter

    def postProcessAlgorithm(self, context, feedback):
        if self.add_metrics:
            pts_layer = QgsProcessingUtils.mapLayerFromString(self.dest_pts, context)
            pts_layer.loadNamedStyle(os.path.join(pluginPath, "styles", "pts.qml"))
        traj_layer = QgsProcessingUtils.mapLayerFromString(self.dest_trajs, context)
        traj_layer.loadNamedStyle(os.path.join(pluginPath, "styles", "traj.qml"))
        return {self.OUTPUT_PTS: self.dest_pts, self.OUTPUT_TRAJS: self.dest_trajs}

    def get_traj_fields(self, fields_to_add=[]):
        length_units = f"{self.speed_units[0]}"
        speed_units = f"{self.speed_units[0]}{self.speed_units[1]}"
        fields = QgsFields()
        fields.append(QgsField(self.traj_id_field, QVariant.String))
        fields.append(QgsField("start_time", QVariant.DateTime))
        fields.append(QgsField("end_time", QVariant.DateTime))
        fields.append(QgsField("duration_seconds", QVariant.Double))
        fields.append(QgsField(f"length_{length_units}", QVariant.Double))
        fields.append(QgsField(f"speed_{speed_units}", QVariant.Double))
        for field in fields_to_add:
            if isinstance(field, str):
                if fields.indexFromName(field) < 0:
                    fields.append(self.input_layer.fields().field(field))
            else:
                if fields.indexFromName(field.name()) < 0:
                    fields.append(field)
        return fields

    def traj_to_sink(self, traj, attr_mean_to_add=[], attr_first_to_add=[]):
        line = QgsGeometry.fromWkt(traj.to_linestringm_wkt())
        f = QgsFeature()
        f.setGeometry(line)
        start_time = traj.get_start_time().isoformat()
        start_time = QDateTime.fromString(start_time, Qt.ISODate)
        end_time = traj.get_end_time().isoformat()
        end_time = QDateTime.fromString(end_time, Qt.ISODate)
        duration = float(traj.get_duration().total_seconds())
        length = traj.get_length(units=self.speed_units[0])
        speed = length / (duration / TIME_FACTOR[self.speed_units[1]])
        attrs = [traj.id, start_time, end_time, duration, length, speed]
        attr_first_to_add = self.fields_to_add + attr_first_to_add
        for a in attr_mean_to_add:
            attrs.append(float(traj.df[a].mean()))
        for a in attr_first_to_add:
            try:
                attrs.append(float(traj.df[a].iloc[0]))
                continue
            except:
                pass
            try: 
                attrs.append(int(traj.df[a].iloc[0]))
                continue
            except:
                pass
            attrs.append(traj.df[a].iloc[0])
        f.setAttributes(attrs)
        self.sink_trajs.addFeature(f, QgsFeatureSink.FastInsert)

    def tc_to_sink(self, tc, field_names_to_add=[]):
        try:
            dfs = tc.to_point_gdf()
        except ValueError:  # when the tc is empty
            return
        dfs[self.timestamp_field] = dfs.index

        names = [field.name() for field in self.fields_pts]
        for field_name in field_names_to_add:
            names.append(field_name)      
        names.append("geometry")
        dfs = dfs[names]

        for _, row in dfs.iterrows():
            f = feature_from_gdf_row(row)
            self.sink_pts.addFeature(f, QgsFeatureSink.FastInsert)
