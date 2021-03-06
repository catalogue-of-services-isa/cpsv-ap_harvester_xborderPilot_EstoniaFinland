# -*- coding: utf-8 -*-
"""
Harvests JSON objects over HTTP and maps to CPSV-AP vocabulary
and save to a triple store

Python ver: 3.5
"""

__author__ = 'PwC EU Services'

from json_mapping_estonia import json_to_rdf
import time

from configparser import ConfigParser

import requests
from SPARQLWrapper import SPARQLWrapper, POST, JSON
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from termcolor import colored
import sys
import rdfextras

rdfextras.registerplugins() # so we can Graph.query()

headers = {'content-type': 'application/json'}  # HTTP header content type
# Configurations
config = ConfigParser()
config.read('config.ini')

ev = sys.argv[1]

endpoint_uri = config['Mandatory']['endpointURI']
graph_uri = config['Mandatory']['graphURI']

# Set up endpoint and access to triple store
sparql = SPARQLWrapper(endpoint_uri)
sparql.setReturnFormat(JSON)
sparql.setMethod(POST)
store = SPARQLUpdateStore(endpoint_uri, endpoint_uri)

# Specify the (named) graph we're working with
sparql.addDefaultGraph(graph_uri)

# Create an in memory graph
g = Graph(store, identifier=graph_uri)

query = ""
if ev == "BE":
	query = "select ?uri ?origin ?name ?desc where {?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/vocab/cpsv#PublicService>; <http://data.europa.eu/m8g/isGroupedBy> ?event. ?event <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://data.europa.eu/m8g/BusinessEvent>. OPTIONAL{?uri <http://purl.org/dc/terms/title> ?name}. OPTIONAL{?uri <http://purl.org/dc/terms/description> ?desc}. OPTIONAL{?uri <http://origin> ?origin}}"
if ev == "LE":
	query = "select ?uri ?origin ?name ?desc where {?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/vocab/cpsv#PublicService>; <http://data.europa.eu/m8g/isGroupedBy> ?event. ?event <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://data.europa.eu/m8g/LifeEvent>. OPTIONAL{?uri <http://purl.org/dc/terms/title> ?name}. OPTIONAL{?uri <http://purl.org/dc/terms/description> ?desc}. OPTIONAL{?uri <http://origin> ?origin}}"
urls = g.query (query)

for row in urls:
	uri = row[0].encode('utf-8')
	if row[1] != None:
		origin = row[1].encode('utf-8')
	else:
		origin = ""
	if row[1] != None:
		name = row[2].encode('utf-8')
	else:
		name = ""
	if row[3] != None:
		desc = row[3].encode('utf-8')
	else:
		desc = ""
	print (uri + "##" + origin + "##" + name + "##" + desc + "@@")

# Cleanup the graph instance
g.close()
