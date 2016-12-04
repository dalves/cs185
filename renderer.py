#!/usr/bin/env python3

from collections import defaultdict
from itertools import combinations
import io
import json
import pickle
import random
import re
import sys

from model import Actor, Graph, Movie

def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def load_graph():
    with open('data.bin', 'rb') as infile:
        graph = pickle.load(infile)
        graph.restore()
        return graph

def render_actor_node(a):
    prestige = sum(m.stars for m in a.movies)
    w = h = (20 + prestige / 2) ** .5
    color = "#00ff00"
    return """
    node [
        id {}
        label "{}"
        type "rectangle"
        w {}
        h {}
        fill "{}"
    ]
    """.format(id(a), a.name, w, h, color)
#    return """
#    node [
#        id {}
#        label "{}"
#        graphics [
#            type "rectangle"
#            w {}
#            h {}
#            fill "{}"
#        ]
#    ]
#    """.format(id(a), a.name, w, h, color)


def render_movie_node(m):
    w = h = (20 + m.stars * 2) ** .5
    color = "#ff0000"
    return """
    node [
        id {}
        label "{}"
        graphics [
            type "rectangle"
            w {}
            h {}
            fill "{}"
        ]
    ]
    """.format(id(m), m.name, w, h, color)

def gml_header():
    return """
graph
[
    directed 1
    """

def render_edge(actor, movie):
    return """
    edge [
        source {}
        target {}
    ]
    """.format(id(actor), id(movie))

def summarize(name, graph):
    edges = sum(len(a.movies) for a in graph.actors)
    nodes = len(graph.movies) + len(graph.actors)
    print(name, ' nodes:', nodes, 'edges: ', edges)


if __name__ == '__main__':

    G = load_graph() # Full graph
    summarize('Full graph', G)

    major_component = G.subgraph_containing_actor(
            G.actors_by_name['Grimwood, Matt'])

    summarize('Major component', major_component)

    graph = major_component

    # Filter out movies with few votes
    print(min(m.votes for m in G.movies))

    # Actors not in major component
    #fringe_actors = G.actors - major_component.actors
    #graph = G.subgraph_containing_actor(random.choice(list(fringe_actors)))
    #summarize('Minor subgraph', graph)


    result = []
    result.append(gml_header())

    for actor in graph.actors:
        result.append(render_actor_node(actor))

    for movie in graph.movies:
        result.append(render_movie_node(movie))

    for actor in graph.actors:
        for movie in actor.movies:
            result.append(render_edge(actor, movie))

    result.append(']')

    out_filename = sys.argv[-1] if len(sys.argv) > 1 else 'test.gml'

    with open(out_filename, 'w') as out:
        log('Writing to ', out_filename)
        out.write('\n'.join(result))
        out.close()

