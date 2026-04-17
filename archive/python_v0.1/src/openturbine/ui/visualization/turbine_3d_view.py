try:
    import vtk
    HAS_VTK = True
except ImportError:
    HAS_VTK = False

try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout
    from PySide6.QtCore import QTimer, Qt
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False

import math
import numpy as np


class Turbine3DVisualization:
    """3D visualization of wind turbine using VTK."""
    
    def __init__(self):
        if not HAS_VTK:
            raise ImportError("VTK is required for 3D visualization. Install with: pip install vtk")
        
        self.renderer = vtk.vtkRenderer()
        self.render_window = None
        self.interactor = None
        
        self.blade_actors = []
        self.hub_actor = None
        self.nacelle_actor = None
        self.tower_actor = None
        
        self.wind_particles = []
        self.wind_particle_actor = None
        
        self.current_rotor_angle = 0.0
        self.rotor_rpm = 12.0
        self.wind_speed = 8.0
        self.num_blades = 3
        self.blade_length = 61.5
        self.rotor_diameter = 126.0
        self.hub_height = 90.0
        
        self.animation_enabled = False
        self.frame_rate = 30
        
        self._create_turbine_model()
        self._create_wind_particles()
    
    def _create_turbine_model(self):
        self._create_tower()
        self._create_nacelle()
        self._create_hub()
        self._create_blades()
    
    def _create_tower(self):
        tower = vtk.vtkCylinderSource()
        tower.SetHeight(self.hub_height)
        tower.SetRadius(3.0)
        tower.SetResolution(32)
        
        tower_mapper = vtk.vtkPolyDataMapper()
        tower_mapper.SetInputConnection(tower.GetOutputPort())
        
        tower_actor = vtk.vtkActor()
        tower_actor.SetMapper(tower_mapper)
        tower_actor.GetProperty().SetColor(0.7, 0.7, 0.7)
        tower_actor.GetProperty().SetSpecular(0.3)
        tower_actor.GetProperty().SetSpecularPower(20)
        
        self.renderer.AddActor(tower_actor)
        self.tower_actor = tower_actor
    
    def _create_nacelle(self):
        nacelle = vtk.vtkBoxSource()
        nacelle.SetXLength(5.6)
        nacelle.SetYLength(2.6)
        nacelle.SetZLength(2.6)
        
        nacelle_mapper = vtk.vtkPolyDataMapper()
        nacelle_mapper.SetInputConnection(nacelle.GetOutputPort())
        
        nacelle_actor = vtk.vtkActor()
        nacelle_actor.SetMapper(nacelle_mapper)
        nacelle_actor.GetProperty().SetColor(0.6, 0.6, 0.6)
        nacelle_actor.GetProperty().SetSpecular(0.4)
        
        nacelle_actor.SetPosition(0, self.hub_height + 1.3, 0)
        self.renderer.AddActor(nacelle_actor)
        self.nacelle_actor = nacelle_actor
    
    def _create_hub(self):
        hub = vtk.vtkSphereSource()
        hub.SetRadius(1.5)
        hub.SetThetaResolution(16)
        hub.SetPhiResolution(16)
        
        hub_mapper = vtk.vtkPolyDataMapper()
        hub_mapper.SetInputConnection(hub.GetOutputPort())
        
        hub_actor = vtk.vtkActor()
        hub_actor.SetMapper(hub_mapper)
        hub_actor.GetProperty().SetColor(0.8, 0.8, 0.2)
        hub_actor.GetProperty().SetSpecular(0.5)
        
        hub_actor.SetPosition(0, self.hub_height + 2.5, 0)
        self.renderer.AddActor(hub_actor)
        self.hub_actor = hub_actor
    
    def _create_blades(self):
        self.blade_actors = []
        
        for i in range(self.num_blades):
            blade_mapper = self._create_blade_geometry()
            blade_actor = vtk.vtkActor()
            blade_actor.SetMapper(blade_mapper)
            blade_actor.GetProperty().SetColor(0.9, 0.9, 0.9)
            blade_actor.GetProperty().SetSpecular(0.2)
            
            angle = 2 * math.pi * i / self.num_blades
            blade_actor.SetPosition(0, self.hub_height + 2.5, 0)
            blade_actor.SetOrientation(0, math.degrees(angle), 90)
            
            self.renderer.AddActor(blade_actor)
            self.blade_actors.append(blade_actor)
    
    def _create_blade_geometry(self):
        points = vtk.vtkPoints()
        polygons = vtk.vtkCellArray()
        
        chord_points = [3.5, 4.1, 4.3, 3.5, 2.5, 1.7, 1.0, 0.65]
        lengths = [0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0]
        
        num_segments = 50
        for i in range(len(chord_points)):
            r = lengths[i] * self.blade_length
            for j in range(num_segments):
                angle = 2 * math.pi * j / num_segments
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                
                chord = chord_points[i]
                points.InsertNextPoint(x, y, -chord/2)
                points.InsertNextPoint(x, y, chord/2)
        
        for i in range(len(chord_points) - 1):
            for j in range(num_segments):
                p1 = i * num_segments * 2 + j * 2
                p2 = i * num_segments * 2 + ((j + 1) % num_segments) * 2
                p3 = (i + 1) * num_segments * 2 + ((j + 1) % num_segments) * 2
                p4 = (i + 1) * num_segments * 2 + j * 2
                
                polygon1 = vtk.vtkPolygon()
                polygon1.GetPointIds().SetId(0, p1)
                polygon1.GetPointIds().SetId(1, p2)
                polygon1.GetPointIds().SetId(2, p3)
                polygons.InsertNextCell(polygon1)
                
                polygon2 = vtk.vtkPolygon()
                polygon2.GetPointIds().SetId(0, p1)
                polygon2.GetPointIds().SetId(1, p3)
                polygon2.GetPointIds().SetId(2, p4)
                polygons.InsertNextCell(polygon2)
        
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetPolys(polygons)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)
        
        return mapper
    
    def _create_wind_particles(self):
        num_particles = 500
        
        points = vtk.vtkPoints()
        velocities = vtk.vtkFloatArray()
        velocities.SetName("velocities")
        velocities.SetNumberOfComponents(3)
        
        for i in range(num_particles):
            x = np.random.uniform(-50, 50)
            y = np.random.uniform(self.hub_height - 30, self.hub_height + 30)
            z = np.random.uniform(-30, 30)
            
            points.InsertNextPoint(x, y, z)
            velocities.InsertNextTuple3(self.wind_speed, 0, 0)
        
        particle_data = vtk.vtkPolyData()
        particle_data.SetPoints(points)
        particle_data.GetPointData().AddArray(velocities)
        
        glyph = vtk.vtkArrowSource()
        glyph.SetTipLength(0.1)
        glyph.SetTipRadius(0.05)
        glyph.SetShaftRadius(0.02)
        
        glyph_filter = vtk.vtkGlyph3D()
        glyph_filter.SetInputData(particle_data)
        glyph_filter.SetSourceConnection(glyph.GetOutputPort())
        glyph_filter.SetVectorModeToUseVector()
        glyph_filter.SetScaleModeToDataScalingOff()
        glyph_filter.SetScaleFactor(0.5)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(glyph_filter.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.3, 0.6, 1.0)
        actor.GetProperty().SetOpacity(0.6)
        
        self.renderer.AddActor(actor)
        self.wind_particle_actor = actor
    
    def update_wind_particles(self, dt):
        if not self.wind_particle_actor:
            return
        
        points = self.wind_particle_actor.GetMapper().GetInput()
        if points:
            point_array = points.GetPoints()
            num_points = point_array.GetNumberOfPoints()
            
            for i in range(num_points):
                p = point_array.GetPoint(i)
                new_x = (p[0] + self.wind_speed * dt) % 50 - 25
                point_array.SetPoint(i, new_x, p[1], p[2])
            
            point_array.Modified()
    
    def update_blade_positions(self, angle):
        self.current_rotor_angle = angle
        
        for i, blade_actor in enumerate(self.blade_actors):
            blade_angle = angle + 2 * math.pi * i / self.num_blades
            blade_actor.SetOrientation(0, math.degrees(blade_angle), 90)
    
    def update_parameters(self, rotor_diameter=None, blade_length=None, hub_height=None,
                         num_blades=None, wind_speed=None, rotor_rpm=None):
        if rotor_diameter is not None:
            self.rotor_diameter = rotor_diameter
        if blade_length is not None:
            self.blade_length = blade_length
        if hub_height is not None:
            self.hub_height = hub_height
        if num_blades is not None and num_blades != self.num_blades:
            self.num_blades = num_blades
            self._recreate_blades()
        if wind_speed is not None:
            self.wind_speed = wind_speed
        if rotor_rpm is not None:
            self.rotor_rpm = rotor_rpm
    
    def _recreate_blades(self):
        for actor in self.blade_actors:
            self.renderer.RemoveActor(actor)
        self.blade_actors = []
        self._create_blades()
    
    def set_animation_enabled(self, enabled):
        self.animation_enabled = enabled
    
    def get_renderer(self):
        return self.renderer
    
    def update_animation(self, dt):
        if self.animation_enabled:
            angular_velocity = self.rotor_rpm * 2 * math.pi / 60.0
            self.current_rotor_angle += angular_velocity * dt
            self.update_blade_positions(self.current_rotor_angle)
            self.update_wind_particles(dt)


