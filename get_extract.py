from asnake.aspace import ASpace
from pprint import pprint as pp
import logging


aspace = ASpace()

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


def group_agents(uri_list):
	all_uris = {}
	all_uris['corporate_entities'] = []
	all_uris['people'] = []
	all_uris['families'] = []
	for uri in uri_list:
		if 'corporate' in uri:
			all_uris['corporate_entities'].append(uri.split('/')[-1])
		elif 'people' in uri:
			all_uris['people'].append(uri.split('/')[-1])
		elif 'families' in uri:
			all_uris['families'].append(uri.split('/')[-1])

	return all_uris


def init_data_dict():
	data_dict = {
		'digital_objects': [],
		'archival_objects': [],
		'accessions': [],
		'resources': [],
		'subjects': [],
		'agents': [],
		'top_containers': [],
	}

	return data_dict


def get_digital_objects(repo):
	r = aspace.repositories(repo)
	dos = r.digital_objects()
	digital_objects = {}
	for do in dos:
		for file_version in do.json()['file_versions']:
			if 'compass' in file_version['file_uri']:
				# If there's more than one file version don't add the DO again.
				if not do.json() in digital_objects:
					do_data = do.json()
					digital_objects[do_data['digital_object_id']] = do_data
	return digital_objects


def get_digital_objects_by_repo(list_of_repos, data_dict):
	for repo in list_of_repos:
		data_dict['digital_objects'].extend(get_digital_objects(repo))

	return data_dict


def get_parent_objects(data_dict):
	all_ao_uris = []
	for do in data_dict['digital_objects']:
		for instance in do['linked_instances']:
			if 'archival_objects' in instance['ref']:
				if not instance['ref'] in all_ao_uris:
					all_ao_uris.append(instance['ref'])
				else:
					record = aspace.client.get(instance['ref'])
					if 'resources' in instance['ref']:
						data_dict['resources'].append(record.json())
					elif 'accessions' in instance['ref']:
						data_dict['accessions'].append(record.json())

	aos_grouped_by_repo = group_uris(all_ao_uris)
	for k, v in aos_grouped_by_repo.items():
		chunks = chunk_ids(v)
		for chunk in chunks:
			archival_objects = aspace.client.get(f'/repositories/{k}/archival_objects?id_set={chunk}')
			data_dict['archival_objects'].extend(archival_objects.json())

	return data_dict


def get_resources(data_dict):
	resource_uris = []
	for ao in data_dict['archival_objects']:
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
			data_dict['resources'].extend(resources.json())

	return data_dict


def get_agents(data_dict):
	agent_uris = []
	for ao in data_dict['archival_objects']:
		if len(ao['linked_agents']) > 0:
			for agent in ao['linked_agents']:
				if not agent['ref'] in agent_uris:
					agent_uris.append(agent['ref'])

	for r in data_dict['resources']:
		if len(r['linked_agents']) > 0:
			for agent in r['linked_agents']:
				if not agent['role'] == 'subject':
					if not agent['ref'] in agent_uris:
						agent_uris.append(agent['ref'])

	agents_grouped_by_type = group_agents(agent_uris)
	for k, v in agents_grouped_by_type.items():
		chunks = chunk_ids(v)
		for chunk in chunks:
			agents = aspace.client.get(f'/agents/{k}?id_set={chunk}')
			data_dict['agents'].extend(agents.json())

	return data_dict


def get_subjects(data_dict):
	subject_uris = []
	for ao in data_dict['archival_objects']:
		if len(ao['subjects']) > 0:
			for subject in ao['subjects']:
				if not subject['ref'] in subject_uris:
					subject_uris.append(subject['ref'].split('/')[-1])

	chunks = chunk_ids(subject_uris)
	for chunk in chunks:
		subjects = aspace.client.get(f'/subjects?id_set={chunk}')
		data_dict['subjects'].extend(subjects.json())

	return data_dict


def get_top_containers(data_dict):
	top_container_uris = []
	for ao in data_dict['archival_objects']:
		if len(ao['instances']) > 0:
			for i in ao['instances']:
				try:
					if not i['sub_container']['top_container']['ref'] in top_container_uris:
						top_container_uris.append(i['sub_container']['top_container']['ref'])
				except KeyError:
					pass
	grouped_by_repo = group_uris(top_container_uris)
	for k, v in grouped_by_repo.items():
		chunks = chunk_ids(v)
		for chunk in chunks:
			tcs = aspace.client.get(f'/repositories/{k}/top_containers?id_set={chunk}')
			data_dict['top_containers'].extend(tcs.json())

	return data_dict



def get_extract(list_of_repos):
	data_dict = init_data_dict()
	return get_top_containers(get_subjects(get_agents(get_resources(get_parent_objects(get_digital_objects_by_repo(list_of_repos, data_dict))))))
