# -*- coding: utf-8 -*-

"""
***************************************************************************
    trajectoriesFromPointLayer.py
    ---------------------
    Date                 : December 2018
    Copyright            : (C) 2018 by Anita Graser
    Email                : anitagraser@gmx.at
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import os
import sys 

from shapely.geometry import Polygon

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsField,QgsFields,
                       QgsGeometry,
                       QgsFeature,
                       QgsFeatureSink,
                       QgsFeatureRequest,
                       QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterString,
                       QgsProcessingParameterExtent,                       
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterEnum,
                       QgsWkbTypes
                      )

sys.path.append("..")

from .qgisUtils import tc_from_pt_layer

pluginPath = os.path.dirname(__file__)


class ClipTrajectoriesByExtentAlgorithm(QgsProcessingAlgorithm):
    # script parameters
    INPUT = 'INPUT'
    TRAJ_ID_FIELD = 'OBJECT_ID_FIELD'
    TIMESTAMP_FIELD = 'TIMESTAMP_FIELD'
    TIMESTAMP_FORMAT = 'TIMESTAMP_FORMAT'
    EXTENT = 'EXTENT'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super().__init__()

    def name(self):
        return "clip_traj_extent"

    def icon(self):
        return QIcon(os.path.join(pluginPath, "icons", "icon.png"))

    def tr(self, text):
        return QCoreApplication.translate("clip_traj_extent", text)

    def displayName(self):
        return self.tr("Clip trajectories by extent")

    def group(self):
        return self.tr("Overlay")

    def groupId(self):
        return "TrajectoryOverlay"

    def shortHelpString(self):
        return self.tr(
            "<p>Creates a LineStringM layer from points grouped by trajectory ID field, " + 
            "ordered by time, and clipped by the provided extent.</p><p>Temporal information " + 
            "is stored as unixtime in the m value.</p>")

    def helpUrl(self):
        return "https://github.com/anitagraser/processing-trajectory"

    def createInstance(self):
        return type(self)()

    def initAlgorithm(self, config=None):
        # input layer
        self.addParameter(QgsProcessingParameterFeatureSource(
            name=self.INPUT,
            description=self.tr("Input point layer"),
            types=[QgsProcessing.TypeVectorPoint]))
        # fields
        self.addParameter(QgsProcessingParameterField(
            name=self.TRAJ_ID_FIELD,
            description=self.tr("Trajectory ID field"),
            defaultValue="trajectory_id",
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.Any,
            allowMultiple=False,
            optional=False))
        self.addParameter(QgsProcessingParameterField(
            name=self.TIMESTAMP_FIELD,
            description=self.tr("Timestamp field"),
            defaultValue="t",
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.Any,
            allowMultiple=False,
            optional=False))
        self.addParameter(QgsProcessingParameterString(
            name=self.TIMESTAMP_FORMAT,
            description=self.tr("Timestamp format"),
            defaultValue="%Y-%m-%d %H:%M:%S+00",
            optional=False))
        self.addParameter(QgsProcessingParameterExtent(
            name=self.EXTENT,
            description=self.tr("Extent"),
            optional=False))
        # output layer
        self.addParameter(QgsProcessingParameterFeatureSink(
            name=self.OUTPUT,
            description=self.tr("Clipped trajectories"),
            type=QgsProcessing.TypeVectorLine))

    def processAlgorithm(self, parameters, context, feedback):
        input_layer = self.parameterAsSource(parameters, self.INPUT, context)
        traj_id_field = self.parameterAsFields(parameters, self.TRAJ_ID_FIELD, context)[0]
        timestamp_field = self.parameterAsFields(parameters, self.TIMESTAMP_FIELD, context)[0]
        timestamp_format = self.parameterAsString(parameters, self.TIMESTAMP_FORMAT, context)
        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        
        output_fields = QgsFields()
        output_fields.append(QgsField(traj_id_field, QVariant.String))
        
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               output_fields, 
                                               QgsWkbTypes.LineStringM, 
                                               input_layer.sourceCrs())
        
        tc = tc_from_pt_layer(input_layer, timestamp_field, traj_id_field, timestamp_format)

        xmin = extent.xMinimum()
        xmax = extent.xMaximum()
        ymin = extent.yMinimum()
        ymax = extent.yMaximum()
        polygon = Polygon([(xmin,ymin), (xmin,ymax), (xmax,ymax), (xmax,ymin), (xmin,ymin)])
        
        tc = tc.clip(polygon)
            
        for traj in tc.trajectories:
            line = QgsGeometry.fromWkt(traj.to_linestringm_wkt())
            f = QgsFeature()
            f.setGeometry(line)
            f.setAttributes([traj.id])
            sink.addFeature(f, QgsFeatureSink.FastInsert)
        
        # default return type for function
        return {self.OUTPUT: dest_id}
