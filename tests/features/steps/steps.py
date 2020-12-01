from behave import given, when, then
from lxml import etree, objectify
import subprocess
import os
import sys
import time
import json
from asnake.aspace import ASpace
import logging
import tempfile

logging.basicConfig(level=logging.INFO)

EXPORTER_PATH = os.path.join(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir), os.pardir), os.pardir)
EXPORTER_PY_FILE = 'export.py'

@given('I set the title of the Digital Object to "{title}"')
def step_impl(context, title):
	aspace = ASpace()

	uri = [uri for uri in context.uris if 'digital_objects' in uri]
	rec = aspace.client.get(uri[0]).json()
	rec['title'] = title
	aspace.client.post(rec['uri'], json=rec)


@given('I set the title of the Archival Object to "{title}"')
def step_impl(context, title):
	aspace = ASpace()

	uri = [uri for uri in context.uris if 'archival_objects' in uri]
	rec = aspace.client.get(uri[0]).json()
	rec['title'] = title
	aspace.client.post(rec['uri'], json=rec)


@given('I set the date of the Archival Object to "{date}"')
def step_impl(context, date):
	aspace = ASpace()

	uri = [uri for uri in context.uris if 'archival_objects' in uri]
	rec = aspace.client.get(uri[0]).json()
	rec['dates'][0]['expression'] = date
	aspace.client.post(rec['uri'], json=rec)


@given('I set the id of the Digital Object to "{do_id}"')
def step_impl(context, do_id):
	aspace = ASpace()

	uri = [uri for uri in context.uris if 'digital_objects' in uri]
	rec = aspace.client.get(uri[0]).json()
	rec['digital_object_id'] = do_id
	aspace.client.post(rec['uri'], json=rec)


@when('I run the exporter')
def step_imp(context):
	context.temp_export_output_dir = tempfile.TemporaryDirectory()
	os.chdir(EXPORTER_PATH)
	shell_command = [sys.executable, EXPORTER_PY_FILE, context.temp_export_output_dir.name]
	result = subprocess.run(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if result.returncode != 0:
		logging.error("export.py error: %s" % result.stderr.decode())
		logging.error("export.py completed %s" % result.stdout.decode())
	else:
		logging.debug("export.py completed %s" % result.stdout.decode())
	# import pdb; pdb.Pdb(stdout=sys.__stdout__).set_trace()
	try:
		with open(context.temp_export_output_dir.name + '/' + context.filename + '.xml', 'rb') as fobj:
			xml = fobj.read()
	except FileNotFoundError as e:
		assert False, "Could not find XML output file %s" % e
	context.xml_output_tree = etree.XML(xml)


@then('I should see a <titleInfo><title> tag that reads "{title}"')
def step_impl(context, title):
	tag = context.xml_output_tree.xpath('x:titleInfo/x:title', namespaces={'x':'http://www.loc.gov/mods/v3'})[0].text
	assert tag == title, 'Tag text not as expected! Wanted: {}. Returned: {}'.format(title, tag)


@then('I should not see a <titleInfo><title> tag that reads "{title}"')
def step_impl(context, title):
	tag = context.xml_output_tree.xpath('x:titleInfo/x:title', namespaces={'x':'http://www.loc.gov/mods/v3'})[0].text
	assert tag != title, 'Tag text not as expected! Wanted: {}. Returned: {}'.format(title, tag)


@then('I should see an <identifier> tag with an attribute of local that reads "{do_id}"')
def step_impl(context, do_id):
	tag = context.xml_output_tree.xpath('x:identifier[@type="local"]', namespaces={'x':'http://www.loc.gov/mods/v3'})[0].text
	assert tag == do_id, 'Tag text not as expected! Wanted: {}. Returned: {}'.format(do_id, tag)
