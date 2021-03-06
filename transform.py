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
    'component_uri': {
        'transform_function': 'component_uri',
        'required': False
    },
    'archival_object_ref': {
        'transform_function': 'archival_object_ref',
        'required': False
    },
    'resource_uri': {
        'transform_function': 'resource_uri',
        'required': False
    },
    'resource_title': {
        'transform_function': 'resource_title',
        'required': False
    },
    'resource_ms_no': {
        'transform_function': 'resource_ms_no',
        'required': False
    },
    'subjects': {
        'transform_function': 'subjects_with_genre_forms_removed',
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
    'physdesc': {
        'transform_function': 'physdesc',
        'required': False,
    },
    'arrangement': {
        'transform_function': 'arrangement',
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
        title = self.remove_EAD_tags(EXTRACTED_DATA['digital_objects'][do_id]['title'])
        return title


    def digital_object_id(self, EXTRACTED_DATA, do_id):
        return do_id


    def digital_object_uri(self, EXTRACTED_DATA, do_id):
        return EXTRACTED_DATA['digital_objects'][do_id]['uri']


    def component_uri(self, EXTRACTED_DATA, do_id):
        component_uri = None
        do = EXTRACTED_DATA['digital_objects'][do_id]
        parent_uri = do['linked_instances'][0]['ref']
        for uri, ao in EXTRACTED_DATA['archival_objects'].items():
            if uri == parent_uri:
                component_uri = ao['uri']
        if component_uri == None:
            component_uri = self._accession_or_resource_parent_uri(EXTRACTED_DATA, do_id)
        
        return component_uri

    
    def _component_object(self, EXTRACTED_DATA, do_id):
        '''Helper function that returns archival object or parent record from EXTRACTED_DATA'''
        uri = self.component_uri(EXTRACTED_DATA, do_id)
        parent = None
        if uri != None:
            # The digital object might not be attached to an archival object
            # Wherever ao_uri != None, this might be the case
            if 'archival_objects' in uri:               
                parent = deepcopy(EXTRACTED_DATA['archival_objects'][uri])
            elif 'accessions' in uri:
                parent = deepcopy(EXTRACTED_DATA['accessions'][uri])
            elif 'resources' in uri:
                parent = deepcopy(EXTRACTED_DATA['resources'][uri])
        
        return parent


    def _subseries(self, EXTRACTED_DATA, do_id):
        '''Helper function to get subseries if there is one from EXTRACTED_Data'''
        component_object = self._component_object(EXTRACTED_DATA, do_id)
        if 'archival_objects' in component_object['uri']:
            if 'parent' in component_object.keys():
                try:
                    subseries = EXTRACTED_DATA['subseries'][component_object['parent']['ref']]
                    return subseries
                except KeyError:
                    return None


    def _series(self, EXTRACTED_DATA, do_id):
        '''Helper function to get series if there is one from EXTRACTED_DATA'''
        component_object = self._component_object(EXTRACTED_DATA, do_id)
        if 'archival_objects' in component_object['uri']:
            if 'parent' in component_object.keys():
                try:
                    series = EXTRACTED_DATA['series'][component_object['parent']['ref']]
                    return series
                except KeyError:
                    try:
                        subseries = self._subseries(EXTRACTED_DATA, do_id)
                        if 'parent' in subseries.keys():
                            try:
                                series = EXTRACTED_DATA['series'][subseries['parent']['ref']]
                                return series
                            except AttributeError:
                                return None
                    except AttributeError:
                        return None


    def _accession_or_resource_parent_uri(self, EXTRACTED_DATA, do_id):
        '''Helper function that checks for digital objects linked to accessions or resources'''
        do = EXTRACTED_DATA['digital_objects'][do_id]
        parent_uri = do['linked_instances'][0]['ref']
        component_uri = None
        for uri, acc in EXTRACTED_DATA['accessions'].items():
            if uri == parent_uri:
                component_uri = acc['uri']
        if component_uri == None:
            for uri, r in EXTRACTED_DATA['resources'].items():
                if uri == parent_uri:
                    component_uri = r['uri']

        return component_uri      


    def archival_object_ref(self, EXTRACTED_DATA, do_id):
        obj_ref = None
        obj = self._component_object(EXTRACTED_DATA, do_id)
        if obj != None:
            if 'ref_id' in obj.keys():
                obj_ref = obj['ref_id']
        
        return obj_ref

    # Possibly make a list
    def resource_uri(self, EXTRACTED_DATA, do_id):
        uri = self.component_uri(EXTRACTED_DATA, do_id)
        resource_uri = None
        if uri != None:
            try:
                ao = EXTRACTED_DATA['archival_objects'][uri]
                resource_uri = ao['resource']['ref']
            except KeyError:
                r = EXTRACTED_DATA['resources'][uri]
                resource_uri = r['uri']
            except KeyError:
                a = EXTRACTED_DATA['accessions'][uri]
                resource_uri = a['related_resources'][0]['ref']
        
        return resource_uri
  
    
    def _resource(self, EXTRACTED_DATA, do_id):
        '''Helper function that returns resource record from EXTRACTED_DATA'''
        resource_uri = self.resource_uri(EXTRACTED_DATA, do_id)
        if resource_uri != None:
            return deepcopy(EXTRACTED_DATA['resources'][resource_uri])

    
    def resource_title(self, EXTRACTED_DATA, do_id):
        title = None
        resource = self._resource(EXTRACTED_DATA, do_id)
        if resource != None:
            # There might not be a resource to which the digital object is related
            # Wherever 'resource != None', this is the case
            title = resource['title']
            return title
        else:
            return None

    
    def resource_ms_no(self, EXTRACTED_DATA, do_id):
        resource = self._resource(EXTRACTED_DATA, do_id)
        if resource != None:
            ms_no = resource['id_0'] + ' ' + resource['id_1'] + ' ' + resource['id_2']
            return ms_no
        else:
            return None


    def subjects_with_genre_forms_removed(self, EXTRACTED_DATA, do_id):
        '''F to remove genre subjects from subject data so they do not get templated incorrectly'''
        subjects = self._subjects(EXTRACTED_DATA, do_id)
        cleaned_subjects = []
        genre_forms = []
        if len(subjects) > 0:
            for sub in subjects:
                for term in sub['terms']:
                    if term['term_type'] == 'genre_form':
                        genre_forms.append(sub)
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
        obj = self._component_object(EXTRACTED_DATA, do_id)
        if obj != None:
            if len(obj['subjects']) > 0:
                # pp(obj.keys())
                for subject in obj['subjects']:
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


    def _get_relator_id(self, relator):
        relator_id = relator['@id'].split('/')[-1]
        return relator_id


    def _get_relator_value(self, relator):
        try:
            relator_value = relator['http://www.loc.gov/mads/rdf/v1#authoritativeLabel'][0]['@value']
            return relator_value.lower()
        except KeyError:
            return None 


    def _make_relator_dict(self, EXTRACTED_DATA, do_id):
        '''Helper function that utilizes relator list from Library of Congress to parse correct relator ids and values'''

        relator_dict = {}
        if EXTRACTED_DATA['relators'] != None:
            for relator in EXTRACTED_DATA['relators']:
                relator_dict[self._get_relator_id(relator)] = self._get_relator_value(relator)

        return relator_dict 


    def agents(self, EXTRACTED_DATA, do_id):
        '''Logic based on rules of inheritance: 
        https://github.com/smith-special-collections/sc-documentation/wiki/Rules-for-description-inheritance-for-digital-object-records'''
        agents = []
        relator_dict = self._make_relator_dict(EXTRACTED_DATA, do_id)
        ao = self._component_object(EXTRACTED_DATA, do_id)
        resource = self._resource(EXTRACTED_DATA, do_id)
        if ao != None:
            # Get agents from archival object
            if len(ao['linked_agents']) > 0:
                for agent in ao['linked_agents']:
                    agent_dict = {}
                    agent_dict['role_value'] = ''
                    try:
                        agent_dict['role'] = agent['relator']
                    except KeyError:
                        if agent['role'] == 'source':
                            agent_dict['role'] = 'donor'
                        else:
                            agent_dict['role'] = agent['role']
                    agent_uri = agent['ref']
                    try:
                        agent_dict['agent_data'] = self.remap_mods_agent_type(deepcopy(EXTRACTED_DATA['agents'][agent_uri]))
                        agents.append(agent_dict)
                    except KeyError:
                        pass
        if resource != None:
            # Get agents from resource
            if len(resource['linked_agents']) > 0:
                for agent in resource['linked_agents']:
                    if agent['role'] != 'subject':
                        agent_dict = {}
                        agent_dict['role_value'] = ''
                        try:
                            agent_dict['role'] = agent['relator']
                        except KeyError:
                            if agent['role'] == 'source':
                                agent_dict['role'] = 'donor'
                            else:
                                agent_dict['role'] = agent['role']
                        agent_uri = agent['ref']
                        try:
                            agent_dict['agent_data'] = self.remap_mods_agent_type(deepcopy(EXTRACTED_DATA['agents'][agent_uri]))
                            agents.append(agent_dict)
                        except KeyError:
                            pass
        
        for k, v in relator_dict.items():
            for agent in agents:
                if k == agent['role']:
                    agent['role_value'] = v
                elif v == agent['role']:
                    agent['role_value'] = v
                    agent['role'] = k

        agents = [i for n, i in enumerate(agents) if i not in agents[n + 1:]]
        return agents


    def extent(self, EXTRACTED_DATA, do_id):
        ao = self._component_object(EXTRACTED_DATA, do_id)
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
        context_str = ''
        ao = self._component_object(EXTRACTED_DATA, do_id)
        if ao != None:
            ao_title = self.remove_EAD_tags(ao['title'])
        else:    
            ao_title = ''
        subseries = self._subseries(EXTRACTED_DATA, do_id)
        if subseries != None:
            subseries_title = self.remove_EAD_tags(subseries['title'])
        else:
            subseries_title = ''
        series = self._series(EXTRACTED_DATA, do_id)
        if series != None:
            series_title = self.remove_EAD_tags(series['title'])
        else:
            series_title = ''
        resource = self._resource(EXTRACTED_DATA, do_id)
        if resource != None:
            resource_title = self.remove_EAD_tags(resource['title'])
        else:
            resource_title = ''
        
        # pp(resource_title) 
        # pp(series_title)
        # pp(subseries_title)
        # pp(ao_title)
        
        if ao != None:
            if len(ao['notes']) > 0:
                for note in ao['notes']:
                    if 'type' in note.keys():
                        if note['type'] == note_type:
                            if note['publish'] == True:
                                try:
                                    cleaned_note = self.remove_EAD_tags(note['subnotes'][0]['content'])
                                    notes_lst.append(cleaned_note)
                                except KeyError:
                                    cleaned_note = self.remove_EAD_tags(note['content'])
                                    notes_lst.append(cleaned_note)
        
        # Check for subseries
        if len(notes_lst) == 0:
            if subseries != None:
                if len(subseries['notes']) > 0:
                    for note in subseries['notes']:
                        if note['publish'] == True:
                            if 'type' in note.keys():
                                if note['type'] == note_type:
                                    if note_type == 'scopecontent':
                                        try:
                                            context_str = f'This material can be found in the {resource_title}, {series_title}, {subseries_title}, {ao_title}.'
                                        except Exception as e:
                                            pp(e)
                                            context_str = ''
                                    pp(context_str)
                                    try:
                                        cleaned_note = self.remove_EAD_tags(note['subnotes'][0]['content'])
                                        if context_str == '':
                                            notes_lst.append(cleaned_note)
                                        else:
                                            notes_lst.append(context_str + ' ' + cleaned_note)
                                    except KeyError:
                                        cleaned_note = self.remove_EAD_tags(note['content'])
                                        if context_str == '':
                                            notes_lst.append(cleaned_note)
                                        else:
                                            notes_lst.append(context_str + ' ' + cleaned_note)

        if len(notes_lst) == 0:
            if series != None:
                if len(series['notes']) > 0:
                    for note in series['notes']:
                        if note['publish'] == True:
                            if 'type' in note.keys():
                                if note['type'] == note_type:
                                    if note_type == 'scopecontent':
                                        try:
                                            context_str = f'This material can be found in the {resource_title}, {series_title}, {ao_title}.'
                                        except Exception as e:
                                            pp(e)
                                            context_str = ''
                                    pp(context_str)
                                    try:
                                        cleaned_note = self.remove_EAD_tags(note['subnotes'][0]['content'])
                                        if context_str == '':
                                            notes_lst.append(cleaned_note)
                                        else:
                                            notes_lst.append(context_str + ' ' + cleaned_note)
                                    except KeyError:
                                        cleaned_note = self.remove_EAD_tags(note['content'])
                                        if context_str == '':
                                            notes_lst.append(cleaned_note)
                                        else:
                                            notes_lst.append(context_str + ' ' + cleaned_note)

        if len(notes_lst) == 0:
            # If there are not any notes at the archival object level or series level, search at the resource level
            if resource != None:
                if len(resource['notes']) > 0:
                    for note in resource['notes']:
                        if note['publish'] == True:
                            if 'type' in note.keys():
                                if note['type'] == note_type:
                                    if note_type == 'scopecontent':
                                        try:
                                            context_str = f'This material can be found in the {resource_title}, {ao_title}.'
                                        except Exception as e:
                                            pp(e)
                                            context_str = ''
                                    pp(context_str)
                                    try:
                                        cleaned_note = self.remove_EAD_tags(note['subnotes'][0]['content'])
                                        if context_str == '':
                                            notes_lst.append(cleaned_note)
                                        else:
                                            notes_lst.append(context_str + ' ' + cleaned_note)
                                    except KeyError:
                                        cleaned_note = self.remove_EAD_tags(note['content'])
                                        if context_str == '':
                                            notes_lst.append(cleaned_note)
                                        else:
                                            notes_lst.append(context_str + ' ' + cleaned_note)


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


    def physdesc(self, EXTRACTED_DATA, do_id):
        physdesc = self.notes(EXTRACTED_DATA, do_id, 'physdesc')
        return physdesc

    
    def arrangement(self, EXTRACTED_DATA, do_id):
        '''Helper function that returns arrangement note'''
        arrangement = []
        ao = self._component_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['notes']) > 0:
                for note in ao['notes']:
                    if note['type'] == 'arrangement':
                        arrangement.extend(note['subnotes'])
        
        for a in arrangement:
            if 'content' in a.keys():
                content = a['content']
                if content[-1] != ':':
                    content = content + ': '
                else:
                    content = content + ' '
            if 'items' in a.keys():
                items = a['items']
                if isinstance(items, list):
                    items = ', '.join(items)
        try:            
            arrangement = content + items
            return arrangement
        except Exception as e:
            return None


    def general_notes(self, EXTRACTED_DATA, do_id):
        general_notes = []
        ao = self._component_object(EXTRACTED_DATA, do_id)
        if ao != None:
            if len(ao['notes']) > 0:
                for note in ao['notes']:
                    if note['type'] == 'odd':
                        # Odd is the term_type for general notes
                        if note['publish'] == True:
                            general_notes.append(self.remove_EAD_tags(note['subnotes'][0]))
       
        if len(general_notes) == 0:
            return None
        else:
            return general_notes


    def language(self, EXTRACTED_DATA, do_id):
        '''Logic based on rules of inheritance: 
        https://github.com/smith-special-collections/sc-documentation/wiki/Rules-for-description-inheritance-for-digital-object-records'''
        langs = []
        ao = self._component_object(EXTRACTED_DATA, do_id)
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
        ao = self._component_object(EXTRACTED_DATA, do_id)
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
        ao_uri = self.component_uri(EXTRACTED_DATA, do_id)
        if ao_uri != None:
            finding_aid_url = 'https://findingaids.smith.edu' + ao_uri
            return finding_aid_url
        else:
            return None


    def folder_number(self, EXTRACTED_DATA, do_id):
        ao = self._component_object(EXTRACTED_DATA, do_id)
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
        ao = self._component_object(EXTRACTED_DATA, do_id)
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
        excerpts = None
        if processinfo != None:
            for p in processinfo:
                if 'select material' in p:
                    excerpts = ' (Excerpts)'
        return excerpts


