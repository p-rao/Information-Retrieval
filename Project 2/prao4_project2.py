#!/usr/bin/env python
# coding: utf-8

from collections import defaultdict
import collections
import json
import io
import sys

def get_IDF_II_TF(filepath):
    # divide each line into a group of tokens
    token_list = []
    postings = []
    # dictionary containing term - postings list values
    unsorted_inverted_index = defaultdict(list)
    tf_dict = defaultdict(list)
    doc_counter = 0
    with open(filepath) as fp:
        for cnt, line in enumerate(fp):
            doc_counter += 1
            token_list = line.split()
            tf_dict[token_list[0]].extend(token_list[1:])
            #print(f"Line {cnt}: {token_list}")
            for i in range(1, len(token_list)):
                postings.append(token_list[0])
                unsorted_inverted_index[token_list[i]].extend(set(postings))
            #print(f"Line {cnt}: {postings}")
            postings.clear()
            token_list.clear()

    # STEP 1
    # get inverted index, sort by document id
    for item in unsorted_inverted_index:
        unsorted_inverted_index[item] = list(set(unsorted_inverted_index[item]))
        unsorted_inverted_index[item].sort()
    inverted_index = dict(unsorted_inverted_index.items())

    # Calculate tf for the above metrics
    tf = {}
    for item in tf_dict:
        terms = list(set(tf_dict[item]))
        tf[item] = {}
        for term in terms:
            tf[item][term] = tf_dict[item].count(term)/len(tf_dict[item])

    # Calculate idf for the above metrics
    idf = {}
    for item in inverted_index:
        idf[item] =  doc_counter/len(inverted_index[item])

    # save the inverted index obtained from STEP 1 to output.txt
    # with open("output.txt", "w+") as file:
    #     file.write(json.dumps(inverted_index, ensure_ascii=False, indent=4))

    return inverted_index, tf, idf


# In[24]:


# STEP 2 get the postings lists for the input terms specified
def getposting(inverted_index, tf, idf, inputfile, outputfile):
    query_terms_list = []
    query_input = ''
    with open(inputfile, "r") as file:
        query_input =  file.read()
        query_terms_list = query_input.split()

    #For each line in the input query
    query_terms_list = []
    terms_dict = defaultdict(list)
    j = 0
    query_input = ''
    with open(inputfile, "r") as file:
        query_input =  file.read()
        query_terms_list = query_input.split('\n')
    for i in query_terms_list:
        if i:
            terms_dict[j] = i.split()
            j += 1

    for query_list in terms_dict:
        #print (terms_dict[query_list])
        #Daat And
        and_result = DAATAnd(terms_dict[query_list], inverted_index)
        #Daat Or
        or_result = DAATOr(terms_dict[query_list], inverted_index)
        #tf-idf
        tf_idf_result_and = tfidf_score(and_result["Results: "], terms_dict[query_list], tf, idf, inverted_index)
        #tf-idf
        tf_idf_result_or = tfidf_score(or_result["Results: "], terms_dict[query_list], tf, idf, inverted_index)

        with open(outputfile, "a") as file:    
            for terms in terms_dict[query_list]:
                postings_list = inverted_index[terms]
                formated_output_posting_list = " ".join(postings_list)
                # Save the obtained output results in format in output_query.txt
                file.write('GetPostings\n' + terms + '\nPostings list: ' + formated_output_posting_list + '\n')
            file.write('DaatAnd\n' + " ".join(terms_dict[query_list]) + '\n')
            for key,value in and_result.items():
                if(type(value) == list):
                    if(not value):
                        file.write(key + "" + "empty")
                    else:
                        file.write(key + "" + " ".join(value))
                else:
                    file.write(key + " " + str(value))
                file.write('\n')
            if(not tf_idf_result_and):
                file.write('TF-IDF\n' + 'Results: empty' + '\n')
            else:
                file.write('TF-IDF\n' + 'Results: ' + " ".join(tf_idf_result_and) + '\n')
            file.write('DaatOr\n' + " ".join(terms_dict[query_list]) + '\n')
            for key,value in or_result.items():
                if(type(value) == list):
                    if(not value):
                        file.write(key + "" + "empty")
                    else:
                        file.write(key + "" + " ".join(value))
                else:
                    file.write(key + " " + str(value))
                file.write('\n')
            if(not tf_idf_result_or):
                file.write('TF-IDF\n' + 'Results: empty' + '\n')
            else:
                file.write('TF-IDF\n' + 'Results: ' + " ".join(tf_idf_result_or) + '\n')
            file.write('\n')

# In[19]:


def DAATAnd(query_terms_list, inverted_index):
    if(len(query_terms_list) == 1):
        return inverted_index[query_terms_list[0]]
    result = inverted_index[query_terms_list[0]][:]
    comparisons = 0
    for i in range(1, len(query_terms_list)):
        r = 0
        p = 0
        posting_list = inverted_index[query_terms_list[i]]
        while(r < len(result) and p < len(posting_list)):
            comparisons += 1
            if(result[r] < posting_list[p]):
                result.remove(result[r])
            elif(result[r] == posting_list[p]):
                r += 1
                p += 1
            else:
                p += 1
            if(p == len(posting_list)):
                result = result[:r]
    result.sort()
    #print(result)
    #print(comparisons)
    daatand = {}
    daatand["Results: "] = result
    daatand["Number of documents in results:"] = len(result)
    daatand["Number of comparisons:"] = comparisons
    #print (result)
    return daatand


# In[20]:


def DAATOr(query_terms_list, inverted_index):
    if(len(query_terms_list) == 1):
        return inverted_index[query_terms_list[0]]
    result = inverted_index[query_terms_list[0]][:]
    comparisons = 0
    for i in range(1, len(query_terms_list)):
        r = 0
        p = 0
        term = inverted_index[query_terms_list[i]]
        while(p < len(term)):
            comparisons += 1
            if(result[r] < term[p]):
                result.append(term[p])
                r += 1
            elif(result[r] == term[p]):
                r += 1
                p += 1
            else:
                result.append(term[p])
                p += 1
    result_list = list(set(result))
    result_list.sort()
    daator = {}
    daator["Results: "] = result_list
    daator["Number of documents in results:"] = len(result_list)
    daator["Number of comparisons:"] = comparisons
    #print (daator)
    return daator


# In[25]:


def tfidf_score(result, query_terms_list, tf, idf, inverted_index):
    tfidf_score = {}
    for doc_id in result:
        tfidf_score[doc_id] = 0
    for terms in query_terms_list:
        for doc_id in result:
            if(doc_id in inverted_index[terms]):
                tfidf_score[doc_id] += tf[doc_id][terms]*idf[terms]
    tf_idf_result = list(sorted(tfidf_score, key=tfidf_score.get, reverse=True))
    #print(tf_idf_result)
    return tf_idf_result


# In[27]:


cmd_line_args = sys.argv
print (cmd_line_args)
path_of_input_corpus = cmd_line_args[1]
outputfile = cmd_line_args[2]
inputfile = cmd_line_args[3]
print (path_of_input_corpus)
print (inputfile)
inverted_index, tf, idf = get_IDF_II_TF(path_of_input_corpus)
getposting(inverted_index, tf, idf, inputfile, outputfile)

# In[ ]:




