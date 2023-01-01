import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from rdflib import Graph
import random
import numpy as np
import tensorflow as tf
import math
import datetime as dt
import _pickle as cPickle
from functools import reduce
import os, json
import codecs

os.environ['TF_CPP_MIN_LOG_LEVEL']='4'
DEVICE = "5"
os.environ["CUDA_VISIBLE_DEVICES"]=DEVICE

from kitchen.i18n import get_translation_object
translations = get_translation_object('example')
_ = translations.ugettext
b_ = translations.lgettext


### Combine two KG
## DY-NB
# dataset_name = 'yago'
# lgd_filename = './DY-NB/'+dataset_name+'.ttl'
# dbp_filename = './DY-NB/dbp_'+dataset_name+'.ttl'
# predicate_graph = cPickle.load(open('./DY-NB/'+dataset_name+'_pred_prox_graph.pickle', 'rb'))
# map_file = './DY-NB/mapping_'+dataset_name+'.ttl'
# # ## DW-NB
dataset_name = 'wd'
lgd_filename = './DW-NB/'+dataset_name+'.ttl'
dbp_filename = './DW-NB/dbp_'+dataset_name+'.ttl'
predicate_graph = cPickle.load(open('./DW-NB/'+dataset_name+'_pred_prox_graph.pickle', 'rb'))
map_file = './DW-NB/mapping_'+dataset_name+'.ttl'

with open( "./test_data/ent_type_vocab_wordnet.json", "r") as data:
	wordnet_dict = json.load(data)

graph = Graph()
graph.parse(location=lgd_filename, format='nt')
graph.parse(location=dbp_filename, format='nt')

map_graph = Graph()
map_graph.parse(location=map_file, format='nt')


def invert_dict(d):
    return dict([(v, k) for k, v in d.items()])


entity_label_dict = dict()

for s,p,o in graph:
    if str(p) == 'http://www.w3.org/2000/01/rdf-schema#label': # the name
        entity_label_dict[s] = str(o)


num_subj_triple = dict()
for s,p,o in graph:
    if num_subj_triple.get(s) == None:
        num_subj_triple[s] = 1
    else:
        num_subj_triple[s] += 1

# DY
# intersection_predicates = ['http://dbpedia.org/ontology/Person/height',
# 'http://dbpedia.org/ontology/PopulatedPlace/populationDensity',
# 'http://dbpedia.org/ontology/PopulatedPlace/populationMetroDensity',
# 'http://dbpedia.org/ontology/activeYearsEndDate',
# 'http://dbpedia.org/ontology/activeYearsStartYear',
# 'http://dbpedia.org/ontology/alias',
# 'http://dbpedia.org/ontology/almaMater',
# 'http://dbpedia.org/ontology/area',
# 'http://dbpedia.org/ontology/areaUrban',
# 'http://dbpedia.org/ontology/award',
# 'http://dbpedia.org/ontology/birthDate',
# 'http://dbpedia.org/ontology/birthName',
# 'http://dbpedia.org/ontology/birthPlace',
# 'http://dbpedia.org/ontology/birthYear',
# 'http://dbpedia.org/ontology/capital',
# 'http://dbpedia.org/ontology/child',
# 'http://dbpedia.org/ontology/citizenship',
# 'http://dbpedia.org/ontology/councilArea',
# 'http://dbpedia.org/ontology/country',
# 'http://dbpedia.org/ontology/county',
# 'http://dbpedia.org/ontology/currency',
# 'http://dbpedia.org/ontology/deathDate',
# 'http://dbpedia.org/ontology/deathPlace',
# 'http://dbpedia.org/ontology/deathYear',
# 'http://dbpedia.org/ontology/dissolutionYear',
# 'http://dbpedia.org/ontology/doctoralAdvisor',
# 'http://dbpedia.org/ontology/doctoralStudent',
# 'http://dbpedia.org/ontology/education',
# 'http://dbpedia.org/ontology/ethnicGroup',
# 'http://dbpedia.org/ontology/field',
# 'http://dbpedia.org/ontology/formerTeam',
# 'http://dbpedia.org/ontology/foundingYear',
# 'http://dbpedia.org/ontology/height',
# 'http://dbpedia.org/ontology/hometown',
# 'http://dbpedia.org/ontology/influenced',
# 'http://dbpedia.org/ontology/influencedBy',
# 'http://dbpedia.org/ontology/isPartOf',
# 'http://dbpedia.org/ontology/knownFor',
# 'http://dbpedia.org/ontology/language',
# 'http://dbpedia.org/ontology/largestCity',
# 'http://dbpedia.org/ontology/leader',
# 'http://dbpedia.org/ontology/length',
# 'http://dbpedia.org/ontology/lieutenancyArea',
# 'http://dbpedia.org/ontology/longName',
# 'http://dbpedia.org/ontology/mainInterest',
# 'http://dbpedia.org/ontology/managerClub',
# 'http://dbpedia.org/ontology/nationality',
# 'http://dbpedia.org/ontology/notableIdea',
# 'http://dbpedia.org/ontology/notableStudent',
# 'http://dbpedia.org/ontology/notableWork',
# 'http://dbpedia.org/ontology/officialLanguage',
# 'http://dbpedia.org/ontology/openingYear',
# 'http://dbpedia.org/ontology/party',
# 'http://dbpedia.org/ontology/picture',
# 'http://dbpedia.org/ontology/populationMetroDensity',
# 'http://dbpedia.org/ontology/populationTotal',
# 'http://dbpedia.org/ontology/principalArea',
# 'http://dbpedia.org/ontology/pseudonym',
# 'http://dbpedia.org/ontology/recordLabel',
# 'http://dbpedia.org/ontology/residence',
# 'http://dbpedia.org/ontology/restingPlace',
# 'http://dbpedia.org/ontology/spouse',
# 'http://dbpedia.org/ontology/stateOfOrigin',
# 'http://dbpedia.org/ontology/successor',
# 'http://dbpedia.org/ontology/team',
# 'http://dbpedia.org/ontology/weight',
# 'http://www.w3.org/2000/01/rdf-schema#label',
# 'http://www.w3.org/2003/01/geo/wgs84_pos#lat',
# 'http://www.w3.org/2003/01/geo/wgs84_pos#long',
# 'http://www.w3.org/2004/02/skos/core#prefLabel',
# 'http://xmlns.com/foaf/0.1/gender',
# 'http://xmlns.com/foaf/0.1/givenName',
# 'http://xmlns.com/foaf/0.1/surname']


