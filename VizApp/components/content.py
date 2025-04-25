import flet as ft

class Content(ft.Control):
    def __init__(self):
        super().__init__()
        self.current_content = None

    def _get_control_name(self):
        return "Content"

    def update_content(self, new_content):
        self.current_content = new_content
        self.update()

    def build(self):
        return ft.Container(
            content=self.current_content or ft.Text(
                "Select a view from the sidebar",
                size=20,
                color=ft.colors.GREY_600,
            ),
            expand=True,
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=ft.border_radius.all(5),
        ) 