#!/usr/bin/env python3
"""
Fallback Wrench Designer - Works without FreeCAD
Creates 2D technical drawings and comprehensive analysis using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math
import os
from matplotlib.backends.backend_pdf import PdfPages

class FallbackWrenchDesigner:
    """Fallback wrench designer using matplotlib for visualization"""
    
    def __init__(self):
        self.wrench_params = {
            'handle_length': 150.0,
            'handle_width': 15.0, 
            'handle_thickness': 8.0,
            'head_width': 30.0,
            'head_length': 25.0,
            'hex_size': 8.0,
            'fillet_radius': 2.0,
            'material': 'Steel',
            'tolerance': 0.1
        }
    
    def create_hex_points(self, center_x, center_y, size):
        """Generate hexagon points for given center and size"""
        radius = size / math.sqrt(3)  # Convert flat-to-flat to circumradius
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append([x, y])
        return np.array(points)
    
    def draw_wrench_top_view(self, ax):
        """Draw top view of wrench"""
        # Handle rectangle
        handle = patches.Rectangle(
            (0, -self.wrench_params['handle_width']/2),
            self.wrench_params['handle_length'],
            self.wrench_params['handle_width'],
            linewidth=2, edgecolor='black', facecolor='lightgray'
        )
        ax.add_patch(handle)
        
        # Head rectangle
        head_y_offset = (self.wrench_params['head_width'] - self.wrench_params['handle_width']) / 2
        head = patches.Rectangle(
            (self.wrench_params['handle_length'], -self.wrench_params['head_width']/2),
            self.wrench_params['head_length'],
            self.wrench_params['head_width'],
            linewidth=2, edgecolor='black', facecolor='lightgray'
        )
        ax.add_patch(head)
        
        # Hexagonal hole
        hex_center_x = self.wrench_params['handle_length'] + self.wrench_params['head_length']/2
        hex_center_y = 0
        hex_points = self.create_hex_points(hex_center_x, hex_center_y, self.wrench_params['hex_size'])
        hex_hole = patches.Polygon(hex_points, closed=True, 
                                 linewidth=2, edgecolor='red', facecolor='white')
        ax.add_patch(hex_hole)
        
        # Add dimensions
        self.add_dimensions_top_view(ax)
        
        ax.set_xlim(-10, self.wrench_params['handle_length'] + self.wrench_params['head_length'] + 10)
        ax.set_ylim(-25, 25)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title('Wrench - Top View', fontsize=14, fontweight='bold')
    
    def draw_wrench_side_view(self, ax):
        """Draw side view of wrench"""
        total_length = self.wrench_params['handle_length'] + self.wrench_params['head_length']
        
        # Main body rectangle (side view)
        body = patches.Rectangle(
            (0, 0),
            total_length,
            self.wrench_params['handle_thickness'],
            linewidth=2, edgecolor='black', facecolor='lightgray'
        )
        ax.add_patch(body)
        
        # Add dimensions
        self.add_dimensions_side_view(ax)
        
        ax.set_xlim(-10, total_length + 10)
        ax.set_ylim(-5, self.wrench_params['handle_thickness'] + 5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title('Wrench - Side View', fontsize=14, fontweight='bold')
    
    def add_dimensions_top_view(self, ax):
        """Add dimension lines to top view"""
        # Overall length
        y_pos = 20
        ax.annotate('', xy=(0, y_pos), xytext=(self.wrench_params['handle_length'] + self.wrench_params['head_length'], y_pos),
                   arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5))
        ax.text((self.wrench_params['handle_length'] + self.wrench_params['head_length'])/2, y_pos + 2,
                f'{self.wrench_params["handle_length"] + self.wrench_params["head_length"]:.0f}mm',
                ha='center', va='bottom', color='blue', fontweight='bold')
        
        # Handle length
        y_pos = -20
        ax.annotate('', xy=(0, y_pos), xytext=(self.wrench_params['handle_length'], y_pos),
                   arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
        ax.text(self.wrench_params['handle_length']/2, y_pos - 2,
                f'{self.wrench_params["handle_length"]:.0f}mm',
                ha='center', va='top', color='green', fontweight='bold')
        
        # Head width
        x_pos = self.wrench_params['handle_length'] + self.wrench_params['head_length'] + 5
        ax.annotate('', xy=(x_pos, -self.wrench_params['head_width']/2), 
                   xytext=(x_pos, self.wrench_params['head_width']/2),
                   arrowprops=dict(arrowstyle='<->', color='orange', lw=1.5))
        ax.text(x_pos + 1, 0, f'{self.wrench_params["head_width"]:.0f}mm',
                ha='left', va='center', color='orange', fontweight='bold', rotation=90)
        
        # Hex size
        hex_center_x = self.wrench_params['handle_length'] + self.wrench_params['head_length']/2
        ax.text(hex_center_x, -5, f'⬡ {self.wrench_params["hex_size"]:.0f}mm',
                ha='center', va='top', color='red', fontweight='bold')
    
    def add_dimensions_side_view(self, ax):
        """Add dimension lines to side view"""
        # Thickness
        x_pos = -5
        ax.annotate('', xy=(x_pos, 0), xytext=(x_pos, self.wrench_params['handle_thickness']),
                   arrowprops=dict(arrowstyle='<->', color='purple', lw=1.5))
        ax.text(x_pos - 1, self.wrench_params['handle_thickness']/2,
                f'{self.wrench_params["handle_thickness"]:.0f}mm',
                ha='right', va='center', color='purple', fontweight='bold', rotation=90)
    
    def create_technical_drawing(self, output_path="/project/workspace/wrench_technical_drawing_fallback.pdf"):
        """Create comprehensive technical drawing with PDF export"""
        try:
            # Create figure with subplots
            fig = plt.figure(figsize=(16, 12))
            
            # Top view
            ax1 = plt.subplot(2, 2, 1)
            self.draw_wrench_top_view(ax1)
            
            # Side view
            ax2 = plt.subplot(2, 2, 2)
            self.draw_wrench_side_view(ax2)
            
            # 3D isometric view
            ax3 = plt.subplot(2, 2, 3, projection='3d')
            self.draw_3d_isometric(ax3)
            
            # Specifications table
            ax4 = plt.subplot(2, 2, 4)
            self.draw_specifications_table(ax4)
            
            # Main title
            fig.suptitle('WRENCH DESIGN - TECHNICAL DRAWING', fontsize=20, fontweight='bold')
            
            # Add notes
            fig.text(0.02, 0.02, 
                    f'Material: {self.wrench_params["material"]} | Tolerance: ±{self.wrench_params["tolerance"]}mm | Scale: 1:1',
                    fontsize=10, style='italic')
            
            plt.tight_layout()
            
            # Export to PDF
            with PdfPages(output_path) as pdf:
                pdf.savefig(fig, bbox_inches='tight', dpi=300)
            
            plt.close()
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✓ Technical drawing exported: {output_path} ({file_size} bytes)")
                return True
            else:
                print("✗ PDF export failed")
                return False
                
        except Exception as e:
            print(f"✗ Technical drawing error: {e}")
            return False
    
    def draw_3d_isometric(self, ax):
        """Draw 3D isometric view"""
        # Define vertices of the wrench
        handle_length = self.wrench_params['handle_length']
        handle_width = self.wrench_params['handle_width']
        handle_thickness = self.wrench_params['handle_thickness']
        head_length = self.wrench_params['head_length']
        head_width = self.wrench_params['head_width']
        
        # Handle vertices
        handle_vertices = np.array([
            [0, -handle_width/2, 0],
            [handle_length, -handle_width/2, 0],
            [handle_length, handle_width/2, 0],
            [0, handle_width/2, 0],
            [0, -handle_width/2, handle_thickness],
            [handle_length, -handle_width/2, handle_thickness],
            [handle_length, handle_width/2, handle_thickness],
            [0, handle_width/2, handle_thickness]
        ])
        
        # Head vertices
        head_offset_y = (head_width - handle_width) / 2
        head_vertices = np.array([
            [handle_length, -head_width/2, 0],
            [handle_length + head_length, -head_width/2, 0],
            [handle_length + head_length, head_width/2, 0],
            [handle_length, head_width/2, 0],
            [handle_length, -head_width/2, handle_thickness],
            [handle_length + head_length, -head_width/2, handle_thickness],
            [handle_length + head_length, head_width/2, handle_thickness],
            [handle_length, head_width/2, handle_thickness]
        ])
        
        # Draw handle
        for i in range(4):
            ax.plot3D(*zip(handle_vertices[i], handle_vertices[(i+1)%4]), 'b-', linewidth=2)
            ax.plot3D(*zip(handle_vertices[i+4], handle_vertices[((i+1)%4)+4]), 'b-', linewidth=2)
            ax.plot3D(*zip(handle_vertices[i], handle_vertices[i+4]), 'b-', linewidth=2)
        
        # Draw head
        for i in range(4):
            ax.plot3D(*zip(head_vertices[i], head_vertices[(i+1)%4]), 'r-', linewidth=2)
            ax.plot3D(*zip(head_vertices[i+4], head_vertices[((i+1)%4)+4]), 'r-', linewidth=2)
            ax.plot3D(*zip(head_vertices[i], head_vertices[i+4]), 'r-', linewidth=2)
        
        # Draw hexagonal hole outline
        hex_center = [handle_length + head_length/2, 0, handle_thickness/2]
        hex_points_3d = []
        for i in range(6):
            angle = i * math.pi / 3
            radius = self.wrench_params['hex_size'] / math.sqrt(3)
            x = hex_center[0]
            y = hex_center[1] + radius * math.cos(angle)
            z = hex_center[2] + radius * math.sin(angle)
            hex_points_3d.append([x, y, z])
        
        hex_points_3d.append(hex_points_3d[0])  # Close the shape
        hex_array = np.array(hex_points_3d)
        ax.plot3D(hex_array[:, 0], hex_array[:, 1], hex_array[:, 2], 'g-', linewidth=3)
        
        ax.set_xlabel('Length (mm)')
        ax.set_ylabel('Width (mm)')
        ax.set_zlabel('Thickness (mm)')
        ax.set_title('3D Isometric View', fontweight='bold')
    
    def draw_specifications_table(self, ax):
        """Draw specifications table"""
        ax.axis('off')
        
        # Calculate derived values
        total_length = self.wrench_params['handle_length'] + self.wrench_params['head_length']
        volume = (self.wrench_params['handle_length'] * self.wrench_params['handle_width'] * 
                 self.wrench_params['handle_thickness']) + \
                (self.wrench_params['head_length'] * self.wrench_params['head_width'] * 
                 self.wrench_params['handle_thickness'])
        
        # Remove hex hole volume
        hex_area = 3 * math.sqrt(3) / 2 * (self.wrench_params['hex_size'] / 2) ** 2
        hex_volume = hex_area * self.wrench_params['handle_thickness']
        net_volume = volume - hex_volume
        
        # Estimate mass and cost
        steel_density = 7.85e-6  # kg/mm³
        mass = net_volume * steel_density
        material_cost = mass * 2.0  # $2/kg
        machining_cost = 20.0  # Estimated
        total_cost = material_cost + machining_cost
        
        specs = [
            ['DESIGN SPECIFICATIONS', ''],
            ['Overall Length', f'{total_length:.1f} mm'],
            ['Handle Length', f'{self.wrench_params["handle_length"]:.1f} mm'],
            ['Handle Width', f'{self.wrench_params["handle_width"]:.1f} mm'],
            ['Head Dimensions', f'{self.wrench_params["head_length"]:.1f} × {self.wrench_params["head_width"]:.1f} mm'],
            ['Thickness', f'{self.wrench_params["handle_thickness"]:.1f} mm'],
            ['Hex Opening', f'{self.wrench_params["hex_size"]:.1f} mm across flats'],
            ['', ''],
            ['MATERIAL PROPERTIES', ''],
            ['Material', self.wrench_params["material"]],
            ['Tolerance', f'±{self.wrench_params["tolerance"]:.1f} mm'],
            ['Volume', f'{net_volume:.0f} mm³'],
            ['Mass', f'{mass:.3f} kg'],
            ['', ''],
            ['COST ESTIMATION', ''],
            ['Material Cost', f'${material_cost:.2f}'],
            ['Machining Cost', f'${machining_cost:.2f}'],
            ['Total Cost', f'${total_cost:.2f}'],
            ['', ''],
            ['MANUFACTURING NOTES', ''],
            ['• CNC machining recommended', ''],
            ['• Use hex broach for opening', ''],
            ['• Heat treatment optional', ''],
            ['• Surface finish: Ra ≤ 3.2 μm', '']
        ]
        
        # Create table
        table_data = []
        colors = []
        for spec in specs:
            if spec[0] and spec[0].isupper() and not spec[1]:
                colors.append(['lightblue', 'lightblue'])
            elif spec[0].startswith('•'):
                colors.append(['lightyellow', 'lightyellow'])
            else:
                colors.append(['white', 'white'])
            table_data.append(spec)
        
        table = ax.table(cellText=table_data,
                        colWidths=[0.6, 0.4],
                        cellLoc='left',
                        loc='center',
                        cellColours=colors)
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        ax.set_title('Design Specifications & Analysis', fontweight='bold', pad=20)
    
    def analyze_manufacturability(self):
        """Perform manufacturability analysis"""
        analysis = {}
        
        # Calculate volumes
        handle_volume = (self.wrench_params['handle_length'] * 
                        self.wrench_params['handle_width'] * 
                        self.wrench_params['handle_thickness'])
        
        head_volume = (self.wrench_params['head_length'] * 
                      self.wrench_params['head_width'] * 
                      self.wrench_params['handle_thickness'])
        
        # Hex hole volume
        hex_area = 3 * math.sqrt(3) / 2 * (self.wrench_params['hex_size'] / 2) ** 2
        hex_volume = hex_area * self.wrench_params['handle_thickness']
        
        net_volume = handle_volume + head_volume - hex_volume
        analysis['volume'] = net_volume
        
        # Surface area estimation
        perimeter = 2 * (self.wrench_params['handle_length'] + self.wrench_params['handle_width']) + \
                   2 * (self.wrench_params['head_length'] + self.wrench_params['head_width'])
        surface_area = 2 * (handle_volume + head_volume) / self.wrench_params['handle_thickness'] + \
                      perimeter * self.wrench_params['handle_thickness']
        analysis['surface_area'] = surface_area
        
        # Material efficiency
        total_stock_volume = (self.wrench_params['handle_length'] + self.wrench_params['head_length']) * \
                           self.wrench_params['head_width'] * self.wrench_params['handle_thickness']
        analysis['material_efficiency'] = (net_volume / total_stock_volume) * 100
        
        # Manufacturing assessment
        constraints = []
        
        if self.wrench_params['handle_thickness'] >= 3.0:
            constraints.append("✓ Adequate thickness for machining")
        else:
            constraints.append("⚠ Thin sections may be difficult to machine")
        
        if 6 <= self.wrench_params['hex_size'] <= 25:
            constraints.append("✓ Standard hex size")
        else:
            constraints.append("⚠ Non-standard hex size")
        
        if self.wrench_params['handle_length'] >= 100:
            constraints.append("✓ Adequate leverage")
        else:
            constraints.append("⚠ Short handle limits torque")
        
        if analysis['material_efficiency'] > 60:
            constraints.append("✓ Good material utilization")
        else:
            constraints.append("⚠ Consider material optimization")
        
        analysis['constraints'] = constraints
        
        # Cost estimation
        steel_density = 7.85e-6  # kg/mm³
        steel_cost = 2.0  # $/kg
        
        mass = net_volume * steel_density
        material_cost = mass * steel_cost
        machining_time = 15 + surface_area / 1000  # minutes
        machining_cost = machining_time * 1.5  # $/min
        
        analysis['cost'] = {
            'mass_kg': mass,
            'material_cost': material_cost,
            'machining_cost': machining_cost,
            'total_cost': material_cost + machining_cost
        }
        
        return analysis
    
    def generate_report(self, analysis, output_path="/project/workspace/wrench_manufacturing_report_fallback.md"):
        """Generate comprehensive manufacturing report"""
        try:
            total_length = self.wrench_params['handle_length'] + self.wrench_params['head_length']
            
            report = f"""# Wrench Design Manufacturing Report (Fallback Analysis)