## DW
intersection_predicates = ['http://www.wikidata.org/entity/P36',\
'http://www.wikidata.org/entity/P185',\
'http://www.wikidata.org/entity/P345',\
'http://www.wikidata.org/entity/P214',\
'http://www.wikidata.org/entity/P40',\
'http://www.wikidata.org/entity/P569',\
'http://www.wikidata.org/entity/P102',\
'http://www.wikidata.org/entity/P175',\
'http://www.wikidata.org/entity/P131',\
'http://www.wikidata.org/entity/P577',\
'http://www.wikidata.org/entity/P140',\
'http://www.wikidata.org/entity/P400',\
'http://www.wikidata.org/entity/P736',\
'http://www.wikidata.org/entity/P1432',\
'http://www.wikidata.org/entity/P159',\
'http://www.wikidata.org/entity/P136',\
'http://www.wikidata.org/entity/P1477',\
'http://www.wikidata.org/entity/P227',\
'http://www.wikidata.org/entity/P6',\
'http://www.wikidata.org/entity/P108',\
'http://www.wikidata.org/entity/P585',\
'http://www.wikidata.org/entity/P239',\
'http://www.wikidata.org/entity/P98',\
'http://www.wikidata.org/entity/P54',\
'http://www.wikidata.org/entity/P17',\
'http://www.wikidata.org/entity/P244',\
'http://www.wikidata.org/entity/P238',\
'http://www.wikidata.org/entity/P287',\
'http://www.wikidata.org/entity/P570',\
'http://www.wikidata.org/entity/P176',\
'http://www.wikidata.org/entity/P119',\
'http://www.wikidata.org/entity/P230',\
'http://www.wikidata.org/entity/P50',\
'http://www.wikidata.org/entity/P57',\
'http://www.wikidata.org/entity/P969',\
'http://www.wikidata.org/entity/P20',\
'http://www.wikidata.org/entity/P374',\
'http://www.wikidata.org/entity/P19',\
'http://www.wikidata.org/entity/P84',\
'http://www.wikidata.org/entity/P166',\
'http://www.wikidata.org/entity/P571',\
'http://www.wikidata.org/entity/P184',\
'http://www.wikidata.org/entity/P473',\
'http://www.wikidata.org/entity/P219',\
'http://www.wikidata.org/entity/P170',\
'http://www.wikidata.org/entity/P26',\
'http://www.wikidata.org/entity/P580',\
'http://www.wikidata.org/entity/P1015',\
'http://www.wikidata.org/entity/P408',\
'http://www.wikidata.org/entity/P172',\
'http://www.wikidata.org/entity/P220',\
'http://www.wikidata.org/entity/P177',\
'http://www.wikidata.org/entity/P178',\
'http://www.wikidata.org/entity/P161',\
'http://www.wikidata.org/entity/P27',\
'http://www.wikidata.org/entity/P742',\
'http://www.wikidata.org/entity/P607',\
'http://www.wikidata.org/entity/P286',\
'http://www.wikidata.org/entity/P361',\
'http://www.wikidata.org/entity/P1082',\
'http://www.wikidata.org/entity/P344',\
'http://www.wikidata.org/entity/P106',\
'http://www.wikidata.org/entity/P112',\
'http://www.wikidata.org/entity/P1036',\
'http://www.wikidata.org/entity/P229',\
'http://www.w3.org/2000/01/rdf-schema#label',\
'http://www.wikidata.org/entity/P126',\
'http://www.wikidata.org/entity/P750',\
'http://www.wikidata.org/entity/P144',\
'http://www.wikidata.org/entity/P69',\
'http://www.wikidata.org/entity/P264',\
'http://www.wikidata.org/entity/P218',\
'http://www.wikidata.org/entity/P110',\
'http://www.wikidata.org/entity/P86',\
'http://www.wikidata.org/entity/P957',\
'http://www.wikidata.org/entity/P1040',\
'http://www.wikidata.org/entity/P200',\
'http://www.wikidata.org/entity/P605',\
'http://www.wikidata.org/entity/P118',\
'http://www.wikidata.org/entity/P127']

intersection_predicates_uri = intersection_predicates


import rdflib
import re
import collections

literal_len = 10

def dataType(string):
    odp='string'
    patternBIT=re.compile('[01]')
    patternINT=re.compile('[0-9]+')
    patternFLOAT=re.compile('[0-9]+\.[0-9]+')
    patternTEXT=re.compile('[a-zA-Z0-9]+')
    if patternTEXT.match(string):
        odp= "string"
    if patternINT.match(string):
        odp= "integer"
    if patternFLOAT.match(string):
        odp= "float"
    return odp

### Return: data, data_type
def getRDFData(o):
    if isinstance(o, rdflib.term.URIRef):
        data_type = "uri"
    else:
        data_type = o.datatype
        if data_type == None:
            data_type = dataType(o)
        else:
            if "#" in o.datatype:
                data_type = o.datatype.split('#')[1].lower()
            else:
                data_type = dataType(o)
        if data_type == 'gmonthday' or data_type=='gyear':
            data_type = 'date'
        if data_type == 'positiveinteger' or data_type == 'int' or data_type == 'nonnegativeinteger':
            data_type = 'integer'
    return o, data_type

def getLiteralArray(o, literal_len, char_vocab):
    literal_object = list()
    for i in range(literal_len):
        literal_object.append(0)
    if o[1] != 'uri':
        max_len = min(literal_len, len(o[0]))
        for i in range(max_len):
            if char_vocab.get(o[0][i]) == None:
                char_vocab[o[0][i]] = len(char_vocab)
            literal_object[i] = char_vocab[o[0][i]]
    elif entity_label_dict.get(o[0]) != None:
        label = entity_label_dict.get(o[0])
        max_len = min(literal_len, len(label))
        for i in range(max_len):
            if char_vocab.get(label[i]) == None:
                char_vocab[label[i]] = len(char_vocab)
            literal_object[i] = char_vocab[label[i]]
        
    return literal_object

entity_vocab = dict()
entity_dbp_vocab = list()
entity_dbp_vocab_neg = list()
entity_lgd_vocab_neg = list()
predicate_vocab = dict()
predicate_vocab['<NONE>'] = 0
entity_literal_vocab = dict()
entity_literal_dbp_vocab_neg = list()
entity_literal_lgd_vocab_neg = list()
data_uri = [] ###[ [[s,p,o,p_trans],[chars],predicate_weight], ... ]
data_uri_0 = []
data_literal_0 = []
data_literal = []
data_uri_trans = []
data_literal_trans = []
char_vocab = dict()
char_vocab['<pad>'] = 0
ent_type_vocab = dict() # all entity types
data_predicate = list()
domain_vocab = dict()
range_vocab = dict()

