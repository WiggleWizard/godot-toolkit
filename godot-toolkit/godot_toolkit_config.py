
try:
	import ConfigParser as configparser
except:
	import configparser
import os


class GodotToolkitConfig():
	__config = {
		"godot_cli": {
			"godot_binaries_path"       : "data/godot_bin",
			"download_tmp"              : "data/tmp",
			"godot_catalogue_cache_path": "data/cache.json",
			"default_launch_version"    : "3.1.1",
			"base_dl_url"               : "https://downloads.tuxfamily.org/godotengine"
		},
		"godot_nightly":
		{
			"manifest_url": "https://archive.hugo.pro/builds/godot/editor/godot-linux-nightly-x86_64.AppImage.manifest.json",
			"dl_url_linux": "https://archive.hugo.pro/builds/godot/editor/godot-linux-nightly-x86_64.AppImage",
			"dl_url_win64": "https://archive.hugo.pro/builds/godot/editor/godot-windows-nightly-x86_64.zip",
			"dl_url_win32": "https://archive.hugo.pro/builds/godot/editor/godot-windows-nightly-x86.zip",
			"dl_url_osx":   "https://archive.hugo.pro/builds/godot/editor/godot-macos-nightly-x86_64.dmg",
		}
	}

	def __init__(self):
		script_dir = os.path.dirname(os.path.realpath(__file__))
		config_path = os.path.realpath(os.path.join(script_dir, "..", "godot-toolkit.cfg"))

		flat_config = {}
		for section in self.__config:
			for key in self.__config[section]:
				flat_config[key] = self.__config[section][key]

		# Now overwrite the class variables with the ones found
		# in the config.
		__config = configparser.ConfigParser(flat_config)
		__config.read(config_path)

	def get(self, section, key):
		if section in self.__config:
			if key in self.__config[section]:
				return self.__config[section][key]

		return None

	def get_adjusted_path(self, section, key):
		if section in self.__config:
			if key in self.__config[section]:
				path = self.__config[section][key]

				if os.path.isabs(path):
					return os.path.realpath(path)
				
				script_path = os.path.dirname(__file__)
				return os.path.realpath(os.path.join(script_path, "..", path))

		return None