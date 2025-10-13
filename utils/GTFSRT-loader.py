from datetime import datetime, timedelta
import os
import tempfile
import minio
import pyarrow as pa
import pyarrow.parquet as pq
from pytz import timezone
import pandas as pd


def fetch_data(
        start_date,
        end_date,
        feed_path: str = "data/york/VehiclePosition/",
        access_key=os.environ.get("MINIO_ACCESS_KEY"),
        secret_key=os.environ.get("MINIO_SECRET_KEY"),
        timezone_str="Europe/Brussels",
) -> pd.DataFrame:
    client = minio.Minio(
        "minio-api.apps.emeralds.ari-aidata.eu",
        access_key=access_key,  
        secret_key=secret_key,  
        secure=True,
    )

    time_zone = timezone(timezone_str)

    start_date = time_zone.localize(
        start_date,
    )
    end_date = time_zone.localize(
        end_date,
    )
    bucket = "public"
    days_of_request = []
    current_date = start_date
    while current_date < end_date:
        days_of_request.append(current_date.strftime("%Y-%m-%d"))
        current_date = current_date + timedelta(days=1)
    service_path = feed_path

    days_in_cloud = list(client.list_objects(bucket, service_path))
    days_in_cloud_names = [day.object_name.split("/")[-2] for day in days_in_cloud]

    def parse_date(date, file_name):
        start_time = file_name.split("/")[-1].split("_")[0]
        end_time = (
            file_name.split("/")[-1]
            .split("_")[2]
            .replace(".parquet", "")
        )

        date_str = date.strftime("%Y-%m-%d")
        file_start_date = datetime.strptime(
            date_str + "_" + start_time, "%Y-%m-%d_%H-%M-%S"
        )
        file_end_date = datetime.strptime(
            date_str + "_" + end_time, "%Y-%m-%d_%H-%M-%S"
        )

        if file_start_date == file_end_date:
            file_end_date = file_start_date + timedelta(days=1)

        return file_start_date, file_end_date

    with tempfile.TemporaryDirectory() as tmpdir:
        for day in days_of_request:
            if day in days_in_cloud_names:
                day_path = service_path + day + "/"
                for file in client.list_objects(bucket, day_path):
                    current_date = datetime.strptime(day, "%Y-%m-%d")
                    file_start_date, file_end_date = parse_date(current_date, file.object_name)
                    file_start_date = time_zone.localize(file_start_date, is_dst=None)
                    file_end_date = time_zone.localize(file_end_date, is_dst=None)

                    if end_date <= file_start_date or start_date >= file_end_date:
                        continue

                    client.fget_object(
                        bucket,
                        file.object_name,
                        tmpdir
                        + "/"
                        + f"{file_start_date.strftime('%Y-%m-%d_%H-%M-%S')}_{file_end_date.strftime('%Y-%m-%d_%H-%M-%S')}.parquet",
                    )

        table = None

        for file in os.listdir(tmpdir):
            current_table = pq.read_table(
                tmpdir + "/" + file,
            )

            if table is None:
                table = current_table
            else:
                table = pa.concat_tables([table, current_table])

    return table.to_pandas()  # Convert to pandas DataFrame for easier handling


# Import necessary QGIS modules
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsCoordinateReferenceSystem,
)

# Reproject map extent to WGS84
canvas = iface.mapCanvas()
src_crs = canvas.mapSettings().destinationCrs()
wgs84_crs = QgsCoordinateReferenceSystem('EPSG:4326')
transform = QgsCoordinateTransform(src_crs, wgs84_crs, QgsProject.instance())
extent_wgs84 = transform.transformBoundingBox(canvas.extent())
print(extent_wgs84)


t_start = datetime(2025,7,22,0)
t_end = datetime(2025,8,13,0)

df = fetch_data(t_start, t_end)

# Filter by WGS84 extent
df = df.dropna(subset=['position_latitude', 'position_longitude'])
df = df[
    (df['position_latitude'].between(extent_wgs84.yMinimum(), extent_wgs84.yMaximum())) &
    (df['position_longitude'].between(extent_wgs84.xMinimum(), extent_wgs84.xMaximum()))
]

t = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_path = f'C:/temp/york_{t}.csv'

df.to_csv(csv_path)
# ,entityId,fetchTime,trip_tripId,trip_routeId,trip_directionId,trip_startTime,trip_startDate,trip_scheduleRelationship,trip_modifiedTrip,vehicle_id,vehicle_label,vehicle_licensePlate,vehicle_wheelchairAccessible,position_latitude,position_longitude,position_bearing,position_odometer,position_speed,currentStopSequence,stopId,currentStatus,timestamp,congestionLevel,occupancyStatus,occupancyPercentage,multiCarriageDetails

# Define URI: file path, X and Y fields, and delimiter
uri = f'file:///{csv_path}?type=csv&delimiter=,&maxFields=10000&detectTypes=yes&xField=position_longitude&yField=position_latitude&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=yes'

# Create the vector layer from CSV
csv_layer = QgsVectorLayer(uri, f"GTFS-RT {t_start} to {t_end}", "delimitedtext")

# Check if the layer is valid
if csv_layer.isValid():
    # Add layer to the current project
    QgsProject.instance().addMapLayer(csv_layer)
    print("CSV loaded successfully!")
else:
    print("Failed to load the CSV layer.")
