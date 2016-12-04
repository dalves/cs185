#!/usr/bin/env python3

from collections import defaultdict
from itertools import combinations
import bisect
import colorsys
import copy
import io
import itertools
import json
import pickle
import random
import re
import string
import sys

from model import Actor, Graph, Movie

TRUE = lambda x: True

def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def load_graph():
    with open('data.bin', 'rb') as infile:
        graph = pickle.load(infile)
        graph.restore()
        return graph


def distribution(data):
    dist = [0] * 11
    for d in data:
        dist[int(d)] += 1
    total = len(data)
    dist = [int(100 * x / total) for x in dist]
    return dist


def hsv_to_rgb(h, s, v):
    # h in [0, 1] 0=red .16=yellow .33=green .5=cyan .66=blue .83=magenta
    # s in [0, 1]
    # v in [0, 1]
    result = colorsys.hsv_to_rgb(h, s, v)
    result = [hex(int(255.99 * x))[2:] for x in result]
    result = ['0' + r if len(r) == 1 else r for r in result]
    return '#' + ''.join(result)


def sanitize(s):
    OK = set(string.ascii_letters + ' .,-')
    safe = ''.join(c for c in s if c in OK)
    return safe


def render_actor_node(a):
    prestige = sum(m.stars_pct for m in a.movies)
    w = h = int(10 + prestige / 50)
    average_rating = sum(m.stars_pct / 10 for m in a.movies) / len(a.movies)
    color = hsv_to_rgb(.5 * average_rating / 10, 1, 1)
    return """
    node [
        id {}
        label "{}"
        graphics [
            type "square"
            w {}
            h {}
            fill "{}"
        ]
    ]
    """.format(id(a), sanitize(a.name), w, h, color)


def render_movie_node(m):
    w = h = int(20 + len(m.actors))
    color = hsv_to_rgb(.5 * m.stars_pct / 100, 1, 1)
    return """
    node [
        id {}
        label "{}"
        graphics [
            type "oval"
            w {}
            h {}
            fill "{}"
        ]
    ]
    """.format(id(m), sanitize(m.name), w, h, color)


def gml_header():
    return """
graph
[
    directed 0
    """


def render_edge(actor, movie):
    return """
    edge [
        source {}
        target {}
        graphics [
            fill "#666666"
        ]
    ]
    """.format(id(actor), id(movie))


def summarize(name, graph):
    edges = sum(len(a.movies) for a in graph.actors)
    nodes = len(graph.movies) + len(graph.actors)
    print(name, ' nodes:', nodes, 'edges: ', edges)


def render_graph(graph, filename):
    result = [gml_header()]

    for actor in graph.actors:
        result.append(render_actor_node(actor))

    for movie in graph.movies:
        result.append(render_movie_node(movie))

    for actor in graph.actors:
        for movie in actor.movies:
            result.append(render_edge(actor, movie))
    result.append(']')

    with open(filename, 'w') as out:
        log('Writing to ', filename)
        out.write('\n'.join(result))
        out.close()
        print('Wrote', len(graph.actors), 'actors,',
                len(graph.movies), 'movies,',
                sum(len(a.movies) for a in graph.actors), 'edges')


def render_partial(graph, filename, movie_predicate=TRUE, actor_predicate=TRUE):
    result = [gml_header()]

    movies = set()
    actors = set()
    for movie in graph.movies:
        if movie_predicate(movie):
            movies.add(movie)
            result.append(render_movie_node(movie))


    for actor in itertools.chain.from_iterable(m.actors for m in movies):
        if actor_predicate(actor) and not actor in actors:
            actors.add(actor)
            result.append(render_actor_node(actor))

    edge_count = 0
    for movie in movies:
        for actor in movie.actors & actors:
            edge_count += 1
            result.append(render_edge(actor, movie))

    result.append(']')

    with open(filename, 'w') as out:
        log('Writing to ', filename)
        out.write('\n'.join(result))
        out.close()
        log('Wrote',
                len(actors), 'actors,',
                len(movies), 'movies,',
                edge_count, 'edges\n')


if __name__ == '__main__':

    G = load_graph() # Full graph
    summarize('Full graph', G)

    log('Computing percentile scores... ', end='')
    stars = [m.stars for m in G.movies]
    stars.sort()
    for m in G.movies:
        idx = (bisect.bisect_left(stars, m.stars) / len(stars) +
               bisect.bisect_right(stars, m.stars) / len(stars)) * 50
        m.stars_pct = idx
    log('done')
    log('Before:', ' '.join(str(x) for x in distribution([m.stars for m in G.movies])))
    log('After: ', ' '.join(str(x) for x in distribution([m.stars_pct / 10 for m in G.movies])))

    #major_component = G.subgraph_containing_actor(
    #        G.actors_by_name['Grimwood, Matt'])

    #summarize('Major component', major_component)

    for year in range(1920, 2016, 10):
        movie_predicate = lambda m: m.year == year
        render_partial(G, str(year) + '.gml', movie_predicate)

    # Actors not in major component
    #fringe_actors = G.actors - major_component.actors
    #graph = G.subgraph_containing_actor(random.choice(list(fringe_actors)))
    #summarize('Minor subgraph', graph)
