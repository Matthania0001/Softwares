import flet as ft

class Header(ft.Control):
    def __init__(self):
        super().__init__()
        self.title = ft.Text(
            "VizApp - Data Visualization & Analysis",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.WHITE,
        )

    def _get_control_name(self):
        return "Header"

    def build(self):
        return ft.Container(
            content=ft.Row(
                controls=[
                    self.title,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=20,
            bgcolor=ft.colors.BLUE_700,
            border_radius=ft.border_radius.all(5),
        ) 