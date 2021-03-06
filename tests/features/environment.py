import behave
from asnake.aspace import ASpace
import add_test_records
import behave
import logging
import os
import subprocess
import json
import time
import re
from lxml import etree, objectify



logging.basicConfig(level=logging.INFO)


# Create Repo, Repo Agent, Controlled Values, Resource, Archival Object, Digital Object, Subjects, Agents, Top Container
def before_all(context):
	here = os.path.dirname(os.path.abspath(__file__))
	filename = os.path.join(here, 'test_records.json')
	with open(filename) as json_file:
		try:
			data = json.load(json_file)
		except Exception as e:
			logging.error(e)
			exit()

	context.data = data
	try:
		aspace = ASpace()
	except Exception as e:
		logging.error("before_all() Couldn't connect to ArchivesSpace: %s" % e)
		exit(1)

	context.uris = []
	uri_dict = add_test_records.macro_setup(aspace, data['repo_agent'][0], data['repo'][0], data['resource'][0])

	context.uris.append(uri_dict['repo_uri'])
	context.uris.append(uri_dict['repo_agent_uri'])
	context.uris.append(uri_dict['resource_uri'])

	time.sleep(5)
	uri_dict = add_test_records.micro_setup(aspace, uri_dict, data['archival_object'][0], data['digital_object'][0], data['agents'][0], data['subjects'][0], data['top_container'][0])

	context.uris.append(uri_dict['do_uri'])
	context.uris.append(uri_dict['tc_uri'])
	context.uris.extend(uri_dict['agent_uris'])
	context.uris.extend(uri_dict['subject_uris'])
	context.uris.append(uri_dict['ao_uri'])

	# Save file name of exporter output
	regex = '(smith:+?\d+)'
	uris = [uri['file_uri'] for uri in data['digital_object'][0]['file_versions'] if 'compass' in uri['file_uri']]
	uri = uris[0] # Takes first URL of list
	islandora_pid = re.search(regex, uri).group()
	formatted_islandora_pid = islandora_pid.replace(':', '_')
	context.filename = formatted_islandora_pid + '_MODS'


# Delete all created records
def after_all(context):
	logging.info("Cleaning up")
	aspace = ASpace()
	for uri in context.uris:
		delete = aspace.client.delete(uri).json()
