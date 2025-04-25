import flet as ft
import pandas as pd
import numpy as np
from components.data_view import DataView
from components.visualization import VisualizationView
from components.map_view import MapView
from components.statistics import StatisticsView
from components.sidebar import Sidebar
from components.content import Content
from components.header import Header
from utils.data_loader import load_csv, load_excel

class App(ft.Control):
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.current_view = None
        self.views = {}
        self.sidebar = Sidebar()
        self.content = Content()
        self.header = Header()

    def _get_control_name(self):
        return "App"

    def build(self):
        # Créer les vues
        self.views = {
            "data": DataView(self),
            "visualization": VisualizationView(self),
            "map": MapView(self),
            "statistics": StatisticsView(self)
        }

        # Créer la mise en page principale
        return ft.Container(
            content=ft.Column(
                controls=[
                    self.header,
                    ft.Row(
                        controls=[
                            self.sidebar,
                            self.content,
                        ],
                        expand=True,
                    ),
                ],
                expand=True,
            ),
            expand=True,
        )

    def switch_view(self, view_name: str):
        """Change la vue actuelle"""
        if view_name in self.views:
            self.current_view = view_name
            self.content.update_content(self.views[view_name])
            self.update() 