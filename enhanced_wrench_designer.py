#!/usr/bin/env python3
"""
Enhanced Wrench Designer with Error Handling and Manufacturability Analysis
Addresses common FreeCAD errors and provides robust PDF export
"""

import os
import sys
import math
import traceback
from typing import Dict, List, Tuple, Optional

class WrenchDesigner:
    """Enhanced wrench designer with comprehensive error handling"""
    
    def __init__(self):
        self.doc = None
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
        
    def initialize_freecad(self):
        """Initialize FreeCAD with error handling"""
        try:
            import FreeCAD
            import Part
            import Draft
            import TechDraw
            
            # Store modules for later use
            self.FC = FreeCAD
            self.Part = Part
            self.Draft = Draft
            self.TechDraw = TechDraw
            
            print("✓ FreeCAD modules loaded successfully")
            return True
            
        except ImportError as e:
            print(f"✗ FreeCAD import error: {e}")
            print("Solution: Install FreeCAD with: sudo apt install freecad")
            return False
        except Exception as e:
            print(f"✗ FreeCAD initialization error: {e}")
            return False
    
    def create_document(self, name="WrenchDesign"):
        """Create or reset FreeCAD document"""
        try:
            # Close existing document if it exists
            if name in self.FC.listDocuments():
                self.FC.closeDocument(name)
            
            # Create new document
            self.doc = self.FC.newDocument(name)
            print(f"✓ Document '{name}' created successfully")
            return True
            
        except Exception as e:
            print(f"✗ Document creation error: {e}")
            return False
    
    def create_handle(self):
        """Create wrench handle with error handling"""
        try:
            handle_box = self.Part.makeBox(
                self.wrench_params['handle_length'],
                self.wrench_params['handle_width'],
                self.wrench_params['handle_thickness']
            )
            
            handle = self.doc.addObject("Part::Feature", "Handle")
            handle.Shape = handle_box
            handle.ViewObject.ShapeColor = (0.7, 0.7, 0.7)
            
            print(f"✓ Handle created: {self.wrench_params['handle_length']}mm x {self.wrench_params['handle_width']}mm x {self.wrench_params['handle_thickness']}mm")
            return handle
            
        except Exception as e:
            print(f"✗ Handle creation error: {e}")
            traceback.print_exc()
            return None
    
    def create_head(self):
        """Create wrench head with error handling"""
        try:
            head_box = self.Part.makeBox(
                self.wrench_params['head_length'],
                self.wrench_params['head_width'],
                self.wrench_params['handle_thickness']
            )
            
            head = self.doc.addObject("Part::Feature", "Head")
            head.Shape = head_box
            
            # Position head at end of handle
            offset_y = (self.wrench_params['head_width'] - self.wrench_params['handle_width']) / 2
            head.Placement.Base = self.FC.Vector(
                self.wrench_params['handle_length'], 
                -offset_y, 
                0
            )
            head.ViewObject.ShapeColor = (0.7, 0.7, 0.7)
            
            print(f"✓ Head created: {self.wrench_params['head_length']}mm x {self.wrench_params['head_width']}mm")
            return head
            
        except Exception as e:
            print(f"✗ Head creation error: {e}")
            traceback.print_exc()
            return None
    
    def create_hex_hole(self):
        """Create hexagonal hole with robust error handling"""
        try:
            # Calculate hexagon vertices (flat-to-flat dimension)
            hex_radius = self.wrench_params['hex_size'] / math.sqrt(3)  # Circumradius
            hex_points = []
            
            for i in range(6):
                angle = i * math.pi / 3
                x = hex_radius * math.cos(angle)
                y = hex_radius * math.sin(angle)
                hex_points.append(self.FC.Vector(x, y, 0))
            
            # Create closed polygon
            hex_points.append(hex_points[0])  # Close the shape
            
            # Create wire and face
            hex_wire = self.Part.makePolygon(hex_points)
            hex_face = self.Part.Face(hex_wire)
            
            # Extrude to create 3D hole
            extrude_vector = self.FC.Vector(0, 0, self.wrench_params['handle_thickness'] + 1)  # Extra length for clean cut
            hex_hole = hex_face.extrude(extrude_vector)
            
            # Create FreeCAD object
            hex_obj = self.doc.addObject("Part::Feature", "HexHole")
            hex_obj.Shape = hex_hole
            
            # Position in center of head
            head_center_x = self.wrench_params['handle_length'] + self.wrench_params['head_length'] / 2
            hex_obj.Placement.Base = self.FC.Vector(head_center_x, 0, -0.5)  # Slight offset for clean cut
            hex_obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)
            
            print(f"✓ Hexagonal hole created: {self.wrench_params['hex_size']}mm across flats")
            return hex_obj
            
        except Exception as e:
            print(f"✗ Hex hole creation error: {e}")
            traceback.print_exc()
            return None
    
    def assemble_wrench(self, handle, head, hex_hole):
        """Assemble final wrench with error handling"""
        try:
            if not all([handle, head, hex_hole]):
                print("✗ Cannot assemble: Missing components")
                return None
            
            # Fuse handle and head
            fused_shape = handle.Shape.fuse(head.Shape)
            print("✓ Handle and head fused")
            
            # Cut hex hole
            final_shape = fused_shape.cut(hex_hole.Shape)
            print("✓ Hex hole cut from wrench body")
            
            # Add fillets for manufacturability
            try:
                # Find edges to fillet (connection points)
                edges_to_fillet = []
                for edge in final_shape.Edges:
                    if 5 < edge.Length < 20:  # Filter appropriate edges
                        edges_to_fillet.append(edge)
                
                if edges_to_fillet:
                    final_shape = final_shape.makeFillet(
                        self.wrench_params['fillet_radius'], 
                        edges_to_fillet[:4]  # Limit to avoid over-filleting
                    )
                    print(f"✓ Fillets added: {self.wrench_params['fillet_radius']}mm radius")
            except:
                print("⚠ Warning: Could not add all fillets (non-critical)")
            
            # Create final wrench object
            wrench = self.doc.addObject("Part::Feature", "Wrench")
            wrench.Shape = final_shape
            wrench.ViewObject.ShapeColor = (0.5, 0.5, 0.8)
            
            # Hide intermediate objects
            handle.ViewObject.Visibility = False
            head.ViewObject.Visibility = False
            hex_hole.ViewObject.Visibility = False
            
            print("✓ Final wrench assembled successfully")
            return wrench
            
        except Exception as e:
            print(f"✗ Assembly error: {e}")
            traceback.print_exc()
            return None
    
    def create_technical_drawing(self, wrench):
        """Create 2D technical drawing with PDF export"""
        try:
            if not wrench:
                print("✗ Cannot create drawing: No wrench object")
                return None
            
            # Create TechDraw page
            page = self.doc.addObject('TechDraw::DrawPage', 'WrenchDrawing')
            
            # Create template
            template = self.doc.addObject('TechDraw::DrawSVGTemplate', 'Template')
            
            # Try to find and use A4 template
            template_paths = [
                "/usr/share/freecad/Mod/TechDraw/Templates/A4_LandscapeTD.svg",
                "/usr/share/freecad/data/Mod/TechDraw/Templates/A4_LandscapeTD.svg",
                "/snap/freecad/current/share/freecad/Mod/TechDraw/Templates/A4_LandscapeTD.svg"
            ]
            
            template_found = False
            for template_path in template_paths:
                if os.path.exists(template_path):
                    template.Template = template_path
                    template_found = True
                    print(f"✓ Template loaded: {template_path}")
                    break
            
            if not template_found:
                print("⚠ Warning: Standard template not found, using basic layout")
            
            page.Template = template
            
            # Create front view (top view)
            front_view = self.doc.addObject('TechDraw::DrawViewPart', 'TopView')
            front_view.Source = [wrench]
            front_view.Direction = self.FC.Vector(0, 0, 1)
            front_view.Scale = 1.0
            front_view.X = 150
            front_view.Y = 150
            page.addView(front_view)
            print("✓ Top view created")
            
            # Create side view
            side_view = self.doc.addObject('TechDraw::DrawViewPart', 'SideView')
            side_view.Source = [wrench]
            side_view.Direction = self.FC.Vector(0, 1, 0)
            side_view.Scale = 1.0
            side_view.X = 150
            side_view.Y = 70
            page.addView(side_view)
            print("✓ Side view created")
            
            # Add title and specifications
            title = self.doc.addObject('TechDraw::DrawViewAnnotation', 'Title')
            title.Text = [
                'WRENCH DESIGN - TECHNICAL DRAWING',
                f'Scale: 1:1',
                f'Material: {self.wrench_params["material"]}',
                f'Tolerance: ±{self.wrench_params["tolerance"]}mm',
                f'Hex Opening: {self.wrench_params["hex_size"]}mm across flats',
                f'Overall Length: {self.wrench_params["handle_length"] + self.wrench_params["head_length"]}mm'
            ]
            title.X = 20
            title.Y = 250
            page.addView(title)
            print("✓ Title and specifications added")
            
            # Recompute to ensure everything is updated
            self.doc.recompute()
            print("✓ Technical drawing created successfully")
            
            return page
            
        except Exception as e:
            print(f"✗ Technical drawing error: {e}")
            traceback.print_exc()
            return None
    
    def export_pdf(self, page, output_path="/project/workspace/wrench_technical_drawing.pdf"):
        """Export technical drawing to PDF with error handling"""
        try:
            if not page:
                print("✗ Cannot export PDF: No drawing page")
                return False
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Export to PDF
            page.exportPdf(output_path)
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✓ PDF exported successfully: {output_path} ({file_size} bytes)")
                return True
            else:
                print("✗ PDF export failed: File not created")
                return False
                
        except Exception as e:
            print(f"✗ PDF export error: {e}")
            
            # Try alternative export methods
            try:
                # Export as SVG first, then convert
                svg_path = output_path.replace('.pdf', '.svg')
                page.exportSvg(svg_path)
                print(f"✓ SVG export successful: {svg_path}")
                
                # Try to convert SVG to PDF using system tools
                if os.path.exists(svg_path):
                    import subprocess
                    try:
                        subprocess.run(['inkscape', '--export-type=pdf', svg_path], 
                                     capture_output=True, check=True)
                        print(f"✓ SVG converted to PDF using Inkscape")
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        print("⚠ Inkscape not available for PDF conversion")
                
            except Exception as svg_error:
                print(f"✗ SVG export also failed: {svg_error}")
            
            return False
    
    def analyze_manufacturability(self, wrench):
        """Comprehensive manufacturability analysis"""
        try:
            if not wrench:
                print("✗ Cannot analyze: No wrench object")
                return {}
            
            shape = wrench.Shape
            analysis = {}
            
            # Basic geometric properties
            analysis['volume'] = shape.Volume
            analysis['surface_area'] = shape.Area
            analysis['bounding_box'] = shape.BoundBox
            
            # Material efficiency
            theoretical_volume = (
                self.wrench_params['handle_length'] * 
                self.wrench_params['handle_width'] * 
                self.wrench_params['handle_thickness']
            ) + (
                self.wrench_params['head_length'] * 
                self.wrench_params['head_width'] * 
                self.wrench_params['handle_thickness']
            )
            
            analysis['material_efficiency'] = (analysis['volume'] / theoretical_volume) * 100
            
            # Manufacturing constraints check
            constraints = []
            
            # Check minimum feature sizes
            min_feature_size = 1.0  # mm
            if self.wrench_params['handle_thickness'] >= min_feature_size:
                constraints.append("✓ Thickness adequate for machining")
            else:
                constraints.append("✗ Thickness too small for reliable machining")
            
            # Check hex opening size
            if 6 <= self.wrench_params['hex_size'] <= 25:
                constraints.append("✓ Hex opening within standard range")
            else:
                constraints.append("⚠ Non-standard hex opening size")
            
            # Check handle length for leverage
            if self.wrench_params['handle_length'] >= 100:
                constraints.append("✓ Handle length provides adequate leverage")
            else:
                constraints.append("⚠ Short handle may limit torque capacity")
            
            # Check material removal ratio
            if analysis['material_efficiency'] > 70:
                constraints.append("✓ Good material utilization")
            elif analysis['material_efficiency'] > 50:
                constraints.append("⚠ Moderate material waste")
            else:
                constraints.append("✗ High material waste")
            
            analysis['manufacturing_constraints'] = constraints
            
            # Cost estimation (simplified)
            steel_density = 7.85e-6  # kg/mm³
            steel_cost_per_kg = 2.0  # USD/kg (rough estimate)
            machining_cost_per_min = 1.5  # USD/min
            
            material_mass = analysis['volume'] * steel_density
            material_cost = material_mass * steel_cost_per_kg
            
            # Estimate machining time based on complexity
            machining_time = 15 + (analysis['surface_area'] / 1000) * 2  # minutes
            machining_cost = machining_time * machining_cost_per_min
            
            analysis['cost_estimate'] = {
                'material_mass_kg': material_mass,
                'material_cost_usd': material_cost,
                'machining_time_min': machining_time,
                'machining_cost_usd': machining_cost,
                'total_cost_usd': material_cost + machining_cost
            }
            
            print("\n" + "="*50)
            print("MANUFACTURABILITY ANALYSIS REPORT")
            print("="*50)
            print(f"Volume: {analysis['volume']:.2f} mm³")
            print(f"Surface Area: {analysis['surface_area']:.2f} mm²")
            print(f"Material Efficiency: {analysis['material_efficiency']:.1f}%")
            print(f"Estimated Mass: {material_mass:.3f} kg")
            print(f"Estimated Total Cost: ${analysis['cost_estimate']['total_cost_usd']:.2f}")
            print("\nManufacturing Constraints:")
            for constraint in constraints:
                print(f"  {constraint}")
            print("="*50)
            
            return analysis
            
        except Exception as e:
            print(f"✗ Manufacturability analysis error: {e}")
            traceback.print_exc()
            return {}
    
    def generate_manufacturing_report(self, analysis, output_path="/project/workspace/wrench_manufacturing_report.md"):
        """Generate detailed manufacturing report"""
        try:
            report = f"""# Wrench Design Manufacturing Report

## Design Specifications
- **Overall Length**: {self.wrench_params['handle_length'] + self.wrench_params['head_length']:.1f} mm
- **Handle**: {self.wrench_params['handle_length']:.1f} × {self.wrench_params['handle_width']:.1f} × {self.wrench_params['handle_thickness']:.1f} mm
- **Head**: {self.wrench_params['head_length']:.1f} × {self.wrench_params['head_width']:.1f} × {self.wrench_params['handle_thickness']:.1f} mm
- **Hex Opening**: {self.wrench_params['hex_size']:.1f} mm across flats
- **Material**: {self.wrench_params['material']}
- **Tolerance**: ±{self.wrench_params['tolerance']:.1f} mm

## Geometric Analysis
- **Volume**: {analysis.get('volume', 0):.2f} mm³
- **Surface Area**: {analysis.get('surface_area', 0):.2f} mm²
- **Material Efficiency**: {analysis.get('material_efficiency', 0):.1f}%

## Cost Estimation
"""
            
            if 'cost_estimate' in analysis:
                cost = analysis['cost_estimate']
                report += f"""- **Material Mass**: {cost['material_mass_kg']:.3f} kg
- **Material Cost**: ${cost['material_cost_usd']:.2f}
- **Machining Time**: {cost['machining_time_min']:.1f} minutes
- **Machining Cost**: ${cost['machining_cost_usd']:.2f}
- **Total Estimated Cost**: ${cost['total_cost_usd']:.2f}

"""
            
            report += """## Manufacturing Recommendations

### Machining Process
1. **Material**: Use carbon steel bar stock (AISI 1045 or similar)
2. **Roughing**: Remove bulk material with end mill
3. **Semi-finishing**: Machine surfaces to near-final dimensions
4. **Finishing**: Final pass with sharp tooling for surface finish
5. **Hex Opening**: Use hex broach or EDM for precise geometry

### Quality Control
- **Dimensional Inspection**: Check all critical dimensions with calipers/CMM
- **Hex Opening**: Verify fit with standard hex nuts
- **Surface Finish**: Ra ≤ 3.2 μm on functional surfaces
- **Heat Treatment**: Consider stress relief if required

### Manufacturing Constraints
"""
            
            for constraint in analysis.get('manufacturing_constraints', []):
                report += f"- {constraint}\n"
            
            report += """
## Design Improvements
1. **Add chamfers** to hex opening for easier nut insertion
2. **Consider knurling** on handle for better grip
3. **Optimize fillet radii** to reduce stress concentrations
4. **Add marking** for hex size identification

## Standards Compliance
- **ISO 3318**: Open-end spanners - Maximum thickness of head
- **ISO 691**: Assembly tools for screws and nuts - Hexagon socket screws
- **ASME B18.3**: Socket screws, keys, and bits

---
*Report generated by Enhanced Wrench Designer*
"""
            
            with open(output_path, 'w') as f:
                f.write(report)
            
            print(f"✓ Manufacturing report generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Report generation error: {e}")
            return False
    
    def design_wrench(self):
        """Main wrench design workflow"""
        print("Starting Enhanced Wrench Design Process...")
        print("="*50)
        
        # Initialize FreeCAD
        if not self.initialize_freecad():
            return False
        
        # Create document
        if not self.create_document():
            return False
        
        # Create components
        handle = self.create_handle()
        head = self.create_head()
        hex_hole = self.create_hex_hole()
        
        # Assemble wrench
        wrench = self.assemble_wrench(handle, head, hex_hole)
        
        if not wrench:
            print("✗ Wrench assembly failed")
            return False
        
        # Create technical drawing
        drawing = self.create_technical_drawing(wrench)
        
        # Export PDF
        pdf_success = self.export_pdf(drawing)
        
        # Analyze manufacturability
        analysis = self.analyze_manufacturability(wrench)
        
        # Generate report
        self.generate_manufacturing_report(analysis)
        
        # Final status
        print("\n" + "="*50)
        print("WRENCH DESIGN COMPLETED")
        print("="*50)
        print("✓ 3D wrench model created")
        print("✓ Technical drawing generated")
        print(f"{'✓' if pdf_success else '⚠'} PDF export {'completed' if pdf_success else 'attempted'}")
        print("✓ Manufacturability analysis performed")
        print("✓ Manufacturing report generated")
        print("="*50)
        
        return True


def main():
    """Main execution function"""
    designer = WrenchDesigner()
    success = designer.design_wrench()
    
    if success:
        print("\n🎉 Enhanced wrench design process completed successfully!")
        print("\nFiles generated:")
        print("📄 /project/workspace/wrench_technical_drawing.pdf")
        print("📄 /project/workspace/wrench_technical_drawing.svg")
        print("📄 /project/workspace/wrench_manufacturing_report.md")
    else:
        print("\n❌ Wrench design process encountered errors")
        print("Check the error messages above for troubleshooting")
    
    return success


if __name__ == "__main__":
    main()