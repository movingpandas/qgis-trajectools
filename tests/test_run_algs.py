import pytest
from qgis.core import QgsApplication
from processing import run, QgsProcessingException
from processing.core.Processing import Processing
from qgis_processing.trajectoolsProvider import TrajectoolsProvider


TESTDATA = "./sample_data/geolife.gpkg"


def test_run_buffer_algorithm():
    # This test just checks that processing algorithms can be 
    # run without errors.
    Processing.initialize()

    alg_params = {
        "DISSOLVE": False,
        "DISTANCE": 1,
        "END_CAP_STYLE": 0,  # Round
        "INPUT": TESTDATA,
        "JOIN_STYLE": 0,  # Round
        "MITER_LIMIT": 2,
        "SEGMENTS": 5,
        "OUTPUT": "TEMPORARY_OUTPUT",
    }
    run("native:buffer", alg_params)


def test_run_create_trajectory_algorithm():
    Processing.initialize()
    provider = TrajectoolsProvider()
    QgsApplication.processingRegistry().addProvider(provider)

    # for alg in QgsApplication.processingRegistry().algorithms():
    #    if not "native:" in alg.id():
    #        print(alg.id(), "--->", alg.displayName())

    alg_params = {
        "INPUT": TESTDATA,
        "TRAJ_ID_FIELD": "trajectory_id",
        "TIME_FIELD": "t",
        "OUTPUT_PTS": "TEMPORARY_OUTPUT",
        "OUTPUT_TRAJS": "TEMPORARY_OUTPUT",
        "FIELDS_TO_ADD": [],
        "ADD_METRICS": True,
        "USE_PARALLEL_PROCESSING": False,
        "SPEED_UNIT": "km/h",
        "MIN_LENGTH": 0,
    }
    run("Trajectory:create_trajectory", alg_params)


def test_run_create_trajectory_with_wrong_time_field():
    Processing.initialize()
    provider = TrajectoolsProvider()
    QgsApplication.processingRegistry().addProvider(provider)

    alg_params = {
        "INPUT": TESTDATA,
        "TRAJ_ID_FIELD": "trajectory_id",
        "TIME_FIELD": "txxx",
        "OUTPUT_PTS": "TEMPORARY_OUTPUT",
        "OUTPUT_TRAJS": "TEMPORARY_OUTPUT",
        "FIELDS_TO_ADD": [],
        "ADD_METRICS": True,
        "USE_PARALLEL_PROCESSING": False,
        "SPEED_UNIT": "km/h",
        "MIN_LENGTH": 0,
    }
    with pytest.raises(QgsProcessingException):
        run("Trajectory:create_trajectory", alg_params)
