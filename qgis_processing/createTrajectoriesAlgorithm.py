import sys

sys.path.append("..")

from .trajectoriesAlgorithm import TrajectoryManipulationAlgorithm, help_str_base, help_str_traj


class CreateTrajectoriesAlgorithm(TrajectoryManipulationAlgorithm):
    def __init__(self):
        super().__init__()

    def name(self):
        return "create_trajectory"

    def displayName(self):
        return self.tr("Create trajectories")

    def group(self):
        return self.tr("Basic")

    def groupId(self):
        return "TrajectoryBasic"

    def shortHelpString(self):
        return self.tr(
            "<p>Creates a trajectory point layers with speed and direction information "
            "as well as a trajectory line layer.</p>"+help_str_base+help_str_traj
        )

    def helpUrl(self):
        return "https://movingpandas.org/units"

    def createInstance(self):
        return type(self)()

    def processTc(self, tc, parameters, context):
        self.tc_to_sink(tc)
        for traj in tc.trajectories:
            self.traj_to_sink(traj)
