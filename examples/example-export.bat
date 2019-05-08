@echo off
setlocal

godot-exporter ^
    --export-template-path="%~dp0../export_templates/win64.official.3.1.1-stable.exe" ^
    --godot-path="%~dp0../bin/Godot_Latest.exe" ^
    --rcedit-path="%~dp0../bin/rcedit-x64.exe" ^
    --project-path="%~dp0../project" ^
    --plugin="%~dp0godot-export-plugin.py" ^
    --out="../Exports/Project.pck" ^
    %*