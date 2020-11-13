MAPPING = {
    'title': {                       # The name of the field as will appear in the template context
        'transform_function': 'title', # The name of the function that will generate the field contents
        'required': True               # If the field doesn't exist, the record can't be made
    },
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
