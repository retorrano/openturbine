import sys
import math
from typing import Optional, Dict, Tuple, Any

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QSplitter,
        QTreeWidget,
        QTreeWidgetItem,
        QTabWidget,
        QStatusBar,
        QMenuBar,
        QMenu,
        QToolBar,
        QDockWidget,
        QLabel,
        QPushButton,
        QGroupBox,
        QFormLayout,
        QLineEdit,
        QSpinBox,
        QDoubleSpinBox,
        QComboBox,
        QCheckBox,
        QSlider,
        QProgressBar,
        QTextEdit,
        QTableWidget,
        QTableWidgetItem,
        QHeaderView,
        QFileDialog,
        QMessageBox,
        QDialog,
        QSizePolicy,
        QFrame,
    )
    from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
    from PySide6.QtGui import QAction, QIcon, QKeySequence

    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False

try:
    import pyqtgraph as pg

    HAS_PYQTGRAPH = True
except ImportError:
    HAS_PYQTGRAPH = False


class ViewPresets:
    """Predefined camera views for 3D visualization."""

    PRESETS: Dict[str, Dict[str, Any]] = {
        "one_point_perspective": {
            "name": "One-Point Perspective",
            "position": (80, 60, 80),
            "focal_point": (0, 90, 0),
            "view_up": (0, 1, 0),
            "description": "Classic front view with depth",
        },
        "isometric": {
            "name": "Isometric",
            "position": (100, 100, 100),
            "focal_point": (0, 90, 0),
            "view_up": (0, 1, 0),
            "description": "Equal angles, technical view",
        },
        "front": {
            "name": "Front View",
            "position": (150, 90, 0),
            "focal_point": (0, 90, 0),
            "view_up": (0, 1, 0),
            "description": "Straight front view",
        },
        "side": {
            "name": "Side View",
            "position": (0, 90, 150),
            "focal_point": (0, 90, 0),
            "view_up": (0, 1, 0),
            "description": "Straight side view",
        },
        "hub_closeup": {
            "name": "Hub Close-up",
            "position": (20, 95, 20),
            "focal_point": (0, 92, 0),
            "view_up": (0, 1, 0),
            "description": "Detailed view of hub and blades",
        },
        "overview": {
            "name": "Overview",
            "position": (120, 100, 120),
            "focal_point": (0, 90, 0),
            "view_up": (0, 1, 0),
            "description": "Full turbine overview",
        },
        "diagonal": {
            "name": "Diagonal View",
            "position": (100, 80, 100),
            "focal_point": (0, 90, 0),
            "view_up": (0, 1, 0),
            "description": "Diagonal perspective",
        },
    }

    @staticmethod
    def get_preset_names() -> list:
        return list(ViewPresets.PRESETS.keys())

    @staticmethod
    def get_preset(name: str) -> Dict[str, Any]:
        return ViewPresets.PRESETS.get(name, ViewPresets.PRESETS["one_point_perspective"])


