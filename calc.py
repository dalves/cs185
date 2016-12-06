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

def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def load_graph():
    with open('data.bin', 'rb') as infile:
        graph = pickle.load(infile)
        graph.restore()
        return graph

def save_graph(graph):
    with open('data.bin', 'wb') as out:
        pickle.dump(graph, out)


def distribution(data):
    dist = [0] * 1 + int(max(data))
    for d in data:
        dist[int(d)] += 1
    total = len(data)
    dist = [int(100 * x / total) for x in dist]
    return dist


def neighbors(x):
    if isinstance(x, Actor):
        return x.movies
    return x.actors

def shortest_paths(graph):
    INF = 1000000
    nodes = list(graph.actors | graph.movies)
    idx = {node:index for index, node in enumerate(nodes)}
    N = len(nodes)
    dist = [[INF] * N for _ in range(N)]
    for n in nodes:
        dist[idx[n]][idx[n]] = 0
        for adj in neighbors(n):
            dist[idx[n]][idx[adj]] = dist[idx[adj]][idx[n]] = 1
    for i in range(0, N):
        for j in range(0, N):
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    for n in nodes:
        dist_sum = 0
        reachable = 0
        for other in nodes:
            distance = dist[idx[n]][idx[other]]
            if distance != INF:
                reachable += 1
                dist_sum += distance
            n.closeness = reachable / dist_sum

    log('closeness distribution',
        ' '.join(str(x) for x in distribution([n.closeness * 10 for n in nodes])))

def actor_graph(graph, years):
    movies = set(m for m in graph.movies if m.year in years)
    adj = defaultdict(set)
    for m in movies:
        for a1, a2 in combinations(m.actors, 2):
            adj[a1].add(a2)
            adj[a2].add(a1)
    return adj

def count_triangles(year, before, after):
    numerator = [0, 0]
    denominator = [0, 0]
    idx = lambda tris: 0 if tris == 0 else 1


    for a1, a2 in combinations(before, 2):
        if a2 not in before[a1]:
            partial_triangles  = len(before[a1] & before[a2])
            i = idx(partial_triangles)
            denominator[i] += 1
            if a2 in after[a1]:
                numerator[i] += 1

    print(year, ',', ','.join(str(numerator[i] / denominator[i]) for i in range(len(numerator))))





if __name__ == '__main__':
    G = load_graph()

    for year in range(1940, 2011, 2):
        before = actor_graph(G, range(year, year + 1))
        after = actor_graph(G, range(year + 1, year + 6))
        count_triangles(year, before, after)



