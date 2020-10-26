import configparser
from get_extract import *
from pprint import pprint as pp
from asnake.aspace import ASpace
import json

if __name__ == '__main__':

	aspace = ASpace()

	config = configparser.ConfigParser()
	config.read('config.ini')

	repos = config['repos']['repos'].split(',')

	extract = get_extract(repos)

	with open('extract.json', 'w') as outfile:
		json.dump(extract, outfile)

	pp('Extract done.')