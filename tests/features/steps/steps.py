from behave import given, when, then
from lxml import etree, objectify
import subprocess
import os
import time
import json
from asnake.aspace import ASpace
import logging
import tempfile

logging.basicConfig(level=logging.INFO)


@given('I set the title of the Digital Object to "{title}"')
def step_impl(context, title):
	aspace = ASpace()

	context.data['digital_object'][0]['title'] = title
	uri = [uri for uri in context.uris if 'digital_objects' in uri]
	aspace.client.post(uri[0], json=context.data['digital_object'][0])


@given('I set the title of the Archival Object to "{title}"')
def step_impl(context, title):
	aspace = ASpace()

	context.data['archival_object'][0]['title'] = title
	uri = [uri for uri in context.uris if 'archival_objects' in uri]
	aspace.client.post(uri[0], json=context.data['archival_object'][0])


@given('I set the date of the Archival Object to "1917 Dec 21"')
def step_impl(context):
	pass


@given('I set the id of the Digital Object to "smith_mrbc_ms00001_as38141_00')
def step_impl(context):
	pass

@when('I run the exporter')
def step_imp(context):
	context.temp_export_output_dir = tempfile.TemporaryDirectory()
	os.chdir('../')
	os.system('python export.py %s' % context.temp_export_output_dir.name)
	os.system('ls %s' % context.temp_export_output_dir.name)
	# import pdb, sys; pdb.Pdb(stdout=sys.__stdout__).set_trace()
	with open(context.temp_export_output_dir.name + '/' + context.filename + '.xml', 'rb') as fobj:
		xml = fobj.read()

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
def step_impl(context, title):
	tag = context.xml_output_tree.xpath('x:identifier[@type=local]', namespaces={'x':'http://www.loc.gov/mods/v3'})[0].text
	assert tag == do_id, 'Tag text not as expected! Wanted: {}. Returned: {}'.format(do_id, tag)
