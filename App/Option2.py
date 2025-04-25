import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableView, QTabWidget, 
                            QToolBar, QStatusBar, QMenu, QLineEdit, QLabel, 
                            QHBoxLayout, QWidget, QVBoxLayout, QFrame, QDockWidget,
                            QStyledItemDelegate, QStyleOptionViewItem, QStyle)
from PyQt6.QtGui import (QStandardItemModel, QStandardItem, QAction, QIcon, 
                         QColor, QFont, QPainter)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint
from PyQt6.QtCharts import QChart, QChartView, QLineSeries
from PyQt6.QtWidgets import QComboBox
import pandas as pd
import numpy as np

class ModernSpreadsheetDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        # Style personnalisé pour les cellules
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, QColor("#5FC7E9FF"))
            painter.setPen(Qt.GlobalColor.white)
        else:
            if index.row() % 2 == 0:
                painter.fillRect(option.rect, QColor("#ffffff"))
            else:
                painter.fillRect(option.rect, QColor("#f8f9fa"))
            painter.setPen(Qt.GlobalColor.black)
        
        # Dessin du texte
        text = index.data(Qt.ItemDataRole.DisplayRole)
        painter.drawText(option.rect.adjusted(4, 0, -4, 0), 
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 
                        str(text if text else ""))

