#!/usr/bin/env python
# coding: utf-8

# In[15]:


# -*- coding: utf-8 -*-

import json
import urllib.request

# inurl = 'http://localhost:8983/solr/corename/select?q=*%3A*&fl=id%2Cscore&wt=json&indent=true&rows=1000'
# outfn = 'path_to_your_file.txt'

models = ["LM", "DFR", "BM25"]
for model in models:
    count = 1
    with open('test_queries.txt', encoding="utf-8") as f:
        for line in f:
            l = line[4:]
            query = l.strip('\n').replace(':', '')
            query = urllib.parse.quote(query)
            query = "text_en:(" + query + ")%20OR%20text_de:(" + query + ")%20OR%20text_ru:(" + query + ")"
            #print (query)
            inurl = 'http://ec2-18-191-149-35.us-east-2.compute.amazonaws.com:8983/solr/IR'+ model +'/select?' + 'q='+ query +'&fl=id%2Cscore&wt=json&indent=true&rows=20' 
            #print (str(inurl))
            qid = str(count).zfill(3)
            outf = open('C:/IRProject3/' + model + '/' + str(count) + '.txt', 'a+')
            # data = urllib2.urlopen(inurl)
            data = urllib.request.urlopen(inurl).read()
            docs = json.loads(data.decode('utf-8'))['response']['docs']
            # the ranking should start from 1 and increase
            rank = 1
            for doc in docs:
                outf.write(str(qid) + ' ' + 'Q0' + ' ' + str(doc['id']) + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + str(model) + '\n')
                rank += 1
            outf.close()
            count += 1

