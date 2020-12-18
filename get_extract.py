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
	for uri in uri_list:
		uri_elems = uri.split('/')
		k = uri_elems[2]
		if k not in all_uris:
			all_uris[k] = []
		all_uris[k].append(uri_elems[-1])
	
	return all_uris


def init_data_dict():
	data_dict = {
		'digital_objects': {},
		'archival_objects': {},
		'series': {},
		'accessions': {},
		'resources': {},
		'subjects': {},
		'agents': {},
		'top_containers': {},
	}

	return data_dict


def get_digital_objects(repo):
	r = aspace.repositories(repo)
	dos = r.digital_objects()
	digital_objects = {}
	for do in dos:
		if 'user_defined' in do.json().keys():
			if do.json()['user_defined']['boolean_1'] == True:
				continue

		for file_version in do.json()['file_versions']:
			if 'compass' in file_version['file_uri']:
				# If there's more than one file version, don't add the DO again.
				do_data = do.json()
				if not do_data['digital_object_id'] in digital_objects:
					digital_objects[do_data['digital_object_id']] = do_data

	return digital_objects


def get_digital_objects_by_repo(list_of_repos, data_dict):
	for repo in list_of_repos:
		data_dict['digital_objects'] = {**data_dict['digital_objects'], **get_digital_objects(repo)}
	return data_dict


def get_parent_objects(data_dict):
	all_ao_uris = []
	for _, do in data_dict['digital_objects'].items():
		for instance in do['linked_instances']:
			if 'archival_objects' in instance['ref']:
				if not instance['ref'] in all_ao_uris:
					all_ao_uris.append(instance['ref'])
				else:
					parent_record = aspace.client.get(instance['ref'])
					if 'resources' in instance['ref']:
						resource_data = parent_record.json()
						data_dict['resources'][resource_data['uri']] = resource_data
					elif 'accessions' in instance['ref']:
						accession_data = parent_record.json()
						data_dict['accessions'][accession_data['uri']] = accession_data

	aos_grouped_by_repo = group_uris(all_ao_uris)
	for k, v in aos_grouped_by_repo.items():
		chunks = chunk_ids(v)
		for chunk in chunks:
			archival_objects = aspace.client.get(f'/repositories/{k}/archival_objects?id_set={chunk}')
			for archival_object_data in archival_objects.json():
				data_dict['archival_objects'][archival_object_data['uri']] = archival_object_data

	return data_dict


def get_series(data_dict):
	all_series_uris = []
	for _, ao in data_dict['archival_objects'].items():
		if 'parent' in ao.keys():
			if 'archival_objects' in ao['parent']['ref']:
				if not ao['parent']['ref'] in all_series_uris:
					all_series_uris.append(ao['parent']['ref'])

	series_grouped_by_repo = group_uris(all_series_uris)
	for k, v in series_grouped_by_repo.items():
		chunks = chunk_ids(v)
		for chunk in chunks:
			records = aspace.client.get(f'/repositories/{k}/archival_objects?id_set={chunk}')
			for record_data in records.json():
				if record_data['level'] == 'series':
					data_dict['series'][record_data['uri']] = record_data

	return data_dict


def get_resources(data_dict):
	resource_uris = []
	for _, ao in data_dict['archival_objects'].items():
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
			resources_list = resources.json()
			resources_dict = {}
			for resource_data in resources_list:
				resources_dict[resource_data['uri']] = resource_data
			data_dict['resources'] = {**data_dict['resources'], **resources_dict}

	return data_dict


def get_agents(data_dict):
	agent_uris = []
	for _, ao in data_dict['archival_objects'].items():
		if len(ao['linked_agents']) > 0:
			for agent in ao['linked_agents']:
				if not agent['ref'] in agent_uris:
					agent_uris.append(agent['ref'])

	for _, r in data_dict['resources'].items():
		if len(r['linked_agents']) > 0:
			for agent in r['linked_agents']:
				if not agent['role'] == 'subject':
					if not agent['ref'] in agent_uris:
						agent_uris.append(agent['ref'])

	agents_grouped_by_type = group_uris(agent_uris)
	for k, v in agents_grouped_by_type.items():
		chunks = chunk_ids(v)
		for chunk in chunks:
			agents = aspace.client.get(f'/agents/{k}?id_set={chunk}')
			agents_list = agents.json()
			agents_dict = {}
			for agent_data in agents_list:
				agents_dict[agent_data['uri']] = agent_data
			data_dict['agents'] = {**data_dict['agents'], **agents_dict}

	return data_dict


def get_subjects(data_dict):
	subject_uris = []
	for _, ao in data_dict['archival_objects'].items():
		if len(ao['subjects']) > 0:
			for subject in ao['subjects']:
				if not subject['ref'] in subject_uris:
					subject_uris.append(subject['ref'].split('/')[-1])

	for _, r in data_dict['resources'].items():
		if len(r['subjects']) > 0:
			for subject in r['subjects']:
				if not subject['ref'] in subject_uris:
					subject_uris.append(subject['ref'].split('/')[-1])

	for _, a in data_dict['accessions'].items():
		if len(a['subjects']) > 0:
			for subject in a['subjects']:
				if not subject['ref'] in subject_uris:
					subject_uris.append(subject['ref'].split('/')[-1])


	chunks = chunk_ids(subject_uris)
	for chunk in chunks:
		subjects = aspace.client.get(f'/subjects?id_set={chunk}')
		subjects_list = subjects.json()
		subjects_dict = {}
		for subject_data in subjects_list:
			subjects_dict[subject_data['uri']] = subject_data
		data_dict['subjects'] = {**data_dict['subjects'], **subjects_dict}

	return data_dict


def get_top_containers(data_dict):
	top_container_uris = []
	for _, ao in data_dict['archival_objects'].items():
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
			tcs_list = tcs.json()
			tcs_dict = {}
			for tc_data in tcs_list:
				tcs_dict[tc_data['uri']] = tc_data
			data_dict['top_containers'] = {**data_dict['top_containers'], **tcs_dict}

	return data_dict


def get_extract(list_of_repos):
	data_dict = init_data_dict()
	data_dict = get_digital_objects_by_repo(list_of_repos, data_dict)
	data_dict = get_parent_objects(data_dict)
	data_dict = get_series(data_dict)
	data_dict = get_resources(data_dict)
	data_dict = get_agents(data_dict)
	data_dict = get_subjects(data_dict)
	data_dict = get_top_containers(data_dict)
	return data_dict
