#!/usr/bin/env python3

from collections import defaultdict, deque
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

def uid(obj, next_id=[1000], memo={}):
    if obj not in memo:
        memo[obj] = next_id[0]
        next_id[0] += 1
    return memo[obj]


def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def load_graph(filename):
    with open(filename, 'rb') as infile:
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
    return tuple(int(255.99 * x) for x in result)


def sanitize(s):
    OK = set(string.digits + string.ascii_letters + ' .,-')
    safe = ''.join(c for c in s if c in OK)
    return safe


def render_actor_node(a):
    label = sanitize(a.name)
    #prestige = sum(m.stars_pct**2 / 100 for m in a.movies)
    size = 20
    average_rating = sum(m.stars_pct / 10 for m in a.movies) / len(a.movies)
    #r, g, b = hsv_to_rgb(.66 * average_rating / 10, 1, .85)
    r,g,b = 120, 120, 120
    return """
    <node id="{id}" label="{label}">
        <viz:color r="{r}" g="{g}" b="{b}" />
        <viz:size value="{size}" />
        <viz:shape value="square" />
    </node>
    """.format(id=uid(a), **locals())


def render_movie_node(m):
    label = sanitize(m.name)
    size = 20 + len(m.actors) / 10
    r, g, b = hsv_to_rgb(.66 * m.stars_pct / 100, 1, .85)
    return """
    <node id="{id}" label="{label}">
        <viz:color r="{r}" g="{g}" b="{b}" />
        <viz:size value="{size}" />
        <viz:shape value="disc" />
    </node>
    """.format(id=uid(m), **locals())

def render_edge(actor, movie, next_eid=[1], deleted=False):
    eid = next_eid[0]
    next_eid[0] += 1
    if not deleted:
        return """
        <edge id="{eid}" source="{aid}" target="{mid}" weight="1">
            <viz:color r="128" g="128" b="128" />
        </edge>
        """.format(eid=eid, aid=uid(actor), mid=uid(movie))
    else:
        return """
        <edge id="{eid}" source="{aid}" target="{mid}" weight="10">
            <viz:color r="255" g="0" b="0" />
        </edge>
        """.format(eid=eid, aid=uid(actor), mid=uid(movie))


def summarize(name, graph):
    edges = sum(len(a.movies) for a in graph.actors)
    nodes = len(graph.movies) + len(graph.actors)
    print(name, ' nodes:', nodes, 'edges: ', edges)


def header():
    return '<gexf xmlns="http://www.gexf.net/1.2draft" xmlns:viz="http://www.gexf.net/1.1draft/viz" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd" version="1.2"> <graph defaultedgetype="undirected"> <nodes>'



def render_graph(graph, filename):
    result = [header()]

    for actor in graph.actors:
        result.append(render_actor_node(actor))

    for movie in graph.movies:
        result.append(render_movie_node(movie))

    result.append('</nodes><edges>')

    for actor in graph.actors:
        for movie in actor.movies:
            result.append(render_edge(actor, movie))

    result.append('</edges></graph></gexf>')

    with open(filename, 'w') as out:
        log('Writing to ', filename)
        out.write('\n'.join(result))
        out.close()
        print('Wrote', len(graph.actors), 'actors,',
                len(graph.movies), 'movies,',
                sum(len(a.movies) for a in graph.actors), 'edges')


def render_partial(graph, filename, movie_predicate=TRUE, actor_predicate=TRUE):
    result = [header()]

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

    result.append('</nodes><edges>')

    edge_count = 0
    for movie in movies:
        for actor in movie.actors & actors:
            edge_count += 1
            result.append(render_edge(actor, movie))

    result.append('</edges></graph></gexf>')

    with open(filename, 'w') as out:
        log('Writing to ', filename)
        out.write('\n'.join(result))
        out.close()
        log('Wrote',
                len(actors), 'actors,',
                len(movies), 'movies,',
                edge_count, 'edges\n')


def neighbors(x):
    if isinstance(x, Actor):
        return x.movies
    return x.actors


if __name__ == '__main__':

    filename = sys.argv[-1] if len(sys.argv) > 1 else 'data.bin'

    G = load_graph(filename) # Full graph
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

    movies = list(G.movies)
    movies.sort(key=lambda x:(x.stars, x.votes), reverse=True)
    G.movies = set(movies[:100])
    G.cleanup()
    G.actors = set(a for a in G.actors if len(a.movies) > 2)
    G.cleanup()

    for m in G.movies:
        log('Movie{{"id": {}, "name": "{}", "year": {}, "stars": {}}}'.format(uid(m), m.name, m.year, m.stars))
    for a in G.actors:
        log('Actor{{"id": {}, "name": "{}"}}'.format(uid(a), a.name))

