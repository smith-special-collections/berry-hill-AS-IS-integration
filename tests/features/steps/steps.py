from behave import given, when, then
from lxml import etree, objectify
import subprocess
import os
import time
import json
from asnake.aspace import ASpace
import logging

logging.basicConfig(level=logging.INFO)


@given('I set the title of the Digital Object to "Strachey to Woolf"')
def step_impl(context):
	pass


@given('I set the title of the Archival Object to "Not This"')
def step_impl(context):
	pass


@given('I set the date of the Archival Object to "1917 Dec 21"')
def step_impl(context):
	pass


@then('I should see a <titleInfo><title> tag that reads "{title}"')
def step_impl(context, title):
	tag = context.xml_output_tree.xpath('x:titleInfo/x:title', namespaces={'x':'http://www.loc.gov/mods/v3'})[0].text
	assert tag == title, 'Tag text not as expected! Wanted: {}. Returned: {}'.format(title, tag) 


@then('I should not see a <titleInfo><title> tag that reads "{title}"')
def step_impl(context, title):
	tag = context.xml_output_tree.xpath('x:titleInfo/x:title', namespaces={'x':'http://www.loc.gov/mods/v3'})[0].text
	assert tag != title, 'Tag text not as expected! Wanted: {}. Returned: {}'.format(title, tag) 

	

