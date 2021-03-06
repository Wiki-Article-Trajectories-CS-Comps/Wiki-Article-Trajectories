import networkx as nx
import statistics

from operator import itemgetter
import pandas as pd
import pickle
import math

def get_unexpected_betweenness(g):
  # for G in G_list:
  degree_dict = dict(g.degree(g.nodes()))
  sorted_degree = sorted(degree_dict.items(), key=itemgetter(1), reverse=True)
  nx.set_node_attributes(g, degree_dict, 'degree')
#   top_degree = [a[0] for a in sorted_degree[:max(5, int(len(sorted_degree)/50))]]

  betweenness_dict = nx.betweenness_centrality(g) # Run betweenness centrality
  #eigenvector_dict = nx.eigenvector_centrality(G) # Run eigenvector centrality
  # Assign each to an attribute in the network
  nx.set_node_attributes(g, betweenness_dict, 'betweenness')
  # nx.set_node_attributes(G, eigenvector_dict, 'eigenvector')
  # First get the top 20 nodes by betweenness as a list
  sorted_betweenness = sorted(betweenness_dict.items(), key=itemgetter(1), reverse=True)
  brokers = []
  for i in range(16):
    top_degree = [a[0] for a in sorted_degree[:i]]
    top_betweenness = sorted_betweenness[:i]
#   top_betweenness = sorted_betweenness[:max(5, int(len(sorted_betweenness)/50))]

    num_unex_brokers = 0
    # Then find and print their degree
    for tb in top_betweenness: # Loop through top_betweenness
        # degree = degree_dict[tb[0]] # Use degree_dict to access a node's degree
        if tb[0] not in top_degree:
            # print("Name:", tb[0], "| Betweenness Centrality:", tb[1], "| Degree:", degree)
            # brokers.append((tb[1], degree))
            num_unex_brokers += 1
    brokers.append(num_unex_brokers)
    
  return brokers


def construct_row(title):
    graph = graph_dict[title]
    brokers = get_unexpected_betweenness(graph)
    lst = [title,]

    n = len(brokers)

    for i in range(1, 16):
        lst.append( statistics.mean(brokers[:min(n, i)]))

    return lst

def construct_dataframe(titles):

    cols = ["T{} Avg Unexpected Brokers".format(i) for i in range(1, 16)] #+ ["Edit Size>i".format(i) for i in range(2, 16)]
    
    row_lst = []
    for i, title in enumerate(titles):
        print(i, title)
        row_lst.append(construct_row(title))

    return pd.DataFrame(row_lst, columns = ['title', *cols] ).set_index('title')


with open('../../../shared/data/article_titles_all.pkl', 'rb') as f:
#with open('../data/article_titles_all.pkl', 'rb') as f:
    class_lists  = pickle.load(f)
titles = [item for sublist in class_lists for item in sublist]

with open('../../../shared/data/graph_dictionary_all.pkl', 'rb') as f:
# with open('../data/graph_dictionary_all.pkl', 'rb') as f:
 graph_dict = pickle.load(f)

df = construct_dataframe(titles)

with open('../data/df_unexpected_brokers_stats.pkl', 'wb') as f:
    pickle.dump(df, f)