pred_weight = dict()
num_triples = 0
for s, p, o in graph:

    num_triples += 1
    s = getRDFData(s)
    p = getRDFData(p)
    o = getRDFData(o)
    
    if pred_weight.get(p[0]) == None:
        pred_weight[p[0]] = 1
    else:
        pred_weight[p[0]] += 1

    ## all vocab for finding neg sample
    if entity_literal_vocab.get(s[0]) == None:
        entity_literal_vocab[s[0]] = len(entity_literal_vocab)
        if str(s[0]).startswith('http://dbpedia.org/resource/'): 
            entity_literal_dbp_vocab_neg.append(s[0])
        else:
            entity_literal_lgd_vocab_neg.append(s[0])
    if entity_literal_vocab.get(o[0]) == None:
        entity_literal_vocab[o[0]] = len(entity_literal_vocab)
        if str(s[0]).startswith('http://dbpedia.org/resource/'): 
            entity_literal_dbp_vocab_neg.append(o[0])
        else:
            entity_literal_lgd_vocab_neg.append(o[0])
        
    if entity_vocab.get(s[0]) == None:
        idx = len(entity_vocab)
        entity_vocab[s[0]] = idx
        if str(s[0]).startswith('http://dbpedia.org/resource/'):
            entity_dbp_vocab.append(idx)
            entity_dbp_vocab_neg.append(s[0])
        else:
            entity_lgd_vocab_neg.append(s[0])
    if predicate_vocab.get(p[0]) == None:
        predicate_vocab[p[0]] = len(predicate_vocab)
    if o[1] == 'uri':
        if entity_vocab.get(o[0]) == None:
            entity_vocab[o[0]] = len(entity_vocab)
            if str(s[0]).startswith('http://dbpedia.org/resource/'):
                entity_dbp_vocab_neg.append(o[0])
            else:
                entity_lgd_vocab_neg.append(o[0])
        literal_object = getLiteralArray(o, literal_len, char_vocab)
        if str(p[0]) not in intersection_predicates_uri:
            data_uri_0.append([[entity_vocab[s[0]], predicate_vocab[p[0]], entity_vocab[o[0]], 0], literal_object])
        else:
            data_uri.append([[entity_vocab[s[0]], predicate_vocab[p[0]], entity_vocab[o[0]], 0], literal_object])
            ### DATA TRANS
            duplicate_preds = [item for item, count in collections.Counter(graph.predicates(o[0],None)).items() if count > 1]
            if True:
              for g1 in graph.triples((o[0],None,None)):
                  if len(g1) > 0:
                      s1,p1,o1 = g1

                      s1 = getRDFData(s1)
                      p1 = getRDFData(p1)
                      o1 = getRDFData(o1)

                      if entity_vocab.get(o1[0]) == None:
                          entity_vocab[o1[0]] = len(entity_vocab)
                      if str(s1[0]).startswith('http://dbpedia.org/resource/'):
                          entity_dbp_vocab_neg.append(o1[0])
                      else:
                          entity_lgd_vocab_neg.append(o1[0])
                      if entity_vocab.get(o1[1]) == None:
                          entity_vocab[o1[1]] = len(entity_vocab)
                      if predicate_vocab.get(p1[0]) == None:
                          predicate_vocab[p1[0]] = len(predicate_vocab)

                      if p[0] != p1[0]                           and len(set(str(x) for x in (graph.predicates(s[0]))).intersection(set(intersection_predicates_uri))) != 0:
                          if isinstance(o1[0], rdflib.term.URIRef) and str(p1[0]) in intersection_predicates_uri:
                              data_uri_trans.append([[entity_vocab[s[0]], predicate_vocab[p[0]], entity_vocab[o1[0]], predicate_vocab[p1[0]]], getLiteralArray(o1, literal_len, char_vocab)])
                          elif isinstance(o1[0], rdflib.term.Literal) and str(p1[0]) == 'http://www.w3.org/2000/01/rdf-schema#label': # the name of object/subject
                              data_literal_trans.append([[entity_vocab[s[0]], predicate_vocab[p[0]], entity_vocab[o1[1]], predicate_vocab[p1[0]]], getLiteralArray(o1, literal_len, char_vocab)])
                              #tmp_data.append((s[0], p[0], o[0], p1[0], o1[0]))
              ##############
    else:
        if entity_vocab.get(o[1]) == None:
            entity_vocab[o[1]] = len(entity_vocab)
        literal_object = getLiteralArray(o, literal_len, char_vocab)
        if str(p[0]) not in intersection_predicates:
            data_literal_0.append([[entity_vocab[s[0]], predicate_vocab[p[0]], entity_vocab[o[1]], 0], literal_object])
        else:
            data_literal.append([[entity_vocab[s[0]], predicate_vocab[p[0]], entity_vocab[o[1]], 0], literal_object])        

    if ent_type_vocab.get(s[1]) == None:
        ent_type_vocab[s[1]] = len(ent_type_vocab)
    if ent_type_vocab.get(o[1]) == None:
        ent_type_vocab[o[1]] = len(ent_type_vocab)

    if p not in predicate_vocab:
        predicate_vocab[p] = len(predicate_vocab)
        
    data_predicate.append([[ent_type_vocab[s[1]],predicate_vocab[p],ent_type_vocab[o[1]], 0], [0]*10, [0]])
    
    if predicate_vocab[p] in domain_vocab:
        domain_vocab[predicate_vocab[p]].add(ent_type_vocab[s[1]])
    else:
        domain_vocab[predicate_vocab[p]] = set()
        domain_vocab[predicate_vocab[p]].add(ent_type_vocab[s[1]])
        
    if predicate_vocab[p] in range_vocab:
        range_vocab[predicate_vocab[p]].add(ent_type_vocab[o[1]])
    else:
        range_vocab[predicate_vocab[p]] = set()
        range_vocab[predicate_vocab[p]].add(ent_type_vocab[o[1]])    

     
reverse_entity_vocab = invert_dict(entity_vocab)
reverse_predicate_vocab = invert_dict(predicate_vocab)
reverse_char_vocab = invert_dict(char_vocab)
reverse_entity_literal_vocab = invert_dict(entity_literal_vocab)

#Add predicate weight (TransE)
for i in range(0, len(data_uri)):
    s = reverse_entity_vocab.get(data_uri[i][0][0])
    p = reverse_predicate_vocab.get(data_uri[i][0][1])
    data_uri[i].append([(pred_weight.get(p)/float(num_triples))]) 

for i in range(0, len(data_uri_0)):
    s = reverse_entity_vocab.get(data_uri_0[i][0][0])
    p = reverse_predicate_vocab.get(data_uri_0[i][0][1])
    data_uri_0[i].append([(pred_weight.get(p)/float(num_triples))])