## Executive Summary
This report provides a comprehensive analysis of the wrench design, including manufacturability assessment, cost estimation, and production recommendations.

## Design Specifications

### Dimensions
- **Overall Length**: {total_length:.1f} mm
- **Handle**: {self.wrench_params['handle_length']:.1f} × {self.wrench_params['handle_width']:.1f} × {self.wrench_params['handle_thickness']:.1f} mm
- **Head**: {self.wrench_params['head_length']:.1f} × {self.wrench_params['head_width']:.1f} × {self.wrench_params['handle_thickness']:.1f} mm
- **Hex Opening**: {self.wrench_params['hex_size']:.1f} mm across flats

### Material Properties
- **Material**: {self.wrench_params['material']}
- **Tolerance**: ±{self.wrench_params['tolerance']:.1f} mm
- **Volume**: {analysis['volume']:.0f} mm³
- **Surface Area**: {analysis['surface_area']:.0f} mm²
- **Material Efficiency**: {analysis['material_efficiency']:.1f}%

## Manufacturing Analysis

### Production Method: CNC Machining
**Recommended Process:**
1. **Material**: Start with steel bar stock
2. **Roughing**: Remove bulk material with end mill
3. **Semi-finishing**: Machine to near-final dimensions
4. **Hex Opening**: Use hex broach or wire EDM
5. **Finishing**: Final pass for surface finish
6. **Quality Control**: Dimensional inspection

