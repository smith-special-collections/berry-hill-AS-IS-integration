from asnake.aspace import ASpace
from pprint import pprint as pp
import logging


def get_digital_objects(repo):
	r = aspace.repositories(repo)
	dos = r.digital_objects()
	digital_objects = []
	for do in dos:
		for file_version in do.json()['file_versions']:
			if 'compass' in file_version['file_uri']:
				if not do.json() in digital_objects:
					digital_objects.append(do.json())

	return digital_objects
	

def chunk_ids(id_list):
	ids = []
	if len(id_list) > 25:
		id_chunks = [id_list[uri:uri + 25] for uri in range(0, len(id_list), 25)] 
		for chunk in id_chunks:
			chunk = [str(i) for i in chunk]
			chunk = ','.join(chunk)
			ids.append(chunk)
	
	else:
		id_list = [str(i) for i in id_list]
		id_list = ','.join(id_list)
		ids.append(id_list)

	return ids


def group_uris(uri_list):
	all_uris = {}
	all_uris['2'] = []
	all_uris['3'] = []
	all_uris['4'] = []
	for uri in uri_list:
		if '/repositories/2' in uri:
			all_uris['2'].append(uri.split('/')[-1])
		elif '/repositories/3' in uri:
			all_uris['3'].append(uri.split('/')[-1])
		elif '/repositories/4' in uri:
			all_uris['4'].append(uri.split('/')[-1])

	return all_uris


if __name__ == "__main__":

	logging.basicConfig(level=logging.INFO)
	aspace = ASpace()

	resource_uris = []
	extracted_data = {}
	extracted_data['digital_objects'] = []
	extracted_data['archival_objects'] = []
	extracted_data['accessions'] = []
	extracted_data['resources'] = []	
	extracted_data['subjects'] = []
	extracted_data['agents'] = []

	# Get digital objects
	repos = [2, 3, 4]
	for repo in repos:	
		extracted_data['digital_objects'].extend(get_digital_objects(repo))

	# Get parent objects (mostly archival objects, a couple accessions and resources)
	all_ao_uris = []
	for do in extracted_data['digital_objects']:
		for instance in do['linked_instances']:
			if 'archival_objects' in instance['ref']:
				if not instance['ref'] in all_ao_uris:
					all_ao_uris.append(instance['ref'])
				else:
					record = aspace.client.get(instance['ref'])
					if 'resources' in instance['ref']:
						extracted_data['resources'].append(record.json())
					elif 'accessions' in instance['ref']:
						extracted_data['accessions'].append(record.json())

	aos_grouped_by_repo = group_uris(all_ao_uris)
	for k, v in aos_grouped_by_repo.items():
		chunks = chunk_ids(v)
		for chunk in chunks:
			archival_objects = aspace.client.get(f'/repositories/{k}/archival_objects?id_set={chunk}')
			extracted_data['archival_objects'].extend(archival_objects.json())

	
	# Get resources
	resource_uris = []
	for ao in extracted_data['archival_objects']:
		try:
			if not ao['resource']['ref'] in resource_uris:
				resource_uris.append(ao['resource']['ref'])
		except TypeError as e:
			continue

	resources_grouped_by_repo = group_uris(resource_uris)
	for k, v in resources_grouped_by_repo.items():
		chunks = chunk_ids(v)
		for chunk in chunks:
			resources = aspace.client.get(f'/repositories/{k}/resources?id_set={chunk}')
			extracted_data['resources'].extend(resources.json())




