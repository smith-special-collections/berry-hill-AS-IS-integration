import configparser
from get_extract import *
from pprint import pprint as pp
from asnake.aspace import ASpace
import json
import argparse
import re
import logging

argparser = argparse.ArgumentParser(description="Export MODS metadata from ArchivesSpace digital objects")
argparser.add_argument('--cachefile', default=None, help="Name of a json file containing cached data. For development and testing purposes.")
cliargs = argparser.parse_args()
CACHEFILE = cliargs.cachefile

def get_export_list(EXTRACTED_DATA):
	to_export = []
	for do_id, do_data in EXTRACTED_DATA['digital_objects'].items():
		compass_pid = get_compass_pid(do_data)
		pp(compass_pid)
		if compass_pid is not None:
			filename = compass_pid.replace(':', '_') + '_MODS.xml'
			to_export.append((do_id, filename))
		else:
			logging.ERROR("Could not find valid pid for %s" % do_id)
	return to_export

def get_compass_pid(do_data):
	namespace = 'smith'
	for file_version in do_data['file_versions']:
		if 'compass' in file_version['file_uri']: # Make sure that this is a compass URL
			matches = re.findall(r'%s:[0-9]+' % namespace, file_version['file_uri'])
			if matches is not None:
				return matches[0]

if __name__ == '__main__':

	aspace = ASpace()

	config = configparser.ConfigParser()
	config.read('config.ini')

	repos = config['repos']['repos'].split(',')

	if CACHEFILE is None:
		EXTRACTED_DATA = get_extract(repos)
		with open('extract.json', 'w') as outfile:
			json.dump(EXTRACTED_DATA, outfile)
	else:
		with open('extract.json', 'r') as infile:
			EXTRACTED_DATA = json.load(infile)

	to_export = get_export_list(EXTRACTED_DATA)

	import pdb; pdb.set_trace()
	pp('Extract done.')
