# -*- coding: utf-8 -*-

"""Godot Exporter class and CLI application.
"""

import sys, os, platform, subprocess, re, time
from godot_config_file import GodotConfigFile


class GodotExporter:
	version = "0.1"

	def __init__(self, plugin_path=None, godot_bin_path=None, godot_version_string=None, export_template_bin_path=None, rcedit_bin_path=None,
	             project_path=None, preset=None, pack_only=False, export_dest=None):
		self.godot_bin_path           = godot_bin_path
		self.export_template_bin_path = export_template_bin_path
		self.rcedit_bin_path          = rcedit_bin_path

		self.project_path = project_path
		self.preset       = preset
		self.pack_only    = pack_only
		self.export_dest  = export_dest

		self.processed_files = []
		self.godot_errors    = []

		self._original_export_presets = None

		self.plugin = None
		if plugin_path:
			print("[+] Attempting to load exporter plugin from " + plugin_path)
			if plugin_path and os.path.isfile(plugin_path):
				import imp
				exporter_plugin_module = imp.load_source('ExporterPlugin', plugin_path)
				if hasattr(exporter_plugin_module, "ExporterPlugin"):
					print("[+] Successfully loaded exporter plugin")
					self.plugin = exporter_plugin_module.ExporterPlugin()
				else:
					print("[-] Could not load exporter plugin. Module has no ExporterClass defined.")

				if self.plugin and hasattr(self.plugin, "on_load"):
					self.plugin.on_load()

	def validate(self):
		if platform.system() == "Windows":
			if not os.path.isfile(self.rcedit_bin_path):
				print("[-] Invalid rcedit path " + self.rcedit_bin_path)
				return False

		if not os.path.isfile(self.godot_bin_path):
			print("[-] Invalid Godot bin path " + self.godot_bin_path)
			return False

		if not os.path.isdir(self.project_path):
			print("[-] Could not find project path " + self.project_path)
			return False

		if not os.path.isfile(self.export_template_bin_path):
			print("[-] Invalid export template bin path " + self.export_template_bin_path)
			return False

		return True

	def prep_export_preset(self):
		export_preset_file_path = os.path.join(self.project_path, "export_presets.cfg")

		# Check if the export presets file even exists, if not then prompt user
		if not os.path.isfile(export_preset_file_path):
			print("[-] Could not find export_presets.cfg")
			return None

		# Take a copy of the file into memory since any modifications we make
		# should be temporary.
		with open(export_preset_file_path, 'r') as f:
			self._original_export_presets = f.read()
		
		config = GodotConfigFile()
		config.read(export_preset_file_path)

		# Check to see if the preset exists
		preset_section = None
		preset_options_section = None
		for section in config.sections():
			if not section.endswith(".options"):
				if config.get(section, "name").strip(r'"') == self.preset:
					preset_section = section
					preset_options_section = preset_section + ".options"

		if preset_section == None:
			print("[-] Could not find preset " + self.preset + " in export_presets.cfg")
			return preset_section

		# Set runnable to false if pack only is set to true
		if self.pack_only == True:
			config.set(preset_section, "runnable", "false")
		else:
			config.set(preset_section, "runnable", "true")
			config.set(preset_options_section, "custom_template/release", "\"" + os.path.realpath(self.export_template_bin_path) + "\"")

		# Allow the plugin the opportunity to modify the export config directly
		if self.plugin and hasattr(self.plugin, "modify_export_config"):
			self.plugin.modify_export_config(self, preset_section, config)

		with open(export_preset_file_path, 'w') as configfile:
			config.write(configfile)

		return preset_section

	def restore_export_presets(self):
		export_preset_file_path = os.path.join(self.project_path, "export_presets.cfg")

		if self._original_export_presets:
			with open(export_preset_file_path, 'w') as f:
				f.seek(0)
				f.write(self._original_export_presets)

	def export(self):
		# Inform the plugin that we are about to build, this will give
		# the plugin an opportunity to modify values.
		if self.plugin and hasattr(self.plugin, "pre_export"):
			self.plugin.pre_export(self)

		section_name = self.prep_export_preset()
		if section_name == None:
			return False

		godot_bin   = os.path.realpath(self.godot_bin_path)
		working_dir = os.path.realpath(self.project_path)
		dest        = os.path.realpath(self.export_dest)

		print("[+] Packing assets using Godot")

		# Run up Godot
		process = subprocess.Popen([godot_bin, "--export", self.preset, dest], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=working_dir)
		while process.poll() is None:
			for line in process.stdout:
				line = line.decode('utf-8')

				# Parse out packed files
				matches = re.finditer(r'savepack: step \d+: Storing File: (.+)\r', line, re.MULTILINE)
				for matchNum, match in enumerate(matches, start=1):
					self.processed_files.append(match.group(1))

				# Catch errors
				err_matches = re.finditer(r'ERROR: (.+)\r', line, re.MULTILINE)
				for matchNum, match in enumerate(err_matches, start=1):
					self.godot_errors.append(match.group(1))

			time.sleep(1)

		print("[+] Packed files: " + str(len(self.processed_files)))

		# Print out errors
		print("[!] Godot errors: " + str(len(self.godot_errors)))
		l = len(self.godot_errors)
		for i in range(l):
			if i >= l - 1:
				print(" └── " + self.godot_errors[i])
			else:
				print(" ├── " + self.godot_errors[i])


		# Give the plugin a chance to do something post export
		if self.plugin and hasattr(self.plugin, "post_export"):
			self.plugin.post_export(self)

		self.restore_export_presets()

		return True

	def gen_base_export_preset(self):
		pass


if __name__ == '__main__':
	class Error(Exception):
		pass

	def dir_path(string):
		if os.path.isdir(string):
			return string
		else:
			print(string + " is not a valid/existing directory")
			exit()

	def file_path(string):
		if os.path.isfile(string):
			return string
		else:
			print(string + " is not a valid/existing file")
			exit()

	import argparse
	parser = argparse.ArgumentParser(prog='godot-exporter', description='godot-exporter is a command line Godot exporter for advanced Godot users.')
	parser.add_argument('-v', '--version',        action='version',              version='%(prog)s version ' + GodotExporter.version)
	parser.add_argument('--pack-only',            action='store_true',           help='Only export the pack file which can be .pck/.zip (defaults to off)')
	parser.add_argument('--export-template-path', required=True, type=file_path, help='Path to the Godot export template')
	parser.add_argument('--rcedit-path',                         type=file_path, help='(Windows only) Path to the rcedit binary')
	parser.add_argument('--project-path',         required=True, type=dir_path,  help='Directory in which the Godot project sits')
	parser.add_argument('--preset',               required=True, type=str,       help='Which preset to use when exporting')
	parser.add_argument('--out',                  required=True, type=str,       help='Output directory for the final game/application')
	parser.add_argument('--plugin',               required=True, type=str,       help='Plugin path')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--godot-path', type=file_path,    help='Path of the Godot binary that will be doing the exporting')
	group.add_argument('--godot-version', type=file_path, help='Which Godot version to use. This will be downloaded if not already done so.')
	args = parser.parse_args()

	godot_exporter = GodotExporter(
		plugin_path              = args.plugin,
		godot_bin_path           = args.godot_path,
		godot_version_string     = args.godot_version,
		export_template_bin_path = args.export_template_path,
		rcedit_bin_path          = args.rcedit_path,
		project_path             = args.project_path,
		preset                   = args.preset,
		pack_only                = args.pack_only,
		export_dest              = args.out)

	# Validate command line arguments
	if not godot_exporter.validate():
		exit()

	# Commit to export
	godot_exporter.export()