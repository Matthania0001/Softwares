import flet as ft
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm

class StatisticsView(ft.Control):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def _get_control_name(self):
        return "StatisticsView"

    def build(self):
        # Onglets pour différents types d'analyses
        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Statistiques descriptives",
                    content=self._build_descriptive_stats()
                ),
                ft.Tab(
                    text="Tests statistiques",
                    content=self._build_statistical_tests()
                ),
                ft.Tab(
                    text="Corrélations",
                    content=self._build_correlation_view()
                )
            ],
            expand=True
        )

        return ft.Column(
            controls=[
                ft.Text("Analyse Statistique", size=24, weight=ft.FontWeight.BOLD),
                self.tabs
            ],
            spacing=20,
            expand=True
        )

    def _build_descriptive_stats(self):
        self.desc_stats_container = ft.Container(
            content=ft.Text("Chargez des données pour voir les statistiques descriptives"),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            expand=True
        )
        return self.desc_stats_container

    def _build_statistical_tests(self):
        self.variable1 = ft.Dropdown(
            label="Variable 1",
            width=200
        )
        self.variable2 = ft.Dropdown(
            label="Variable 2",
            width=200
        )
        self.test_type = ft.Dropdown(
            label="Type de test",
            width=200,
            options=[
                ft.dropdown.Option("ttest", "Test t de Student"),
                ft.dropdown.Option("anova", "ANOVA"),
                ft.dropdown.Option("chi2", "Test du Chi²"),
                ft.dropdown.Option("normality", "Test de normalité")
            ]
        )
        self.test_results = ft.Container(
            content=ft.Text("Sélectionnez des variables et un test"),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            expand=True
        )

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self.variable1,
                        self.variable2,
                        self.test_type,
                        ft.ElevatedButton(
                            "Exécuter le test",
                            on_click=self._run_statistical_test
                        )
                    ],
                    wrap=True,
                    spacing=20
                ),
                self.test_results
            ],
            spacing=20,
            expand=True
        )

    def _build_correlation_view(self):
        self.correlation_container = ft.Container(
            content=ft.Text("Chargez des données pour voir la matrice de corrélation"),
            padding=20,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            expand=True
        )
        return self.correlation_container

    def _run_statistical_test(self, e):
        if not self.app.current_data is not None:
            return

        df = self.app.current_data
        var1 = self.variable1.value
        var2 = self.variable2.value
        test = self.test_type.value

        try:
            result_text = ""
            if test == "ttest":
                stat, pval = stats.ttest_ind(df[var1], df[var2])
                result_text = f"Test t de Student:\nStatistique = {stat:.4f}\np-valeur = {pval:.4f}"
            
            elif test == "anova":
                groups = [group for _, group in df.groupby(var2)[var1]]
                stat, pval = stats.f_oneway(*groups)
                result_text = f"ANOVA:\nStatistique F = {stat:.4f}\np-valeur = {pval:.4f}"
            
            elif test == "chi2":
                contingency = pd.crosstab(df[var1], df[var2])
                stat, pval, dof, expected = stats.chi2_contingency(contingency)
                result_text = f"Test du Chi²:\nStatistique = {stat:.4f}\np-valeur = {pval:.4f}\nDegrés de liberté = {dof}"
            
            elif test == "normality":
                stat, pval = stats.normaltest(df[var1])
                result_text = f"Test de normalité:\nStatistique = {stat:.4f}\np-valeur = {pval:.4f}"

            self.test_results.content = ft.Text(result_text)
            self.test_results.update()

        except Exception as e:
            self.test_results.content = ft.Text(f"Erreur: {str(e)}")
            self.test_results.update()

    def update_data(self, df: pd.DataFrame):
        """Met à jour l'affichage avec un nouveau DataFrame"""
        # Mise à jour des statistiques descriptives
        desc_stats = df.describe()
        desc_stats_text = "Statistiques descriptives:\n\n" + str(desc_stats)
        self.desc_stats_container.content = ft.Text(desc_stats_text, selectable=True)

        # Mise à jour des options pour les tests statistiques
        columns = list(df.columns)
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        self.variable1.options = [ft.dropdown.Option(col) for col in numeric_columns]
        self.variable2.options = [ft.dropdown.Option(col) for col in columns]

        # Mise à jour de la matrice de corrélation
        corr_matrix = df.select_dtypes(include=[np.number]).corr()
        corr_text = "Matrice de corrélation:\n\n" + str(corr_matrix)
        self.correlation_container.content = ft.Text(corr_text, selectable=True)

        self.update() 