for i in range(0, len(data_uri_trans)):
    s = reverse_entity_vocab.get(data_uri_trans[i][0][0])
    p = reverse_predicate_vocab.get(data_uri_trans[i][0][1])
    data_uri_trans[i].append([(pred_weight.get(p)/float(num_triples))])
    
for i in range(0, len(data_literal)):
    s = reverse_entity_vocab.get(data_literal[i][0][0])
    p = reverse_predicate_vocab.get(data_literal[i][0][1])
    data_literal[i].append([(pred_weight.get(p)/float(num_triples))])

for i in range(0, len(data_literal_0)):
    s = reverse_entity_vocab.get(data_literal_0[i][0][0])
    p = reverse_predicate_vocab.get(data_literal_0[i][0][1])
    data_literal_0[i].append([(pred_weight.get(p)/float(num_triples))])
    
for i in range(0, len(data_literal_trans)):
    s = reverse_entity_vocab.get(data_literal_trans[i][0][0])
    p = reverse_predicate_vocab.get(data_literal_trans[i][0][1])
    data_literal_trans[i].append([(pred_weight.get(p)/float(num_triples))])
    
if len(data_uri_trans) < 100:
    data_uri_trans = data_uri_trans+data_uri_trans
    
print (len(entity_vocab), len(predicate_vocab), len(char_vocab), len(entity_dbp_vocab))


# predicate proximity triples
ent_type_vocab = dict()
data_predicate = list()
domain_vocab = dict()
range_vocab = dict()
for prox_t in  predicate_graph:
    prox_s,p,prox_o = prox_t
    if p not in predicate_vocab:
        predicate_vocab[p] = len(predicate_vocab)
    
    for s in prox_s:
        if s not in ent_type_vocab:
            ent_type_vocab[s] = len(ent_type_vocab)
        if predicate_vocab[p] not in domain_vocab:
            domain_vocab[predicate_vocab[p]] = set()
            domain_vocab[predicate_vocab[p]].add(ent_type_vocab[s])
        else:
            domain_vocab[predicate_vocab[p]].add(ent_type_vocab[s])
        
    for o in prox_o:
        if o not in ent_type_vocab:
            ent_type_vocab[o] = len(ent_type_vocab)
        if predicate_vocab[p] not in range_vocab:
            range_vocab[predicate_vocab[p]] = set()
            range_vocab[predicate_vocab[p]].add(ent_type_vocab[o])
        else:
            range_vocab[predicate_vocab[p]].add(ent_type_vocab[o])

    data_predicate.append([[ent_type_vocab[s],predicate_vocab[p],ent_type_vocab[o], 0], [0]*10, [0]])


invert_ent_type_vocab = invert_dict(ent_type_vocab)

def elementwise_add(list1, list2):
  result = []
  for i in range(len(list1)):
    result.append(list1[i] + list2[i])
  return result


def tfidf_matrix(corpus):
    terms = set()
    for document in corpus:
        for term in document:
            terms.add(term)

    matrix = []
    for document in corpus:
        doc_vector = []
        for term in terms:
            tf = document.count(term) / len(document)
            idf = math.log(len(corpus) / sum(1 for d in corpus if term in d))
            doc_vector.append(tf * idf)
        matrix.append(doc_vector)

    return matrix


def getBatch(data, batchSize, current, entityVocab, literal_len, char_vocab):
    hasNext = current+batchSize < len(data)
    
    if (len(data) - current) < batchSize:
        current = current - (batchSize - (len(data) - current))
    
    dataPos_all = data[current:current+batchSize]
    dataPos = list()
    charPos = list()
    pred_weight_pos = list()
    dataNeg = list()
    predNeg = list()
    predTransNeg = list()
    charNeg = list()
    pred_weight_neg = list()
    for triples,chars, pred_weight in dataPos_all:
        s,p,o,p_trans = triples
        dataPos.append([s,p,o,p_trans])
        charPos.append(chars)
        pred_weight_pos.append(pred_weight)
        lr = round(random.random())
        
        if lr == 0:
            try:
                o_type = getRDFData(reverse_entity_vocab[o])
            except:
                o_type = 'not_uri'
            
            literal_array = []
            rerun = True
            while rerun or negElm[0] == (reverse_entity_vocab[o] and literal_array == chars):
                if o_type[1] == 'uri':
                    if str(s).startswith('http://dbpedia.org/resource/'):
                        negElm = entity_dbp_vocab_neg[random.randint(0, len(entity_dbp_vocab_neg)-1)]
                        negElm = reverse_entity_vocab[entity_vocab[negElm]]
                    else:
                        negElm = entity_lgd_vocab_neg[random.randint(0, len(entity_lgd_vocab_neg)-1)]
                        negElm = reverse_entity_vocab[entity_vocab[negElm]]
                else:
                    if str(s).startswith('http://dbpedia.org/resource/'):
                        negElm = entity_literal_dbp_vocab_neg[random.randint(0, len(entity_literal_dbp_vocab_neg)-1)]
                        negElm = reverse_entity_literal_vocab[entity_literal_vocab[negElm]]
                    else:
                        negElm = entity_literal_lgd_vocab_neg[random.randint(0, len(entity_literal_lgd_vocab_neg)-1)]
                        negElm = reverse_entity_literal_vocab[entity_literal_vocab[negElm]]
                if o_type == 'uri' and negElm[1] == 'uri':
                    rerun = False
                elif o_type != 'uri':
                    rerun = False
                if (isinstance(negElm, rdflib.term.URIRef)) or (isinstance(negElm, rdflib.term.Literal)):
                    negElm = getRDFData(negElm)
                    literal_array = getLiteralArray(negElm, literal_len, char_vocab)
                else:
                    rerun = True    
            if negElm[1] == 'uri':
                dataNeg.append([s, p, entity_vocab[negElm[0]], p_trans])
            else:
                dataNeg.append([s, p, entity_vocab[negElm[1]], p_trans])
            charNeg.append(literal_array)
            predNeg.append(p)
            pred_weight_neg.append(pred_weight)
        else:
            ### SUBJECTS only contains URI
            negElm = random.randint(0, len(entity_vocab)-1)
            while negElm == s:
                negElm = random.randint(0, len(entity_vocab)-1)
            dataNeg.append([negElm, p, o, p_trans])
            charNeg.append(chars)
            predNeg.append(p)
            pred_weight_neg.append(pred_weight)

    typePos_h = list()
    for i in range(len(dataPos)):
        typePos_h.append(list(domain_vocab.get(dataPos[i][0], {0}))) # [[], []] 
    
    typePos_t = list()
    for i in range(len(dataPos)):
        typePos_t.append(list(range_vocab.get(dataPos[i][2], {0}))) # [[], []] 
        
    typeNeg_h = list()
    for i in range(len(dataNeg)):
        typeNeg_h.append(list(domain_vocab.get(dataNeg[i][0], {0}))) # [[], []] 

    typeNeg_t = list()
    for i in range(len(dataNeg)):
        typeNeg_t.append(list(range_vocab.get(dataNeg[i][2], {0}))) # [[], []] 

    typePos_h_attw = list()
    for train_set in typePos_h:
        train_set= [invert_ent_type_vocab[i] for i in train_set]
        tfidf_matrix_train = tfidf_matrix(train_set)
        i_attw = [0]*4
        for type_word in train_set:
            if type_word not in wordnet_dict:
                wordnet_dict[type_word] = 10
            w =int(wordnet_dict[type_word])
            tfidf_matrix_train =  list_to_array(list(i*w for i in tfidf_matrix_train))
            for i in tfidf_matrix_train:
                i_attw = elementwise_add(i_attw, i)
        typePos_h_attw.append(i_attw)

    typePos_t_attw = list()
    for train_set in typePos_t:
        train_set= [invert_ent_type_vocab[i] for i in train_set]
        tfidf_matrix_train = tfidf_matrix(train_set)
        i_attw = [0]*4
        for type_word in train_set:
            if type_word not in wordnet_dict:
                wordnet_dict[type_word] = 10
            w =int(wordnet_dict[type_word])
            tfidf_matrix_train =  list_to_array(list(i*w for i in tfidf_matrix_train))
            for i in tfidf_matrix_train:
                i_attw = elementwise_add(i_attw, i)
        typePos_t_attw.append(i_attw)
    

    dataPos = np.array(list_to_array(dataPos))
    typePos_h = np.array(list_to_array(typePos_h))
    typePos_t = np.array(list_to_array(typePos_t))
    typeNeg_h = np.array(list_to_array(typeNeg_h))
    typeNeg_t = np.array(list_to_array(typeNeg_t))
    typePos_h_attw = np.array(list_to_array(typePos_h_attw))
    charPos = np.array(charPos)
    pred_weight_pos = np.array(pred_weight_pos)
    dataNeg = np.array(dataNeg)
    predNeg = np.array(predNeg)
    predTransNeg = np.array(predTransNeg)
    charNeg = np.array(charNeg)
    pred_weight_neg = np.array(pred_weight_neg)
    
    return hasNext, current+batchSize, dataPos[:,0], dataPos[:,1], dataPos[:,2], dataPos[:,3], pred_weight_pos, charPos, dataNeg[:,0], dataNeg[:,1], dataNeg[:,2], dataNeg[:,3], pred_weight_neg, charNeg, typePos_h, typePos_t, typeNeg_h, typeNeg_t, typePos_h_attw, typePos_t_attw


