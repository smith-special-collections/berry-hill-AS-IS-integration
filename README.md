# berry-hill-AS-IS-integration
A metadata synchronization system between ArchivesSpace and Islandora for use in Smith College Special Collections.

# Code
## get_extract.py
This file pulls and caches all digital objects with Compass URLs in each repository indicated in config.json. In addition to each digital object, it also caches all associated parent objects (archival object, subseries, series, and resource [or accession]) if they exist. 

This code is called in export.py and the resulting data object is passed in its entirety to the methods in transform.py, for parsing.

## transform.py
This file contains the Transforms class and the method mapping object. The data object from get_extract.py is passed to each method in the class and each returned result is mapped to the appropriate key in the mapping object. The keys in the mapping object correspond to the name of the method.

## export.py
This code calls get_extract.py, creates the cache, creates an instance of the Transforms class, passes the cache to its methods, and produces a mapping object for each digital object in the cache. The mapping object is passed to the Jinja template and a MODS XML file is outputted.

## compass-mods-template.xml
Jinja template to create custom MODS XML file.

# Run
python3 export.py

Update config.json to change which and how many repositories to pull from.