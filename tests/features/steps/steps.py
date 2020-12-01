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
	os.chdir('../')
	os.system('python3 export.py %s' % context.temp_export_output_dir.name)
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
def step_impl(context, do_id):
	tag = context.xml_output_tree.xpath('x:identifier[@type="local"]', namespaces={'x':'http://www.loc.gov/mods/v3'})[0].text
	assert tag == do_id, 'Tag text not as expected! Wanted: {}. Returned: {}'.format(do_id, tag)