batchSize = 20 #100
hidden_size = 100
totalEpoch = 400
verbose = 1000
margin = 1.0
literal_len = literal_len
entitySize = len(entity_vocab)
charSize = len(char_vocab)
predSize = len(predicate_vocab)
ppEntSize = len(ent_type_vocab)
valid_size = 100 
top_k = 10


import random
from rdflib import URIRef

# temp for coding
file_lgd = open(map_file, 'r')
valid_dataset_list = list()
for line in file_lgd:
    elements = line.split(' ')
    s = codecs.decode(elements[0], 'unicode-escape') #DBpedia
    p = codecs.decode(elements[1], 'unicode-escape')
    o = codecs.decode(elements[2], 'unicode-escape') #LGD
    
    if (entity_vocab[URIRef(s.replace('<','').replace('>',''))] in entity_dbp_vocab) and (URIRef(o.replace('<','').replace('>','')) in entity_vocab):
            valid_dataset_list.append((o, s))

file_lgd.close()
print("valid_dataset_list:", len(valid_dataset_list))

valid_examples = [entity_vocab[URIRef(k.replace('<','').replace('>',''))] for k,_ in valid_dataset_list] #LGD
valid_answer = [entity_dbp_vocab.index(entity_vocab[URIRef(k.replace('<','').replace('>',''))]) for _,k in valid_dataset_list] #DBpedia


def list_to_array (x):    
    x = [ i+[0]*(4-len(i)) if len(i) < 4 else i[:4] for i in x]
    return x

tfgraph = tf.Graph()

