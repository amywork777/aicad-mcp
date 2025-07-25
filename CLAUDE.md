# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Diagram
```
                             +----------------+
                             |                |
                             |  Claude Agent  |
                             |                |
                             +-------+--------+
                                     |
                                     | MCP Protocol
                                     v
+------------------+          +------+---------+
|                  |          |                |
|     FreeCAD      +<-------->+  Taiyaki AI   |
|                  |  XML-RPC |   MCP Server  |
+------------------+          |                |
                              +-------+--------+
                                      |
                              +-------v--------+
                              |                |
                              | Knowledge Base |
                              |                |
                              +----------------+
```

## Build/Run Commands
- Install Just: `brew install just` (macOS) or see https://just.systems/man/en/chapter_5.html
- Run the server: `python mcp-server.py`
- Run with Taiyaki: `python run-taiyaki.py`
- Build package: `uv pip install -e .`
- Run tests: `python -m unittest discover`

## FreeCAD Integration
1. **Installation**:
   - Copy the addon files to FreeCAD Mod directory:
     ```bash
     # macOS
     cp -r addon/FreeCADMCP ~/Library/Application\ Support/FreeCAD/Mod/
     
     # Windows
     xcopy /E /I addon\FreeCADMCP "%APPDATA%\FreeCAD\Mod\FreeCADMCP"
     
     # Linux
     cp -r addon/FreeCADMCP ~/.local/share/FreeCAD/Mod/
     ```

2. **Installing Required Dependencies**:
   - Run the installer script: `python install_deps.py`
   - Or manually install dependencies to FreeCAD's Python:
     ```bash
     # Find FreeCAD's Python executable (in FreeCAD's Python console):
     import sys; print(sys.executable)
     
     # Install dependencies (replace path with your FreeCAD Python path)
     /Applications/FreeCAD.app/Contents/Resources/bin/python -m pip install httpx anthropic python-dotenv pandas tabulate
     ```
   
3. **Starting the Integration**:
   - Launch FreeCAD
   - Select the "Taiyaki AI" workbench from the workbench list
   - The RPC server starts automatically within FreeCAD
   - Start the MCP server with `python mcp-server.py`

4. **Using the Chat Interface**:
   - When the "Taiyaki AI" workbench is selected, a chat panel will appear on the right side
   - Enter commands or queries in the text field and press Send
   - You can use the "Add Image" button to include images in your prompts

5. **API Key Setup**:
   - Create a .env file in the FreeCAD Mod directory:
     ```bash
     echo "CLAUDE_API_KEY=your_api_key_here" > ~/Library/Application\ Support/FreeCAD/Mod/FreeCADMCP/.env
     ```

## Code Style Guidelines
- **Type Hints**: Use Python type hints for all functions and variables
- **Imports**: Standard library first, third-party next, relative imports last
- **Error Handling**: Use try/except blocks with specific error types
- **Logging**: Use the logging module with appropriate levels
- **Formatting**: Four-space indentation, descriptive variable names
- **Documentation**: Include detailed docstrings with parameters, returns, and examples
- **Function Naming**: Use snake_case for functions and variables
- **Class Naming**: Use PascalCase for class names
- **Constants**: Use UPPER_CASE for constants
- **Prompt Organization**: Keep domain knowledge in separate prompt files

## Ultrathinking Process
- Analyze full problem space before implementing
- Evaluate all edge cases for CAD operations
- Consider manufacturing implications of 3D designs
- Think through user workflows and use cases
- Explore multiple solution paths before choosing one
- Document design decisions and rationale