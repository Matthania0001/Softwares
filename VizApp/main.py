import flet as ft
from components.app import App
from components.data_import_view import DataImportView
from components.visualization import VisualizationView
from components.statistics import StatisticsView
from components.map_view import MapView

def main(page: ft.Page):
    # Page configuration
    page.title = "VizApp"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 800
    page.window_min_height = 600

    # Create the main app first
    app = App()

    # Create views with the app instance
    data_import_view = DataImportView()
    visualization_view = VisualizationView(app)
    statistics_view = StatisticsView(app)
    map_view = MapView(app)

    # Add views to the page
    page.add(app)

    # Handle data update events
    def handle_data_update(e):
        data = e.data
        visualization_view.update_data(data)
        statistics_view.update_data(data)
        map_view.update_data(data)

    # Handle view change events
    def handle_view_change(e):
        view_name = e.data
        if view_name == "data_import":
            app.content.update_content(data_import_view)
        elif view_name == "visualization":
            app.content.update_content(visualization_view)
        elif view_name == "statistics":
            app.content.update_content(statistics_view)
        elif view_name == "map":
            app.content.update_content(map_view)

    # Add event handlers
    page.event_handlers["data_update"] = handle_data_update
    page.event_handlers["view_change"] = handle_view_change

    # Update the page
    page.update()

# Run the app
ft.app(target=main) 