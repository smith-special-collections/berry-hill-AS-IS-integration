from asnake.aspace import ASpace
from pprint import pprint as pp
import logging
import time
import json


def macro_setup(aspace, repo_agent, repo, resource):
    'Creates Repository, Repository Agent, and Resource for testing as well as adds enum values'
    uri_dict = {}
    try:
        repo_agent_post = aspace.client.post('/agents/corporate_entities', json=repo_agent)
        repo_agent_uri = repo_agent_post.json()['uri']
        repo['agent_representation']['ref'] = repo_agent_uri
        uri_dict['repo_agent_uri'] = repo_agent_uri
        try:
            repo_post = aspace.client.post('/repositories', json=repo)
            repo_uri = repo_post.json()['uri']
            uri_dict['repo_uri'] = repo_uri
            logging.info('Test Repository created')  
        except KeyError:
            logging.error('Failure to create Repository')
            pp(repo_post.json())
            exit()
    except KeyError:
        logging.error('Failure to create Repository Agent')
        pp(repo_agent_post.json())
        exit()

    # Create resource
    try:
        resource_post = aspace.client.post(uri_dict['repo_uri'] + '/resources', json=resource)
        resource_uri = resource_post.json()['uri']
        uri_dict['resource_uri'] = resource_uri
        logging.info('Resource created')
    except KeyError:
        logging.error('Failure to create Resource')
        pp(resource_post.json())
        exit()

    enumeration = aspace.client.get('/config/enumerations/4').json()
    enumeration['values'].append('lcsh')
    enumeration_post = aspace.client.post(f'/config/enumerations/4', json=enumeration)

    enumeration = aspace.client.get(f'/config/enumerations/23').json()
    enumeration['values'].append('homosaurus')
    enumeration_post = aspace.client.post('/config/enumerations/23', json=enumeration)
    # pp(uri_dict)
    return uri_dict


def micro_setup(aspace, uri_dict, archival_object, digital_object, agents, subjects, top_container):
    'Creates Archival Object record and associated records for testing'

    # Create do
    try:
        digital_object_post = aspace.client.post(uri_dict['repo_uri'] + '/digital_objects', json=digital_object)
        digital_object_uri = digital_object_post.json()['uri']
        uri_dict['do_uri'] = digital_object_uri
        logging.info('Digital Object created')
    except KeyError:
        logging.error('Failure to create Digital Object')
        pp(digital_object_post.json())
        exit()
    
    # Create top container
    try:
        top_container_post = aspace.client.post(uri_dict['repo_uri'] + '/top_containers', json=top_container)
        top_container_uri = top_container_post.json()['uri']
        uri_dict['tc_uri'] = top_container_uri
        logging.info('Top Container created')
    except KeyError:
        logging.error('Failure to create Top Container')
        pp(top_container_post.json())
        exit()

    # Create agents
    uri_dict['agent_uris'] = []
    for agent in agents:
        if agent['jsonmodel_type'] == 'agent_corporate_entity':
            try:
                agent_post = aspace.client.post('/agents/corporate_entities', json=agent)
                agent_uri = agent_post.json()['uri']
                uri_dict['agent_uris'].append(agent_uri)
                logging.info('Agent Corporate Entity created')
            except KeyError:
                logging.error('Failure to create Agent Corporate Entity')
                pp(agent_post.json())
                exit()
        elif agent['jsonmodel_type'] == 'agent_person':
            try:
                agent_post = aspace.client.post('/agents/people', json=agent)
                agent_uri = agent_post.json()['uri']
                uri_dict['agent_uris'].append(agent_uri)
                logging.info('Agent Person created')
            except KeyError:
                logging.error('Failure to create Agent Person')
                pp(agent_post.json())
                exit()                
        elif agent['jsonmodel_type'] == 'agent_family':
            try:
                agent_post = aspace.client.post('/agents/families', json=agent)
                agent_uri = agent_post.json()['uri']
                uri_dict['agent_uris'].append(agent_uri)
                logging.info('Agent Family created')
            except KeyError:    
                logging.error('Failure to create Agent Corporate Entity')
                pp(agent_post.json())
                exit()

    # Create subjects
    uri_dict['subject_uris'] = []
    for subject in subjects:
        try:
            subject_post = aspace.client.post('/subjects', json=subject)
            subject_uri = subject_post.json()['uri']
            uri_dict['subject_uris'].append(subject_uri)
            logging.info('Subject created')
        except KeyError:
            logging.error('Failure to create Subject')
            pp(subject_post.json())
            exit()

    # Create ao
    agent_roles = ['source', 'creator', 'subject']
    archival_object['instances'][0]['sub_container']['top_container']['ref'] = top_container_uri
    archival_object['instances'][1]['digital_object']['ref'] = digital_object_uri
    for agent_uri in uri_dict['agent_uris']:
        linked_agent = {'ref': agent_uri, 'role': agent_roles[-1], 'terms': []}
        archival_object['linked_agents'].append(linked_agent)
        agent_roles.pop()
    for subject_uri in uri_dict['subject_uris']:
        linked_subject = {'ref': subject_uri}
        archival_object['subjects'].append(linked_subject)
    archival_object['resource']['ref'] = uri_dict['resource_uri']
    try:
        archival_object_post = aspace.client.post(uri_dict['repo_uri'] + '/archival_objects', json=archival_object)
        archival_object_uri = archival_object_post.json()['uri']
        uri_dict['ao_uri'] = archival_object_uri
        logging.info('Archival Object created')
    except KeyError:
        logging.error('Failure to create Archival Object')
        pp(archival_object_post.json())
        exit()
    # pp(uri_dict)
    return uri_dict


def micro_teardown(aspace, uri_dict):
    for k,v in uri_dict.items():
        if not 'repo' in k:
            if type(v) is list:
                for i in v:
                    aspace.client.delete(i)
                    logging.info('{} deleted'.format(i))
            else:
                aspace.client.delete(v)
                logging.info('{} deleted'.format(v))


def macro_teardown(aspace, uri_dict):
    aspace.client.delete(uri_dict['repo_uri'])
    logging.info('{} deleted'.format(uri_dict['repo_uri']))
    aspace.client.delete(uri_dict['repo_agent_uri'])
    logging.info('{} deleted'.format(uri_dict['repo_agent_uri']))



