import flet as ft
from utils.data_loader import load_csv, load_excel

class Sidebar(ft.Control):
    def __init__(self):
        super().__init__()
        self.nav_buttons = {
            "Data Import": ft.Icons.UPLOAD_FILE,
            "Data Overview": ft.Icons.TABLE_CHART,
            "Visualization": ft.Icons.BAR_CHART,
            "Statistics": ft.Icons.CALCULATE,
            "Maps": ft.Icons.MAP,
        }
        self.file_picker = None

    def _get_control_name(self):
        return "Sidebar"

    def build(self):
        # Créer le FilePicker
        self.file_picker = ft.FilePicker()
        self.page.overlay.append(self.file_picker)
        self.page.update()

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Navigation",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE_700,
                    ),
                    ft.Divider(),
                    *[
                        ft.ElevatedButton(
                            text=name,
                            icon=icon,
                            on_click=lambda e, name=name: self.page.dispatch(
                                "view_change", {"view": name.lower().replace(" ", "_")}
                            ),
                            style=ft.ButtonStyle(
                                color=ft.colors.BLUE_700,
                                bgcolor=ft.colors.WHITE,
                                elevation=0,
                            ),
                            width=200,
                        )
                        for name, icon in self.nav_buttons.items()
                    ],
                ],
                spacing=10,
            ),
            width=250,
            padding=20,
            bgcolor=ft.colors.GREY_100,
            border_radius=ft.border_radius.all(5),
        ) 