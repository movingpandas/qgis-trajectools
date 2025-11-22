from qgis_processing.trajectoolsProvider import TrajectoolsProvider


def test_name():
    provider = TrajectoolsProvider()
    assert provider.name() == "Trajectools"