class MainWindow:
    """Main window for OpenTurbine wind turbine simulation application."""

    def __init__(self):
        if not HAS_PYSIDE6:
            raise ImportError("PySide6 is required for the UI. Install with: pip install PySide6")

        self.app = QApplication(sys.argv)
        self.app.setApplicationName("OpenTurbine")
        self.app.setOrganizationName("OpenTurbine")
        self.app.setOrganizationDomain("openturbine.org")

        self.window = QMainWindow()
        self.window.setWindowTitle("OpenTurbine - Wind Turbine Simulation")
        self.window.setMinimumSize(1280, 800)

        self.simulation_running = False
        self.current_results = None
        self.animation_enabled = False
        self.results_history = []

        self.current_view_preset = "one_point_perspective"
        self.display_options = {
            "ground_plane": True,
            "sky": True,
            "wind_particles": True,
            "wake_effect": True,
            "wireframe": False,
            "shadows": True,
        }

        from openturbine.simulation_runner import create_simple_simulation

        self.simulator = create_simple_simulation()

        self._create_menu_bar()
        self._create_tool_bar()
        self._create_central_widget()
        self._create_dock_widgets()
        self._create_status_bar()
        self._create_view_controls_dock()

        self._create_connections()

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.blade_angle = 0.0
        self.prev_blade_angle = 0.0

        self._update_results_display()

    def _create_menu_bar(self):
        menubar = self.window.menuBar()

        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Project", self.window)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_action)

        open_action = QAction("&Open...", self.window)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._on_open)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self.window)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self.window)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self._on_save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        import_action = QAction("&Import Configuration...", self.window)
        import_action.triggered.connect(self._on_import_config)
        file_menu.addAction(import_action)

        export_action = QAction("&Export Results...", self.window)
        export_action.triggered.connect(self._on_export_results)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self.window)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.window.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self.window)
        undo_action.setShortcut(QKeySequence.Undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self.window)
        redo_action.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        preferences_action = QAction("&Preferences...", self.window)
        preferences_action.triggered.connect(self._on_preferences)
        edit_menu.addAction(preferences_action)

        simulation_menu = menubar.addMenu("&Simulation")

        run_action = QAction("&Run Simulation", self.window)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self._on_run_clicked)
        simulation_menu.addAction(run_action)

        stop_action = QAction("&Stop Simulation", self.window)
        stop_action.setShortcut("F6")
        stop_action.triggered.connect(self._on_stop_clicked)
        simulation_menu.addAction(stop_action)

        simulation_menu.addSeparator()

        parametric_action = QAction("&Parametric Sweep...", self.window)
        parametric_action.triggered.connect(self._on_parametric_sweep)
        simulation_menu.addAction(parametric_action)

        view_menu = menubar.addMenu("&View")

        reset_layout_action = QAction("&Reset Layout", self.window)
        reset_layout_action.triggered.connect(self._on_reset_layout)
        view_menu.addAction(reset_layout_action)

        view_menu.addSeparator()

        self.view_3d_action = QAction("&3D View", self.window)
        self.view_3d_action.setCheckable(True)
        self.view_3d_action.setChecked(True)
        self.view_3d_action.toggled.connect(self._on_toggle_3d_view)
        view_menu.addAction(self.view_3d_action)

        self.view_2d_action = QAction("&2D Schematic", self.window)
        self.view_2d_action.setCheckable(True)
        self.view_2d_action.toggled.connect(self._on_toggle_2d_view)
        view_menu.addAction(self.view_2d_action)

        view_menu.addSeparator()

        self.view_presets_menu = QMenu("&View Presets", self.window)
        view_menu.addMenu(self.view_presets_menu)
        self.view_preset_actions = {}

        for preset_key in ViewPresets.get_preset_names():
            preset = ViewPresets.get_preset(preset_key)
            action = QAction(preset["name"], self.window)
            action.setData(preset_key)
            action.setToolTip(preset["description"])
            self.view_presets_menu.addAction(action)
            self.view_preset_actions[preset_key] = action

        self.view_presets_menu.menuAction().triggered.connect(self._on_view_preset_menu_triggered)

        reset_view_action = QAction("&Reset View", self.window)
        reset_view_action.setShortcut("R")
        reset_view_action.setToolTip("Reset to default view (R)")
        reset_view_action.triggered.connect(self._on_reset_3d_view)
        view_menu.addAction(reset_view_action)

        charts_action = QAction("&Charts Dashboard", self.window)
        charts_action.setCheckable(True)
        charts_action.setChecked(True)
        charts_action.toggled.connect(self._on_toggle_charts)
        view_menu.addAction(charts_action)

        tools_menu = menubar.addMenu("&Tools")

        airfoil_action = QAction("&Airfoil Editor...", self.window)
        airfoil_action.triggered.connect(self._on_airfoil_editor)
        tools_menu.addAction(airfoil_action)

        wake_action = QAction("&Wake Analysis...", self.window)
        wake_action.triggered.connect(self._on_wake_analysis)
        tools_menu.addAction(wake_action)

        tools_menu.addSeparator()

        compare_action = QAction("&Compare Designs...", self.window)
        compare_action.triggered.connect(self._on_compare_designs)
        tools_menu.addAction(compare_action)

        help_menu = menubar.addMenu("&Help")

        tutorial_action = QAction("&Tutorial...", self.window)
        tutorial_action.triggered.connect(self._on_tutorial)
        help_menu.addAction(tutorial_action)

        documentation_action = QAction("&Documentation...", self.window)
        documentation_action.triggered.connect(self._on_documentation)
        help_menu.addAction(documentation_action)

        about_action = QAction("&About OpenTurbine", self.window)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _on_new_project(self):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self.window,
            "New Project",
            "New project created.\n\nTurbine parameters set to defaults.",
        )
        self.status_label.setText("New project - defaults loaded")
        self.results_history = []
        self.results_table.setRowCount(0)
        if hasattr(self, "power_plot"):
            self.power_plot.clear()
        if hasattr(self, "rpm_plot"):
            self.rpm_plot.clear()

    def _update_ui_from_simulator(self):
        self.edit_rotor_diameter.setValue(self.simulator.rotor_diameter)
        self.edit_hub_height.setValue(self.simulator.hub_height)
        self.edit_num_blades.setValue(self.simulator.num_blades)
        self.edit_rated_power.setValue(self.simulator.rated_power / 1e6)
        self.edit_blade_length.setValue(self.simulator.blade_length)
        self.edit_tsr.setValue(self.simulator.tsr_optimal)
        self.edit_cp_max.setValue(self.simulator.cp_max)
        self.edit_cut_in_ws.setValue(self.simulator.cut_in_wind_speed)
        self.edit_rated_ws.setValue(self.simulator.rated_wind_speed)
        self.edit_cut_out_ws.setValue(self.simulator.cut_out_wind_speed)
        self.edit_air_density.setValue(self.simulator.air_density)
        self.edit_turbulence.setValue(self.simulator.turbulence_intensity)

    def _on_open(self):
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self.window, "Open Configuration", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                import json

                with open(file_path, "r") as f:
                    config = json.load(f)
                self.simulator.config = config
                self.simulator._parse_config()
                self._update_ui_from_simulator()
                self.current_file = file_path
                QMessageBox.information(self.window, "Open", f"Configuration loaded:\n{file_path}")
                self.status_label.setText(f"Loaded: {file_path}")
            except Exception as e:
                QMessageBox.warning(self.window, "Error", f"Failed to load:\n{str(e)}")
                self.status_label.setText(f"Error: {str(e)[:30]}")

    def _on_save(self):
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self.window, "Save Configuration", "", "JSON Files (*.json)"
        )
        if file_path:
            if not file_path.endswith(".json"):
                file_path += ".json"
            self._save_to_file(file_path)
            self.current_file = file_path
            QMessageBox.information(self.window, "Save", f"Configuration saved:\n{file_path}")

    def _on_save_as(self):
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self.window, "Save Configuration As", "", "JSON Files (*.json)"
        )
        if file_path:
            if not file_path.endswith(".json"):
                file_path += ".json"
            self._save_to_file(file_path)
            self.current_file = file_path
            QMessageBox.information(self.window, "Save As", f"Configuration saved:\n{file_path}")

    def _save_to_file(self, file_path):
        try:
            import json

            config = {
                "turbine": {
                    "rotor": {
                        "diameter": {"value": self.simulator.rotor_diameter},
                        "number_of_blades": {"value": self.simulator.num_blades},
                        "rated_power": {"value": self.simulator.rated_power},
                    },
                    "hub_height": {"value": self.simulator.hub_height},
                },
                "aerodynamics": {
                    "blade_length": {"value": self.simulator.blade_length},
                    "cut_in_wind_speed": {"value": self.simulator.cut_in_wind_speed},
                    "rated_wind_speed": {"value": self.simulator.rated_wind_speed},
                    "cut_out_wind_speed": {"value": self.simulator.cut_out_wind_speed},
                    "cp_max": {"value": self.simulator.cp_max},
                    "tsr_optimal": {"value": self.simulator.tsr_optimal},
                },
                "environment": {"air_density": {"value": self.simulator.air_density}},
            }
            with open(file_path, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.status_label.setText(f"Save error: {str(e)[:50]}")

    def _on_import_config(self):
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self.window, "Import Configuration", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                import json

                with open(file_path, "r") as f:
                    config = json.load(f)
                self.simulator.config = config
                self.simulator._parse_config()
                self._update_ui_from_simulator()
                self.current_file = file_path
                QMessageBox.information(
                    self.window, "Import", f"Configuration imported:\n{file_path}"
                )
                self.status_label.setText(f"Imported: {file_path}")
            except Exception as e:
                QMessageBox.warning(self.window, "Error", f"Failed to import:\n{str(e)}")
                self.status_label.setText(f"Error: {str(e)[:30]}")

    def _on_export_results(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox

        file_path, _ = QFileDialog.getSaveFileName(
            self.window, "Export Results", "", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                import csv

                data = [["Wind Speed (m/s)", "Power (MW)", "RPM", "Thrust (kN)"]]
                for ws in range(0, 26):
                    result = self.simulator.run_steady_state(float(ws))
                    data.append([ws, result["power_mw"], result["rotor_rpm"], result["thrust_kn"]])
                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(data)
                QMessageBox.information(self.window, "Export", f"Results exported:\n{file_path}")
                self.status_label.setText(f"Exported: {file_path}")
            except Exception as e:
                QMessageBox.warning(self.window, "Error", f"Failed to export:\n{str(e)}")
                self.status_label.setText(f"Error: {str(e)[:30]}")

    def _on_reset_layout(self):
        self.status_label.setText("Layout reset")

    def _on_preferences(self):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(self.window, "Preferences", "Preferences dialog - coming soon")

    def _on_parametric_sweep(self):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(self.window, "Parametric Sweep", "Parametric sweep - coming soon")

    def _on_airfoil_editor(self):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(self.window, "Airfoil Editor", "Airfoil editor - coming soon")

    def _on_wake_analysis(self):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(self.window, "Wake Analysis", "Wake analysis - coming soon")

    def _on_compare_designs(self):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(self.window, "Compare Designs", "Design comparison - coming soon")

    def _on_toggle_3d_view(self, checked):
        if hasattr(self, "viewport_3d"):
            self.viewport_3d.setVisible(checked)

    def _on_toggle_2d_view(self, checked):
        if hasattr(self, "viewport_2d"):
            self.viewport_2d.setVisible(checked)

    def _on_toggle_charts(self, checked):
        if hasattr(self, "charts_widget"):
            self.charts_widget.setVisible(checked)

    def _on_tutorial(self):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self.window, "Tutorial", "Tutorials available at:\nhttps://openturbine.readthedocs.io/"
        )

    def _on_documentation(self):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self.window,
            "Documentation",
            "Documentation available at:\nhttps://openturbine.readthedocs.io/\n\nParameter reference:\ndocs/parameters.md",
        )

    def _on_about(self):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.about(
            self.window,
            "About OpenTurbine",
            "<h3>OpenTurbine</h3>"
            "<p>Version 0.1.0</p>"
            "<p>Open-source wind turbine simulation software</p>"
            "<p>Author: Romano E. Torrano</p>"
            "<p>Licensed under Apache License 2.0</p>"
            "<p><a href='https://github.com/retorrano/openturbine'>GitHub Repository</a></p>",
        )

    def _create_tool_bar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.window.addToolBar(toolbar)

        new_btn = QPushButton("New")
        new_btn.clicked.connect(self._on_new_project)
        toolbar.addWidget(new_btn)

        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self._on_open)
        toolbar.addWidget(open_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._on_save)
        toolbar.addWidget(save_btn)

        toolbar.addSeparator()

        self.run_btn = QPushButton("Run")
        self.run_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 15px;")
        self.run_btn.clicked.connect(self._on_run_clicked)
        toolbar.addWidget(self.run_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; padding: 5px 15px;")
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        toolbar.addWidget(self.stop_btn)

        toolbar.addSeparator()

        self.view_preset_combo = QComboBox()
        self.view_preset_combo.setMinimumWidth(150)
        for preset_key in ViewPresets.get_preset_names():
            preset = ViewPresets.get_preset(preset_key)
            self.view_preset_combo.addItem(preset["name"], preset_key)
        toolbar.addWidget(QLabel("View:"))
        toolbar.addWidget(self.view_preset_combo)

        reset_view_btn = QPushButton("Reset")
        reset_view_btn.setToolTip("Reset to default view (R)")
        reset_view_btn.setMaximumWidth(60)
        reset_view_btn.clicked.connect(self._on_reset_3d_view)
        toolbar.addWidget(reset_view_btn)

        toolbar.addSeparator()

        self.wind_speed_slider = QSlider(Qt.Horizontal)
        self.wind_speed_slider.setMinimum(0)
        self.wind_speed_slider.setMaximum(30)
        self.wind_speed_slider.setValue(8)
        self.wind_speed_slider.setTickPosition(QSlider.TicksBelow)
        self.wind_speed_slider.setTickInterval(5)
        toolbar.addWidget(QLabel("Wind (0-25):"))
        toolbar.addWidget(self.wind_speed_slider)
        toolbar.addWidget(QLabel("m/s"))

        self.wind_speed_label = QLabel("8.0 m/s")
        toolbar.addWidget(self.wind_speed_label)

        toolbar.addSeparator()

        self.animation_btn = QPushButton("Animate")
        self.animation_btn.setCheckable(True)
        toolbar.addWidget(self.animation_btn)

    def _create_central_widget(self):
        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        splitter = QSplitter(Qt.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.param_tabs = QTabWidget()

        turbine_edit = self._create_turbine_edit_panel()
        self.param_tabs.addTab(turbine_edit, "Turbine")

        aero_edit = self._create_aero_edit_panel()
        self.param_tabs.addTab(aero_edit, "Aerodynamics")

        struct_edit = self._create_struct_edit_panel()
        self.param_tabs.addTab(struct_edit, "Structural")

        control_edit = self._create_control_edit_panel()
        self.param_tabs.addTab(control_edit, "Control")

        env_edit = self._create_env_edit_panel()
        self.param_tabs.addTab(env_edit, "Environment")

        left_layout.addWidget(self.param_tabs, 1)

        splitter.addWidget(left_panel)

        self.right_widget = QTabWidget()

        self.viewport_3d = self._create_3d_viewport()
        self.right_widget.addTab(self.viewport_3d, "3D View")

        self.viewport_2d = self._create_2d_viewport()
        self.right_widget.addTab(self.viewport_2d, "2D Schematic")

        self.charts_widget = self._create_charts_widget()
        self.right_widget.addTab(self.charts_widget, "Charts")

        splitter.addWidget(self.right_widget)

        splitter.setSizes([300, 980])

        main_layout.addWidget(splitter)

    def _create_turbine_edit_panel(self) -> QWidget:
        panel = QWidget()
        layout = QFormLayout(panel)

        self.edit_rotor_diameter = QDoubleSpinBox()
        self.edit_rotor_diameter.setRange(10, 300)
        self.edit_rotor_diameter.setValue(126.0)
        self.edit_rotor_diameter.setSuffix(" m")
        self.edit_rotor_diameter.valueChanged.connect(self._on_rotor_diameter_changed)
        layout.addRow("Rotor Diameter:", self.edit_rotor_diameter)

        self.edit_hub_height = QDoubleSpinBox()
        self.edit_hub_height.setRange(20, 200)
        self.edit_hub_height.setValue(90.0)
        self.edit_hub_height.setSuffix(" m")
        self.edit_hub_height.valueChanged.connect(self._on_hub_height_changed)
        layout.addRow("Hub Height:", self.edit_hub_height)

        self.edit_num_blades = QSpinBox()
        self.edit_num_blades.setRange(1, 5)
        self.edit_num_blades.setValue(3)
        self.edit_num_blades.valueChanged.connect(self._on_num_blades_changed)
        layout.addRow("Number of Blades:", self.edit_num_blades)

        self.edit_rated_power = QDoubleSpinBox()
        self.edit_rated_power.setRange(0.1, 20)
        self.edit_rated_power.setValue(5.0)
        self.edit_rated_power.setSuffix(" MW")
        self.edit_rated_power.valueChanged.connect(self._on_rated_power_changed)
        layout.addRow("Rated Power:", self.edit_rated_power)

        self.edit_cone_angle = QDoubleSpinBox()
        self.edit_cone_angle.setRange(0, 15)
        self.edit_cone_angle.setValue(2.5)
        self.edit_cone_angle.setSuffix(" deg")
        layout.addRow("Cone Angle:", self.edit_cone_angle)

        return panel

    def _create_aero_edit_panel(self) -> QWidget:
        panel = QWidget()
        layout = QFormLayout(panel)

        self.edit_blade_length = QDoubleSpinBox()
        self.edit_blade_length.setRange(5, 150)
        self.edit_blade_length.setValue(61.5)
        self.edit_blade_length.setSuffix(" m")
        self.edit_blade_length.valueChanged.connect(self._on_blade_length_changed)
        layout.addRow("Blade Length:", self.edit_blade_length)

        self.edit_tsr = QDoubleSpinBox()
        self.edit_tsr.setRange(1, 15)
        self.edit_tsr.setValue(7.55)
        self.edit_tsr.setDecimals(2)
        self.edit_tsr.valueChanged.connect(self._on_tsr_changed)
        layout.addRow("Tip Speed Ratio:", self.edit_tsr)

        self.edit_cp_max = QDoubleSpinBox()
        self.edit_cp_max.setRange(0.1, 0.59)
        self.edit_cp_max.setValue(0.42)
        self.edit_cp_max.setDecimals(3)
        self.edit_cp_max.valueChanged.connect(self._on_cp_max_changed)
        layout.addRow("Max Cp:", self.edit_cp_max)

        self.edit_cut_in_ws = QDoubleSpinBox()
        self.edit_cut_in_ws.setRange(1, 10)
        self.edit_cut_in_ws.setValue(3.0)
        self.edit_cut_in_ws.setSuffix(" m/s")
        self.edit_cut_in_ws.valueChanged.connect(self._on_cut_in_ws_changed)
        layout.addRow("Cut-in Wind:", self.edit_cut_in_ws)

        self.edit_rated_ws = QDoubleSpinBox()
        self.edit_rated_ws.setRange(5, 20)
        self.edit_rated_ws.setValue(11.4)
        self.edit_rated_ws.setSuffix(" m/s")
        self.edit_rated_ws.valueChanged.connect(self._on_rated_ws_changed)
        layout.addRow("Rated Wind:", self.edit_rated_ws)

        self.edit_cut_out_ws = QDoubleSpinBox()
        self.edit_cut_out_ws.setRange(15, 35)
        self.edit_cut_out_ws.setValue(25.0)
        self.edit_cut_out_ws.setSuffix(" m/s")
        self.edit_cut_out_ws.valueChanged.connect(self._on_cut_out_ws_changed)
        layout.addRow("Cut-out Wind:", self.edit_cut_out_ws)

        return panel

    def _create_struct_edit_panel(self) -> QWidget:
        panel = QWidget()
        layout = QFormLayout(panel)

        self.edit_blade_density = QDoubleSpinBox()
        self.edit_blade_density.setRange(1000, 5000)
        self.edit_blade_density.setValue(3450)
        self.edit_blade_density.setSuffix(" kg/m³")
        self.edit_blade_density.valueChanged.connect(self._on_blade_density_changed)
        layout.addRow("Blade Density:", self.edit_blade_density)

        self.edit_young_modulus = QDoubleSpinBox()
        self.edit_young_modulus.setRange(10, 200)
        self.edit_young_modulus.setValue(40)
        self.edit_young_modulus.setSuffix(" GPa")
        self.edit_young_modulus.valueChanged.connect(self._on_young_modulus_changed)
        layout.addRow("Young's Modulus:", self.edit_young_modulus)

        self.edit_tower_density = QDoubleSpinBox()
        self.edit_tower_density.setRange(1000, 10000)
        self.edit_tower_density.setValue(8500)
        self.edit_tower_density.setSuffix(" kg/m³")
        self.edit_tower_density.valueChanged.connect(self._on_tower_density_changed)
        layout.addRow("Tower Density:", self.edit_tower_density)

        self.edit_safety_factor = QDoubleSpinBox()
        self.edit_safety_factor.setRange(1.0, 5.0)
        self.edit_safety_factor.setValue(1.5)
        self.edit_safety_factor.setDecimals(1)
        self.edit_safety_factor.valueChanged.connect(self._on_safety_factor_changed)
        layout.addRow("Safety Factor:", self.edit_safety_factor)

        return panel

    def _create_control_edit_panel(self) -> QWidget:
        panel = QWidget()
        layout = QFormLayout(panel)

        self.edit_pitch_kp = QDoubleSpinBox()
        self.edit_pitch_kp.setRange(0.001, 0.1)
        self.edit_pitch_kp.setValue(0.018)
        self.edit_pitch_kp.setDecimals(4)
        self.edit_pitch_kp.valueChanged.connect(self._on_pitch_kp_changed)
        layout.addRow("Pitch Kp:", self.edit_pitch_kp)

        self.edit_pitch_ki = QDoubleSpinBox()
        self.edit_pitch_ki.setRange(0.0, 0.05)
        self.edit_pitch_ki.setValue(0.002)
        self.edit_pitch_ki.setDecimals(4)
        self.edit_pitch_ki.valueChanged.connect(self._on_pitch_ki_changed)
        layout.addRow("Pitch Ki:", self.edit_pitch_ki)

        self.edit_rated_pitch = QDoubleSpinBox()
        self.edit_rated_pitch.setRange(0, 15)
        self.edit_rated_pitch.setValue(2.0)
        self.edit_rated_pitch.setSuffix(" deg")
        self.edit_rated_pitch.valueChanged.connect(self._on_rated_pitch_changed)
        layout.addRow("Rated Pitch:", self.edit_rated_pitch)

        self.edit_rated_torque = QDoubleSpinBox()
        self.edit_rated_torque.setRange(10000, 100000)
        self.edit_rated_torque.setValue(41000)
        self.edit_rated_torque.setSuffix(" N·m")
        self.edit_rated_torque.valueChanged.connect(self._on_rated_torque_changed)
        layout.addRow("Rated Torque:", self.edit_rated_torque)

        self.edit_yaw_enabled = QCheckBox()
        self.edit_yaw_enabled.setChecked(True)
        self.edit_yaw_enabled.stateChanged.connect(self._on_yaw_enabled_changed)
        layout.addRow("Yaw Enabled:", self.edit_yaw_enabled)

        return panel

    def _create_env_edit_panel(self) -> QWidget:
        panel = QWidget()
        layout = QFormLayout(panel)

        self.edit_air_density = QDoubleSpinBox()
        self.edit_air_density.setRange(0.8, 1.5)
        self.edit_air_density.setValue(1.225)
        self.edit_air_density.setSuffix(" kg/m³")
        self.edit_air_density.setDecimals(3)
        self.edit_air_density.valueChanged.connect(self._on_air_density_changed)
        layout.addRow("Air Density:", self.edit_air_density)

        self.edit_turbulence = QDoubleSpinBox()
        self.edit_turbulence.setRange(0, 0.5)
        self.edit_turbulence.setValue(0.14)
        self.edit_turbulence.setDecimals(2)
        self.edit_turbulence.valueChanged.connect(self._on_turbulence_changed)
        layout.addRow("Turbulence:", self.edit_turbulence)

        self.edit_shear_exp = QDoubleSpinBox()
        self.edit_shear_exp.setRange(0, 0.4)
        self.edit_shear_exp.setValue(0.14)
        self.edit_shear_exp.setDecimals(2)
        self.edit_shear_exp.valueChanged.connect(self._on_shear_changed)
        layout.addRow("Shear Exponent:", self.edit_shear_exp)

        self.edit_turbulence_enabled = QCheckBox()
        self.edit_turbulence_enabled.setChecked(True)
        self.edit_turbulence_enabled.stateChanged.connect(self._on_turbulence_enabled_changed)
        layout.addRow("Turbulence On:", self.edit_turbulence_enabled)

        return panel

    def _on_rotor_diameter_changed(self, value):
        self.simulator.rotor_diameter = value
        self._draw_turbine_schematic(self.wind_speed_slider.value(), self.blade_angle)

    def _on_hub_height_changed(self, value):
        self.simulator.hub_height = value
        self._draw_turbine_schematic(self.wind_speed_slider.value(), self.blade_angle)

    def _on_num_blades_changed(self, value):
        self.simulator.num_blades = value
        self._draw_turbine_schematic(self.wind_speed_slider.value(), self.blade_angle)
        if hasattr(self, "blade_actors_3d"):
            self._rebuild_3d_blades()
        self._update_power_display()
        for blade in self.blade_actors_3d:
            self.renderer.RemoveActor(blade)
        self.blade_actors_3d = []

        for i in range(self.simulator.num_blades):
            blade_actor = self._create_3d_blade_vtk(i)
            self.blade_actors_3d.append(blade_actor)
            self.renderer.AddActor(blade_actor)

        if hasattr(self, "vtk_interactor"):
            self.vtk_interactor.GetRenderWindow().Render()

    def _on_rated_power_changed(self, value):
        self.simulator.rated_power = value * 1e6

    def _on_blade_length_changed(self, value):
        self.simulator.blade_length = value
        self._draw_turbine_schematic(self.wind_speed_slider.value(), self.blade_angle)

    def _on_tsr_changed(self, value):
        self.simulator.tsr_optimal = value
        self._update_power_display()

    def _on_cp_max_changed(self, value):
        self.simulator.cp_max = value
        self._update_power_display()

    def _on_cut_in_ws_changed(self, value):
        self.simulator.cut_in_wind_speed = value

    def _on_rated_ws_changed(self, value):
        self.simulator.rated_wind_speed = value
        self._update_power_display()

    def _on_cut_out_ws_changed(self, value):
        self.simulator.cut_out_wind_speed = value

    def _update_power_display(self):
        result = self.simulator.run_steady_state(float(self.wind_speed_slider.value()))
        self.status_label.setText(
            f"Power: {result['power_mw']:.5f} MW, RPM: {result['rotor_rpm']:.5f}"
        )
        self.power_label.setText(f"Power: {result['power_mw']:.5f} MW")

    def _on_blade_density_changed(self, value):
        pass

    def _on_young_modulus_changed(self, value):
        pass

    def _on_tower_density_changed(self, value):
        pass

    def _on_safety_factor_changed(self, value):
        pass

    def _on_pitch_kp_changed(self, value):
        pass

    def _on_pitch_ki_changed(self, value):
        pass

    def _on_rated_pitch_changed(self, value):
        pass

    def _on_rated_torque_changed(self, value):
        pass

    def _on_yaw_enabled_changed(self, state):
        pass

    def _on_air_density_changed(self, value):
        self.simulator.air_density = value
        result = self.simulator.run_steady_state(float(self.wind_speed_slider.value()))
        self.status_label.setText(
            f"Power: {result['power_mw']:.5f} MW, RPM: {result['rotor_rpm']:.5f}"
        )
        self.power_label.setText(f"Power: {result['power_mw']:.5f} MW")

    def _on_turbulence_changed(self, value):
        self.simulator.turbulence_intensity = value

    def _on_shear_changed(self, value):
        pass

    def _on_turbulence_enabled_changed(self, state):
        pass

    def _create_3d_viewport(self) -> QWidget:
        try:
            import os

            os.environ["QT_QPA_PLATFORM"] = "offscreen"
            import vtk
            from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
        except Exception as e:
            widget = QFrame()
            layout = QVBoxLayout(widget)
            label = QLabel(f"VTK Error: {str(e)[:50]}\n\n3D disabled - using 2D")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #888; font-size: 12px;")
            layout.addWidget(label)
            return widget

        widget = QFrame()
        layout = QVBoxLayout(widget)

        self.vtk_interactor = QVTKRenderWindowInteractor(widget)
        layout.addWidget(self.vtk_interactor)

        controls = QHBoxLayout()

        self.view_preset_combo_3d = QComboBox()
        self.view_preset_combo_3d.setMinimumWidth(120)
        for preset_key in ViewPresets.get_preset_names():
            preset = ViewPresets.get_preset(preset_key)
            self.view_preset_combo_3d.addItem(preset["name"], preset_key)
        self.view_preset_combo_3d.currentIndexChanged.connect(self._on_view_preset_changed)
        controls.addWidget(QLabel("View:"))
        controls.addWidget(self.view_preset_combo_3d)

        reset_btn = QPushButton("Reset")
        reset_btn.setToolTip("Reset view (R)")
        reset_btn.clicked.connect(self._on_reset_3d_view)
        controls.addWidget(reset_btn)

        self.wireframe_btn = QPushButton("Wire")
        self.wireframe_btn.setCheckable(True)
        self.wireframe_btn.setToolTip("Toggle wireframe")
        self.wireframe_btn.clicked.connect(self._on_wireframe_toggle)
        controls.addWidget(self.wireframe_btn)

        self.shadows_btn = QPushButton("Shadows")
        self.shadows_btn.setCheckable(True)
        self.shadows_btn.setChecked(False)
        self.shadows_btn.setToolTip("Toggle shadows (disabled)")
        self.shadows_btn.clicked.connect(self._on_shadows_toggle)
        self.shadows_btn.setEnabled(False)
        controls.addWidget(self.shadows_btn)

        self.ground_btn = QPushButton("Ground")
        self.ground_btn.setCheckable(True)
        self.ground_btn.setChecked(True)
        self.ground_btn.setToolTip("Toggle ground plane")
        self.ground_btn.clicked.connect(self._on_ground_toggle)
        controls.addWidget(self.ground_btn)

        controls.addStretch()
        layout.addLayout(controls)

        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.7, 0.85, 0.95)

        self.vtk_interactor.GetRenderWindow().AddRenderer(self.renderer)

        self.renderer.ResetCamera()

        self._build_3d_turbine()

        style = vtk.vtkInteractorStyleTrackballCamera()
        self.vtk_interactor.SetInteractorStyle(style)

        self.vtk_interactor.Initialize()

        self._set_view_preset(self.current_view_preset)

        return widget

    def _create_gradient_sky(self):
        import vtk

        sky = vtk.vtkSphereSource()
        sky.SetCenter(0, 0, 0)
        sky.SetRadius(400)
        sky.SetThetaResolution(32)
        sky.SetPhiResolution(32)

        skyMapper = vtk.vtkPolyDataMapper()
        skyMapper.SetInputConnection(sky.GetOutputPort())

        sky_actor = vtk.vtkActor()
        sky_actor.SetMapper(skyMapper)
        sky_actor.GetProperty().SetColor(0.52, 0.76, 0.92)
        sky_actor.GetProperty().SetLighting(0)
        sky_actor.PickableOff()
        sky_actor.SetPosition(0, 0, 0)

        return sky_actor

    def _create_ground_plane(self):
        import vtk

        ground = vtk.vtkPlaneSource()
        ground.SetOrigin(-150, 0, -150)
        ground.SetPoint1(150, 0, -150)
        ground.SetPoint2(-150, 0, 150)
        ground.SetResolution(10, 10)

        groundMapper = vtk.vtkPolyDataMapper()
        groundMapper.SetInputConnection(ground.GetOutputPort())

        groundActor = vtk.vtkActor()
        groundActor.SetMapper(groundMapper)
        groundActor.GetProperty().SetColor(0.35, 0.55, 0.25)
        groundActor.GetProperty().SetSpecular(0.1)

        gridActor = vtk.vtkActor()
        gridActor.PickableOff()

        return groundActor, gridActor

    def _build_3d_turbine(self):
        import vtk
        import math

        self.blade_actors_3d = []

        rotor_radius = self.simulator.rotor_diameter / 2.0
        hub_height = self.simulator.hub_height
        blade_length = self.simulator.blade_length

        if hasattr(self, "ground_actor") and self.ground_actor:
            self.renderer.RemoveActor(self.ground_actor)
        if hasattr(self, "grid_actor") and self.grid_actor:
            self.renderer.RemoveActor(self.grid_actor)

        ground_actor, grid_actor = self._create_ground_plane()
        self.renderer.AddActor(ground_actor)
        self.renderer.AddActor(grid_actor)
        self.ground_actor = ground_actor
        self.grid_actor = grid_actor

        tower = vtk.vtkCylinderSource()
        tower.SetHeight(hub_height)
        tower.SetRadius(rotor_radius * 0.04)
        tower.SetResolution(32)
        tower_mapper = vtk.vtkPolyDataMapper()
        tower_mapper.SetInputConnection(tower.GetOutputPort())
        tower_actor = vtk.vtkActor()
        tower_actor.SetMapper(tower_mapper)
        tower_actor.GetProperty().SetColor(0.55, 0.55, 0.6)
        tower_actor.GetProperty().SetSpecular(0.3)
        tower_actor.SetPosition(0, hub_height / 2, 0)
        self.renderer.AddActor(tower_actor)

        hub_source = vtk.vtkSphereSource()
        hub_source.SetRadius(rotor_radius * 0.025)
        hub_source.SetThetaResolution(24)
        hub_source.SetPhiResolution(24)
        hub_mapper = vtk.vtkPolyDataMapper()
        hub_mapper.SetInputConnection(hub_source.GetOutputPort())
        self.hub_actor = vtk.vtkActor()
        self.hub_actor.SetMapper(hub_mapper)
        self.hub_actor.GetProperty().SetColor(0.85, 0.65, 0.1)
        self.hub_actor.GetProperty().SetSpecular(0.5)
        self.hub_actor.SetPosition(0, hub_height + rotor_radius * 0.04, 0)
        self.renderer.AddActor(self.hub_actor)

        nacelle_source = vtk.vtkCubeSource()
        nacelle_source.SetXLength(rotor_radius * 0.08)
        nacelle_source.SetYLength(rotor_radius * 0.04)
        nacelle_source.SetZLength(rotor_radius * 0.04)
        nacelle_mapper = vtk.vtkPolyDataMapper()
        nacelle_mapper.SetInputConnection(nacelle_source.GetOutputPort())
        nacelle_actor = vtk.vtkActor()
        nacelle_actor.SetMapper(nacelle_mapper)
        nacelle_actor.GetProperty().SetColor(0.4, 0.4, 0.45)
        nacelle_actor.GetProperty().SetSpecular(0.4)
        nacelle_actor.SetPosition(0, hub_height + rotor_radius * 0.02, 0)
        self.renderer.AddActor(nacelle_actor)

        self.blade_actors_3d = []
        for i in range(self.simulator.num_blades):
            blade_actor = self._create_3d_blade_vtk(i, blade_length, rotor_radius)
            self.blade_actors_3d.append(blade_actor)
            self.renderer.AddActor(blade_actor)

        self._create_wind_particles()

        light = vtk.vtkLight()
        light.SetPosition(100, 150, 100)
        light.SetFocalPoint(0, hub_height / 2, 0)
        light.SetColor(1.0, 0.98, 0.95)
        light.SetIntensity(0.8)
        self.renderer.AddLight(light)

        light2 = vtk.vtkLight()
        light2.SetPosition(-50, 100, -50)
        light2.SetFocalPoint(0, hub_height / 2, 0)
        light2.SetColor(0.6, 0.7, 0.9)
        light2.SetIntensity(0.4)
        self.renderer.AddLight(light2)

        self.renderer.SetAmbient(0.3, 0.3, 0.3)

    def _create_3d_blade_vtk(self, blade_index, blade_length=60.0, rotor_radius=63.0):
        import vtk
        import math

        num_stations = 10
        num_foil_points = 12

        def naca_airfoil(x, thickness=0.12):
            if x <= 0 or x >= 1:
                return 0
            t = thickness
            return (
                5
                * t
                * (
                    0.2969 * math.sqrt(x)
                    - 0.126 * x
                    - 0.3516 * x**2
                    + 0.2843 * x**3
                    - 0.1015 * x**4
                )
            )

        def get_chord(r_norm):
            if r_norm < 0.05:
                return 5.0
            elif r_norm < 0.25:
                return 4.5 - (r_norm - 0.05) * 3
            elif r_norm < 0.7:
                return 3.0 - (r_norm - 0.25) * 2
            else:
                return 1.0 - (r_norm - 0.7) * 1.5

        def get_twist(r_norm):
            return 12.0 * math.pow(max(0, 1.0 - r_norm), 0.8)

        points = vtk.vtkPoints()
        triangles = vtk.vtkCellArray()
        point_id = 0
        station_ids = []

        for i in range(num_stations):
            r_norm = i / (num_stations - 1)
            r = r_norm * blade_length
            chord = get_chord(r_norm)
            twist = get_twist(r_norm)
            twist_rad = math.radians(twist)

            station_points = []
            for j in range(num_foil_points):
                x_foil = j / (num_foil_points - 1)
                thickness = naca_airfoil(x_foil, 0.10) * chord

                z_pos = -chord / 2 + x_foil * chord

                px = 0
                py = thickness * math.cos(twist_rad) - z_pos * math.sin(twist_rad)
                pz = z_pos * math.cos(twist_rad) + thickness * math.sin(twist_rad)

                points.InsertNextPoint(r, py, pz)
                station_points.append(point_id)
                point_id += 1

                py = -thickness * math.cos(twist_rad) - z_pos * math.sin(twist_rad)
                pz = z_pos * math.cos(twist_rad) - thickness * math.sin(twist_rad)

                points.InsertNextPoint(r, py, pz)
                station_points.append(point_id)
                point_id += 1

            station_ids.append(station_points)

        for i in range(num_stations - 1):
            for j in range(num_foil_points - 1):
                p1 = station_ids[i][j * 2]
                p2 = station_ids[i][j * 2 + 1]
                p3 = station_ids[i + 1][j * 2 + 1]
                p4 = station_ids[i + 1][j * 2]

                t1 = vtk.vtkTriangle()
                t1.GetPointIds().SetId(0, p1)
                t1.GetPointIds().SetId(1, p2)
                t1.GetPointIds().SetId(2, p3)
                triangles.InsertNextCell(t1)

                t2 = vtk.vtkTriangle()
                t2.GetPointIds().SetId(0, p1)
                t2.GetPointIds().SetId(1, p3)
                t2.GetPointIds().SetId(2, p4)
                triangles.InsertNextCell(t2)

        pd = vtk.vtkPolyData()
        pd.SetPoints(points)
        pd.SetPolys(triangles)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(pd)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.85, 0.85, 0.9)
        actor.GetProperty().SetSpecular(0.3)
        hub_z = self.simulator.hub_height + rotor_radius * 0.04
        actor.SetPosition(0, hub_z, 0)
        angle_offset = 2 * math.pi * blade_index / self.simulator.num_blades
        actor.RotateZ(90 + math.degrees(angle_offset))

        return actor

    def _create_wind_particles(self):
        pass

    def _update_3d_animation(self, delta_angle):
        try:
            import vtk
            import math

            for i, blade in enumerate(self.blade_actors_3d):
                blade.RotateZ(math.degrees(delta_angle))

            if hasattr(self, "vtk_interactor"):
                self.vtk_interactor.GetRenderWindow().Render()
        except Exception:
            pass

    def _set_view_preset(self, preset_key: str):
        preset = ViewPresets.get_preset(preset_key)
        if not hasattr(self, "renderer") or not self.renderer:
            return

        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(*preset["position"])
        camera.SetFocalPoint(*preset["focal_point"])
        camera.SetViewUp(*preset["view_up"])

        self.renderer.ResetCamera()

        if hasattr(self, "vtk_interactor"):
            self.vtk_interactor.GetRenderWindow().Render()

        self.current_view_preset = preset_key

    def _on_view_preset_changed(self, index):
        if hasattr(self, "view_preset_combo_3d"):
            preset_key = self.view_preset_combo_3d.currentData()
            if preset_key:
                self._set_view_preset(preset_key)

    def _on_reset_3d_view(self):
        if hasattr(self, "renderer"):
            self.renderer.ResetCamera()
            self.vtk_interactor.GetRenderWindow().Render()

    def _on_wireframe_toggle(self, checked):
        if hasattr(self, "blade_actors_3d"):
            for blade in self.blade_actors_3d:
                if checked:
                    blade.GetProperty().SetRepresentationToWireframe()
                else:
                    blade.GetProperty().SetRepresentationToSurface()
            if hasattr(self, "vtk_interactor"):
                self.vtk_interactor.GetRenderWindow().Render()

    def _on_shadows_toggle(self, checked):
        pass

    def _on_ground_toggle(self, checked):
        if hasattr(self, "ground_actor"):
            self.ground_actor.SetVisibility(checked)
        if hasattr(self, "grid_actor"):
            self.grid_actor.SetVisibility(checked)
        if hasattr(self, "vtk_interactor"):
            self.vtk_interactor.GetRenderWindow().Render()

    def _create_2d_viewport(self) -> QWidget:
        try:
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure
        except ImportError:
            widget = QFrame()
            layout = QVBoxLayout(widget)
            label = QLabel("Matplotlib not available")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            return widget

        self.fig = Figure(figsize=(8, 8))
        self.fig.patch.set_facecolor("#1a1a2e")
        self.canvas_2d = FigureCanvas(self.fig)

        self.ax_2d = self.fig.add_subplot(111)
        self.ax_2d.set_facecolor("#1a1a2e")

        self._draw_turbine_schematic(8.0, 0.0)

        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        layout = QVBoxLayout(widget)
        layout.addWidget(self.canvas_2d)

        return widget

    def _draw_turbine_schematic(self, wind_speed, blade_angle):
        self.ax_2d.clear()
        self.ax_2d.set_facecolor("#1a1a2e")

        rotor_d = 126.0
        hub_h = 90.0
        blade_len = 61.5

        anim_params = self.simulator.get_animation_parameters(wind_speed)
        is_running = anim_params["rotor_rpm"] > 0

        x_tower = [0, 6, 6, -6, -6, 0]
        y_tower = [0, 0, hub_h, hub_h, 0, 0]
        self.ax_2d.fill(x_tower, y_tower, color="#555", alpha=0.8)

        self.ax_2d.plot([0, 0], [0, hub_h], "k--", alpha=0.3)

        nacelle = self.ax_2d.bar(-3, bottom=hub_h, width=6, height=3, color="#666")

        hub_x, hub_y = 0, hub_h + 3.5
        hub_color = "#cc0" if is_running else "#665500"
        hub_circle = plt.Circle((hub_x, hub_y), 1.5, color=hub_color, alpha=0.9)
        self.ax_2d.add_patch(hub_circle)

        for i in range(self.simulator.num_blades):
            angle = blade_angle + 2 * np.pi * i / self.simulator.num_blades

            blade_color = "white" if is_running else "#888888"

            blade_pts_x = [hub_x + 5 * np.cos(angle)]
            blade_pts_y = [hub_y + 5 * np.sin(angle)]

            for t in np.linspace(0.2, 1.0, 5):
                r = t * blade_len
                chord_width = 4.0 * (1.0 - t * 0.7)
                bx = hub_x + r * np.cos(angle)
                by = hub_y + r * np.sin(angle)
                blade_pts_x.append(bx)
                blade_pts_y.append(by)

            blade_pts_x.append(hub_x + blade_len * np.cos(angle))
            blade_pts_y.append(hub_y + blade_len * np.sin(angle))

            perp_angle = angle + np.pi / 2
            blade_width = 4.0

            left_x, left_y = [], []
            right_x, right_y = [], []
            for t in np.linspace(0, 1, 20):
                r = 5 + t * (blade_len - 5)
                chord = 4.0 * (1.0 - t * 0.7)
                bx = hub_x + r * np.cos(angle)
                by = hub_y + r * np.sin(angle)
                left_x.append(bx + chord * 0.5 * np.cos(perp_angle))
                left_y.append(by + chord * 0.5 * np.sin(perp_angle))
                right_x.append(bx - chord * 0.5 * np.cos(perp_angle))
                right_y.append(by - chord * 0.5 * np.sin(perp_angle))

            tip_x = hub_x + blade_len * np.cos(angle)
            tip_y = hub_y + blade_len * np.sin(angle)

            full_x = left_x + [tip_x] + right_x[::-1] + [left_x[0]]
            full_y = left_y + [tip_y] + right_y[::-1] + [left_y[0]]

            self.ax_2d.fill(full_x, full_y, color=blade_color, alpha=0.9)
            self.ax_2d.plot(
                left_x + [tip_x] + right_x[::-1],
                left_y + [tip_y] + right_y[::-1],
                "k-",
                linewidth=1,
            )

        rotor_circle = plt.Circle(
            (hub_x, hub_y),
            blade_len,
            fill=False,
            color="gray",
            linestyle="--",
            linewidth=1,
            alpha=0.5,
        )
        self.ax_2d.add_patch(rotor_circle)

        arrow_color = "cyan" if is_running else "#444444"
        for i in range(-3, 4):
            x_pos = -60 + i * 20
            speed_factor = wind_speed * 2 if is_running else 0
            self.ax_2d.annotate(
                "",
                xy=(x_pos + speed_factor, hub_y),
                xytext=(x_pos, hub_y),
                arrowprops=dict(arrowstyle="->", color=arrow_color, lw=2, alpha=0.7),
            )

        self.ax_2d.set_xlim(-rotor_d / 2 - 20, rotor_d / 2 + 20)
        self.ax_2d.set_ylim(-10, hub_h + rotor_d / 2 + 20)
        self.ax_2d.set_aspect("equal")
        self.ax_2d.axis("off")

        if is_running:
            self.ax_2d.set_title(
                f'Wind Turbine - {wind_speed:.0f} m/s | Power: {anim_params["power_mw"]:.2f} MW',
                color="white",
                fontsize=12,
                pad=10,
            )
        else:
            self.ax_2d.set_title(
                f"TURBINE STOPPED (wind > 25 m/s cut-out)", color="yellow", fontsize=12, pad=10
            )

        self.fig.tight_layout()
        self.canvas_2d.draw()

    def _create_charts_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        if HAS_PYQTGRAPH:
            tabs = QTabWidget()

            power_tab = QWidget()
            power_layout = QVBoxLayout(power_tab)
            self.power_plot = pg.PlotWidget(title="Power Output")
            self.power_plot.setLabel("left", "Power", units="MW")
            self.power_plot.setLabel("bottom", "Wind Speed", units="m/s")
            power_layout.addWidget(self.power_plot)
            tabs.addTab(power_tab, "Power Curve")

            rpm_tab = QWidget()
            rpm_layout = QVBoxLayout(rpm_tab)
            self.rpm_plot = pg.PlotWidget(title="Rotor RPM")
            self.rpm_plot.setLabel("left", "RPM")
            self.rpm_plot.setLabel("bottom", "Wind Speed", units="m/s")
            rpm_layout.addWidget(self.rpm_plot)
            tabs.addTab(rpm_tab, "RPM Curve")

            time_tab = QWidget()
            time_layout = QVBoxLayout(time_tab)
            self.time_plot = pg.PlotWidget(title="Time Series")
            self.time_plot.setLabel("left", "Value")
            self.time_plot.setLabel("bottom", "Time", units="s")
            time_layout.addWidget(self.time_plot)
            tabs.addTab(time_tab, "Time Series")

            layout.addWidget(tabs)
        else:
            label = QLabel("Charts available with pyqtgraph installed")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)

        return widget

    def _create_dock_widgets(self):
        results_dock = QDockWidget("Results", self.window)
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)

        self.results_table = QTableWidget(10, 4)
        self.results_table.setHorizontalHeaderLabels(
            ["Wind Speed (m/s)", "Power (MW)", "RPM", "Thrust (kN)"]
        )
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_layout.addWidget(self.results_table)

        results_dock.setWidget(results_widget)
        self.window.addDockWidget(Qt.BottomDockWidgetArea, results_dock)

    def _create_status_bar(self):
        status_bar = QStatusBar()
        self.window.setStatusBar(status_bar)

        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        status_bar.addPermanentWidget(self.progress_bar)

        self.fps_label = QLabel("FPS: --")
        status_bar.addPermanentWidget(self.fps_label)

        self.power_label = QLabel("Power: -- MW")
        status_bar.addPermanentWidget(self.power_label)

    def _create_view_controls_dock(self):
        dock = QDockWidget("View Controls", self.window)
        dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)

        widget = QWidget()
        layout = QVBoxLayout(widget)

        preset_group = QGroupBox("Camera Presets")
        preset_layout = QVBoxLayout(preset_group)

        for preset_key in ViewPresets.get_preset_names():
            preset = ViewPresets.get_preset(preset_key)
            btn = QPushButton(preset["name"])
            btn.setToolTip(preset["description"])
            btn.clicked.connect(lambda checked, k=preset_key: self._set_view_preset(k))
            preset_layout.addWidget(btn)

        layout.addWidget(preset_group)

        display_group = QGroupBox("Display Options")
        display_layout = QVBoxLayout(display_group)

        self.opt_ground = QCheckBox("Ground Plane")
        self.opt_ground.setChecked(True)
        self.opt_ground.toggled.connect(
            lambda c: self._on_ground_toggle(c) if hasattr(self, "ground_actor") else None
        )
        display_layout.addWidget(self.opt_ground)

        self.opt_wireframe = QCheckBox("Wireframe")
        self.opt_wireframe.setChecked(False)
        self.opt_wireframe.toggled.connect(self._on_wireframe_toggle)
        display_layout.addWidget(self.opt_wireframe)

        self.opt_shadows = QCheckBox("Shadows")
        self.opt_shadows.setChecked(True)
        self.opt_shadows.toggled.connect(self._on_shadows_toggle)
        display_layout.addWidget(self.opt_shadows)

        layout.addWidget(display_group)

        help_group = QGroupBox("Mouse Controls")
        help_layout = QVBoxLayout(help_group)
        help_layout.addWidget(QLabel("Left-drag: Orbit"))
        help_layout.addWidget(QLabel("Middle-drag: Pan"))
        help_layout.addWidget(QLabel("Right-drag: Zoom"))
        help_layout.addWidget(QLabel("Scroll: Zoom in/out"))
        help_layout.addWidget(QLabel("R key: Reset view"))
        layout.addWidget(help_group)

        layout.addStretch()

        dock.setWidget(widget)
        self.window.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.view_controls_dock = dock

    def _create_connections(self):
        self.wind_speed_slider.valueChanged.connect(self._on_wind_speed_changed)
        self.animation_btn.toggled.connect(self._on_animation_toggled)

        if hasattr(self, "view_preset_combo"):
            self.view_preset_combo.currentIndexChanged.connect(self._on_toolbar_view_preset_changed)

    @Slot()
    def _on_toolbar_view_preset_changed(self, index):
        if hasattr(self, "view_preset_combo"):
            preset_key = self.view_preset_combo.currentData()
            if preset_key:
                self._set_view_preset(preset_key)
                if hasattr(self, "view_preset_combo_3d"):
                    idx = self.view_preset_combo_3d.findData(preset_key)
                    if idx >= 0:
                        self.view_preset_combo_3d.blockSignals(True)
                        self.view_preset_combo_3d.setCurrentIndex(idx)
                        self.view_preset_combo_3d.blockSignals(False)

    @Slot()
    def _on_view_preset_menu_triggered(self, action):
        preset_key = action.data()
        if preset_key:
            self._set_view_preset(preset_key)
            if hasattr(self, "view_preset_combo"):
                idx = self.view_preset_combo.findData(preset_key)
                if idx >= 0:
                    self.view_preset_combo.blockSignals(True)
                    self.view_preset_combo.setCurrentIndex(idx)
                    self.view_preset_combo.blockSignals(False)
            if hasattr(self, "view_preset_combo_3d"):
                idx = self.view_preset_combo_3d.findData(preset_key)
                if idx >= 0:
                    self.view_preset_combo_3d.blockSignals(True)
                    self.view_preset_combo_3d.setCurrentIndex(idx)
                    self.view_preset_combo_3d.blockSignals(False)

    @Slot()
    def _on_wind_speed_changed(self, value):
        self.wind_speed_label.setText(f"{value:.1f} m/s")
        result = self.simulator.run_steady_state(float(value))
        self.status_label.setText(
            f"Wind: {value} m/s | Power: {result['power_mw']:.5f} MW | RPM: {result['rotor_rpm']:.5f}"
        )

    @Slot()
    def _on_run_clicked(self):
        wind_speed = self.wind_speed_slider.value()

        self.simulation_running = True
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText(f"Running simulation at {wind_speed} m/s...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        result = self.simulator.run_steady_state(float(wind_speed))
        self.current_results = result

        self.progress_bar.setValue(100)
        self._update_results_display()

        if result["rotor_rpm"] > 0:
            self.status_label.setText(
                f"Power: {result['power_mw']:.5f} MW, RPM: {result['rotor_rpm']:.5f}"
            )
            self.power_label.setText(f"Power: {result['power_mw']:.5f} MW")
        else:
            self.status_label.setText("TURBINE STOPPED (wind > cut-out)")
            self.power_label.setText("STOPPED (wind > 25 m/s)")

        self.simulation_running = False
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    @Slot()
    def _on_stop_clicked(self):
        self.simulation_running = False
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Simulation stopped")
        self.progress_bar.setVisible(False)

    @Slot()
    def _on_animation_toggled(self, checked):
        if checked:
            self.animation_enabled = True
            self.animation_timer.start(33)
            self.status_label.setText("Animation running...")
        else:
            self.animation_enabled = False
            self.animation_timer.stop()
            self.status_label.setText("Animation paused")

    def _update_animation(self):
        wind_speed = self.wind_speed_slider.value()
        anim_params = self.simulator.get_animation_parameters(float(wind_speed))

        rpm = anim_params["rotor_rpm"]

        if rpm > 0:
            self.prev_blade_angle = self.blade_angle
            self.blade_angle += anim_params["angular_velocity"] * 0.033
            delta = self.blade_angle - self.prev_blade_angle
            self._draw_turbine_schematic(float(wind_speed), self.blade_angle)
            self._update_3d_animation(delta)
            self.power_label.setText(f"Power: {anim_params['power_mw']:.5f} MW | RPM: {rpm:.5f}")
            self.fps_label.setText(f"FPS: 30")
        else:
            self._draw_turbine_schematic(float(wind_speed), self.blade_angle)
            self.power_label.setText(f"STOPPED (wind > 25 m/s)")
            self.fps_label.setText(f"FPS: 0")

    def _update_results_display(self):
        if self.current_results is None:
            return

        result = self.current_results
        self.results_history.append(result)

        if len(self.results_history) > 100:
            self.results_history = self.results_history[-100:]

        self.results_table.setRowCount(len(self.results_history))
        for i, res in enumerate(self.results_history):
            self.results_table.setItem(i, 0, QTableWidgetItem(f"{res['wind_speed']:.5f}"))
            self.results_table.setItem(i, 1, QTableWidgetItem(f"{res['power_mw']:.5f}"))
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{res['rotor_rpm']:.5f}"))
            self.results_table.setItem(i, 3, QTableWidgetItem(f"{res['thrust_kn']:.5f}"))

        if len(self.results_history) >= 2:
            wind_speeds = [r["wind_speed"] for r in self.results_history]
            powers = [r["power_mw"] for r in self.results_history]
            rpms = [r["rotor_rpm"] for r in self.results_history]

            if hasattr(self, "power_plot"):
                self.power_plot.clear()
                self.power_plot.plot(wind_speeds, powers, pen="b")

            if hasattr(self, "rpm_plot"):
                self.rpm_plot.clear()
                self.rpm_plot.plot(wind_speeds, rpms, pen="g")

    def run(self):
        self.window.show()
        self.app.setQuitOnLastWindowClosed(True)
        self.app.aboutToQuit.connect(self.animation_timer.stop)
        return self.app.exec()


def main():
    window = MainWindow()
    sys.exit(window.run())


if __name__ == "__main__":
    main()
