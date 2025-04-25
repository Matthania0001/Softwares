import flet as ft
import pandas as pd
import openpyxl

class DataImportView(ft.Control):
    def __init__(self):
        super().__init__()
        self.file_picker = ft.FilePicker()
        self.data = None
        self.preview_table = ft.DataTable(
            columns=[],
            rows=[],
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
        )

    def _get_control_name(self):
        return "DataImportView"

    def build(self):
        return ft.Column(
            controls=[
                ft.Text("Import Data", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Import CSV",
                            icon=ft.icons.UPLOAD_FILE,
                            on_click=lambda _: self.file_picker.pick_files(
                                allowed_extensions=["csv"],
                                on_result=self._handle_file_pick,
                            ),
                        ),
                        ft.ElevatedButton(
                            "Import Excel",
                            icon=ft.icons.UPLOAD_FILE,
                            on_click=lambda _: self.file_picker.pick_files(
                                allowed_extensions=["xlsx", "xls"],
                                on_result=self._handle_file_pick,
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=self.preview_table,
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.colors.WHITE,
                    expand=True,
                ),
            ],
            expand=True,
        )

    def _handle_file_pick(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return

        file_path = e.files[0].path
        file_extension = file_path.split(".")[-1].lower()

        try:
            if file_extension == "csv":
                self.data = pd.read_csv(file_path)
            elif file_extension in ["xlsx", "xls"]:
                self.data = pd.read_excel(file_path)

            # Update preview table
            self._update_preview_table()
            
            # Dispatch event to update other views
            self.page.dispatch("data_update", {"data": self.data})

        except Exception as e:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error loading file: {str(e)}"))
            )

    def _update_preview_table(self):
        if self.data is None:
            return

        # Update columns
        self.preview_table.columns = [
            ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD))
            for col in self.data.columns
        ]

        # Update rows (show first 100 rows)
        rows = []
        for _, row in self.data.head(100).iterrows():
            cells = [ft.DataCell(ft.Text(str(val))) for val in row]
            rows.append(ft.DataRow(cells=cells))

        self.preview_table.rows = rows
        self.update() 