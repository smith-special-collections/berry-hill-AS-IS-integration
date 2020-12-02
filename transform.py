from copy import deepcopy
import re
import html
from pprint import pprint as pp

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
        'transform_function': 'subjects_with_genre_forms_removed',
        'required': False
    },
    'genre_subjects': {
        'transform_function': 'genre_subjects',
        'required': False
    },
    'creator_agents': {
        'transform_function': 'creator_agents',
        'required': False
    },
    'donor_agents': {
        'transform_function': 'donor_agents',
        'required': False
    },
    'subject_agents': {
        'transform_function': 'subject_agents',
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
    'arrangement': {
        'transform_function': 'arrangement',
        'required': False
    },
    'arrangement_items': {
        'transform_function': 'arrangement_items',
        'required': False
    },
    'general_notes': {
        'transform_function': 'general_notes',
        'required': False
    },
    'language': {
        'transform_function': 'language',
        'required': False
    },
    'dates': {
        'transform_function': 'dates',
        'required': False
    },
    'repository': {
        'transform_function': 'repository',
        'required': False
    },
    'resource_location': {
        'transform_function': 'resource_location',
        'required': False
    },
    'archival_object_location': {
        'transform_function': 'archival_object_location',
        'required': False
    },
    'folder_number': {
        'transform_function': 'folder_number',
        'required': False
    },
    'top_container': {
        'transform_function': 'top_container',
        'required': False
    },
    'excerpts': {
        'transform_function': 'excerpts',
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
        title = EXTRACTED_DATA['digital_objects'][do_id]['title']
        return title


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

    
    def _archival_object(self, EXTRACTED_DATA, do_id):
        '''Helper function that returns archival object record from EXTRACTED_DATA'''
        ao_uri = self.archival_object_uri(EXTRACTED_DATA, do_id)
        if ao_uri != None:
            # The digital object might not be attached to an archival object
            # Wherever ao_uri != None, this might be the case
            return deepcopy(EXTRACTED_DATA['archival_objects'][ao_uri])


    def archival_object_ref(self, EXTRACTED_DATA, do_id):
        ao = self._archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            ao_ref = ao['ref_id']
            return ao_ref


    def resource_uri(self, EXTRACTED_DATA, do_id):
        ao_uri = self.archival_object_uri(EXTRACTED_DATA, do_id)
        if ao_uri != None:
            ao = EXTRACTED_DATA['archival_objects'][ao_uri]
            resource_uri = ao['resource']['ref']
            return resource_uri
  
    
    def _resource(self, EXTRACTED_DATA, do_id):
        '''Helper function that returns resource record from EXTRACTED_DATA'''
        resource_uri = self.resource_uri(EXTRACTED_DATA, do_id)
        if resource_uri != None:
            return deepcopy(EXTRACTED_DATA['resources'][resource_uri])

    
    def resource_title(self, EXTRACTED_DATA, do_id):
        resource = self._resource(EXTRACTED_DATA, do_id)
        if resource != None:
            # There might not be a resource to which the digital object is related
            # Wherever 'resource != None', this is the case
            return resource['title']

    
    def resource_ms_no(self, EXTRACTED_DATA, do_id):
        resource = self._resource(EXTRACTED_DATA, do_id)
        if resource != None:
            ms_no = resource['id_0'] + ' ' + resource['id_1'] + ' ' + resource['id_2']
            return ms_no


    def subjects_with_genre_forms_removed(self, EXTRACTED_DATA, do_id):
        '''F to remove genre subjects from subject data so they do not get templated incorrectly'''
        subjects = self._subjects(EXTRACTED_DATA, do_id)
        cleaned_subjects = []
        if len(subjects) > 0:
            for sub in subjects:
                for term in sub['terms']:
                    if term['term_type'] == 'genre_form':
                        continue
                    else:
                        if sub not in cleaned_subjects:
                            cleaned_subjects.append(sub)
        if len(cleaned_subjects) == 0:
            return None
        else:
            return cleaned_subjects


    def _subjects(self, EXTRACTED_DATA, do_id):
        '''A helper function to get all the subjects at the archival object level; logic based on rules of inheritance: 
        https://github.com/smith-special-collections/sc-documentation/wiki/Rules-for-description-inheritance-for-digital-object-records'''
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
        subjects = self._subjects(EXTRACTED_DATA, do_id)
        genre_subjects = []
        if len(subjects) > 0:
            for sub in subjects:
                for term in sub['terms']:
                    if term['term_type'] == 'genre_form':
                        if sub not in genre_subjects:
                            genre_subjects.append(sub)

        if len(genre_subjects) == 0:
            return None
        else:
            return genre_subjects


    def remap_mods_agent_type(self, agent_data):
        '''Remaps jsonmodel_type to mods agent type in deepcopy'''
        if agent_data['jsonmodel_type'] == 'agent_person':
            agent_data['jsonmodel_type'] = 'personal'
        elif agent_data['jsonmodel_type'] == 'agent_corporate_entity':
            agent_data['jsonmodel_type'] = 'corporate'
        elif agent_data['jsonmodel_type'] == 'agent_family':
            agent_data['jsonmodel_type'] = 'family'

        return agent_data


    def agents(self, EXTRACTED_DATA, do_id):
        '''Logic based on rules of inheritance: 
        https://github.com/smith-special-collections/sc-documentation/wiki/Rules-for-description-inheritance-for-digital-object-records'''
        agents = []
        ao = self._archival_object(EXTRACTED_DATA, do_id)
        resource = self._resource(EXTRACTED_DATA, do_id)
        if ao != None:
            # Get agents from archival object
            if len(ao['linked_agents']) > 0:
                for agent in ao['linked_agents']:
                    agent_dict = {}
                    agent_dict['role'] = agent['role']
                    agent_uri = agent['ref']
                    agent_dict['agent_data'] = self.remap_mods_agent_type(deepcopy(EXTRACTED_DATA['agents'][agent_uri]))
                    agents.append(agent_dict)
        if resource != None:
            # Get agents from resource
            if len(resource['linked_agents']) > 0:
                for agent in resource['linked_agents']:
                    if agent['role'] != 'subject':
                        agent_dict = {}
                        agent_dict['role'] = agent['role']
                        agent_uri = agent['ref']
                        agent_dict['agent_data'] = self.remap_mods_agent_type(deepcopy(EXTRACTED_DATA['agents'][agent_uri]))
                        agents.append(agent_dict)
        
        agents = [i for n, i in enumerate(agents) if i not in agents[n + 1:]]
        pp(agents)
        pp(len(agents))
        return agents


    def subject_agents(self, EXTRACTED_DATA, do_id):
        subject_agents = []
        agents = self.agents(EXTRACTED_DATA, do_id)
        if len(agents) > 0:
            for agent in agents:
                if agent['role'] == 'subject':
                    subject_agents.append(agent)
        # print(subject_agents)
        if len(subject_agents) == 0:
            return None
        else:
            return subject_agents


    def donor_agents(self, EXTRACTED_DATA, do_id):
        donor_agents = []
        agents = self.agents(EXTRACTED_DATA, do_id)
        if len(agents) > 0:
            for agent in agents:
                if agent['role'] == 'source':
                    donor_agents.append(agent)
        if len(donor_agents) == 0:
            return None
        else:
            return donor_agents


    def creator_agents(self, EXTRACTED_DATA, do_id):
        creator_agents = []
        agents = self.agents(EXTRACTED_DATA, do_id)
        if len(agents) > 0:
            for agent in agents:
                if agent['role'] == 'creator':
                    creator_agents.append(agent)
        if len(creator_agents) == 0:
            return None
        else:
            return creator_agents


    def extent(self, EXTRACTED_DATA, do_id):
        ao = self._archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['extents']) > 0:
                return ao['extents'][0]


    def remove_EAD_tags(self, note):
        '''Helper function to remove HTML entities from note content'''
        regex = '(<.*?>)'
        try:
            chars_to_remove = re.findall(regex, note)
            if len(chars_to_remove) > 0:
                for char in chars_to_remove:
                    note = html.unescape(note)
                    note = note.replace(char, '')
                    note = html.escape(note)
            return note      
        except Exception as e:  
            print(e)
            return note


    def notes(self, EXTRACTED_DATA, do_id, note_type):
        '''Logic based on rules of inheritance: 
        https://github.com/smith-special-collections/sc-documentation/wiki/Rules-for-description-inheritance-for-digital-object-records'''
        notes_lst = []
        ao = self._archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['notes']) > 0:
                for note in ao['notes']:
                     if note['type'] == note_type:
                        if note['publish'] == True:
                            notes_lst.append(self.remove_EAD_tags(note['subnotes'][0]['content']))
        if len(notes_lst) == 0:
            # If there are not any notes at the archival object level, search at the resource level
            resource = self._resource(EXTRACTED_DATA, do_id)
            if resource != None:
                if len(resource['notes']) > 0:
                    for note in resource['notes']:
                        if note['publish'] == True:
                            if note['type'] == note_type:
                                notes_lst.append(self.remove_EAD_tags(note['subnotes'][0]['content']))
        return notes_lst


    def abstract(self, EXTRACTED_DATA, do_id):
        abstract = self.notes(EXTRACTED_DATA, do_id, 'scopecontent')
        return abstract


    def userestrict(self, EXTRACTED_DATA, do_id):
        userestrict = self.notes(EXTRACTED_DATA, do_id, 'userestrict')
        return userestrict


    def accessrestrict(self, EXTRACTED_DATA, do_id):
        accessrestrict = self.notes(EXTRACTED_DATA, do_id, 'accessrestrict')
        return accessrestrict 


    def arrangement(self, EXTRACTED_DATA, do_id):
        '''Returns arrangement note'''
        arrangement = []
        ao = self._archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['notes']) > 0:
                for note in ao['notes']:
                    if note['type'] == 'arrangement':
                        arrangement.append(note['subnotes']) # Fix this to ensure more than one arrangement note

        # Creates a dictionary of components from the arrangement note if there is one that is then passed to self.arrangement_items
        if len(arrangement) > 0:
            arrangement_dict = {}
            arrangement_dict['content'] = []
            arrangement_dict['items'] = []
            for a in arrangement:
                arrangement_dict['content'].append(a['content'])
            try:
                for item in a['items']:
                    arrangement_dict['items'].append(item)
            except KeyError:
                pass
            
            return arrangement_dict
        
        else:
            return None


    def arrangement_items(self, EXTRACTED_DATA, do_id):
        arrangement = self.arrangement(EXTRACTED_DATA, do_id)
        if isinstance(arrangement, dict):
            if len(arrangement['items']) > 0:
                return arrangement['items']
            else:
                return None


    def general_notes(self, EXTRACTED_DATA, do_id):
        general_notes = []
        ao = self._archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['notes']) > 0:
                for note in ao['notes']:
                    if note['type'] == 'odd':
                        # Odd is the term_type for general notes
                        if note['publish'] == True:
                            general_notes.append(note['subnotes'][0])
       
        if len(general_notes) == 0:
            return None
        else:
            return general_notes


    def language(self, EXTRACTED_DATA, do_id):
        '''Logic based on rules of inheritance: 
        https://github.com/smith-special-collections/sc-documentation/wiki/Rules-for-description-inheritance-for-digital-object-records'''
        langs = []
        ao = self._archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['lang_materials']) > 0:
                for lang in ao['lang_materials']:
                    try:
                        langs.append(lang['language_and_script']['language'])
                    except KeyError:
                        pass
                    except Exception as e:
                        print(e)
            if len(langs) == 0:
                resource = self._resource(EXTRACTED_DATA, do_id)
                if resource != None:
                    if len(resource['lang_materials']) > 0:
                        for lang in resource['lang_materials']:
                            try:
                                langs.append(lang['language_and_script']['language'])
                            except KeyError:
                                pass
                            except Exception as e:
                                print(e)

        if len(langs) == 0:
            return None
        else: 
            return langs


    def dates(self, EXTRACTED_DATA, do_id):
        '''Logic based on rules of inheritance: 
        https://github.com/smith-special-collections/sc-documentation/wiki/Rules-for-description-inheritance-for-digital-object-records'''
        dates = None
        ao = self._archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['dates']) > 0:
                # Dates returned as strings
                dates = ao['dates']
        if dates == None:
            resource = self._resource(EXTRACTED_DATA, do_id)
            if resource != None:
                if len(resource['dates']) > 0:
                    resource['dates'][0]['certainty'] = 'approximate'
                    dates = resource['dates']
        return dates


    def repository(self, EXTRACTED_DATA, do_id):
        repo = None
        do_uri = self.digital_object_uri(EXTRACTED_DATA, do_id)
        repo_num = do_uri.split('/')[2]
        try: 
            repo = EXTRACTED_DATA['repositories'][repo_num]
            return repo
        except KeyError:
            return repo


    def resource_location(self, EXTRACTED_DATA, do_id):
        resource_uri = self.resource_uri(EXTRACTED_DATA, do_id)
        if resource_uri != None:
            finding_aid_url = EXTRACTED_DATA['url_stem'] + resource_uri
            return finding_aid_url
        else:
            return None


    def archival_object_location(self, EXTRACTED_DATA, do_id):
        ao_uri = self.archival_object_uri(EXTRACTED_DATA, do_id)
        if ao_uri != None:
            finding_aid_url = 'https://findingaids.smith.edu' + ao_uri
            return finding_aid_url
        else:
            return None


    def folder_number(self, EXTRACTED_DATA, do_id):
        ao = self._archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            try:
                fol = ao['instances'][0]['sub_container']['type_2'].capitalize()
                num = ao['instances'][0]['sub_container']['indicator_2']
                return fol + ' ' + num
            except KeyError:
                return None
        else:
            return None


    def top_container(self, EXTRACTED_DATA, do_id):
        top_container_string = None
        ao = self._archival_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['instances']) > 0:
                for instance in ao['instances']:
                    if 'sub_container' in instance.keys():
                        top_container_uri = instance['sub_container']['top_container']['ref']
                        top_container = EXTRACTED_DATA['top_containers'][top_container_uri]
                        top_container_string = top_container['display_string']
        return top_container_string


    def excerpts(self, EXTRACTED_DATA, do_id):
        '''Function to determine if (Excerpts) should be appended to title''' 
        processinfo = self.notes(EXTRACTED_DATA, do_id, 'processinfo')
        if processinfo != None:
            for p in processinfo:
                if 'select material' in p:
                    excerpts = ' (Excerpts)'
                    return excerpts


