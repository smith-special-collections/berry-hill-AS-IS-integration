import configparser
from get_extract import *
from pprint import pprint as pp
from asnake.aspace import ASpace
import json
import argparse

argparser = argparse.ArgumentParser(description="Export MODS metadata from ArchivesSpace digital objects")
argparser.add_argument('--cachefile', default=None, help="Name of a json file containing cached data. For development and testing purposes.")
cliargs = argparser.parse_args()
CACHEFILE = cliargs.cachefile

if __name__ == '__main__':

	aspace = ASpace()

	config = configparser.ConfigParser()
	config.read('config.ini')

	repos = config['repos']['repos'].split(',')

	if CACHEFILE is None:
		EXTRACT = get_extract(repos)
		with open('extract.json', 'w') as outfile:
			json.dump(EXTRACT, outfile)
	else:
		with open('extract.json', 'r') as infile:
			EXTRACT = json.load(infile)

	import pdb; pdb.set_trace()
	pp('Extract done.')
