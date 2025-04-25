import flet as ft
import folium
import pandas as pd
import numpy as np
from folium.plugins import MarkerCluster
import tempfile
import os

class MapView(ft.Control):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.data = None
        self.lat_column = ft.Dropdown(label="Latitude Column", on_change=self.update_map)
        self.lon_column = ft.Dropdown(label="Longitude Column", on_change=self.update_map)
        self.color_column = ft.Dropdown(label="Color Column", on_change=self.update_map)
        self.map_container = ft.Container()

    def _get_control_name(self):
        return "MapView"

    def update_data(self, data):
        self.data = data
        if data is not None:
            columns = data.columns.tolist()
            self.lat_column.options = [ft.dropdown.Option(col) for col in columns]
            self.lon_column.options = [ft.dropdown.Option(col) for col in columns]
            self.color_column.options = [ft.dropdown.Option(col) for col in columns]
            self.update()

    def update_map(self, e):
        if self.data is None or self.lat_column.value is None or self.lon_column.value is None:
            return

        # Create a map centered on the mean coordinates
        lat_mean = self.data[self.lat_column.value].mean()
        lon_mean = self.data[self.lon_column.value].mean()
        m = folium.Map(location=[lat_mean, lon_mean], zoom_start=10)

        # Add markers
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in self.data.iterrows():
            lat = row[self.lat_column.value]
            lon = row[self.lon_column.value]
            
            if self.color_column.value:
                color = self._get_color(row[self.color_column.value])
            else:
                color = 'blue'

            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                popup=f"Lat: {lat:.4f}, Lon: {lon:.4f}",
            ).add_to(marker_cluster)

        # Save the map to a temporary HTML file
        m.save('temp_map.html')
        
        # Convert the map to an image
        self.map_container.content = ft.Image(
            src="temp_map.html",
            width=800,
            height=600,
        )
        self.update()

    def _get_color(self, value):
        # Simple color mapping based on value
        if isinstance(value, (int, float)):
            if value < 0:
                return 'red'
            elif value > 0:
                return 'green'
            else:
                return 'blue'
        return 'blue'

    def build(self):
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self.lat_column,
                        self.lon_column,
                        self.color_column,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),
                self.map_container,
            ],
            expand=True,
        ) 