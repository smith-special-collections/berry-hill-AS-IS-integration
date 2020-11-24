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
    'genre_subjects': {
        'transform_function': 'genre_subjects',
        'required': False
    },
    'agents': {
        'transform_function': 'agents',
        'required': False
    },
    'extent': {
        'transform_function': 'extent',
        'required': False
    },
    'abstract': {
        'transform_function': 'abstract',
        'required': False
    },
    'userestrict': {
        'transform_function': 'userestrict',
        'required': False
    },
    'accessrestrict': {
        'transform_function': 'accessrestrict',
        'required': False
    },
    'language': {
        'transform_function': 'language',
        'required': False
    },
    'dates': {
        'transform_function': 'dates',
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

    
    def archival_object(self, EXTRACTED_DATA, do_id):
        ao_uri = self.archival_object_uri(EXTRACTED_DATA, do_id)
        if ao_uri != None:
            return EXTRACTED_DATA['archival_objects'][ao_uri]


    def archival_object_ref(self, EXTRACTED_DATA, do_id):
        ao = self.archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            ao_ref = ao['ref_id']
            return ao_ref


    def resource_uri(self, EXTRACTED_DATA, do_id):
        ao_uri = self.archival_object_uri(EXTRACTED_DATA, do_id)
        if ao_uri != None:
            ao = EXTRACTED_DATA['archival_objects'][ao_uri]
            resource_uri = ao['resource']['ref']
            return resource_uri
  
    
    def resource(self, EXTRACTED_DATA, do_id):
        resource_uri = self.resource_uri(EXTRACTED_DATA, do_id)
        if resource_uri != None:
            return EXTRACTED_DATA['resources'][resource_uri]

    
    def resource_title(self, EXTRACTED_DATA, do_id):
        resource = self.resource(EXTRACTED_DATA, do_id)
        if resource != None:
            return resource['title']

    
    def resource_ms_no(self, EXTRACTED_DATA, do_id):
        resource = self.resource(EXTRACTED_DATA, do_id)
        if resource != None:
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


    def genre_subjects(self, EXTRACTED_DATA, do_id):
        subjects = self.subjects(EXTRACTED_DATA, do_id)
        genre_subjects = []
        for sub in subjects:
            for term in sub['terms']:
                if term['type'] == 'genre_form':
                    if sub not in genre_subjects:
                        genre_subjects.append(sub)

        return genre_subjects


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
        ao = self.archival_object(EXTRACTED_DATA, do_id)
        resource = self.resource(EXTRACTED_DATA, do_id)
        if ao != None:
            # Get agents from archival object
            if len(ao['linked_agents']) > 0:
                for agent in ao['linked_agents']:
                    agent_dict = {}
                    agent_dict['role'] = agent['role']
                    agent_uri = agent['ref']
                    agent_dict['agent_data'] = self.set_mods_agent_type(EXTRACTED_DATA['agents'][agent_uri])
                    agents.append(agent_dict)
        if resource != None:
            # Get agents from resource
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
        ao = self.archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['extents']) > 0:
                return ao['extents'][0]


    def notes(self, EXTRACTED_DATA, do_id, note_type):
        n = None
        ao = self.archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['notes']) > 0:
                for note in ao['notes']:
                     if note['type'] == note_type:
                        if note['publish'] == True:
                            n = note['subnotes'][0]['content']
        if n == None:
            resource = self.resource(EXTRACTED_DATA, do_id)
            if resource != None:
                if len(resource['notes']) > 0:
                    for note in resource['notes']:
                        if note['publish'] == True:
                            if note['type'] == note_type:
                                n = note['subnotes'][0]['content']

        return n

     
    def abstract(self, EXTRACTED_DATA, do_id):
        abstract = self.notes(EXTRACTED_DATA, do_id, 'scopecontent')
        return abstract


    def userestrict(self, EXTRACTED_DATA, do_id):
        userestrict = self.notes(EXTRACTED_DATA, do_id, 'userestrict')
        return userestrict


    def accessrestrict(self, EXTRACTED_DATA, do_id):
        accessrestrict = self.notes(EXTRACTED_DATA, do_id, 'accessrestrict')
        return accessrestrict 


    def language(self, EXTRACTED_DATA, do_id):
        langs = []
        ao = self.archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['lang_materials']) > 0:
                for lang in ao['lang_materials']:
                    try:
                        langs.append(lang['language_and_script']['language'])
                    except KeyError:
                        continue
        if len(langs) == 0:
            resource = self.resource(EXTRACTED_DATA, do_id)
            if resource != None:
                if len(resource['lang_materials']) > 0:
                    for lang in resource['lang_materials']:
                        try:
                            langs.append(lang['language_and_script']['language'])
                        except KeyError:
                            continue
        return langs


    def dates(self, EXTRACTED_DATA, do_id):
        dates = None
        ao = self.archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['dates']) > 0:
                dates = ao['dates']
        if dates == None:
            resource = self.resource(EXTRACTED_DATA, do_id)
            if resource != None:
                if len(resource['dates']) > 0:
                    resource['dates']['certainty'] = 'approximate'
                    dates = resource['dates']
        return dates