### Manufacturing Constraints
"""
            
            for constraint in analysis['constraints']:
                report += f"- {constraint}\n"
            
            report += f"""
## Cost Analysis

### Material Cost
- **Mass**: {analysis['cost']['mass_kg']:.3f} kg
- **Material Cost**: ${analysis['cost']['material_cost']:.2f}

### Production Cost
- **Machining Cost**: ${analysis['cost']['machining_cost']:.2f}
- **Total Estimated Cost**: ${analysis['cost']['total_cost']:.2f}

*Note: Costs are estimates based on standard rates and may vary by supplier and quantity.*

## Quality Requirements

### Dimensional Tolerances
- **Critical Dimensions**: ±{self.wrench_params['tolerance']:.1f} mm
- **Hex Opening**: ±0.05 mm (critical for fit)
- **Surface Finish**: Ra ≤ 3.2 μm on functional surfaces

### Testing Requirements
- **Dimensional Check**: All critical dimensions
- **Fit Test**: Verify hex opening with standard nuts
- **Load Test**: 150% of rated torque (if specified)

## Design Recommendations

### Performance Optimization
1. **Add chamfers** (0.5mm) to hex opening edges for easier nut insertion
2. **Consider knurling** on handle for improved grip
3. **Optimize fillet radii** at handle-head junction for stress relief

