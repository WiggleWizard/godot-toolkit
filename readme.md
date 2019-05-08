# Godot Toolkit
A cross platform command line toolkit for interacting with Godot projects, managing Godot versions and enabling automation of certain aspects of Godot.

## Installation
Currently there's no cross platform way to install Godot Toolkit. There are plans to add scripts later in the project's lifecycle.

### Requirements
As said above, there's no OS requirement however you must be running **Python 3.7.x**. Python 3.5.x will likely be fine, but is currently untested with anything below 3.7.x.

### Linux
For installation on Linux machines just execute the following.
```
git clone git@github.com:WiggleWizard/godot-toolkit.git /opt/godot-toolkit
ln -s /opt/godot-toolkit/bin/* /usr/local/bin/
pip install bs4 requests
```
This will install Godot Toolkit to the `/opt/godot-toolkit` directory and symlink the binaries to the required places in order for the toolkit to be runnable from command line.

### Windows
Installation on Windows systems is a little more tricky. You will have to add the `bin` directory to the `$PATH` environment variables.

## Usage
### Manager
Godot Toolkit allows you to have multiple versions of Godot installed at once. It will show you which versions are available and download the ones you require. Even nightly builds are accessible through the toolkit.

You can download a specific version of Godot using `godot-cli --download version [release] [system_arch]`. As an example the following command line entry will download v3.1 rc3 for Linux: `godot-cli --download 3.1 rc3 linux`.

If no release is specified then `stable` will be downloaded and if no system is specified then Godot Toolkit will download the appropriate Godot version for your system.

### Exporter
Godot Toolkit comes with a fully command line driven exporter: `godot-exporter`. This is handy for fully automating exports of your Godot applications/games.

For all switch descriptions simply type `godot-exporter --help`:
```
usage: godot-exporter [-h] [-v] [--pack-only] --export-template-path
                      EXPORT_TEMPLATE_PATH [--rcedit-path RCEDIT_PATH]
                      --project-path PROJECT_PATH --preset PRESET --out OUT
                      --plugin PLUGIN
                      (--godot-path GODOT_PATH | --godot-version GODOT_VERSION)

godot-exporter is a command line Godot exporter for advanced Godot users.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --pack-only           Only export the pack file which can be .pck/.zip
                        (defaults to off)
  --export-template-path EXPORT_TEMPLATE_PATH
                        Path to the Godot export template
  --rcedit-path RCEDIT_PATH
                        (Windows only) Path to the rcedit binary
  --project-path PROJECT_PATH
                        Directory in which the Godot project sits
  --preset PRESET       Which preset to use when exporting
  --out OUT             Output directory for the final game/application
  --plugin PLUGIN       Plugin path
  --godot-path GODOT_PATH
                        Path of the Godot binary that will be doing the
                        exporting
  --godot-version GODOT_VERSION
                        Which Godot version to use. This will be downloaded if
                        not already done so.
```

For example scripts check the examples directory. For Linux there's `examples/example-export.sh` and for Windows there's `examples/example.export.bat`. These scripts will help you get up and running with exporting a Godot project from the command line.

#### Plugin accessiblity
The exporter has a very simple plugin interface which hooks into various parts of the export process. An example plugin can be found in the examples directory: `examples/example-plugin.py`.