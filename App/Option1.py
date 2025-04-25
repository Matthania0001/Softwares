import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableView, 
                            QTabWidget, QToolBar, QStatusBar, QMenu,
                            QLineEdit, QLabel, QHBoxLayout, QWidget,
                            QVBoxLayout, QFrame, QDockWidget)
from PyQt6.QtGui import (QStandardItemModel, QStandardItem, QAction,
                         QIcon, QColor, QFont)
from PyQt6.QtCore import Qt, QSize

class ModernSpreadsheetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuration principale
        self.setWindowTitle("NexusSheet - Classeur Moderne")
        self.setGeometry(100, 100, 1400, 900)
        
        # Police moderne
        self.app_font = QFont("Segoe UI", 10)
        QApplication.setFont(self.app_font)
        
        # Style global
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                margin: 0px;
                padding: 0px;
            }
            QTabBar::tab {
                padding: 8px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #0d6efd;
            }
        """)
        
        # Création du modèle
        self._setup_data_model()
        
        # Interface utilisateur
        self._setup_ui()
        
        # Barre d'état
        self._setup_status_bar()
        
        # Connecteurs
        self._connect_actions()
    
    def _setup_data_model(self):
        """Initialise le modèle de données"""
        self.model = QStandardItemModel(10000, 26)  # 10,000 lignes
        for col in range(self.model.columnCount()):
            # En-têtes de colonnes (A, B, ..., Z, AA, AB, ...)
            if col < 26:
                header = chr(65 + col)
            else:
                header = chr(64 + col//26) + chr(65 + col%26)
            self.model.setHorizontalHeaderItem(col, QStandardItem(header))
        
        # Exemple de données
        for row in range(10):
            for col in range(5):
                item = QStandardItem(f"Ex {row+1}-{col+1}")
                self.model.setItem(row, col, item)
    
    def _setup_ui(self):
        """Configure l'interface utilisateur principale"""
        # Conteneur central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Barre d'outils supérieure
        self._setup_main_toolbar()
        
        # Barre de formule
        self._setup_formula_bar()
        main_layout.addWidget(self.formula_toolbar)
        
        # Zone d'onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        main_layout.addWidget(self.tab_widget)
        
        # Ajout de la première feuille
        self._add_new_sheet("Feuille1")
        
        # Panneau latéral (optionnel)
        self._setup_side_panel()
    
    def _setup_main_toolbar(self):
        """Configure la barre d'outils principale"""
        self.main_toolbar = self.addToolBar("Main Toolbar")
        self.main_toolbar.setIconSize(QSize(24, 24))
        self.main_toolbar.setMovable(False)
        self.main_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Actions
        actions = [
            ("Nouveau", "document-new", self._new_file),
            ("Ouvrir", "document-open", self._open_file),
            ("Enregistrer", "document-save", self._save_file),
            None,  # Séparateur
            ("Couper", "edit-cut", self._cut),
            ("Copier", "edit-copy", self._copy),
            ("Coller", "edit-paste", self._paste),
            None,
            ("Annuler", "edit-undo", self._undo),
            ("Rétablir", "edit-redo", self._redo),
            None,
            ("Graphique", "insert-chart", self._insert_chart),
            ("Fonctions", "math-function", self._show_functions)
        ]
        
        for action in actions:
            if action is None:
                self.main_toolbar.addSeparator()
            else:
                name, icon_name, handler = action
                act = QAction(QIcon.fromTheme(icon_name), name, self)
                act.triggered.connect(handler)
                self.main_toolbar.addAction(act)
        
        # Style
        self.main_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #ffffff;
                border: none;
                border-bottom: 1px solid #dee2e6;
                padding: 4px;
            }
            QToolButton {
                padding: 4px 8px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #e9ecef;
            }
        """)
    
    def _setup_formula_bar(self):
        """Configure la barre de formule avancée"""
        self.formula_toolbar = QToolBar()
        self.formula_toolbar.setFixedHeight(40)
        
        formula_container = QWidget()
        formula_layout = QHBoxLayout(formula_container)
        formula_layout.setContentsMargins(5, 0, 5, 0)
        
        # Label "fx"
        fx_label = QLabel("fx")
        fx_label.setStyleSheet("font-weight: bold; color: #0d6efd;")
        
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
                box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
            }
        """)
        
        formula_layout.addWidget(fx_label)
        formula_layout.addWidget(self.formula_input)
        self.formula_toolbar.addWidget(formula_container)
        
        # Style
        self.formula_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
        """)
    
    def _setup_side_panel(self):
        """Configure le panneau latéral pour les propriétés/fonctions"""
        self.side_panel = QDockWidget("Outils", self)
        self.side_panel.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.side_panel.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                       Qt.DockWidgetArea.RightDockWidgetArea)
        
        panel_content = QWidget()
        panel_layout = QVBoxLayout(panel_content)
        
        # Ajout d'éléments au panneau
        properties_group = QFrame()
        properties_group.setFrameShape(QFrame.Shape.StyledPanel)
        properties_layout = QVBoxLayout(properties_group)
        properties_layout.addWidget(QLabel("<b>Propriétés de la cellule</b>"))
        
        panel_layout.addWidget(properties_group)
        panel_layout.addStretch()
        
        self.side_panel.setWidget(panel_content)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.side_panel)
    
    def _setup_status_bar(self):
        """Configure la barre d'état améliorée"""
        self.status_bar = self.statusBar()
        
        # Widgets dans la barre d'état
        self.cell_position = QLabel("A1")
        self.cell_value = QLabel("")
        self.sheet_info = QLabel("Feuille1")
        
        self.status_bar.addPermanentWidget(self.cell_position)
        self.status_bar.addPermanentWidget(self.cell_value, 1)
        self.status_bar.addPermanentWidget(self.sheet_info)
        
        # Style
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
            QStatusBar::item {
                border: none;
            }
        """)
    
    def _add_new_sheet(self, name):
        """Ajoute une nouvelle feuille avec une table moderne"""
        table = QTableView()
        table.setModel(self.model)
        
        # Configuration avancée
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        table.setSelectionMode(QTableView.SelectionMode.ContiguousSelection)
        
        # Style moderne
        table.setStyleSheet("""
            QTableView {
                background-color: #ffffff;
                gridline-color: #e9ecef;
                font: 12px;
                border: none;
            }
            QTableView::item {
                padding: 4px;
            }
            QTableView::item:selected {
                background-color: #0d6efd;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 4px;
                border: 1px solid #dee2e6;
            }
        """)
        
        self.tab_widget.addTab(table, name)
    
    def _connect_actions(self):
        """Connecte les signaux et slots"""
        # À implémenter selon les besoins
        pass
    
    # Méthodes des actions (à implémenter)
    def _new_file(self): ...
    def _open_file(self): ...
    def _save_file(self): ...
    def _cut(self): ...
    def _copy(self): ...
    def _paste(self): ...
    def _undo(self): ...
    def _redo(self): ...
    def _insert_chart(self): ...
    def _show_functions(self): ...

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Thème moderne
    app.setStyle("Fusion")
    
    # Palette de couleurs moderne
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
    palette.setColor(palette.ColorRole.Highlight, QColor(13, 110, 253))
    palette.setColor(palette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = ModernSpreadsheetApp()
    window.show()
    
    sys.exit(app.exec())