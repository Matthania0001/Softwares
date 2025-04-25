import flet as ft
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots

class VisualizationView(ft.Control):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.current_plot = None

    def _get_control_name(self):
        return "VisualizationView"

    def build(self):
        # Contrôles pour la configuration du graphique
        self.plot_type = ft.Dropdown(
            label="Type de graphique",
            options=[
                ft.dropdown.Option("scatter", "Nuage de points"),
                ft.dropdown.Option("line", "Ligne"),
                ft.dropdown.Option("bar", "Barres"),
                ft.dropdown.Option("box", "Boîte à moustaches"),
                ft.dropdown.Option("histogram", "Histogramme"),
                ft.dropdown.Option("pie", "Camembert"),
                ft.dropdown.Option("heatmap", "Carte de chaleur"),
            ],
            width=200,
            on_change=self._update_plot
        )

        self.x_axis = ft.Dropdown(
            label="Axe X",
            width=200,
            on_change=self._update_plot
        )

        self.y_axis = ft.Dropdown(
            label="Axe Y",
            width=200,
            on_change=self._update_plot
        )

        self.color_by = ft.Dropdown(
            label="Couleur par",
            width=200,
            on_change=self._update_plot
        )

        # Zone d'affichage du graphique
        self.plot_container = ft.Container(
            content=ft.Text("Sélectionnez des données pour commencer"),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            expand=True
        )

        return ft.Column(
            controls=[
                ft.Text("Visualisation", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        self.plot_type,
                        self.x_axis,
                        self.y_axis,
                        self.color_by,
                    ],
                    wrap=True,
                    spacing=20
                ),
                self.plot_container
            ],
            spacing=20,
            expand=True
        )

    def _update_plot(self, e=None):
        if not self.app.current_data is not None:
            return

        df = self.app.current_data
        plot_type = self.plot_type.value
        x = self.x_axis.value
        y = self.y_axis.value
        color = self.color_by.value

        if not all([plot_type, x, y]):
            return

        fig = None

        try:
            if plot_type == "scatter":
                fig = px.scatter(df, x=x, y=y, color=color)
            elif plot_type == "line":
                fig = px.line(df, x=x, y=y, color=color)
            elif plot_type == "bar":
                fig = px.bar(df, x=x, y=y, color=color)
            elif plot_type == "box":
                fig = px.box(df, x=x, y=y, color=color)
            elif plot_type == "histogram":
                fig = px.histogram(df, x=x, color=color)
            elif plot_type == "pie":
                fig = px.pie(df, values=y, names=x)
            elif plot_type == "heatmap":
                pivot_table = pd.pivot_table(df, values=y, index=x, columns=color, aggfunc='mean')
                fig = px.imshow(pivot_table)

            if fig:
                # Configuration du layout
                fig.update_layout(
                    template="plotly_white",
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=600
                )

                # Convertir en HTML
                plot_html = fig.to_html(include_plotlyjs='cdn', full_html=False)
                
                # Afficher dans un WebView
                self.plot_container.content = ft.WebView(
                    html=plot_html,
                    expand=True
                )
                self.plot_container.update()

        except Exception as e:
            self.plot_container.content = ft.Text(f"Erreur: {str(e)}")
            self.plot_container.update()

    def update_data(self, df: pd.DataFrame):
        """Met à jour les options des menus déroulants en fonction des données"""
        columns = list(df.columns)
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(exclude=[np.number]).columns.tolist()

        self.x_axis.options = [ft.dropdown.Option(col) for col in columns]
        self.y_axis.options = [ft.dropdown.Option(col) for col in numeric_columns]
        self.color_by.options = [ft.dropdown.Option(col) for col in categorical_columns]

        self.update() 