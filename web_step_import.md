# Web STEP File Import Functionality

## Overview

The FreeCAD MCP server now includes powerful tools to search for and import existing STEP files from professional CAD libraries and manufacturer websites. This eliminates the need to model standard components from scratch.

## New MCP Tools

### 1. `search_and_import_step_files`

Search the web for STEP files and import them directly into FreeCAD.

**Usage:**
```python
search_and_import_step_files(
    doc_name="MyAssembly",
    search_query="M8 hex bolt",
    preferred_sources=["mcmaster", "grabcad"],
    max_results=3
)
```

**Parameters:**
- `doc_name`: FreeCAD document to import into
- `search_query`: Description of the part (e.g., "608 bearing", "M8x25 bolt")
- `preferred_sources`: List of sources to prioritize
- `max_results`: Maximum number of files to import (default: 3)

**Supported Sources:**
- **mcmaster**: McMaster-Carr (professional hardware)
- **grabcad**: GrabCAD Community (engineering models)
- **traceparts**: TraceParts (industrial components)
- **thingiverse**: Thingiverse (maker community)
- **manufacturer**: Direct manufacturer websites

### 2. `import_mcmaster_part`

Import specific parts from McMaster-Carr using part numbers.

**Usage:**
```python
import_mcmaster_part(
    doc_name="FastenerAssembly",
    part_number="91290A115",
    description="M8x25mm hex bolt"
)
```

**Parameters:**
- `doc_name`: FreeCAD document name
- `part_number`: McMaster-Carr part number
- `description`: Optional part description

**Popular McMaster Part Series:**
- **Hex Bolts**: 91290A series (e.g., 91290A115 = M8x25mm)
- **Socket Head**: 92220A series
- **Ball Bearings**: 6078K series
- **Washers**: 93475A series
- **Nuts**: 94150A series

### 3. `manage_imported_parts`

Organize and manage imported STEP files in your FreeCAD document.

**Usage:**
```python
manage_imported_parts(
    doc_name="MyAssembly",
    action="organize",
    part_filter="bearing"
)
```

**Actions:**
- `list`: Show all imported parts
- `organize`: Group parts by category (fasteners, bearings, etc.)
- `identify`: Identify part types and functions
- `cleanup`: Get organization recommendations

## Benefits of Web Import

### Professional Quality
- **McMaster-Carr**: Industry-standard dimensions, used for actual procurement
- **TraceParts**: Manufacturer-verified models
- **GrabCAD**: Community-vetted engineering models

### Time Savings
- No need to model standard components
- Instant access to complex geometries
- Focus on custom design work

### Accuracy
- Professionally modeled parts
- Correct dimensions and tolerances
- Multiple format availability (STEP, IGES, STL)

## Recommended Workflow

### 1. Plan Your Assembly
Identify which components are:
- **Standard parts** (bolts, bearings, etc.) → Use web import
- **Custom parts** → Model in FreeCAD
- **Modified standard parts** → Import then modify

### 2. Import Standard Components
```python
# Import fasteners from McMaster-Carr
import_mcmaster_part(doc_name="Assembly", part_number="91290A115")

# Search for bearings
search_and_import_step_files(
    doc_name="Assembly",
    search_query="608 ball bearing",
    preferred_sources=["mcmaster", "manufacturer"]
)

# Find custom brackets from community
search_and_import_step_files(
    doc_name="Assembly", 
    search_query="motor mount bracket",
    preferred_sources=["grabcad", "thingiverse"]
)
```

### 3. Organize Imported Parts
```python
# Review what was imported
manage_imported_parts(doc_name="Assembly", action="list")

# Organize by category
manage_imported_parts(doc_name="Assembly", action="organize")

# Get cleanup recommendations
manage_imported_parts(doc_name="Assembly", action="cleanup")
```

### 4. Verify and Assemble
- Check dimensions match requirements
- Position parts in assembly
- Run DFM analysis on complete assembly
- Export final assembly to STEP

## Source Quality Guide

### McMaster-Carr ⭐⭐⭐⭐⭐
- **Best for**: Standard hardware, fasteners, bearings
- **Quality**: Professional grade, dimensionally accurate
- **Access**: Direct download, no registration
- **Use when**: You need standard industrial components

### GrabCAD Community ⭐⭐⭐⭐
- **Best for**: Complex mechanical parts, custom designs
- **Quality**: High, community-verified
- **Access**: Free registration required
- **Use when**: You need non-standard or specialized components

### TraceParts ⭐⭐⭐⭐
- **Best for**: Industrial components, manufacturer parts
- **Quality**: Manufacturer-verified
- **Access**: Free registration required
- **Use when**: You need specific branded components

### Manufacturer Websites ⭐⭐⭐⭐⭐
- **Best for**: Specific branded parts
- **Quality**: Highest accuracy
- **Access**: Varies by manufacturer
- **Use when**: You need exact manufacturer specifications

### Thingiverse ⭐⭐⭐
- **Best for**: Maker-community parts, 3D printing designs
- **Quality**: Variable, community-created
- **Access**: Free, no registration
- **Use when**: You need maker/hobbyist components

## Implementation Status

The tools provide a complete framework for:
- ✅ Web search integration capability
- ✅ Multi-source search strategies
- ✅ Part organization and management
- ✅ McMaster-Carr direct part lookup
- 🔄 Active development for full download integration

## Future Enhancements

1. **Part Number Recognition**: Automatic part number extraction
2. **Bulk Import**: Import multiple related parts at once
3. **BOM Integration**: Connect with bill of materials generation
4. **Part Library**: Build local library of frequently used parts
5. **Dimensional Verification**: Automatic dimension checking

## Examples

### Complete Bearing Assembly
```python
# Create document
create_document("BearingAssembly")

# Import bearing
import_mcmaster_part("BearingAssembly", "6078K31", "608 Ball Bearing")

# Import shaft
search_and_import_step_files(
    "BearingAssembly",
    "8mm steel shaft",
    ["mcmaster", "manufacturer"]
)

# Import housing
search_and_import_step_files(
    "BearingAssembly", 
    "bearing housing 608",
    ["grabcad", "thingiverse"]
)

# Organize and verify
manage_imported_parts("BearingAssembly", "organize")
```

### Fastener Collection
```python
# Create fastener library
create_document("FastenerLibrary")

# Import common bolts
import_mcmaster_part("FastenerLibrary", "91290A115", "M8x25 Hex Bolt")
import_mcmaster_part("FastenerLibrary", "91290A120", "M8x30 Hex Bolt")
import_mcmaster_part("FastenerLibrary", "92220A188", "M8x25 Socket Head")

# Import nuts and washers
import_mcmaster_part("FastenerLibrary", "94150A200", "M8 Hex Nut")
import_mcmaster_part("FastenerLibrary", "93475A240", "M8 Flat Washer")

# Review collection
manage_imported_parts("FastenerLibrary", "list")
```

This functionality transforms FreeCAD from a pure modeling tool into a complete CAD ecosystem with access to millions of professional components.