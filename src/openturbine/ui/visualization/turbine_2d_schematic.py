import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Rectangle, Polygon, Arc
from matplotlib.collections import PatchCollection, LineCollection
import matplotlib.patches as mpatches


class Turbine2DSchematic:
    """2D schematic view of wind turbine components."""
    
    def __init__(self, rotor_diameter=126.0, hub_height=90.0, num_blades=3):
        self.rotor_diameter = rotor_diameter
        self.hub_height = hub_height
        self.num_blades = num_blades
        self.blade_length = rotor_diameter / 2 - 3
        self.current_blade_angle = 0.0
        
        self.fig, self.ax = plt.subplots(1, 1, figsize=(12, 10))
        self._setup_axes()
    
    def _setup_axes(self):
        margin = self.rotor_diameter * 0.3
        self.ax.set_xlim(-self.rotor_diameter/2 - margin, self.rotor_diameter/2 + margin)
        self.ax.set_ylim(0, self.hub_height + self.rotor_diameter/2 + margin)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel('Distance (m)')
        self.ax.set_ylabel('Height (m)')
    
    def draw_tower(self):
        tower_base = self.rotor_diameter * 0.08
        tower_top = self.rotor_diameter * 0.04
        
        x = [0, tower_base/2, tower_base/2, -tower_base/2, -tower_base/2, 0]
        y = [0, 0, self.hub_height, self.hub_height, 0, 0]
        
        tower = Polygon(list(zip(x, y)), facecolor='#888888', edgecolor='black', linewidth=2)
        self.ax.add_patch(tower)
        
        self.ax.plot([0, 0], [0, self.hub_height], 'k--', alpha=0.5)
    
    def draw_nacelle(self):
        nacelle_length = self.rotor_diameter * 0.08
        nacelle_height = self.rotor_diameter * 0.04
        
        nacelle = FancyBboxPatch(
            (-nacelle_length/2, self.hub_height),
            nacelle_length, nacelle_height,
            boxstyle="round,pad=0.02",
            facecolor='#666666',
            edgecolor='black',
            linewidth=2
        )
        self.ax.add_patch(nacelle)
    
    def draw_hub(self):
        hub_radius = self.rotor_diameter * 0.03
        
        hub = Circle((0, self.hub_height + self.rotor_diameter * 0.04), hub_radius,
                     facecolor='#CCCC00', edgecolor='black', linewidth=2)
        self.ax.add_patch(hub)
        
        return hub_radius
    
    def draw_blades(self, angle=None):
        if angle is None:
            angle = self.current_blade_angle
        
        hub_radius = self.rotor_diameter * 0.03
        blade_root = self.hub_height + self.rotor_diameter * 0.04 + hub_radius
        
        chord_points = np.array([
            [3.5, 4.1, 4.3, 3.5, 2.5, 1.7, 1.0, 0.65]
        ])
        lengths = np.array([0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0])
        
        for i in range(self.num_blades):
            blade_angle = angle + 2 * np.pi * i / self.num_blades
            
            blade_x = []
            blade_y = []
            
            for j in range(len(chord_points[0])):
                r = lengths[j] * self.blade_length
                x = r * np.cos(blade_angle)
                y = blade_root + r * np.sin(blade_angle)
                blade_x.append(x)
                blade_y.append(y)
            
            self.ax.plot(blade_x, blade_y, 'w-', linewidth=8, solid_capstyle='round')
            self.ax.plot(blade_x, blade_y, 'k-', linewidth=2)
    
    def draw_rotor_disk(self):
        hub_radius = self.rotor_diameter * 0.03
        hub_center = self.hub_height + self.rotor_diameter * 0.04 + hub_radius
        
        disk = Circle((0, hub_center), self.blade_length,
                      facecolor='none', edgecolor='gray', 
                      linewidth=1, linestyle='--', alpha=0.5)
        self.ax.add_patch(disk)
        
        return hub_center, hub_radius
    
    def draw_wind_arrows(self, wind_speed=8.0):
        num_arrows = 7
        arrow_spacing = self.rotor_diameter / (num_arrows + 1)
        
        for i in range(num_arrows):
            x = -self.rotor_diameter/2 + (i + 1) * arrow_spacing
            y = self.hub_height
            length = wind_speed * 0.3
            
            self.ax.annotate('', 
                           xy=(x + length, y), 
                           xytext=(x, y),
                           arrowprops=dict(arrowstyle='->', color='cyan', lw=2))
    
    def draw_wake_effect(self):
        hub_center, _ = self.draw_rotor_disk()
        
        wake_x = [0, self.rotor_diameter/2, self.rotor_diameter * 2]
        wake_width = [self.blade_length, self.blade_length * 1.5, self.blade_length * 2.5]
        
        wake_points = []
        for i in range(len(wake_x)):
            wake_points.append([wake_x[i], hub_center - wake_width[i]/2])
        for i in range(len(wake_x) - 1, -1, -1):
            wake_points.append([wake_x[i], hub_center + wake_width[i]/2])
        
        wake_polygon = Polygon(wake_points, facecolor='#FF6666', alpha=0.2, edgecolor='none')
        self.ax.add_patch(wake_polygon)
        
        self.ax.text(self.rotor_diameter * 0.8, hub_center, 'Wake', 
                    fontsize=10, color='red', alpha=0.7, ha='center')
    
    def draw_airfoil_section(self):
        fig_size = self.fig.get_size_inches()
        
        inset_ax = self.fig.add_axes([0.7, 0.65, 0.2, 0.2])
        
        chord = 4.0
        x = np.linspace(-chord/2, chord/2, 100)
        
        y_upper = 0.12 * chord * np.sqrt(1 - (2*x/chord)**2)
        y_lower = -0.06 * chord * np.sqrt(1 - (2*x/chord)**2)
        
        inset_ax.fill_between(x, y_lower, y_upper, color='#CCCCCC', edgecolor='black')
        inset_ax.plot(x, y_upper, 'k-', linewidth=2)
        inset_ax.plot(x, y_lower, 'k-', linewidth=2)
        inset_ax.plot([0, 0], [y_lower.min(), y_upper.max()], 'r--', linewidth=1)
        
        inset_ax.set_xlim(-chord/2 - 0.5, chord/2 + 0.5)
        inset_ax.set_ylim(-1, 1)
        inset_ax.set_aspect('equal')
        inset_ax.set_title('Airfoil Profile', fontsize=9)
        inset_ax.axis('off')
    
    def draw_force_diagram(self):
        inset_ax = self.fig.add_axes([0.7, 0.35, 0.2, 0.2])
        
        lift_arrow = [2, 1.5]
        drag_arrow = [1, 0.3]
        
        inset_ax.arrow(0, 0, lift_arrow[0], lift_arrow[1], 
                       head_width=0.2, head_length=0.1, fc='blue', ec='blue')
        inset_ax.arrow(0, 0, drag_arrow[0], drag_arrow[1], 
                       head_width=0.2, head_length=0.1, fc='red', ec='red')
        
        resultant = [lift_arrow[0] + drag_arrow[0], lift_arrow[1] + drag_arrow[1]]
        inset_ax.arrow(0, 0, resultant[0], resultant[1], 
                       head_width=0.2, head_length=0.1, fc='green', ec='green', linestyle='--')
        
        inset_ax.text(1.5, 1.8, 'Lift', fontsize=8, color='blue')
        inset_ax.text(1.2, 0.2, 'Drag', fontsize=8, color='red')
        inset_ax.text(2.5, 1.2, 'Resultant', fontsize=8, color='green')
        
        inset_ax.set_xlim(-0.5, 4)
        inset_ax.set_ylim(-0.5, 2.5)
        inset_ax.set_aspect('equal')
        inset_ax.set_title('Blade Forces', fontsize=9)
        inset_ax.axis('off')
        inset_ax.grid(True, alpha=0.3)
    
    def draw_all(self, wind_speed=8.0, show_details=True):
        self.ax.clear()
        self._setup_axes()
        
        self.draw_tower()
        self.draw_nacelle()
        self.draw_hub()
        self.draw_rotor_disk()
        self.draw_blades()
        self.draw_wind_arrows(wind_speed)
        self.draw_wake_effect()
        
        if show_details:
            self.draw_airfoil_section()
            self.draw_force_diagram()
        
        self.fig.tight_layout()
        return self.fig
    
    def update_blade_angle(self, angle):
        self.current_blade_angle = angle
        return self.draw_all(wind_speed=self.wind_speed if hasattr(self, 'wind_speed') else 8.0)
    
    def set_wind_speed(self, wind_speed):
        self.wind_speed = wind_speed
    
    def set_parameters(self, rotor_diameter=None, hub_height=None, num_blades=None):
        if rotor_diameter is not None:
            self.rotor_diameter = rotor_diameter
            self.blade_length = rotor_diameter / 2 - 3
        if hub_height is not None:
            self.hub_height = hub_height
        if num_blades is not None:
            self.num_blades = num_blades


def create_schematic_plot(rotor_diameter=126.0, hub_height=90.0, num_blades=3, 
                         wind_speed=8.0, blade_angle=0.0):
    """Create a complete 2D schematic plot."""
    schematic = Turbine2DSchematic(rotor_diameter, hub_height, num_blades)
    schematic.current_blade_angle = blade_angle
    schematic.wind_speed = wind_speed
    
    fig = schematic.draw_all(wind_speed=wind_speed, show_details=True)
    
    fig.suptitle(f'Wind Turbine Schematic\n'
                f'{rotor_diameter}m Diameter, {num_blades} Blades, '
                f'Hub Height {hub_height}m, Wind {wind_speed}m/s',
                fontsize=12, y=0.98)
    
    return fig, schematic
