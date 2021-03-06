# -*- coding: utf-8 -*-
"""Generating Article Trajectory Extensions

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Y92-NJ1gE59bYONwsXr2pnZ3H9SEBw6N
"""

import networkx as nx
import requests
import json
import matplotlib.pyplot as plt
import statistics
import pandas as pd
import pickle

"""# Graph Creation Functions"""

def get_article_revisions(title):
    revisions = []
    # create a base url for the api and then a normal url which is initially
    # just a copy of it
    # The following line is what the requests call is doing, basically.
    # "http://en.wikipedia.org/w/api.php/?action=query&titles={0}&prop=revisions&rvprop=flags|timestamp|user|size|ids&rvlimit=500&format=json&continue=".format(title)
    wp_api_url = "http://en.wikipedia.org/w/api.php/"

    # list_parameters = {'action' : 'query',
    #               'generator' : 'allpages',
    #               'prop' : 'pageassessments',
    #               'rvprop' : 'flags|timestamp|user|size|ids',
    #               'rvlimit' : 500,
    #               'format' : 'json',
    #               'continue' : ''}

    title_parameters = {'action' : 'query',
                  'titles' : title,
                  'prop' : 'revisions',
                  'rvprop' : 'flags|timestamp|user|size|ids',
                  'rvlimit' : 500,
                  'format' : 'json',
                  'continue' : '' }
    while True:
        # the first line open the urls but also handles unicode urls
        call = requests.get(wp_api_url, params=title_parameters)
        # call = requests.get(wp_api_url, params=list_parameters)
        api_answer = call.json()

        # get the list of pages from the json object
        pages = api_answer["query"]["pages"]

        # for every page, (there should always be only one) get its revisions:
        for page in pages.keys():
            query_revisions = pages[page]["revisions"]

            # Append every revision to the revisions list
            for rev in query_revisions:
                revisions.append(rev)

        # 'continue' tells us there's more revisions to add
        if 'continue' in api_answer:
            # replace the 'continue' parameter with the contents of the
            # api_answer dictionary.
            title_parameters.update(api_answer['continue'])
            # list_parameters.update(api_answer['continue'])
        else:
            break

    for r in revisions:
      if 'anon' in r:
        r['user'] = "Anon:" + r['user']
      if 'userhidden' in r:
        r['user'] = "Hidden"

    return(revisions)

def create_article_trajectory_graph(revisions, directed=True):
  if directed:
    g = nx.DiGraph()
  else:
    g = nx.Graph()

  for i in range(len(revisions)):
    # if weighted:
    #     if g.has_edge(revisions[i]['user'], revisions[i-1]['user']):
    #         g[revisions[i]['user']][revisions[i-1]['user']]['weight'] += 1
    #     else:
    #         g.add_edge(revisions[i]['user'], revisions[i-1]['user'], weight=1)
    # else:
    g.add_edge(revisions[i]['user'], revisions[i-1]['user'])

  return g

"""# Data Frame Constrution"""

diameter = nx.algorithms.distance_measures.diameter

def average_closeness(g):
  return statistics.mean(nx.algorithms.centrality.closeness_centrality(g).values())

def average_clustering(g):
  return statistics.mean(nx.algorithms.cluster.clustering(g).values())

def average_betweenness(g):
  return statistics.mean(nx.networkx.algorithms.centrality.betweenness_centrality(g).values())

def construct_dataframe(article_titles):
  rows = [create_article_row(title) for title in article_titles]
  return pd.DataFrame(rows, columns = ['title', 'diameter', 'closeness',
                                       'clustering', 'betweenness',
                                       'edit count', 'editor count',
                                       'article size']).set_index('title')

def create_article_row(title):
  print(title)
  revisions = get_article_revisions(title)
  graph = create_article_trajectory_graph(revisions, directed=False) #NOTE HARDCODING
  return (
    title,
    diameter(graph),
    average_closeness(graph),
    average_clustering(graph),
    average_betweenness(graph),
    len(revisions), #num edits
    len(graph), #num editors
    revisions[0]['size'] #article length in bytes
  )

"""# Create DFs"""

with open('./data/DF-All-FA900.pkl', 'rb') as f:
  df = pickle.load(f)

lst = list(df["title"])
df_undirected = construct_dataframe(lst)

with open('./data/DF-All-Undirected-NoClass.pkl', 'wb') as f:
   pickle.dump(df_undirected, f)

df_base = df[["title", "class", "class_alpha"]]
df_full = df_undirected.join(df_base.set_index("title"))
with open('./data/DF-All-Undirected.pkl', 'wb') as f:
   pickle.dump(df_full, f)