with tfgraph.as_default():
    
    # input placeholder #
    pos_h = tf.placeholder(tf.int32, [None])
    pos_t = tf.placeholder(tf.int32, [None])
    pos_r = tf.placeholder(tf.int32, [None])
    pos_r_trans = tf.placeholder(tf.int32, [None])
    pos_c = tf.placeholder(tf.int32, [None, literal_len])
    pos_pred_weight = tf.placeholder(tf.float32, [None,1], name='pos_pred_weight')
    
    pos_h_type = tf.placeholder(tf.int32, [None,4]) # [b, 4]
    pos_t_type = tf.placeholder(tf.int32, [None,4]) # [b, 4]
    neg_h_type = tf.placeholder(tf.int32, [None,4]) # [b, 4]
    neg_t_type = tf.placeholder(tf.int32, [None,4]) # [b, 4]

    pos_h_type_attw = tf.placeholder(tf.float32, [None,4])
    pos_t_type_attw = tf.placeholder(tf.float32, [None,4])

    neg_h = tf.placeholder(tf.int32, [None])
    neg_t = tf.placeholder(tf.int32, [None])
    neg_r = tf.placeholder(tf.int32, [None])
    neg_r_trans = tf.placeholder(tf.int32, [None])
    neg_c = tf.placeholder(tf.int32, [None, literal_len])
    neg_pred_weight = tf.placeholder(tf.float32, [None,1], name='neg_pred_weight')
    
    type_data = tf.placeholder(tf.int32, [1])
    type_trans = tf.placeholder(tf.int32, [1])
    ######################
    
    # embedding variables #
    ent_embeddings_ori = tf.get_variable(name = "relationship_triple_ent_embedding", shape = [entitySize, hidden_size], initializer = tf.contrib.layers.xavier_initializer(uniform = False))
    atr_embeddings_ori = tf.get_variable(name = "attribute_triple_ent_embedding", shape = [entitySize, hidden_size], initializer = tf.contrib.layers.xavier_initializer(uniform = False))
    ent_rel_embeddings = tf.get_variable(name = "proximity_triple_pred_embedding", shape = [predSize, hidden_size], initializer = tf.contrib.layers.xavier_initializer(uniform = False))
    pp_ent_embeddings = tf.get_variable(name = "proximity_triple_ent_embedding", shape = [ppEntSize, hidden_size], initializer = tf.contrib.layers.xavier_initializer(uniform = False))
    char_embeddings = tf.get_variable(name = "attribute_triple_char_embedding", shape = [charSize, hidden_size], initializer = tf.contrib.layers.xavier_initializer(uniform = False))
    
    ent_indices = tf.concat([pos_h, pos_t, neg_h, neg_t], 0)
    ent_indices = tf.reshape(ent_indices,[-1,1])
    ent_value = tf.concat([tf.nn.embedding_lookup(ent_embeddings_ori, pos_h),\
                          tf.nn.embedding_lookup(ent_embeddings_ori, pos_t),\
                          tf.nn.embedding_lookup(ent_embeddings_ori, neg_h),\
                          tf.nn.embedding_lookup(ent_embeddings_ori, neg_t)], 0)
    part_ent_embeddings = tf.scatter_nd([ent_indices], [ent_value], ent_embeddings_ori.shape)
    ent_embeddings = part_ent_embeddings + tf.stop_gradient(-part_ent_embeddings + ent_embeddings_ori)
    
    atr_indices = tf.concat([pos_h, pos_t, neg_h, neg_t], 0)
    atr_indices = tf.reshape(atr_indices,[-1,1])
    atr_value = tf.concat([tf.nn.embedding_lookup(atr_embeddings_ori, pos_h),\
                          tf.nn.embedding_lookup(atr_embeddings_ori, pos_t),\
                          tf.nn.embedding_lookup(atr_embeddings_ori, neg_h),\
                          tf.nn.embedding_lookup(atr_embeddings_ori, neg_t)], 0)
    part_atr_embeddings = tf.scatter_nd([atr_indices], [atr_value], atr_embeddings_ori.shape)
    atr_embeddings = part_atr_embeddings + tf.stop_gradient(-part_atr_embeddings + atr_embeddings_ori)
    ########################
    
    
    # PREDICATE PROXIMITY TRIPLES #
    pp_pos_r_e = tf.nn.embedding_lookup(ent_rel_embeddings, pos_r)
    pp_neg_h_e = tf.nn.embedding_lookup(pp_ent_embeddings, neg_h)
    pp_neg_t_e = tf.nn.embedding_lookup(pp_ent_embeddings, neg_t)
    pp_neg_r_e = tf.nn.embedding_lookup(ent_rel_embeddings, neg_r)

    pp_pos_h_e = tf.nn.embedding_lookup(pp_ent_embeddings, pos_h_type) # [b, 4, hidden_size]
    pp_pos_t_e = tf.nn.embedding_lookup(pp_ent_embeddings, pos_t_type) # [b, 4, hidden_size]
    # pp_pos_h_e =  tf.reshape(pp_pos_h_e, [-1, hidden_size])  # [b*4, hid]
    
    pp_pos_h_e = tf.reduce_sum(tf.multiply(tf.expand_dims(pos_h_type_attw, axis=-1), pp_pos_h_e), axis=1)
    pp_pos_t_e = tf.reduce_sum(tf.multiply(tf.expand_dims(pos_t_type_attw, axis=-1), pp_pos_t_e), axis=1)
    pp_pos = tf.reduce_sum(abs(pp_pos_h_e + pp_pos_r_e - pp_pos_t_e), 1, keep_dims = True)
    pp_neg = tf.reduce_sum(abs(pp_neg_h_e + pp_neg_r_e - pp_neg_t_e), 1, keep_dims = True)
    #pp_learning_rate = 0.0001 # LGD/GEO
    pp_learning_rate = 0.0001 # YAGO
    pp_opt_vars_ent = [v for v in tf.trainable_variables() if v.name.startswith("proximity_triple")]
    #pp_loss = tf.reduce_sum(tf.maximum(pp_pos - pp_neg + 1, 0)) # LGD/GEO
    pp_loss = tf.reduce_sum(tf.maximum(pp_pos - pp_neg + 10, 0)) # YAGO
    pp_optimizer = tf.train.AdamOptimizer(pp_learning_rate).minimize(pp_loss, var_list=pp_opt_vars_ent)
    ########################
    
    
    # RELATIONSHIP TRIPLES #
    rt_pos_h_e = tf.nn.embedding_lookup(ent_embeddings, pos_h)
    rt_pos_t_e = tf.nn.embedding_lookup(ent_embeddings, pos_t)
    rt_pos_r_e = tf.stop_gradient(tf.nn.embedding_lookup(ent_rel_embeddings, pos_r)) # YAGO
    rt_neg_h_e = tf.nn.embedding_lookup(ent_embeddings, neg_h)
    rt_neg_t_e = tf.nn.embedding_lookup(ent_embeddings, neg_t)
    rt_neg_r_e = tf.stop_gradient(tf.nn.embedding_lookup(ent_rel_embeddings, neg_r)) # YAGO
    
    ent_emb = tf.nn.embedding_lookup(ent_embeddings, pos_h)
    atr_emb = tf.nn.embedding_lookup(atr_embeddings, pos_h)
    norm_ent_emb = tf.nn.l2_normalize(ent_emb,1)
    norm_atr_emb = tf.nn.l2_normalize(atr_emb,1)
    cos_sim = tf.reduce_sum(tf.multiply(norm_ent_emb, norm_atr_emb), 1, keep_dims=True)
    
    rt_pos = tf.reduce_sum(abs(rt_pos_h_e + rt_pos_r_e - rt_pos_t_e), 1, keep_dims = True)
    rt_neg = tf.reduce_sum(abs(rt_neg_h_e + rt_neg_r_e - rt_neg_t_e), 1, keep_dims = True)
    #rt_learning_rate = tf.reduce_min(pos_pred_weight)*0.001 # LGD/GEO
    rt_learning_rate = 0.0001 # YAGO
    rt_opt_vars_ent = [v for v in tf.trainable_variables() if v.name.startswith("relationship_triple")]
    #rt_loss = tf.reduce_sum(tf.maximum(rt_pos - rt_neg + 1, 0)) # LGD/GEO
    rt_loss = tf.reduce_sum(tf.maximum(rt_pos - rt_neg + 10, 0)) # YAGO
    rt_optimizer = tf.train.AdamOptimizer(rt_learning_rate).minimize(rt_loss, var_list=rt_opt_vars_ent)
    ########################
                            
                            
    # ATTRIBUTE TRIPLES #
    at_pos_h_e = tf.nn.embedding_lookup(atr_embeddings, pos_h)
    pos_c_e = tf.nn.embedding_lookup(char_embeddings, pos_c)
    at_pos_r_e = tf.stop_gradient(tf.nn.embedding_lookup(ent_rel_embeddings, pos_r))
    #at_pos_r_e = tf.nn.embedding_lookup(atr_rel_embeddings, pos_r)
    at_neg_h_e = tf.nn.embedding_lookup(atr_embeddings, neg_h)
    neg_c_e = tf.nn.embedding_lookup(char_embeddings, neg_c)
    at_neg_r_e = tf.stop_gradient(tf.nn.embedding_lookup(ent_rel_embeddings, neg_r))
    #at_neg_r_e = tf.nn.embedding_lookup(atr_rel_embeddings, neg_r)
    
    #Zero-Mask for char embedding
    mask_constant_0 = np.zeros([1,hidden_size])
    mask_constant_1 = np.ones([1,hidden_size])
    mask_constant = np.concatenate([mask_constant_0, mask_constant_1])
    mask_constant = tf.constant(mask_constant, tf.float32)
    flag_pos_c_e = tf.sign(tf.abs(pos_c))
    mask_pos_c_e = tf.nn.embedding_lookup(mask_constant, flag_pos_c_e)
    pos_c_e = pos_c_e * mask_pos_c_e
    flag_neg_c_e = tf.sign(tf.abs(neg_c))
    mask_neg_c_e = tf.nn.embedding_lookup(mask_constant, flag_neg_c_e)
    neg_c_e = neg_c_e * mask_neg_c_e
    
    
    #N-GRAM
    def calculate_ngram_weight(unstacked_tensor):
        stacked_tensor = tf.stack(unstacked_tensor, 1)
        stacked_tensor = tf.reverse(stacked_tensor, [1])
        index = tf.constant(len(unstacked_tensor))
        expected_result = tf.zeros([batchSize, hidden_size])
        def condition(index, summation):
            return tf.greater(index, 0)
        def body(index, summation):
            precessed = tf.slice(stacked_tensor,[0,index-1,0], [-1,-1,-1])
            summand = tf.reduce_mean(precessed, 1)
            return tf.subtract(index, 1), tf.add(summation, summand)
        result = tf.while_loop(condition, body, [index, expected_result])
        return result[1]
    pos_c_e_in_lstm = tf.unstack(pos_c_e, literal_len, 1)
    pos_c_e_lstm = calculate_ngram_weight(pos_c_e_in_lstm)
    neg_c_e_in_lstm = tf.unstack(neg_c_e, literal_len, 1)
    neg_c_e_lstm = calculate_ngram_weight(neg_c_e_in_lstm)
    
    at_pos = tf.reduce_sum(abs(at_pos_h_e + at_pos_r_e - pos_c_e_lstm), 1, keep_dims = True)
    at_neg = tf.reduce_sum(abs(at_neg_h_e + at_neg_r_e - neg_c_e_lstm), 1, keep_dims = True)
    at_pos_h_e = tf.multiply(at_pos, pos_pred_weight)
    at_neg_h_e = tf.multiply(at_neg, neg_pred_weight)
    #at_learning_rate = tf.reduce_min(pos_pred_weight)*0.001 # LGD/GEO
    at_learning_rate = tf.reduce_min(pos_pred_weight)*0.01 # YAGO
    at_opt_vars_atr = [v for v in tf.trainable_variables() if v.name.startswith("attribute_triple") or v.name.startswith("rnn")]
    at_loss = tf.reduce_sum(tf.maximum(at_pos - at_neg + 1, 0))
    at_optimizer = tf.train.AdamOptimizer(at_learning_rate).minimize(at_loss, var_list=at_opt_vars_atr)
    ########################
                            
    
    # TRANSITIVE TRIPLES #
    pos_r_e_trans = tf.stop_gradient(tf.nn.embedding_lookup(ent_rel_embeddings, pos_r_trans))
    neg_r_e_trans = tf.stop_gradient(tf.nn.embedding_lookup(ent_rel_embeddings, neg_r_trans))
    tr_pos_r_e = tf.multiply(at_pos_r_e, pos_r_e_trans)
    tr_neg_r_e = tf.multiply(at_neg_r_e, neg_r_e_trans)
    tr_pos = tf.reduce_sum(abs(at_pos_h_e + tr_pos_r_e - pos_c_e_lstm), 1, keep_dims = True)
    tr_neg = tf.reduce_sum(abs(at_neg_h_e + tr_neg_r_e - neg_c_e_lstm), 1, keep_dims = True)
    tr_pos_h_e = tf.multiply(tr_pos, pos_pred_weight)
    tr_neg_h_e = tf.multiply(tr_neg, neg_pred_weight)
    #tr_learning_rate = tf.reduce_min(pos_pred_weight)*0.001 # LGD/GEO
    tr_learning_rate = tf.reduce_min(pos_pred_weight)*0.01 # YAGO
    tr_opt_vars_atr = [v for v in tf.trainable_variables() if v.name.startswith("attribute_triple") or v.name.startswith("rnn")]
    tr_loss = tf.reduce_sum(tf.maximum(tr_pos - tr_neg + 1, 0))
    tr_optimizer = tf.train.AdamOptimizer(tr_learning_rate).minimize(tr_loss, var_list=tr_opt_vars_atr)
    ######################
    
    
    #Entity Embeddings & Attribute Embeddings Similarity
    sim_ent_emb = tf.nn.embedding_lookup(ent_embeddings, pos_h)
    sim_atr_emb = tf.nn.embedding_lookup(atr_embeddings, pos_h)
    norm_ent_emb = tf.nn.l2_normalize(sim_ent_emb,1)
    norm_atr_emb = tf.nn.l2_normalize(sim_atr_emb,1)
    cos_sim = tf.reduce_sum(tf.multiply(norm_ent_emb, norm_atr_emb), 1, keep_dims=True)
    sim_loss = tf.reduce_sum(1-cos_sim)
    opt_vars_sim = [v for v in tf.trainable_variables() if v.name.startswith("relationship_triple_ent_embedding")]
    sim_optimizer = tf.train.AdamOptimizer(0.01).minimize(sim_loss, var_list=opt_vars_sim)
    ####################################################
    
    
    # testing
    norm = tf.sqrt(tf.reduce_sum(tf.square(ent_embeddings_ori), 1, keep_dims=True))
    normalized_embeddings = ent_embeddings_ori / norm
    
    valid_dataset = tf.constant(valid_examples, dtype=tf.int32)
    valid_embeddings = tf.nn.embedding_lookup(normalized_embeddings, valid_dataset)
    similarity = tf.matmul(valid_embeddings, normalized_embeddings, transpose_b=True)
    
    init = tf.global_variables_initializer()
    #########


