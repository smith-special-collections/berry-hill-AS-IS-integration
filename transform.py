MAPPING = {
    'title': {                       # The name of the field as will appear in the template context
        'transform_function': 'title', # The name of the function that will generate the field contents
        'required': True               # If the field doesn't exist, the record can't be made
    },
    'digital_object_id': {
        'transform_function': 'digital_object_id',
        'required': True
    },
    'digital_object_uri': {
        'transform_function': 'digital_object_uri',
        'required': True
    },
    'archival_object_uri': {
        'transform_function': 'archival_object_uri',
        'required': True
    },
    'archival_object_ref': {
        'transform_function': 'archival_object_ref',
        'required': True
    },
    'resource_uri': {
        'transform_function': 'resource_uri',
        'required': True
    },
    'resource_title': {
        'transform_function': 'resource_title',
        'required': True
    },
    'resource_ms_no': {
        'transform_function': 'resource_ms_no',
        'required': True
    },
    'subjects': {
        'transform_function': 'subjects',
        'required': False
    },
    'agents': {
        'transform_function': 'agents',
        'required': False
    },
    'extent': {
        'transform_function': 'extent',
        'required': False
    }
}

class Transforms():
    """The Transforms class contains the set of methods referred to in the
    mapping above in the "transform_function" variable of each mapping. The
    transform always takes the full extracted data data structure, and the
    digital object id of the digital object record of the record currently
    being processed. The transform function returns the value that will be
    saved to the template_context data structure.
    """

    def title(self, EXTRACTED_DATA, do_id):
        return EXTRACTED_DATA['digital_objects'][do_id]['title']


    def digital_object_id(self, EXTRACTED_DATA, do_id):
        return do_id


    def digital_object_uri(self, EXTRACTED_DATA, do_id):
        return EXTRACTED_DATA['digital_objects'][do_id]['uri']


    def archival_object_uri(self, EXTRACTED_DATA, do_id):
        do = EXTRACTED_DATA['digital_objects'][do_id]
        parent_uri = do['linked_instances'][0]['ref']
        for uri, ao in EXTRACTED_DATA['archival_objects'].items():
            if uri == parent_uri:
                ao_uri = ao['uri']
                return ao_uri


    def archival_object_ref(self, EXTRACTED_DATA, do_id):
        ao_uri = self.archival_object_uri(EXTRACTED_DATA, do_id)
        if ao_uri != None:
            ao = EXTRACTED_DATA['archival_objects'][ao_uri]
            ao_ref = ao['ref_id']
            return ao_ref


    def resource_uri(self, EXTRACTED_DATA, do_id):
        ao_uri = self.archival_object_uri(EXTRACTED_DATA, do_id)
        if ao_uri != None:
            ao = EXTRACTED_DATA['archival_objects'][ao_uri]
            resource_uri = ao['resource']['ref']
            return resource_uri

    
    def resource_title(self, EXTRACTED_DATA, do_id):
        resource_uri = self.resource_uri(EXTRACTED_DATA, do_id)
        if resource_uri != None:
            resource = EXTRACTED_DATA['resources'][resource_uri]
            return resource['title']

    
    def resource_ms_no(self, EXTRACTED_DATA, do_id):
        resource_uri = self.resource_uri(EXTRACTED_DATA, do_id)
        if resource_uri != None:
            resource = EXTRACTED_DATA['resources'][resource_uri]
            ms_no = resource['id_1'] + ' ' + resource['id_2']
            return ms_no


    def subjects(self, EXTRACTED_DATA, do_id):
        subjects = []
        ao_uri = self.archival_object_uri(EXTRACTED_DATA, do_id)
        if ao_uri != None:
            ao = EXTRACTED_DATA['archival_objects'][ao_uri]
            if len(ao['subjects']) > 0:
                for subject in ao['subjects']:
                    sub_uri = subject['ref']
                    if EXTRACTED_DATA['subjects'][sub_uri] not in subjects:
                        subjects.append(EXTRACTED_DATA['subjects'][sub_uri])

        return subjects


    def set_mods_agent_type(self, agent_data):
        if agent_data['jsonmodel_type'] == 'agent_person':
            agent_data['jsonmodel_type'] = 'personal'
        elif agent_data['jsonmodel_type'] == 'agent_corporate_entity':
            agent_data['jsonmodel_type'] = 'corporate'
        elif agent_data['jsonmodel_type'] == 'agent_family':
            agent_data['jsonmodel_type'] = 'family'

        return agent_data


    def agents(self, EXTRACTED_DATA, do_id):
        agents = []
        ao_uri = self.archival_object_uri(EXTRACTED_DATA, do_id)
        resource_uri = self.resource_uri(EXTRACTED_DATA, do_id)
        if ao_uri != None:
            ao = EXTRACTED_DATA['archival_objects'][ao_uri]
            if len(ao['linked_agents']) > 0:
                for agent in ao['linked_agents']:
                    agent_dict = {}
                    agent_dict['role'] = agent['role']
                    agent_uri = agent['ref']
                    agent_dict['agent_data'] = self.set_mods_agent_type(EXTRACTED_DATA['agents'][agent_uri])
                    agents.append(agent_dict)
        if resource_uri != None:
            resource = EXTRACTED_DATA['resources'][resource_uri]
            if len(resource['linked_agents']) > 0:
                for agent in resource['linked_agents']:
                    if agent['role'] != 'subject':
                        agent_dict = {}
                        agent_dict['role'] = agent['role']
                        agent_uri = agent['ref']
                        agent_dict['agent_data'] = self.set_mods_agent_type(EXTRACTED_DATA['agents'][agent_uri])
                        agents.append(agent_dict)
        
        return agents


    def extent(self, EXTRACTED_DATA, do_id):
        ao_uri = self.archival_object_uri(EXTRACTED_DATA, do_id)
        if ao_uri != None:
            ao = EXTRACTED_DATA['archival_objects'][ao_uri]
            if len(ao['extents']) > 0:
                return ao['extents'][0]