class ModernSpreadsheetApp(QMainWindow):
    formula_submitted = pyqtSignal(str, int, int)  # formule, row, col

    def __init__(self):
        super().__init__()
        
        # Configuration initiale
        self.setWindowTitle("NexusSheet Pro")
        self.setGeometry(100, 100, 1400, 900)
        
        # Style et apparence
        self._setup_style()
        
        # Données et modèle
        self._setup_data_model()
        
        # Interface utilisateur
        self._setup_ui()
        
        # Connecteurs
        self._connect_signals()
        
        # Initialisation
        self._add_new_sheet("Feuille1")
        self._update_status_bar()

    def _setup_style(self):
        """Configure le style global de l'application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QToolBar {
                background-color: #ffffff;
                border: none;
                border-bottom: 1px solid #dee2e6;
                spacing: 5px;
                padding: 4px;
            }
            QToolButton {
                padding: 6px 12px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #e9ecef;
            }
            QTabBar::tab {
                padding: 8px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
                background-color: #f1f3f5;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #1a73e8;
            }
            QDockWidget {
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(undock.png);
            }
            QDockWidget::title {
                padding: 4px;
                background-color: #f1f3f5;
            }
        """)
        
        # Police moderne
        self.font = QFont("Segoe UI", 10)
        QApplication.setFont(self.font)

    def _setup_data_model(self):
        """Initialise le modèle de données"""
        self.models = {}  # Dictionnaire pour stocker les modèles par feuille
        self.current_model = QStandardItemModel(10000, 26)  # 10,000 lignes, 26 colonnes
        self._setup_headers(self.current_model)
        self.formulas = {}  # Pour stocker les formules

    def _setup_headers(self, model):
        """Configure les en-têtes de colonnes"""
        for col in range(model.columnCount()):
            # Convertit l'index de colonne en notation Excel (A, B, ..., Z, AA, AB, etc.)
            if col < 26:
                header = chr(65 + col)
            else:
                header = chr(64 + col//26) + chr(65 + col%26)
            model.setHorizontalHeaderItem(col, QStandardItem(header))
        
        # En-têtes de lignes
        for row in range(model.rowCount()):
            model.setVerticalHeaderItem(row, QStandardItem(str(row + 1)))

    def _setup_ui(self):
        """Configure l'interface utilisateur principale"""
        # Conteneur central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barres d'outils
        self._setup_main_toolbar()
        self._setup_formula_bar()
        main_layout.addWidget(self.main_toolbar)
        main_layout.addWidget(self.formula_toolbar)
        
        # Onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        main_layout.addWidget(self.tab_widget)
        
        # Panneau latéral
        self._setup_side_panel()
        
        # Barre d'état
        self._setup_status_bar()

    def _setup_main_toolbar(self):
        """Configure la barre d'outils principale"""
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setIconSize(QSize(24, 24))
        self.main_toolbar.setMovable(False)
        self.addToolBar(self.main_toolbar)
        
        # Actions principales
        actions = [
            ("Nouveau", "document-new", self._new_file, "Ctrl+N"),
            ("Ouvrir", "document-open", self._open_file, "Ctrl+O"),
            ("Enregistrer", "document-save", self._save_file, "Ctrl+S"),
            None,  # Séparateur
            ("Couper", "edit-cut", self._cut, "Ctrl+X"),
            ("Copier", "edit-copy", self._copy, "Ctrl+C"),
            ("Coller", "edit-paste", self._paste, "Ctrl+V"),
            None,
            ("Annuler", "edit-undo", self._undo, "Ctrl+Z"),
            ("Rétablir", "edit-redo", self._redo, "Ctrl+Y"),
            None,
            ("Graphique", "insert-chart", self._insert_chart, None),
            ("Fonctions", "math-function", self._show_functions, None)
        ]
        
        for action in actions:
            if action is None:
                self.main_toolbar.addSeparator()
            else:
                name, icon_name, handler, shortcut = action
                act = QAction(QIcon.fromTheme(icon_name), name, self)
                act.triggered.connect(handler)
                if shortcut:
                    act.setShortcut(shortcut)
                self.main_toolbar.addAction(act)

    def _setup_formula_bar(self):
        """Configure la barre de formule avancée"""
        self.formula_toolbar = QToolBar()
        self.formula_toolbar.setFixedHeight(40)
        
        formula_container = QWidget()
        formula_layout = QHBoxLayout(formula_container)
        formula_layout.setContentsMargins(5, 0, 5, 0)
        
        # Label "fx"
        fx_label = QLabel("fx")
        fx_label.setStyleSheet("font-weight: bold; color: #1a73e8;")
        
        # Champ de formule
        self.formula_input = QLineEdit()
        self.formula_input.setPlaceholderText("Saisissez une formule (ex: =SOMME(A1:A10))...")
        self.formula_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
                font: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #86b7fe;
                box-shadow: 0 0 0 0.25rem rgba(26, 115, 232, 0.25);
            }
        """)
        
        formula_layout.addWidget(fx_label)
        formula_layout.addWidget(self.formula_input)
        self.formula_toolbar.addWidget(formula_container)

    def _setup_side_panel(self):
        """Configure le panneau latéral pour les propriétés/fonctions"""
        self.side_panel = QDockWidget("Outils", self)
        self.side_panel.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | 
                                   QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        
        panel_content = QWidget()
        panel_layout = QVBoxLayout(panel_content)
        
        # Groupe Propriétés
        properties_group = QFrame()
        properties_group.setFrameShape(QFrame.Shape.StyledPanel)
        properties_layout = QVBoxLayout(properties_group)
        properties_layout.addWidget(QLabel("<b>Propriétés de la cellule</b>"))
        
        # Ajouter des contrôles de propriétés
        self.cell_format_combo = self._create_combo(["Général", "Nombre", "Pourcentage", "Date"])
        properties_layout.addWidget(QLabel("Format:"))
        properties_layout.addWidget(self.cell_format_combo)
        
        panel_layout.addWidget(properties_group)
        panel_layout.addStretch()
        
        self.side_panel.setWidget(panel_content)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.side_panel)

    def _create_combo(self, items):
        """Crée une combobox stylisée"""
        combo = QComboBox()
        combo.addItems(items)
        combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ced4da;
                border-radius: 4px;
            }
            QComboBox:hover {
                border-color: #adb5bd;
            }
        """)
        return combo

    def _setup_status_bar(self):
        """Configure la barre d'état améliorée"""
        self.status_bar = self.statusBar()
        
        # Widgets dans la barre d'état
        self.cell_position = QLabel("A1")
        self.cell_content = QLabel("")
        self.sheet_info = QLabel("Feuille1")
        
        self.status_bar.addPermanentWidget(self.cell_position)
        self.status_bar.addPermanentWidget(self.cell_content, 1)
        self.status_bar.addPermanentWidget(self.sheet_info)

    def _add_new_sheet(self, name):
        """Ajoute une nouvelle feuille avec une table moderne"""
        table = QTableView()
        table.setModel(self.current_model)
        
        # Configuration avancée
        table.setAlternatingRowColors(False)  # Nous gérons nous-mêmes les couleurs
        table.setItemDelegate(ModernSpreadsheetDelegate())
        table.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        table.setSelectionMode(QTableView.SelectionMode.ContiguousSelection)
        
        # Stocke le modèle
        self.models[name] = self.current_model
        
        # Ajoute l'onglet
        self.tab_widget.addTab(table, name)
        
        # Connecte les signaux
        table.selectionModel().selectionChanged.connect(self._update_status_bar)
        
        return table

    def _update_status_bar(self):
        """Met à jour la barre d'état avec les infos actuelles"""
        current_table = self.tab_widget.currentWidget()
        if current_table and isinstance(current_table, QTableView):
            selection = current_table.selectionModel()
            if selection.hasSelection():
                index = selection.currentIndex()
                col_name = self.current_model.headerData(index.column(), Qt.Orientation.Horizontal)
                self.cell_position.setText(f"{col_name}{index.row() + 1}")
                self.cell_content.setText(str(self.current_model.data(index)))
        
        current_tab = self.tab_widget.currentIndex()
        if current_tab >= 0:
            self.sheet_info.setText(self.tab_widget.tabText(current_tab))

    def _connect_signals(self):
        """Connecte tous les signaux et slots"""
        self.formula_input.returnPressed.connect(self._apply_formula)
        self.tab_widget.currentChanged.connect(self._tab_changed)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.formula_submitted.connect(self._handle_formula)

    def _apply_formula(self):
        """Traite la formule saisie"""
        formula = self.formula_input.text()
        current_table = self.tab_widget.currentWidget()
        
        if current_table and isinstance(current_table, QTableView):
            index = current_table.selectionModel().currentIndex()
            if index.isValid():
                self.formula_submitted.emit(formula, index.row(), index.column())

    def _handle_formula(self, formula, row, col):
        """Gère une formule soumise"""
        # Ici vous implémenteriez votre moteur de formules
        print(f"Formule '{formula}' appliquée à {row},{col}")
        self.formulas[(row, col)] = formula
        
        # Pour l'exemple, nous affichons simplement la formule
        self.current_model.setItem(row, col, QStandardItem(formula))
        self._update_status_bar()

    def _tab_changed(self, index):
        """Gère le changement d'onglet"""
        if index >= 0:
            table = self.tab_widget.widget(index)
            if table:
                self.current_model = table.model()
                self._update_status_bar()

    def _close_tab(self, index):
        """Ferme un onglet"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            print("Impossible de fermer le dernier onglet")

    # Méthodes des actions (à implémenter complètement)
    def _new_file(self):
        """Crée un nouveau classeur"""
        self.current_model = QStandardItemModel(10000, 26)
        self._setup_headers(self.current_model)
        self._add_new_sheet("Feuille1")
        self.formulas.clear()

    def _open_file(self):
        """Ouvre un fichier existant"""
        print("Ouverture de fichier - À implémenter")

    def _save_file(self):
        """Enregistre le fichier actuel"""
        print("Enregistrement - À implémenter")

    def _cut(self):
        """Coupe la sélection"""
        print("Couper - À implémenter")

    def _copy(self):
        """Copie la sélection"""
        print("Copier - À implémenter")

    def _paste(self):
        """Colle la sélection"""
        print("Coller - À implémenter")

    def _undo(self):
        """Annule la dernière action"""
        print("Annuler - À implémenter")

    def _redo(self):
        """Rétablit la dernière action annulée"""
        print("Rétablir - À implémenter")

    def _insert_chart(self):
        """Insère un graphique"""
        print("Insertion graphique - À implémenter")
        self._show_sample_chart()

    def _show_sample_chart(self):
        """Affiche un exemple de graphique"""
        series = QLineSeries()
        series.append(0, 6)
        series.append(2, 4)
        series.append(3, 8)
        series.append(7, 4)
        series.append(10, 5)
        
        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setTitle("Exemple de Graphique")
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Crée un dock pour le graphique
        chart_dock = QDockWidget("Graphique", self)
        chart_dock.setWidget(chart_view)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, chart_dock)

    def _show_functions(self):
        """Affiche la palette de fonctions"""
        print("Palette de fonctions - À implémenter")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configuration du style fusion
    app.setStyle("Fusion")
    
    # Configuration de la palette pour un look moderne
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(248, 249, 250))
    palette.setColor(palette.ColorRole.WindowText, QColor(33, 37, 41))
    palette.setColor(palette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(palette.ColorRole.AlternateBase, QColor(233, 236, 239))
    palette.setColor(palette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(palette.ColorRole.ToolTipText, QColor(33, 37, 41))
    palette.setColor(palette.ColorRole.Text, QColor(33, 37, 41))
    palette.setColor(palette.ColorRole.Button, QColor(233, 236, 239))
    palette.setColor(palette.ColorRole.ButtonText, QColor(33, 37, 41))
    palette.setColor(palette.ColorRole.BrightText, QColor(255, 255, 255))
    palette.setColor(palette.ColorRole.Highlight, QColor(26, 115, 232))
    palette.setColor(palette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = ModernSpreadsheetApp()
    window.show()
    
    sys.exit(app.exec())