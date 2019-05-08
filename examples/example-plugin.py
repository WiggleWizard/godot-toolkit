import os
import json
import datetime
import time


class ExportPlugin():
	def __init__(self):
		self.windows_bin_properties = {
			"CompanyName":     "My Company",
			"FileDescription": "Description of file",
			"LegalCopyright":  "[REDACTED]",
			"ProductName":     "godot-cli-exporter",
		}

	def on_load(self):
		print("[+] Loaded export plugin")

	def pre_export(self, godot_exporter):
		print("[+] Modifying build time")

		version_file_path = os.path.join(godot_exporter.project_path, "version.json")

		versions = None
		with open(version_file_path, 'r') as f:
			versions = json.load(f)
			versions['build_time'] = datetime.datetime.utcnow().isoformat()
			versions['build_epoch'] = int(time.time())
		with open(version_file_path, 'w') as f:
			json.dump(versions, f, indent=4)

	def modify_export_config(self, godot_exporter, section, export_config):
		export_config.set(section, "include_filter", r'"version.json"')

	def post_export(self, godot_exporter):
		if len(godot_exporter.processed_files) > 0:
			# Ensure that version.json is included in the export
			if "res://version.json" not in godot_exporter.processed_files:
				print("[-] Version file was not included in the export!")

			# Now increase the build number
			version_file_path = os.path.join(godot_exporter.project_path, "version.json")

			versions = None
			with open(version_file_path, 'r') as f:
				versions = json.load(f)
				print("[+] Increasing build number [" + str(versions['build']) + " -> " + str(versions['build'] + 1) + "]")
				versions['build'] += 1
			with open(version_file_path, 'w') as f:
				json.dump(versions, f, indent=4)