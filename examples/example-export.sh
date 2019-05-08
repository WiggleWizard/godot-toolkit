#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

godot-exporter \
    --godot-path="$DIR/../bin/Godot_Latest.exe" \
    --export-template-path="$DIR/../export_templates/win64.official.3.1.1-stable.exe" \
    --rcedit-path="$DIR/../bin/rcedit-x64.exe" \
    --project-path="$DIR/../project" \
    --plugin="$DIR/godot-export-plugin.py" \
    --out="../Exports/Project.pck" \
    "$@"