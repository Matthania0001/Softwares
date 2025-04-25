import flet as ft
import pandas as pd
import numpy as np
from math import isnan

class SpreadsheetApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self._setup_page()
        self._init_data()
        self._build_ui()
        self._update_grid()

    def _setup_page(self):
        """Configure la page principale"""
        self.page.title = "Classeur Flet"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.padding = 10

    def _init_data(self):
        """Initialise les données avec 10 colonnes et 100 lignes"""
        self.data = pd.DataFrame(
            np.nan, 
            index=range(100), 
            columns=[self._col_to_letter(i) for i in range(10)]
        )
        self.current_cell = (0, 0)  # (row, col)

    def _col_to_letter(self, col_idx: int) -> str:
        """Convertit l'index de colonne en lettre Excel (0->A, 1->B...)"""
        return chr(65 + col_idx)

    def _build_ui(self):
        """Construit l'interface utilisateur"""
        # Barre d'outils
        self.toolbar = ft.Row(
            controls=[
                ft.IconButton(ft.icons.SAVE, on_click=self._save_data),
                ft.IconButton(ft.icons.ADD, on_click=self._add_column),
            ]
        )

        # Barre de formule
        self.formula_bar = ft.TextField(
            hint_text="Saisissez une valeur ou formule...",
            on_submit=self._update_cell_value,
            expand=True
        )

        # Grille de données
        self.data_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(col)) for col in self.data.columns],
            rows=self._create_data_rows(),
            border=ft.border.all(1),
            vertical_lines=ft.border.BorderSide(1),
            horizontal_lines=ft.border.BorderSide(1),
        )

        # Conteneur principal
        self.main_container = ft.Column(
            controls=[
                self.toolbar,
                self.formula_bar,
                ft.Container(
                    content=ft.ListView(
                        controls=[self.data_table],
                        expand=True,
                    ),
                    expand=True,
                ),
            ],
            expand=True,
        )

        self.page.add(self.main_container)

    def _create_data_rows(self):
        """Crée les lignes de données pour la table"""
        rows = []
        for row_idx in range(len(self.data)):
            cells = []
            for col_idx in range(len(self.data.columns)):
                value = self.data.iat[row_idx, col_idx]
                cells.append(
                    ft.DataCell(
                        ft.Text("" if pd.isna(value) else str(value)),
                        on_tap=lambda e, r=row_idx, c=col_idx: self._cell_selected(r, c),
                    )
                )
            rows.append(ft.DataRow(cells=cells))
        return rows

    def _cell_selected(self, row: int, col: int):
        """Gère la sélection d'une cellule"""
        self.current_cell = (row, col)
        value = self.data.iat[row, col]
        self.formula_bar.value = "" if pd.isna(value) else str(value)
        self.page.update()

    def _update_cell_value(self, e):
        """Met à jour la valeur d'une cellule"""
        row, col = self.current_cell
        new_value = self.formula_bar.value
        
        try:
            # Essaye de convertir en nombre si possible
            num_value = float(new_value)
            self.data.iat[row, col] = num_value
        except ValueError:
            # Garde comme texte si ce n'est pas un nombre
            self.data.iat[row, col] = new_value if new_value else np.nan
        
        self._update_grid()

    def _update_grid(self):
        """Met à jour toute la grille"""
        self.data_table.rows = self._create_data_rows()
        self.page.update()

    def _add_column(self, e):
        """Ajoute une nouvelle colonne"""
        new_col = self._col_to_letter(len(self.data.columns))
        self.data[new_col] = np.nan
        self.data_table.columns.append(ft.DataColumn(ft.Text(new_col)))
        self._update_grid()

    def _save_data(self, e):
        """Sauvegarde les données (exemple)"""
        print("Données actuelles:")
        print(self.data.head())
        self.page.snack_bar = ft.SnackBar(ft.Text("Données sauvegardées (voir console)"))
        self.page.snack_bar.open = True
        self.page.update()

def main(page: ft.Page):
    app = SpreadsheetApp(page)

if __name__ == "__main__":
    ft.app(target=main)