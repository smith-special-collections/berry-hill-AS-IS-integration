import behave
from asnake.aspace import ASpace
import add_test_records
import behave
import logging
import os
import json

# Create Repo, Repo Agent, Controlled Values
def before_all(context):
	here = os.path.dirname(os.path.abspath(__file__))
	filename = os.path.join(here, 'test_records.json')
	with open(filename) as json_file:
		try:
			data = json.load(json_file)
		except Exception as e:
			logging.error(e)
			exit()


	aspace = ASpace()
	uri_dict = add_test_records.macro_setup(aspace, data['repo_agent'][0], data['repo'][0], data['resource'][0])

	context.uris = []
	context.uris.append(uri_dict['repo_uri'])
	context.uris.append(uri_dict['repo_agent_uri'])
	context.uris.append(uri_dict['resource_uri'])

	print('Repository and Resource created.')
	print(context.uris)



# Delete all created records
def after_all(context):
	aspace = ASpace()
	for uri in context.uris:
		delete = aspace.delete(uri).json()
		print('{} deleted.'.format(delete['uri']))

