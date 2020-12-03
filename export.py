import configparser
from get_extract import *
from pprint import pprint as pp
from asnake.aspace import ASpace
import json
import argparse
import re
import logging
import os.path
import jinja2
from transform import MAPPING, Transforms


argparser = argparse.ArgumentParser(description="Export MODS metadata from ArchivesSpace digital objects")
argparser.add_argument('--cachefile', default=None, help="Name of a json file containing cached data. For development and testing purposes.")
argparser.add_argument("OUTPUTPATH", help="File path for record output.")
cliargs = argparser.parse_args()
CACHEFILE = cliargs.cachefile


logging.basicConfig(level=logging.INFO)

def get_export_list(EXTRACTED_DATA):
	to_export = []
	for do_id, do_data in EXTRACTED_DATA['digital_objects'].items():
		compass_pid = get_compass_pid(do_data)
		if compass_pid is not None:
			filename = compass_pid.replace(':', '_') + '_MODS.xml'
			to_export.append((do_id, filename))
		else:
			logging.error("Could not find valid pid for %s" % do_id)
	return to_export


def get_compass_pid(do_data):
	namespace = 'smith'
	for file_version in do_data['file_versions']:
		if 'compass' in file_version['file_uri']: # Make sure that this is a compass URL
			matches = re.findall(r'%s:[0-9]+' % namespace, file_version['file_uri'])
			if matches is not None:
				return matches[0]


def render_record(mapping): 
    templateLoader = jinja2.FileSystemLoader(searchpath=".")
    templateEnv = jinja2.Environment(loader=templateLoader)

    # Merge the template and data
    template = templateEnv.get_template('compass-mods-template.xml')

    return template.render(mapping)


if __name__ == '__main__':

	aspace = ASpace()

	with open('config.json') as config_file:
		try:
			configs = json.load(config_file)
		except:
			logging.error('No config file found')
			exit(1)

	## Uncomment when testing:
	# repo_data = aspace.client.get('/repositories?all_ids=true').json()
	# repos = []
	# for repo in repo_data:
	# 	repo_id = repo['uri'].split('/')[-1]
	# 	repos.append(repo_id)

	## Comment out this line when testing:
	repos = configs['config']['repos']

	if CACHEFILE is None:
		EXTRACTED_DATA = get_extract(repos)
		with open('extract.json', 'w') as outfile:
			json.dump(EXTRACTED_DATA, outfile)
	else:
		with open('extract.json', 'r') as infile:
			EXTRACTED_DATA = json.load(infile)

	# Add repository names and finding aid url to extracted data
	EXTRACTED_DATA['repositories'] = configs['config']['repositories']
	EXTRACTED_DATA['url_stem'] = configs['config']['findingaid_url']

	to_export = get_export_list(EXTRACTED_DATA)

	transforms = Transforms()

	save_path = cliargs.OUTPUTPATH

	if os.path.isdir(save_path) != False:
		for current_record in to_export:
			do_id = current_record[0]
			pp(do_id)
			template_context = {}
			record_valid = True
			for field_name, field_recipe in MAPPING.items():
				try:
					transform_method = getattr(transforms, field_recipe['transform_function'])
				except AttributeError as e:
					print("No transform named '%s'. Please add a transform method to the Transforms class in transform.py." % field_recipe['transform_function'])
					exit(1)

				try:
					transform_return_value = transform_method(EXTRACTED_DATA, do_id)
				except Exception as e:
					logging.warning("%s %s %s" % (do_id, field_name, str(e)))
					transform_return_value = None
				if (transform_return_value is None):
					if ('required' in field_recipe) & (field_recipe['required'] is True):
						logging.error("Required field '%s' missing in %s. Skipping record." % (field_name, do_id))
						record_valid = False
					else:
						logging.warning("Information not found in %s field for digital object %s" % (field_name, do_id))
						template_context[field_name] = transform_return_value
				else:
					template_context[field_name] = transform_return_value
						
			if record_valid == True:
				logging.info('Rendering MODS record for %s' % current_record[0])
				xml = render_record(template_context)
				handle = current_record[1]
				filename = os.path.join(save_path, handle)

				try:
					with open(filename, "w") as fh:
						logging.info('Writing %s' % filename)
						fh.write(xml)
				except Exception as e:
					logging.error('File could not be written for %s' % (handle))

		logging.info('All files written.')        

	else:
		logging.error("Directory not found. Please create if not created. Files cannot be written without an existing directory to store them.")
		exit(1)

	# import pdb; pdb.set_trace()
