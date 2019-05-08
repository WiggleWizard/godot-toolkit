import platform
from enum import Enum

class UnknownSysArch(Exception):
	pass


class GodotSystemArch(Enum):
	OS_UNKNOWN = 0
	OS_LINUX32 = 1
	OS_LINUX64 = 2
	OS_WIN32   = 3
	OS_WIN64   = 4
	OS_OSX64   = 5

	OS_LINUX_HEADLESS_64 = 6
	OS_LINUX_SERVER_64   = 7

	OS_AUTO = 99

	def to_file_suffix(self):
		file_suffix_map = GodotSystemArch.get_file_suffix_map()
		for k in file_suffix_map:
			if self == file_suffix_map[k]:
				return k

		return "unknown"
		
	def get_formatted_binary_name(self, version, release):
		file_suffix_map_reverse = GodotSystemArch.get_file_suffix_map_reverse()
		file_suffix = file_suffix_map_reverse[self]

		return "Godot_v{}-{}_{}".format(version, release, file_suffix)

	@classmethod
	def get_file_suffix_map(cls):
		return {
			"win32.exe"        : cls.OS_WIN32,
			"win64.exe"        : cls.OS_WIN64,
			"x11.32"           : cls.OS_LINUX32,
			"x11.64"           : cls.OS_LINUX64,
			"linux_headless.64": cls.OS_LINUX_HEADLESS_64,
			"linux_server.64"  : cls.OS_LINUX_SERVER_64,
			"osx.64"           : cls.OS_OSX64,
		}

	@classmethod
	def get_file_suffix_map_reverse(cls):
		file_suffix_map = cls.get_file_suffix_map()

		d = {}
		for k in file_suffix_map:
			d[file_suffix_map[k]] = k

		return d

	@classmethod
	def get_os_string_map(cls):
		return {
			"linux"    : cls.OS_LINUX64,
			"linux64"  : cls.OS_LINUX64,
			"linux32"  : cls.OS_LINUX32,
			"windows"  : cls.OS_WIN64,
			"windows64": cls.OS_WIN64,
			"win64"    : cls.OS_WIN64,
			"windows32": cls.OS_WIN32,
			"win32"    : cls.OS_WIN32,
			"osx"      : cls.OS_OSX64,
		}

	@classmethod
	def from_file_suffix(cls, file_suffix):
		file_suffix_map = cls.get_file_suffix_map()
		for k in file_suffix_map:
			if file_suffix == k:
				return file_suffix_map[k]

		return cls.OS_UNKNOWN

	@classmethod
	def from_os_string(cls, os_string):
		if os_string == None:
			return cls.from_current_os()
			
		os_string = os_string.lower()
		os_string_map = cls.get_os_string_map()
		
		for k in os_string_map:
			if os_string == k:
				return os_string_map[k]
		
		raise UnknownSysArch()

	@classmethod
	def from_current_os(cls):
		operating_system = platform.system()
		is_64bit = platform.machine().endswith('64')

		if operating_system == "Linux":
			return cls.OS_LINUX64 if is_64bit else cls.OS_LINUX32
		elif operating_system == "Windows":
			return cls.OS_WIN64 if is_64bit else cls.OS_WIN32
		elif operating_system == "Darwin":
			return cls.OS_OSX64