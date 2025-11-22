import sys
from qgis.core import QgsGeometry, QgsVectorLayer

sys.path.append("..")

from qgis_processing.qgisUtils import tc_from_pt_layer


TESTDATA = "./sample_data/geolife.gpkg"
ID_COL = "trajectory_id"
TIME_COL_STR = "t"
TIME_COL_DT = "dt"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S+00"


def test_qgis_imports():
    polygon = QgsGeometry.fromWkt("POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))")
    result = polygon.area()
    assert result == 100


def test_dataset_availability():
    vl = QgsVectorLayer(TESTDATA, "test data")
    assert vl.isValid()


def test_tc_from_pt_layer_with_string_timestamp():
    vl = QgsVectorLayer(TESTDATA, "test data")
    tc = tc_from_pt_layer(vl, TIME_COL_STR, ID_COL)
    assert len(tc) == 5


def test_tc_from_pt_layer_with_proper_datetime():
    vl = QgsVectorLayer(TESTDATA, "test data")
    tc = tc_from_pt_layer(vl, TIME_COL_DT, ID_COL)
    assert len(tc) == 5
