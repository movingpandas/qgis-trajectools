import os
import sys
import pandas as pd

from movingpandas import (
    TemporalSplitter, 
    ObservationGapSplitter, 
    StopSplitter, 
    ValueChangeSplitter,
)

from qgis.core import (
    QgsProcessingParameterString,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterField,
)

sys.path.append("..")

from .trajectoriesAlgorithm import TrajectoryManipulationAlgorithm, help_str_base, help_str_traj


CPU_COUNT = os.cpu_count()


class SplitTrajectoriesAlgorithm(TrajectoryManipulationAlgorithm):
    def __init__(self):
        super().__init__()

    def group(self):
        return self.tr("Trajectory splitting")

    def groupId(self):
        return "TrajectorySplitting"


class ObservationGapSplitterAlgorithm(SplitTrajectoriesAlgorithm):
    TIME_GAP = "TIME_GAP"
    TIME_DELTA_UNITS = "TIME_DELTA_UNITS"
    TIME_DELTA_UNITS_OPTIONS = [
        "Weeks",
        "Days",
        "Hours",
        "Minutes",
        "Seconds",
        "Milliseconds"
    ]

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.TIME_GAP,
                description=self.tr("Time gap value"),
                defaultValue=1,
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.TIME_DELTA_UNITS,
                description=self.tr("Time gap unit"),
                defaultValue=3,
                options=self.TIME_DELTA_UNITS_OPTIONS,
            )
        )        

    def name(self):
        return "split_gap"

    def displayName(self):
        return self.tr("Split trajectories at observation gaps")

    def shortHelpString(self):
        return self.tr(
            "<p>Splits trajectories into subtrajectories "
            "whenever there is a gap in the observations</p>"
            "<p>For more information on trajectory splitters see: "
            "https://movingpandas.readthedocs.io/en/main/api/trajectorysplitter.html</p>"
            ""+help_str_base+help_str_traj
        )

    def processTc(self, tc, parameters, context):
        time_gap = self.parameterAsDouble(parameters, self.TIME_GAP, context)
        td_units = self.parameterAsInt(parameters, self.TIME_DELTA_UNITS, context)
        td_units = self.TIME_DELTA_UNITS_OPTIONS[td_units]
        if td_units == "Weeks": 
            td_units = "W"
        time_gap = pd.Timedelta(f"{time_gap} {td_units}").to_pytimedelta()
        for traj in tc.trajectories:
            try: 
                splits = ObservationGapSplitter(traj).split(
                    gap=time_gap, 
                    min_length=tc.min_length, 
                    n_processes=CPU_COUNT
                )
            except TypeError:
                raise TypeError("TypeError: cannot pickle 'QVariant' object. This error is usually caused by None values in input layer fields. Try to remove None values or run without Add movement metrics.")
        
            self.tc_to_sink(splits)
            for split in splits:
                self.traj_to_sink(split)


class TemporalSplitterAlgorithm(SplitTrajectoriesAlgorithm):
    SPLIT_MODE = "SPLIT_MODE"
    SPLIT_MODE_OPTIONS = [
        "year",
        "month",
        "day",
        "hour",
    ]

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.SPLIT_MODE,
                description=self.tr("Splitting mode"),
                defaultValue="day",
                options=self.SPLIT_MODE_OPTIONS,
                optional=False,
            )
        )

    def name(self):
        return "split_temporally"

    def displayName(self):
        return self.tr("Split trajectories at time intervals")

    def shortHelpString(self):
        return self.tr(
            "<p>Splits trajectories into subtrajectories "
            "using regular time intervals (year, month, day, hour). </p>"
            "<p>For more information on trajectory splitters see: "
            "https://movingpandas.readthedocs.io/en/main/trajectorysplitter.html</p>"
            ""+help_str_base+help_str_traj
        )

    def processTc(self, tc, parameters, context):
        split_mode = self.parameterAsInt(parameters, self.SPLIT_MODE, context)
        split_mode = self.SPLIT_MODE_OPTIONS[split_mode]
        try:
            splits = TemporalSplitter(tc).split(
                    mode=split_mode, 
                    min_length=tc.min_length, 
                    n_processes=CPU_COUNT
                )    
        except TypeError:
            raise TypeError("TypeError: cannot pickle 'QVariant' object. This error is usually caused by None values in input layer fields. Try to remove None values or run without Add movement metrics.")
        self.tc_to_sink(splits)
        for split in splits:
            self.traj_to_sink(split)


class StopSplitterAlgorithm(SplitTrajectoriesAlgorithm):
    MAX_DIAMETER = "MAX_DIAMETER"
    MIN_DURATION = "MIN_DURATION"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.MAX_DIAMETER,
                description=self.tr("Max stop diameter (meters)"),
                defaultValue=30,
                optional=False,
                type=QgsProcessingParameterNumber.Double,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.MIN_DURATION,
                description=self.tr(
                    "Min stop duration (timedelta, e.g. 1 hours, 15 minutes)"
                ),
                defaultValue="2 minutes",
                optional=False,
            )
        )

    def name(self):
        return "split_stops"

    def displayName(self):
        return self.tr("Split trajectories at stops")

    def shortHelpString(self):
        return self.tr(
            "<p>Splits trajectories into subtrajectories at stops. </p>"
            "<p>For more information on trajectory splitters see: "
            "https://movingpandas.readthedocs.io/en/main/trajectorysplitter.html</p>"
            ""+help_str_base+help_str_traj
        )

    def processTc(self, tc, parameters, context):
        max_diameter = self.parameterAsDouble(parameters, self.MAX_DIAMETER, context)
        min_duration = self.parameterAsString(parameters, self.MIN_DURATION, context)
        min_duration = pd.Timedelta(min_duration).to_pytimedelta()
        try: 
            splits = StopSplitter(tc).split(
                max_diameter=max_diameter, 
                min_duration=min_duration, 
                min_length=tc.min_length, 
                n_processes=CPU_COUNT
            )
        except TypeError:
            raise TypeError("TypeError: cannot pickle 'QVariant' object. This error is usually caused by None values in input layer fields. Try to remove None values or run without Add movement metrics.")

        self.tc_to_sink(splits)
        for split in splits:
            self.traj_to_sink(split)


class ValueChangeSplitterAlgorithm(SplitTrajectoriesAlgorithm):
    FIELD = "FIELD"

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        super().initAlgorithm(config)
        self.addParameter(
            QgsProcessingParameterField(
                name=self.FIELD,
                description=self.tr("Field to check for changing values"),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any,
                allowMultiple=False,
                optional=False,
            )
        )

    def name(self):
        return "split_value_change"

    def displayName(self):
        return self.tr("Split trajectories at field value change")

    def shortHelpString(self):
        return self.tr(
            "<p>Splits trajectories into subtrajectories "
            "whenever there is a change in the specified field's value.</p>"
            "<p>For more information on trajectory splitters see: "
            "https://movingpandas.readthedocs.io/en/main/api/trajectorysplitter.html</p>"
            ""+help_str_base+help_str_traj         
        )

    def processTc(self, tc, parameters, context):
        self.field = self.parameterAsFields(parameters, self.FIELD, context)[0]
        for traj in tc.trajectories:
            try: 
                splits = ValueChangeSplitter(traj).split(
                    col_name=self.field, 
                    min_length=tc.min_length, 
                    n_processes=CPU_COUNT
                )
            except TypeError:
                raise TypeError("TypeError: cannot pickle 'QVariant' object. This error is usually caused by None values in input layer fields. Try to remove None values or run without Add movement metrics.")

            self.tc_to_sink(splits)
            for split in splits:
                self.traj_to_sink(split)
