from behave import given, when, then
from lxml import etree, objectify
import subprocess
import os
import time
import add_test_records
import json
from asnake.aspace import ASpace
import logging
import re

logging.basicConfig(level=logging.INFO)



# 	regex = '(smith:+?\d+)'
# 	uris = [uri['file_uri'] for uri in data['digital_object'][0]['file_versions'] if 'compass' in uri['file_uri']]
# 	uri = uris[0] # Takes first URL of list
# 	islandora_pid = re.search(regex, uri).group()
# 	formatted_islandora_pid = islandora_pid.replace(':', '_')
# 	context.filename = formatted_islandora_pid + '_MODS'


@when('I run the export')
def step_impl(context):
	pass
	# os.chdir('../')
	# subprocess.call(['python3', 'exportASAOtoMODS.py', 'features'])


def save_xml_output(context):
	# os.chdir('features')
	with open(context.filename + '.xml', 'rb') as fobj:
		xml = fobj.read()

	context.xml_output_tree = etree.XML(xml)


@given('I attach a Person Agent named "Bell, Quentin." with a role of "creator" to an Archival Object')
def step_impl(context):
	pass


@given('I attach a Person Agent named "Hogarth Press." with a role of "donor" to an Archival Object')
def step_impl(context):
	pass


@given('I set the repository name to "Mortimer Rare Book Collection (MRBC)"')
def step_impl(context):
	pass


@given('I set the digital object component id to "smith_mrbc_ms00001_as38141_00"')
def step_impl(context):
	pass


@given('I set the dateCreated field to "1917 Dec 21"')
def step_impl(context):
	pass


@given('I set the dateValid field to "1917-12-21"')
def step_impl(context):
	pass


@then('I should see a <originInfo><dateCreated> field with an attribute keyDate of "{attribute}" that reads "{date_string}"')
def step_impl(context, attribute, date_string):
    assert context.xml_output_tree.xpath('x:originInfo/x:dateCreated[@type=%s]' % attribute, namespaces={'x':'http://www.loc.gov/mods/v3'}).text == date_string


@then('I should see a <originInfo><dateValid> field with an attribute encoding of "{attribute1}" and an attribute point of "{attribute2}" that reads "{date_string}"')
def step_impl(context, attribute1, attribute2, date_string):
	assert context.xml_output_tree.xpath('x:originInfo/x:dateValue[@encoding=%s and (@point=%s)]' % (attribute1, attribute2), namespaces={'x':'http://www.loc.gov/mods/v3'}).text == date_string


# Fix this
@then('I should see a <name><namePart> field that reads "{repository_name}"')
def step_impl(context, repository_name):
	assert context.xml_output_tree.xpath('x:name/x:namePart').text == repository_name


# Fix this
@then('I should see a <name><role><roleTerm> field with an attribute authority of "{attribute1}" and an attribute type of "{attribute2}" that reads "{unit_string}"')
def step_impl(context, attribute1, attribute2, unit_string):
	assert context.xml_output_tree.xpath('x:name/x:role/x:roleTerm[@authority=%s and (@type=%s)]' % (attribute1, attribute2), namespaces={'x':'http://www.loc.gov/mods/v3'}).text == unit_string


@then('I should see a <name> field with an attribute type of "{atype}" and an attribute authority of "{authority}"')
def step_impl(context, atype, authority):
	assert len(context.xml_output_tree.xpath('x:name[@type=%s and (@authority=%s)]' % atype, authority), namespaces={'x':'http://www.loc.gov/mods/v3'}) > 0


@then('I should see a <name><role><roleTerm> field with an attribute type of "text" and an attribute authority of "marcrelator" that reads "{role}"')
def step_impl(context, role):
	assert context.xml_output_tree.xpath('x:name/x:role/x:roleTerm[@type="text" and (@authority="marcrelator")]', namespaces={'x':'http://www.loc.gov/mods/v3'}).text == role



	

