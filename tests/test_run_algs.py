import pytest
from qgis.core import QgsApplication
from processing import run, QgsProcessingException
from processing.core.Processing import Processing
from qgis_processing.trajectoolsProvider import TrajectoolsProvider


TEST_DATA = "./sample_data/geolife.gpkg"
TEST_OVERLAY = "./sample_data/polys.geojson"


def get_processing_registry_and_provider():
    Processing.initialize()
    provider = TrajectoolsProvider()
    registry = QgsApplication.processingRegistry()
    registry.removeProvider(provider)  # in case it was already added
    # for alg in QgsApplication.processingRegistry().algorithms():
    #    if not "native:" in alg.id():
    #        print(alg.id(), "--->", alg.displayName())
    return registry, provider


def test_run_buffer_algorithm():
    # This test just checks that processing algorithms can be
    # run without errors.
    Processing.initialize()

    alg_params = {
        "DISSOLVE": False,
        "DISTANCE": 1,
        "END_CAP_STYLE": 0,  # Round
        "INPUT": TEST_DATA,
        "JOIN_STYLE": 0,  # Round
        "MITER_LIMIT": 2,
        "SEGMENTS": 5,
        "OUTPUT": "TEMPORARY_OUTPUT",
    }
    run("native:buffer", alg_params)


def test_run_create_trajectory_algorithm():
    registry, provider = get_processing_registry_and_provider()
    registry.addProvider(provider)
    alg_params = {
        "INPUT": TEST_DATA,
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
    results = run("Trajectory:create_trajectory", alg_params)
    assert "OUTPUT_PTS" in results
    assert "OUTPUT_TRAJS" in results
    assert results["OUTPUT_TRAJS"].featureCount() == 5


def test_run_create_trajectory_with_wrong_time_field():
    registry, provider = get_processing_registry_and_provider()
    registry.addProvider(provider)
    alg_params = {
        "INPUT": TEST_DATA,
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


def test_run_clip_traj_vector():
    registry, provider = get_processing_registry_and_provider()
    registry.addProvider(provider)
    alg_params = {
        "INPUT": TEST_DATA,
        "TRAJ_ID_FIELD": "trajectory_id",
        "TIME_FIELD": "t",
        "OUTPUT_PTS": "TEMPORARY_OUTPUT",
        "OUTPUT_TRAJS": "TEMPORARY_OUTPUT",
        "FIELDS_TO_ADD": [],
        "ADD_METRICS": True,
        "USE_PARALLEL_PROCESSING": False,
        "SPEED_UNIT": "km/h",
        "MIN_LENGTH": 0,
        "OVERLAY_LAYER": TEST_OVERLAY,
    }
    results = run("Trajectory:clip_traj_vector", alg_params)
    assert "OUTPUT_PTS" in results
    assert "OUTPUT_TRAJS" in results
    assert results["OUTPUT_TRAJS"].featureCount() == 10
