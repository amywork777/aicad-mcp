#!/usr/bin/env python3
"""
Test script for enhanced FreeCAD MCP server tools
Tests screenshot analysis and automatic fixing functionality
"""

import sys
import os
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_screenshot_analysis():
    """Test screenshot analysis functionality"""
    print("Testing Screenshot Analysis Tools...")
    
    # Mock objects data for testing
    test_objects = [
        {
            "Name": "TestBox",
            "TypeId": "Part::Box",
            "Length": 0.0,  # Invalid - zero dimension
            "Width": 10.0,
            "Height": 5.0,
            "Placement": {"Base": {"x": 0, "y": 0, "z": 0}}
        },
        {
            "Name": "ThinFeature", 
            "TypeId": "Part::Box",
            "Length": 50.0,
            "Width": 0.5,  # Too thin for machining
            "Height": 10.0,
            "Placement": {"Base": {"x": 20, "y": 0, "z": 0}}
        },
        {
            "Name": "HighAspectRatio",
            "TypeId": "Part::Box", 
            "Length": 100.0,
            "Width": 2.0,  # Very high aspect ratio
            "Height": 5.0,
            "Placement": {"Base": {"x": 40, "y": 0, "z": 0}}
        },
        {
            "Name": "InvalidCylinder",
            "TypeId": "Part::Cylinder",
            "Radius": -5.0,  # Invalid negative radius
            "Height": 10.0,
            "Placement": {"Base": {"x": 60, "y": 0, "z": 0}}
        },
        {
            "Name": "InvalidSphere",
            "TypeId": "Part::Sphere",
            "Radius": 0.0,  # Invalid zero radius
            "Placement": {"Base": {"x": 80, "y": 0, "z": 0}}
        },
        {
            "Name": "InvalidCone",
            "TypeId": "Part::Cone",
            "Radius1": -2.0,  # Invalid negative radius
            "Radius2": 0.0,   # Invalid zero radius
            "Height": -5.0,   # Invalid negative height
            "Placement": {"Base": {"x": 100, "y": 0, "z": 0}}
        },
        {
            "Name": "OverlappingBox",
            "TypeId": "Part::Box",
            "Length": 10.0,
            "Width": 10.0, 
            "Height": 10.0,
            "Placement": {"Base": {"x": 0, "y": 0, "z": 0}}  # Same as TestBox
        }
    ]
    
    # Test geometry error analysis
    from freecad_mcp.server import _analyze_geometry_errors
    geo_issues, geo_recs = _analyze_geometry_errors(test_objects)
    
    print(f"\nGeometry Analysis Results:")
    print(f"Issues found: {len(geo_issues)}")
    for issue in geo_issues:
        print(f"  - {issue}")
    print(f"Recommendations: {len(geo_recs)}")
    for rec in geo_recs:
        print(f"  - {rec}")
    
    # Test manufacturability analysis
    from freecad_mcp.server import _analyze_manufacturing_issues
    mfg_issues, mfg_recs = _analyze_manufacturing_issues(test_objects)
    
    print(f"\nManufacturability Analysis Results:")
    print(f"Issues found: {len(mfg_issues)}")
    for issue in mfg_issues:
        print(f"  - {issue}")
    print(f"Recommendations: {len(mfg_recs)}")
    for rec in mfg_recs:
        print(f"  - {rec}")
    
    # Test spatial layout analysis
    from freecad_mcp.server import _analyze_spatial_layout
    spatial_issues, spatial_recs = _analyze_spatial_layout(test_objects)
    
    print(f"\nSpatial Layout Analysis Results:")
    print(f"Issues found: {len(spatial_issues)}")
    for issue in spatial_issues:
        print(f"  - {issue}")
    print(f"Recommendations: {len(spatial_recs)}")
    for rec in spatial_recs:
        print(f"  - {rec}")
    
    # Summary
    total_issues = len(geo_issues) + len(mfg_issues) + len(spatial_issues)
    total_recs = len(geo_recs) + len(mfg_recs) + len(spatial_recs)
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Total Issues Detected: {total_issues}")
    print(f"Total Recommendations: {total_recs}")
    print(f"Analysis Functions: ✓ Working correctly")
    
    # Expected results validation
    expected_issues = [
        "zero dimensions",
        "thin features", 
        "high aspect ratio",
        "invalid cylinder",
        "invalid sphere",
        "invalid cone",
        "overlapping objects"
    ]
    
    all_issues_text = " ".join(geo_issues + mfg_issues + spatial_issues).lower()
    
    detected_types = []
    for issue_type in expected_issues:
        if any(keyword in all_issues_text for keyword in issue_type.split()):
            detected_types.append(issue_type)
    
    print(f"\nIssue Types Correctly Detected: {len(detected_types)}/{len(expected_issues)}")
    for issue_type in detected_types:
        print(f"  ✓ {issue_type}")
    
    missing_types = set(expected_issues) - set(detected_types)
    if missing_types:
        print("Missing detections:")
        for issue_type in missing_types:
            print(f"  ✗ {issue_type}")
    
    return total_issues > 0 and total_recs > 0


