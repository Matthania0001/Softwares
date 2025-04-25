import flet as ft
import pandas as pd
import numpy as np

class DataView(ft.Control):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.df = None

    def _get_control_name(self):
        return "DataView"

    def build(self):
        self.data_table = ft.DataTable(
            columns=[],
            rows=[],
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
            column_spacing=50,
        )

        return ft.Column(
            controls=[
                ft.Text("Aperçu des données", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        ft.Text("Dimensions: "),
                        self._create_info_text("0 lignes × 0 colonnes")
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.Text("Types de données: "),
                        self._create_info_text("Aucune donnée")
                    ]
                ),
                ft.Divider(),
                ft.Container(
                    content=self.data_table,
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.colors.WHITE,
                )
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    def _create_info_text(self, text: str):
        return ft.Container(
            content=ft.Text(text),
            bgcolor=ft.colors.BLUE_50,
            padding=10,
            border_radius=5
        )

    def update_data(self, df: pd.DataFrame):
        """Met à jour l'affichage avec un nouveau DataFrame"""
        self.df = df
        self.app.current_data = df

        # Mise à jour des informations
        dimensions = f"{df.shape[0]} lignes × {df.shape[1]} colonnes"
        types = ", ".join([f"{col}: {str(dtype)}" for col, dtype in df.dtypes.items()])

        # Mise à jour des colonnes
        self.data_table.columns = [
            ft.DataColumn(
                ft.Text(col, weight=ft.FontWeight.BOLD)
            ) for col in df.columns
        ]

        # Mise à jour des lignes (afficher les 100 premières lignes)
        rows = []
        for _, row in df.head(100).iterrows():
            cells = [
                ft.DataCell(ft.Text(str(val)))
                for val in row
            ]
            rows.append(ft.DataRow(cells=cells))
        self.data_table.rows = rows

        self.update() 