# Required fields (Sep 14 2020)
Present: Claire & Tristan
ArchivesSpace requires these fields, so let's assume that they are available for every output record:

- Title
- Digital Object ID

## AS record URI should be required
It's possible that a given digital object be linked to an accession or resource record (rather than an Archival Object). This is so that we can publish recently digitized materials before the collection(s) has been processed.
The URI of the ArchivesSpace record to which the digital object is linked (AO, Resource, or Accession) should be required in the output.

Note: The ref id isn't made for accessions or resources so it will only be required when the AS record is an archival object.

# Declarative instead of procedural structure for mappings and transforms (Sep 14 2020)
Present: Claire & Tristan
We will use a data structure to declare a mapping of all destination fields and their creation. This will make the code more readable and easier to debug. This will also ensure that each field is created by a single function with an isolated namespace, which will prevent bugs created by name collisions or reuse of variables.

# ETL model (Sep 14 2020)
Present: Tristan & Claire
We will use the Extract Transform Load model to organize our code. What this means is that the code will be separated into three distinct sections.

- Extract: will wholesale grab data from ArchivesSpace. This source data will not be edited in memory. It will be treated as immutable. A copy of the data may be made inside of a transform function, which will be destroyed when the function returns. Python doesn't have a way to strictly enforce this so we will make it convention.
- Transform: will transform that data into the desired fields and export it into a MODS file. As a rule, nowhere in the Transform section of the code will the system make more queries to ArchivesSpace.
- Load: This will be accomplished by the already existing Islandora Datastream CRUD drush tool.