def metric(y_true, y_pred, answer_vocab, k=10):
    file_result = open('correct_1.txt','w')
    file_result_2 = open('correct_10.txt','w')
    list_rank = list()
    total_hits = 0
    total_hits_1 = 0
    for i in range(len(y_true)):
        result = y_pred[i]
        result = result[answer_vocab]
        #sort result first
        result = (-result).argsort()
        
        #Mean Rank
        for j in range(len(result)):
            if result[j] == y_true[i]:
                rank = j
                break
        list_rank.append(j)
        #Mean Rank
        
        #Hit @K
        result = result[:k]
        for j in range(len(result)):
            if result[j] == y_true[i]:
                total_hits += 1
                if j == 0:
                    total_hits_1 += 1
                    file_result.write(str(result[j])+'\n')
                file_result_2.write(str(result[j])+'\n')
                break

    #RETURN: MeanRank, Hits@K
    file_result.close()
    file_result_2.close()
    return reduce(lambda x, y: x + y, list_rank) / len(list_rank), float(total_hits)/len(y_true), float(total_hits_1)/len(y_true)


def run(graph, totalEpoch):
    writer = open('log.txt', 'w')
    with tf.Session(graph=graph) as session:
        writer_tb=tf.summary.FileWriter('./tensorboard_study', session.graph)
        init.run()
        
        for epoch in range(totalEpoch):
            if epoch % 2 == 0:
                data = [data_predicate, data_uri_0, data_uri, data_literal_0, data_literal, []]
            else:
                data = [data_literal]
            start_time_epoch = dt.datetime.now()
            for i in range(0, len(data)):
                random.shuffle(data[i])
                hasNext = True
                current = 0
                step = 0
                average_loss = 0
                  
                while(hasNext and len(data[i]) > 0):
                    step += 1
                    if epoch % 2 == 0 and i == 0:
                        hasNext, current, ph, pr, pt, pr_trans, ppred, pc, nh, nr, nt, nr_trans, npred, nc, ph_type, pt_type, nh_type, nt_type, ph_type_attw, pt_type_attw = getBatch(data[i], batchSize, current, entity_vocab, literal_len, char_vocab)
                    else:
                        hasNext, current, ph, pr, pt, pr_trans, ppred, pc, nh, nr, nt, nr_trans, npred, nc, ph_type, pt_type, nh_type, nt_type, ph_type_attw, pt_type_attw = getBatch(data[i], batchSize, current, entity_vocab, literal_len, char_vocab)
                    feed_dict = {
                        pos_h: ph,
                        pos_t: pt,
                        pos_r: pr,
                        pos_r_trans: pr_trans,
                        pos_pred_weight : ppred,
                        pos_c: pc,
                        neg_h: nh,
                        neg_t: nt,
                        neg_r: nr,
                        neg_r_trans: nr_trans,
                        neg_c: nc,
                        neg_pred_weight: npred,
                        pos_h_type:ph_type,
                        pos_t_type:pt_type,
                        neg_h_type:nh_type,
                        neg_t_type:nt_type,
                        pos_h_type_attw: ph_type_attw,
                        pos_t_type_attw: pt_type_attw
                    }
                    # compute entity embedding and attribute embedding
                    if epoch % 2 == 0:
                        if i == 0: # predicate proximity triples
                            __, loss_val = session.run([pp_optimizer, pp_loss], feed_dict=feed_dict)
                            average_loss += loss_val
                        elif i == 1 or i == 2: # relationship triples
                            __, loss_val = session.run([rt_optimizer, rt_loss], feed_dict=feed_dict)
                            average_loss += loss_val
                        elif i == 3 or i == 4: # attribute triples
                            __, loss_val = session.run([at_optimizer, at_loss], feed_dict=feed_dict)
                            average_loss += loss_val
                        elif i == 5: # transitive triples
                            __, loss_val = session.run([tr_optimizer, tr_loss], feed_dict=feed_dict)
                            average_loss += loss_val
                    # compute entity embedding similarity
                    else:
                        __, loss_val = session.run([sim_optimizer, sim_loss], feed_dict=feed_dict)
                        average_loss += loss_val

                    if step % verbose == 0:
                        average_loss /= verbose
                        print('Epoch: ', epoch, ' Average loss at step ', step, ': ', average_loss)
                        writer.write('Epoch: '+ str(epoch)+ ' Average loss at step '+ str(step)+ ': '+ str(average_loss)+'\n')
                        average_loss = 0
                if len(data[i]) > 0:
                        average_loss /= ((len(data[i])%(verbose*batchSize))/batchSize)
                        print('Epoch: ', epoch, ' Average loss at step ', step, ': ', average_loss)
                        writer.write('Epoch: '+ str(epoch)+ ' Average loss at step '+ str(step)+ ': '+ str(average_loss)+ '\n')

            end_time_epoch = dt.datetime.now()
            print("Training time took {} seconds to run 1 epoch".format((end_time_epoch-start_time_epoch).total_seconds()))
            writer.write("Training time took {} seconds to run 1 epoch\n".format((end_time_epoch-start_time_epoch).total_seconds()))
            if (epoch+1) % 2 == 0:  # testing interval
                start_time_epoch = dt.datetime.now()
                sim = similarity.eval()
                mean_rank, hits_at_10, hits_at_1 = metric(valid_answer, sim, entity_dbp_vocab, top_k)
                print ("Mean Rank: ", mean_rank, " of ", len(entity_dbp_vocab))
                writer.write("Mean Rank: "+ str(mean_rank)+ " of "+ str(len(entity_dbp_vocab))+ "\n")
                print ("Hits @ "+str(top_k)+": ", hits_at_10)
                writer.write("Hits @ "+str(top_k)+": "+ str(hits_at_10)+ "\n")
                print ("Hits @ "+str(1)+": ", hits_at_1)
                writer.write("Hits @ "+str(1)+": "+ str(hits_at_1)+ "\n")
                end_time_epoch = dt.datetime.now()
                print("Testing time took {} seconds.".format((end_time_epoch-start_time_epoch).total_seconds()))
                writer.write("Testing time took {} seconds.\n\n".format((end_time_epoch-start_time_epoch).total_seconds()))
                print()
            #break
        final_embeddings_normalized = normalized_embeddings.eval()
        final_embeddings_entity = ent_embeddings_ori.eval()
        final_embeddings_predicate = ent_rel_embeddings.eval()
        np.savetxt('TextKE_final_embedding_normalize.txt',final_embeddings_normalized)
        np.savetxt('TextKE_final_embedding_entity.txt',final_embeddings_entity)
        np.savetxt('TextKE_final_embedding_predicate.txt',final_embeddings_predicate)
        cPickle.dump( reverse_entity_vocab, open( "TextKE_dictionary_entity.pickle", "wb" ) )
        cPickle.dump( reverse_predicate_vocab, open( "TextKE_dictionary_predicate.pickle", "wb" ) )
    writer.close()
    writer_tb.close()


start_time = dt.datetime.now()
run(tfgraph, 400) # 800 
end_time = dt.datetime.now()
print("Training time took {} seconds to run {} epoch".format((end_time-start_time).total_seconds(), totalEpoch))




