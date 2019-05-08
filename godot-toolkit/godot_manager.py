"""A Godot version manager
"""

import json, urllib, os, platform, sys, zipfile, shutil, datetime
from urllib.request import urlopen
import urllib.request
from distutils.version import LooseVersion

from godot_toolkit_config import GodotToolkitConfig
from godot_binaries_cache import GodotBinariesCache
from godot_binaries_cache import VersionOrReleaseError
from godot_binaries_manifest import GodotBinariesManifest
from godot_sys_arch import GodotSystemArch
from godot_sys_arch import UnknownSysArch

try:
	import requests
except:
	print("[-] requests Python module needs to be installed. Install it with `pip install requests`")
	exit()


class GodotManager():
	version = "0.1"

	def __init__(self):
		self.godot_toolkit_config = GodotToolkitConfig()
		self.manifest             = GodotBinariesManifest()
		self.cache                = GodotBinariesCache()

		self.binaries_dir = self.godot_toolkit_config.get_adjusted_path("godot_cli", "godot_binaries_path")
		self.download_tmp = self.godot_toolkit_config.get_adjusted_path("godot_cli", "download_tmp")

		if not os.path.exists(self.download_tmp):
			os.makedirs(self.download_tmp)

	def download_version(self, version="latest", release="stable", sys_arch: GodotSystemArch=GodotSystemArch.from_current_os()):
		file_download_url = None
		file_name         = None
		try:
			file_download_url, file_name = self.cache.construct_download_url(version, release, sys_arch)
		except VersionOrReleaseError as e:
			print("An error occurred while downloading {version}: {error}".format(version=version, error=e))
			return False

		# Check to see if we don't already have the requested file downloaded
		bin_info = self.manifest.get_binary_info(version, release, sys_arch)
		if bin_info:
			print("Already have this version")
			return True

		with open(os.path.join(self.download_tmp, file_name), 'wb') as f:
			response = requests.get(file_download_url, stream=True)
			total = response.headers.get('content-length')

			if total is None:
				f.write(response.content)
			else:
				downloaded = 0
				total = int(total)
				for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
					downloaded += len(data)
					f.write(data)
					done = int(50*downloaded/total)
					sys.stdout.write('\r[{}{}]'.format('█' * done, '.' * (50-done)))
					sys.stdout.flush()
		sys.stdout.write('\n')

		full_zip_path = os.path.join(self.download_tmp, file_name)

		# Unzip and retrieve the gold inside
		binary_filename = self.unzip(file_name)

		# Ingest the binary into the manifest
		self.manifest.add_binary(version, release, sys_arch, os.path.join(full_zip_path + ".unzip", binary_filename))

		# Remove intermediate files
		os.remove(full_zip_path)
		shutil.rmtree(full_zip_path + ".unzip")

	def unzip(self, src_filename):
		zip_full_path = os.path.join(self.download_tmp, src_filename)
		unzip_dest_path = os.path.join(self.download_tmp, src_filename + ".unzip")

		zip_ref = zipfile.ZipFile(zip_full_path, 'r')

		# Unzip
		if not os.path.exists(unzip_dest_path):
			os.makedirs(unzip_dest_path)
		zip_ref.extractall(unzip_dest_path)

		zip_ref.close()

		# Look for binary inside unzipped directory
		binary_filename = os.listdir(unzip_dest_path)[0]

		return binary_filename

	def recache(self):
		self.cache.recache()
		

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(prog='godot-cli', description='A CLI application that allows management and launch control over Godot versions.')
	parser.add_argument('-v', '--version',             action='version',              version='%(prog)s version ' + GodotManager.version)
	parser.add_argument('--avail-versions',            action='store_true',           help='Check what versions are available.')
	parser.add_argument('--avail-releases',            action='store_true',           help='Check which releases of a specific version are available.')
	parser.add_argument('--recache',                   action='store_true',           help='Check which releases of a specific version are available.')
	parser.add_argument('--download',                  action='store_true',           help='Check which releases of a specific version are available.')
	parser.add_argument('downloadversion', nargs='?', default="latest")
	parser.add_argument('downloadrelease', nargs='?', default="stable")
	parser.add_argument('downloadarch', nargs='?', default=None)
	args = parser.parse_args()

	godot_manager = GodotManager()

	if args.recache == True:
		print("[+] Recaching")
		godot_manager.unzip("Godot_v3.1-rc3_x11.64.zip", "")

	if args.avail_versions == True:
		print("TODO")
		quit()

	if args.download == True:
		try:
			sys_arch = GodotSystemArch.from_os_string(args.downloadarch)
			godot_manager.download_version(args.downloadversion, args.downloadrelease, sys_arch)
		except UnknownSysArch as e:
			print("Unknown arch {arch}".format(arch=args.downloadarch))