class VTKViewportWidget:
    """Qt widget containing VTK viewport for 3D visualization."""
    
    def __init__(self, parent=None):
        if not HAS_VTK or not HAS_PYSIDE:
            raise ImportError("VTK and PySide6 are required for 3D visualization")
        
        self.widget = QWidget(parent)
        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.visualization = Turbine3DVisualization()
        renderer = self.visualization.get_renderer()
        
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetOffScreenRendering(1)
        self.render_window.AddRenderer(renderer)
        
        self.interactor = vtk.vtkGenericRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        
        self.widget.SetBackend(self.interactor)
        
        renderer.SetBackground(0.1, 0.1, 0.15)
        renderer.ResetCamera()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer)
        self.last_time = 0
    
    def _on_timer(self):
        import time
        current_time = time.time()
        if self.last_time > 0:
            dt = current_time - self.last_time
            self.visualization.update_animation(dt)
            self.render_window.Render()
        self.last_time = current_time
    
    def start_animation(self):
        self.visualization.set_animation_enabled(True)
        self.timer.start(33)
    
    def stop_animation(self):
        self.visualization.set_animation_enabled(False)
        self.timer.stop()
    
    def update_parameters(self, **kwargs):
        self.visualization.update_parameters(**kwargs)
        self.render_window.Render()
    
    def get_visualization(self):
        return self.visualization