### Manufacturing Optimization
1. **Use standard bar stock** to minimize material waste
2. **Consider investment casting** for high-volume production
3. **Add tool access features** for automated machining

### Cost Reduction Opportunities
1. **Material optimization**: Reduce head width if torque allows
2. **Near-net shape**: Consider forging for high volumes
3. **Standard components**: Use standard hex broaches

## Standards and Compliance

### Applicable Standards
- **ISO 3318**: Open-end spanners - Maximum thickness of head
- **ISO 691**: Assembly tools for screws and nuts
- **ASME B18.3**: Socket screws and hexagon keys
- **DIN 911**: Hexagon socket head cap screws

### Safety Considerations
- **Material selection**: Ensure adequate strength for intended torque
- **Heat treatment**: Consider if high loads are expected
- **Surface treatment**: Anti-corrosion coating if required

## Production Recommendations

### Small Volume (1-100 units)
- **Method**: CNC machining from bar stock
- **Lead time**: 2-3 weeks
- **Cost**: Higher per-unit cost, lower tooling cost

### Medium Volume (100-1000 units)
- **Method**: CNC with dedicated fixtures
- **Lead time**: 4-6 weeks (including fixture design)
- **Cost**: Moderate per-unit cost

### High Volume (1000+ units)
- **Method**: Investment casting + machining
- **Lead time**: 8-12 weeks (including tooling)
- **Cost**: Lower per-unit cost, higher initial investment

