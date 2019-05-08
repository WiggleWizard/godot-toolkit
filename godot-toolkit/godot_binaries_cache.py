import re, os, json, datetime, urllib

from godot_toolkit_config import GodotToolkitConfig
from godot_sys_arch import GodotSystemArch

try:
	from bs4 import BeautifulSoup
except:
	print("[-] bs4 Python module needs to be installed. Install it with `pip install bs4`")
	exit()

class VersionOrReleaseError(Exception):
	pass


class GodotBinariesCache():
	def __init__(self, suppress_recache=False):
		self.__cache = None

		self.time_format          = "%Y-%m-%d %H:%MZ"
		self.godot_toolkit_config = GodotToolkitConfig()

		self.cache_path = self.godot_toolkit_config.get_adjusted_path("godot_cli", "godot_catalogue_cache_path")

		# Construct cache file if it doesn't exist
		if not os.path.exists(self.cache_path):
			with open(self.cache_path, 'w') as f:	
				f.write("{}")
		
		with open(self.cache_path, 'r') as f:
			self.__cache = json.load(f)

		# Check the last time the catalog was written to, if it's been a day then
		# rewrite with latest Godot releases versions.
		recache_catalogue = False
		if self.__cache != None:
			if "last_cache_datetime" in self.__cache:
				last_catalogue_time = datetime.datetime.strptime(self.__cache["last_cache_datetime"], self.time_format)
				if (datetime.datetime.utcnow() - last_catalogue_time) > datetime.timedelta(days=1):
					recache_catalogue = True
			else:
				recache_catalogue = True

		if recache_catalogue == True:
			print("[+] Outdated cache, rebuilding")
			self.recache()

	def get_cache(self):
		return self.__cache

	def recache(self):
		print("[+] Building cache")
		self.__cache = { "versions": {} }

		# Fetch all the versions available and insert them into the cache
		self.__cache['versions'] = self.scrape_versions()
		for version in self.__cache['versions']:
			self.__cache['versions'][version]['releases'] = {}

			releases = self.scrape_version_releases(version)
			for release in releases:
				self.__cache['versions'][version]['releases'][release] = releases[release]

		now = datetime.datetime.utcnow()
		self.__cache['last_cache_datetime'] = now.strftime(self.time_format)

		self.cache_nightly_manifest()

		self.save_changes_to_cache()
		
	def save_changes_to_cache(self):
		with open(self.cache_path, 'w') as f:
			json.dump(self.__cache, f, indent=4)

	def construct_download_url(self, version, release="stable", sys_arch=GodotSystemArch.from_current_os()):
		# If nightly is specified we need to do some specific stuff
		if version == "nightly":
			os_suffix = sys_arch.to_file_suffix()
			full_url = self.__cache['versions']['nightly']['downloads'][os_suffix]
			
			file_ext = full_url.split("/")[-1].split(".")[-1]
			file_name = "Godot-nightly-%s_%s.%s" % (self.__cache['versions']['nightly']['commit'][:7], os_suffix, file_ext)

			return full_url, file_name

		# Figure out what the latest version is in the cache
		if version == "latest":
			versions = list(self.__cache['versions'].keys())
			versions.remove("nightly")

			from distutils.version import LooseVersion
			versions.sort(key=LooseVersion)

			version = versions[-1]
		
		if version not in self.__cache['versions']:
			raise VersionOrReleaseError("{version} not available. If this is a new version then you may need to --recache".format(version=version))

		version_info = self.__cache['versions'][version]
		releases     = version_info['releases']

		# Check to see if release is valid
		if release != "stable" and release not in releases:
			raise VersionOrReleaseError("{release} not available in {version}. If this is a new version/release then you may need to --recache".format(release=release, version=version))

		# Construct default URLs
		base_url = self.godot_toolkit_config.get("godot_cli", "base_dl_url")
		extended_base_url = "{base_url}/{version}/{release}".format(base_url=base_url, version=version, release=release)

		# If stable release specified we have to format the extended base url differently
		if release == "stable":
			extended_base_url = "{base_url}/{version}".format(base_url=base_url, version=version)

		# Now we take a wild (educated) guess as to what the file name is
		binary_name = sys_arch.get_formatted_binary_name(version, release)
		download_file_name = binary_name + ".zip"

		return "{extended_base_url}/{file_name}".format(extended_base_url=extended_base_url, file_name=download_file_name), download_file_name

	def scrape_versions(self):
		base_url = self.godot_toolkit_config.get("godot_cli", "base_dl_url") + "/"
		f = urllib.request.urlopen(base_url)

		soup = BeautifulSoup(f.read(), 'html.parser')

		# Hunt for table rows that have versions
		version_list = {}
		for tr in soup.find_all("tr"):
			elem_n = tr.find("td", {"class": "n"})
			elem_a = elem_n.a if elem_n else None
			elem_t = tr.find("td", {"class": "t"})
			elem_m = tr.find("td", {"class": "m"})
			elem_s = tr.find("td", {"class": "s"})

			if elem_n and elem_t.get_text() == "Directory":
				matches = re.finditer(r'(\d+\.\d+\.*\d*\.*\d*)', elem_a.get_text(), re.MULTILINE)
				for matchNum, match in enumerate(matches, start=1):
					version = match.group(1)
					version_list[version] = {
						"link": elem_a.get('href'),
						"last_modified": elem_m.get_text(),
						#"downloads": {}
					}

					#file_suffix_map_reverse = GodotSystemArch.get_file_suffix_map_reverse()
					#for sys_arch in file_suffix_map_reverse:
					#	version_list[version]['downloads'][sys_arch.name] = sys_arch.get_formatted_binary_name(version, "stable") + ".zip"

		return version_list

	def scrape_version_releases(self, version):
		base_url = self.godot_toolkit_config.get("godot_cli", "base_dl_url") + "/"
		f = urllib.request.urlopen(base_url + version)

		soup = BeautifulSoup(f.read(), 'html.parser')

		releases = {}
		for tr in soup.find_all("tr"):
			elem_n = tr.find("td", {"class": "n"})
			elem_a = elem_n.a if elem_n else None
			elem_t = tr.find("td", {"class": "t"})
			elem_m = tr.find("td", {"class": "m"})
			elem_s = tr.find("td", {"class": "s"})

			if elem_a and elem_t:
				release_name = elem_a.get_text()
				if elem_t.get_text() == "Directory" and release_name != "Parent Directory" and release_name != "mono" and release_name != "fixup":
					releases[release_name] = {
						"link": elem_a.get('href'),
						"last_modified": elem_m.get_text(),
						#"downloads": {}
					}

					#file_suffix_map_reverse = GodotSystemArch.get_file_suffix_map_reverse()
					#for sys_arch in file_suffix_map_reverse:
					#	releases[release_name]['downloads'][sys_arch.name] = sys_arch.get_formatted_binary_name(version, release_name) + ".zip"

		return releases

	def cache_nightly_manifest(self, save_cache=False):
		'''Caches latest nightly commit hash to disk
		'''
		f = urllib.request.urlopen(self.godot_toolkit_config.get("godot_nightly", "manifest_url"))
		manifest = json.loads(f.read())
		
		self.__cache['versions']['nightly'] = {
			"commit": manifest['commit'],
			"date":   manifest['date'],
			"sha256": manifest['sha256'],
			"downloads": {
				GodotSystemArch.OS_LINUX64.name: self.godot_toolkit_config.get("godot_nightly", "dl_url_linux"),
				GodotSystemArch.OS_WIN64.name  : self.godot_toolkit_config.get("godot_nightly", "dl_url_win64"),
				GodotSystemArch.OS_WIN32.name  : self.godot_toolkit_config.get("godot_nightly", "dl_url_win32"),
				GodotSystemArch.OS_OSX64.name  : self.godot_toolkit_config.get("godot_nightly", "dl_url_osx"),
			}
		}

		if save_cache == True:
			self.save_changes_to_cache()