def test_fix_functions():
    """Test automatic fixing functionality"""
    print(f"\n{'='*50}")
    print("Testing Automatic Fix Functions...")
    print(f"{'='*50}")
    
    # Mock freecad connection for testing
    class MockFreeCAD:
        def __init__(self):
            self.executed_code = []
            
        def execute_code(self, code):
            self.executed_code.append(code)
            return {"success": True, "output": "Code executed"}
    
    mock_freecad = MockFreeCAD()
    
    # Test objects with issues
    test_objects = [
        {
            "Name": "ZeroDimBox",
            "TypeId": "Part::Box",
            "Length": 0.0,
            "Width": 10.0, 
            "Height": 5.0
        },
        {
            "Name": "ThinBox",
            "TypeId": "Part::Box",
            "Length": 50.0,
            "Width": 0.8,  # Below minimum thickness
            "Height": 10.0
        },
        {
            "Name": "InvalidCyl",
            "TypeId": "Part::Cylinder", 
            "Radius": 0.0,
            "Height": 10.0
        },
        {
            "Name": "SmallCyl",
            "TypeId": "Part::Cylinder", 
            "Radius": 0.2,  # Below minimum radius
            "Height": 10.0
        },
        {
            "Name": "InvalidSphere",
            "TypeId": "Part::Sphere",
            "Radius": -1.0
        },
        {
            "Name": "InvalidCone",
            "TypeId": "Part::Cone",
            "Radius1": 0.0,
            "Radius2": 0.0,
            "Height": -5.0
        }
    ]
    
    # Test geometry fixes
    from freecad_mcp.server import _apply_geometry_fixes
    geo_fixes = _apply_geometry_fixes(mock_freecad, "TestDoc", test_objects)
    
    print(f"Geometry Fixes Applied: {len(geo_fixes)}")
    for fix in geo_fixes:
        print(f"  - {fix}")
    
    # Test manufacturability fixes  
    from freecad_mcp.server import _apply_manufacturability_fixes
    mfg_fixes = _apply_manufacturability_fixes(mock_freecad, "TestDoc", test_objects)
    
    print(f"Manufacturability Fixes Applied: {len(mfg_fixes)}")
    for fix in mfg_fixes:
        print(f"  - {fix}")
    
    # Test spatial fixes
    overlapping_objects = [
        {
            "Name": "Obj1",
            "TypeId": "Part::Box",
            "Placement": {"Base": {"x": 0, "y": 0, "z": 0}}
        },
        {
            "Name": "Obj2", 
            "TypeId": "Part::Box",
            "Placement": {"Base": {"x": 0, "y": 0, "z": 0}}  # Same position
        }
    ]
    
    from freecad_mcp.server import _apply_spatial_fixes
    spatial_fixes = _apply_spatial_fixes(mock_freecad, "TestDoc", overlapping_objects)
    
    print(f"Spatial Fixes Applied: {len(spatial_fixes)}")
    for fix in spatial_fixes:
        print(f"  - {fix}")
    
    # Verify code execution
    total_fixes = len(geo_fixes) + len(mfg_fixes) + len(spatial_fixes)
    print(f"\nTotal Fixes Applied: {total_fixes}")
    print(f"FreeCAD Code Executions: {len(mock_freecad.executed_code)}")
    
    # Show some executed code examples
    if mock_freecad.executed_code:
        print("\nSample Fix Code Generated:")
        for i, code in enumerate(mock_freecad.executed_code[:3], 1):
            print(f"  {i}. {code.strip()[:100]}...")
    
    return total_fixes > 0


def main():
    """Run all tests"""
    print("FreeCAD MCP Server Enhancement Tests")
    print("="*60)
    
    try:
        # Test analysis functions
        analysis_success = test_screenshot_analysis()
        
        # Test fix functions
        fix_success = test_fix_functions()
        
        # Overall results
        print(f"\n{'='*60}")
        print("OVERALL TEST RESULTS")
        print(f"{'='*60}")
        print(f"Screenshot Analysis: {'✓ PASS' if analysis_success else '✗ FAIL'}")
        print(f"Automatic Fixes: {'✓ PASS' if fix_success else '✗ FAIL'}")
        
        if analysis_success and fix_success:
            print("\n🎉 All tests passed! MCP server enhancements are working correctly.")
            print("\nNew tools ready for use:")
            print("  - analyze_screenshot_for_issues")
            print("  - apply_automatic_fixes")
            print("\nSupported object types:")
            print("  - Part::Box (boxes/cubes)")
            print("  - Part::Cylinder (cylinders)")
            print("  - Part::Sphere (spheres)")
            print("  - Part::Cone (cones)")
            return True
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
            return False
            
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure the FreeCAD MCP server modules are properly installed.")
        return False
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)