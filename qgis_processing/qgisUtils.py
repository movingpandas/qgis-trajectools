import sys
import platform
import multiprocessing
import pandas as pd
from os import path
from pyproj import CRS
from datetime import datetime

from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsFeatureSink,
    QgsMessageLog,
    Qgis,
)
from qgis.PyQt.QtCore import QDateTime

try:
    from movingpandas import TrajectoryCollection
except ImportError as error:
    raise ImportError(
        "Missing dependency. To use the trajectory analysis algorithms "
        "please install MovingPandas. For details see: "
        "https://github.com/movingpandas/qgis-processing-trajectory."
    ) from error


def set_multiprocess_path():
    # This function is courtesy of the SemiAutomaticClassificationPlugin
    # Copyright (C) 2012-2024 by Luca Congedo

    python_path = None
    system_platform = platform.system()
    if system_platform == 'Windows':
        try:
            python_path = path.abspath(
                path.join(sys.exec_prefix, 'pythonw.exe')
            )
            if path.isfile(python_path):
                multiprocessing.set_executable(python_path)
            else:
                # from https://trac.osgeo.org/osgeo4w/ticket/392
                python_path = path.abspath(
                    path.join(sys.exec_prefix, '../../bin/pythonw.exe')
                )
                if path.isfile(python_path):
                    multiprocessing.set_executable(python_path)
                else:
                    qgis_utils.iface.messageBar().pushMessage(
                        'Semi-Automatic Classification Plugin',
                        QApplication.translate(
                            'semiautomaticclassificationplugin',
                            'Error. Python library not found'
                        ),
                        level=Qgis.Info
                    )
        except Exception as err:
            str(err)
    elif system_platform == 'Darwin':
        try:
            python_path = path.abspath(
                path.join(sys.exec_prefix, 'bin', 'python3')
            )
            if path.isfile(python_path):
                multiprocessing.set_executable(python_path)
            else:
                python_path = path.abspath(
                    path.join(
                        sys.exec_prefix, '../Resources/bin/python3'
                    )
                )
                if path.isfile(python_path):
                    multiprocessing.set_executable(python_path)
                else:
                    qgis_utils.iface.messageBar().pushMessage(
                        'Semi-Automatic Classification Plugin',
                        QApplication.translate(
                            'semiautomaticclassificationplugin',
                            'Error. Python library not found'
                        ),
                        level=Qgis.Info
                    )
        except Exception as err:
            str(err)


def trajectories_from_qgis_point_layer(
    layer, time_field_name, trajectory_id_field, time_format
):
    # TODO: remove
    return tc_from_pt_layer(layer, time_field_name, trajectory_id_field, time_format)


def df_from_pt_layer(layer, time_field_name, trajectory_id_field):
    names = [field.name() for field in layer.fields()]
    data = []
    for feature in layer.getFeatures():
        my_dict = {}
        for i, a in enumerate(feature.attributes()):
            # QgsMessageLog.logMessage(f"{names[i]} | {time_field_name}", "Trajectools", level=Qgis.Info )
            if names[i] == time_field_name:  
                try:
                    a = a.toPyDateTime()
                except:
                    pass
            my_dict[names[i]] = a
        pt = feature.geometry().asPoint()
        my_dict["geom_x"] = pt.x()
        my_dict["geom_y"] = pt.y()
        data.append(my_dict)
    df = pd.DataFrame(data)
    return df


def tc_from_pt_layer(layer, time_field_name, trajectory_id_field, min_length=0):
    df = df_from_pt_layer(layer, time_field_name, trajectory_id_field)
    crs = CRS(int(layer.sourceCrs().geographicCrsAuthId().split(":")[1]))
    return tc_from_df(df, time_field_name, trajectory_id_field, crs, min_length)


def tc_from_df(df, time_field_name, trajectory_id_field, crs, min_length=0):
    df.drop(columns=['geometry'], inplace=True, errors='ignore'),  # Fixes Error when attribute table contains geometry column #44

    if trajectory_id_field == "trajectory_id" and "trajectory_id" not in df.columns:
        df["trajectory_id"] = 1

    tc = TrajectoryCollection(
        df,
        traj_id_col=trajectory_id_field,
        x="geom_x",
        y="geom_y",
        t=time_field_name,
        crs=crs,
        min_length=min_length,
    )
    return tc


def feature_from_gdf_row(row):
    f = QgsFeature()
    f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(row.geometry.x, row.geometry.y)))
    values = row.values.tolist()[:-1]
    for i, value in enumerate(values):
        if isinstance(value, datetime):
            values[i] = QDateTime(value)
    # for v in values:
    #    QgsMessageLog.logMessage(str(type(v)), "Trajectools", level=Qgis.Info )
    f.setAttributes(values)
    return f


def feature_from_df_row(row):
    f = QgsFeature()
    try:
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(row["geom_x"], row["geom_y"])))
    except:
        raise(KeyError(str(row)))
    values = row.values.tolist()[:-1]
    f.setAttributes(values)
    return f    