def create_simple_turbine_plot(rotor_diameter=126.0, hub_height=90.0, num_blades=3):
    """Create a simple matplotlib 3D plot of a wind turbine for fallback."""
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    ax.set_xlim([-rotor_diameter/2, rotor_diameter/2])
    ax.set_ylim([-rotor_diameter/2, rotor_diameter/2])
    ax.set_zlim([0, hub_height + rotor_diameter/2])
    
    theta = np.linspace(0, 2*np.pi, 100)
    
    ax.plot([0, 0], [0, 0], [0, hub_height], 'gray', linewidth=10, label='Tower')
    
    ax.scatter([0], [0], [hub_height], color='yellow', s=500, label='Hub')
    
    blade_length = rotor_diameter / 2 - 3
    for i in range(num_blades):
        angle = 2 * np.pi * i / num_blades
        x = blade_length * np.cos(angle) * np.sin(theta)
        y = blade_length * np.sin(angle) * np.sin(theta)
        z = hub_height + 2.5 + blade_length * np.cos(theta)
        
        ax.plot(x, y, z, 'white', linewidth=3)
    
    wind_x = np.linspace(-rotor_diameter, rotor_diameter, 20)
    wind_y = np.zeros(20)
    wind_z = np.ones(20) * hub_height
    ax.quiver(wind_x, wind_y, wind_z, 10*np.ones(20), np.zeros(20), np.zeros(20), 
              color='cyan', alpha=0.3, arrow_length_ratio=0.3)
    
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title(f'Wind Turbine - {rotor_diameter}m Diameter, {num_blades} Blades')
    ax.legend()
    
    return fig
