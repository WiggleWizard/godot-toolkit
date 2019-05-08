import os, json, shutils

from godot_toolkit_config import GodotToolkitConfig
from godot_sys_arch import GodotSystemArch


class GodotBinariesManifest():
	"""
	"""

	def __init__(self):
		self.__manifest = None

		self.godot_toolkit_config = GodotToolkitConfig()
		self.binaries_dir         = self.godot_toolkit_config.get_adjusted_path("godot_cli", "godot_binaries_path")
		self.manifest_path        = os.path.join(self.binaries_dir, "manifest.json")

		if not os.path.exists(self.binaries_dir):
			os.makedirs(self.binaries_dir)

		# Construct manifest file that holds references to each downloaded binary file
		if not os.path.exists(self.manifest_path):
			with open(self.manifest_path, 'w') as f:
				f.write("{}")

		self.load_manifest()

	def load_manifest(self):
		'''Loads the manifest file contents into structured memory.
		'''
		with open(self.manifest_path, 'r') as f:
			self.__manifest = json.load(f)

	def save_manifest(self):
		with open(self.manifest_path, 'w') as f:
			json.dump(self.__manifest, f, indent=4)

	def add_binary(self, version, release, sys_arch: GodotSystemArch, binary_path):
		'''Adds a binary to the manifest. Copies the binary into location defined by the config.
		'''
		new_binary_name = sys_arch.get_formatted_binary_name(version, release)
		binary_dest_path = os.path.join(self.binaries_dir, new_binary_name)

		# Move the binary to the right location
		if os.path.exists(binary_path):
			shutils.copyfile(binary_path, binary_dest_path)

		# If successfully moved then add it to the manifest
		if os.path.exists(binary_dest_path):
			if not 'versions' in self.__manifest:
				self.__manifest['versions'] = {}

			if not version in self.__manifest['versions']:
				self.__manifest['versions'][version] = {}

			if not release in self.__manifest['versions'][version]:
				self.__manifest['versions'][version][release] = {}

			if not sys_arch.name in self.__manifest['versions'][version][release]:
				self.__manifest['versions'][version][release][sys_arch.name] = {
					"added_timestamp": "",
					"bin": new_binary_name
				}

		self.save_manifest()

		return True

	def remove_binary(self, version, release, system_arch: GodotSystemArch):
		pass

	def get_binary_path(self, version, release, sys_arch: GodotSystemArch):
		self.__verify_sys_arch(system_arch)

		if version == "latest":
			raise Exception("Cannot request \"latest\" as version from manifest")

		binary_filename = None
		if 'versions' in self.__manifest \
			and version in self.__manifest['versions'] \
			and release in self.__manifest['versions'][version] \
			and system_arch.name in self.__manifest['versions'][version][release]:
			binary_filename = self.__manifest['versions'][version][release][system_arch.name]

		# Combine binary filename into a full path
		if binary_filename:
			binary_path = os.path.join(self.binaries_dir, binary_filename)
			if os.path.exists(binary_path) and os.path.isfile(binary_path):
				return binary_path

		return None

	def get_binary_info(self, version, release, system_arch: GodotSystemArch):
		'''Check if version exists in the manifest (aka if it's downloaded already).
		'''
		self.__verify_sys_arch(system_arch)

		if version == "latest":
			raise Exception("Cannot request \"latest\" as version from manifest")

		with open(self.manifest_path, 'r') as f:
			manifest_json = json.load(f)

			if 'versions' in manifest_json \
			   and version in manifest_json['versions'] \
			   and release in manifest_json['versions'][version] \
			   and system_arch.name in manifest_json['versions'][version][release]:
				return manifest_json['versions'][version][release][system_arch.name]

		return None

	def __verify_sys_arch(self, sys_arch):
		if not isinstance(sys_arch, GodotSystemArch):
			raise Exception("system_arch argument is not of type {} but instead of type {}".format(GodotSystemArch.__name__, sys_arch.__class__.__name__))