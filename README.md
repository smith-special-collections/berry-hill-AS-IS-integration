# berry-hill-AS-IS-integration
A metadata synchronization system between ArchivesSpace and Islandora for use in Smith College Special Collections.

# Code
## get_extract.py
This file pulls and caches all digital objects with Compass URLs in each repository indicated in config.json. In addition to each digital object, it also caches all associated parent objects (archival object, subseries, series, and resource [or accession]) if they exist.