## Conclusion

The wrench design is manufacturable using standard machining processes. The design shows good material efficiency at {analysis['material_efficiency']:.1f}% and reasonable cost structure. Key considerations for production include:

1. Hex opening precision is critical for functionality
2. Material selection should match intended torque requirements
3. Production method should be selected based on volume requirements
4. Quality control focus on dimensional accuracy and surface finish

---

*This analysis was generated using the Fallback Wrench Designer system.*
*Report generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            with open(output_path, 'w') as f:
                f.write(report)
            
            print(f"✓ Manufacturing report generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Report generation error: {e}")
            return False
    
    def design_wrench(self):
        """Main design workflow"""
        print("Starting Fallback Wrench Design Process...")
        print("="*60)
        
        # Create technical drawing
        print("Creating 2D technical drawing...")
        drawing_success = self.create_technical_drawing()
        
        # Analyze manufacturability
        print("Performing manufacturability analysis...")
        analysis = self.analyze_manufacturability()
        
        # Generate report
        print("Generating manufacturing report...")
        report_success = self.generate_report(analysis)
        
        # Display summary
        print("\n" + "="*60)
        print("MANUFACTURABILITY ANALYSIS SUMMARY")
        print("="*60)
        print(f"Volume: {analysis['volume']:.0f} mm³")
        print(f"Surface Area: {analysis['surface_area']:.0f} mm²")
        print(f"Material Efficiency: {analysis['material_efficiency']:.1f}%")
        print(f"Estimated Mass: {analysis['cost']['mass_kg']:.3f} kg")
        print(f"Estimated Cost: ${analysis['cost']['total_cost']:.2f}")
        
        print("\nManufacturing Assessment:")
        for constraint in analysis['constraints']:
            print(f"  {constraint}")
        
        print("\n" + "="*60)
        print("DESIGN PROCESS COMPLETED")
        print("="*60)
        print(f"{'✓' if drawing_success else '✗'} Technical drawing {'created' if drawing_success else 'failed'}")
        print("✓ Manufacturability analysis completed")
        print(f"{'✓' if report_success else '✗'} Manufacturing report {'generated' if report_success else 'failed'}")
        print("="*60)
        
        return drawing_success and report_success


def main():
    """Main execution function"""
    try:
        designer = FallbackWrenchDesigner()
        success = designer.design_wrench()
        
        if success:
            print("\n🎉 Fallback wrench design completed successfully!")
            print("\nGenerated files:")
            print("📄 wrench_technical_drawing_fallback.pdf")
            print("📄 wrench_manufacturing_report_fallback.md")
        else:
            print("\n❌ Some components of the design process failed")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Design process failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()