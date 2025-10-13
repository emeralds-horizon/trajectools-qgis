import zipfile
import io
import pandas as pd
import datetime
from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsProject,
    QgsPointXY,
    QgsGeometry,
    QgsFeature,
    QgsVectorLayer,
    QgsField,
    QgsFields,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem
)

# Path to the ZIP archive
zip_path = r'C:\Users\...\FCD.zip'

# Reproject map extent to WGS84
canvas = iface.mapCanvas()
src_crs = canvas.mapSettings().destinationCrs()
wgs84_crs = QgsCoordinateReferenceSystem('EPSG:4326')
transform = QgsCoordinateTransform(src_crs, wgs84_crs, QgsProject.instance())
extent_wgs84 = transform.transformBoundingBox(canvas.extent())
print(extent_wgs84)

# Create in-memory layer
mem_layer = QgsVectorLayer("Point?crs=EPSG:4326", "FCD", "memory")
prov = mem_layer.dataProvider()
fields = QgsFields()
fields.append(QgsField("device_id", QVariant.String))
fields.append(QgsField("timestamp", QVariant.String))
fields.append(QgsField("heading", QVariant.Double))
fields.append(QgsField("speed", QVariant.Double))
prov.addAttributes(fields)
mem_layer.updateFields()

i=0

with zipfile.ZipFile(zip_path, 'r') as z:
    for filename in z.namelist():
        print(filename)
        if filename.endswith('.csv'):
            with z.open(filename) as file:
               
                    df = pd.read_csv(file, encoding='utf-8', sep=';')
                    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')  # convert to float

                    # Filter by WGS84 extent
                    df = df.dropna(subset=['latitude', 'longitude'])
                    df = df[
                        (df['latitude'].between(extent_wgs84.yMinimum(), extent_wgs84.yMaximum())) &
                        (df['longitude'].between(extent_wgs84.xMinimum(), extent_wgs84.xMaximum()))
                    ]

                    # Add features
                    for _, row in df.iterrows():
                        point = QgsPointXY(row['longitude'], row['latitude'])
                        feat = QgsFeature()
                        feat.setGeometry(QgsGeometry.fromPointXY(point))
                        dt = datetime.datetime.utcfromtimestamp(row['timestamp'])
                        feat.setAttributes([
                            row['device_id'],
                            dt.strftime('%Y-%m-%d %H:%M:%S'),
                            float(row['heading']),
                            float(row['speed'])
                        ])
                        prov.addFeature(feat)
                    
            i+=1
            

# Finalize
mem_layer.updateExtents()
QgsProject.instance().addMapLayer(mem_layer)
print("Loaded points within extent.")
