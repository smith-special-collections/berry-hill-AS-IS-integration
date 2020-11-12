# Procedure:

# ~Extract~
# 1. Get all Digital Objects (that have compass URIs)
# 2. Get all Archival Objects/Resources/Accessions connected to digital objects
# 3. Get all Agents (in a minimum of queries using id_set)
# 4. Get all Subjects (in a minimum of queries using id_set)
# 5. Get all top containers linked to the associated archival objects
# 6. Save this all into a giant data structure called "EXTRACTED_DATA"

# Make a list of all of the output records to be exported and their destination file names
# Save them to the to_export list as a list of tuples/dictionaries of the digital object ID and the output filename

# Loop through each intended output record
  # ~Transform~
  # Loop through mapping data structure:
  #   For a given output field call the given processor function, and pass it the extracted_data structure
  #   Add the returned value from the processor function to the template context data structure
  #
  # ~Save / Export~
  # Create the XML from the template context data structure
  # Save the file to the given output filename
  # Log that it completed successfully or unsuccessfully for the final report

## mapping data structure
mapping = {
  title: {                       # The name of the field as will appear in the template context
    transform_function: 'title', # The name of the function that will generate the field contents
    required: True               # If the field doesn't exist, the record can't be made
  },
  subjects_topic: {
    transform_function: 'subject_topic',
  }
  subjects_genre: {
    transform_function: 'subject_genre',
  }
  subjects_geographic: {
    transform_function: 'subject_geographic',
  }
  #  subject_temporal: # return to this
  # subject_name:
}

## transform functions
def title(extracted_data, do_id):
  digital_object = extracted_data['digital_objects']['do_id']
  # Title comes from the digital object record now!
  title = html_escape(digital_object['title'])
  return title

def get_subjects_by_type(extracted_data, do_id, type):
  digital_object = extracted_data['digital_objects']['do_id']
  parent_component = get_linked_instance(digital_object['linked instance'], extracted_data)
  aspace_subjects = parent_component['subjects']
  subjects = []
  for subject in aspace_subjects:
    if subject['term_type'] == type:
      subjects.append(subject)
  return subjects

def subject_topic(extracted_data, do_id):
  return get_subjects_by_type(extracted_data, do_id, 'topic')

def subject_genre(extracted_data, do_id):
  return get_subjects_by_type(extracted_data, do_id, 'genre/form')

def subject_genre(extracted_data, do_id):
  return get_subjects_by_type(extracted_data, do_id, 'geographic')


## TEMPLATE CODE

{% if context.subjects_topic|length > 0 %}
  {% for subject_topical in context.subjects_topic%}
  <subject><topic>{{subject_topical.title}}</topic></subject>
  {% endfor %}
{% endif %}
