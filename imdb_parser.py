#!/usr/bin/env python3

from collections import defaultdict
from itertools import combinations
import io
import re
import sys
import json

top250 = [line.strip() for line in open('top250.txt', 'r', encoding='latin-1')]
REGEX = re.compile('|'.join(x.replace('(', '\\(').replace(')', '\\)')
                    for x in top250))

def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def parse_title(string):
    m = re.match(REGEX, string)
    if m:
        return m.group(0)
    return None

    #    if string.startswith(t):
    #        return t
    #return None

    # Ignore TV shows
    #if re.search('#[0-9]+\\.[0-9]+', string):
    #    return None

    #parsed = re.match('"([^"]*)" (\\([?0-9]+.*\\))', string)
    #if parsed:
    #    return '{} ({})'.format(parsed.group(1).strip(), parsed.group(2))
    #parsed = re.match('(.*) \\(([?0-9]+.*)\\)', string)
    #if parsed:
    #    return '{} ({})'.format(parsed.group(1).strip(), parsed.group(2))
    #raise Exception('Unable to parse title: ' + string)

def summarize():
    log('Parsed ', len(actors_to_movies), 'actors')
    log('Parsed ', len(movies_to_actors), 'movies')



def parse_stdin():
    actors_to_movies = {}
    actor = None
    movies = set()
    stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='latin-1')

    for idx, line in enumerate(stdin, 1):
        # Remove trailing whitespace
        line = line.rstrip()
        if idx < 240 or idx >= 20494549:
            # Actual data starts on line 240 and ends on
            continue
        if not line:
            if movies:
                actors_to_movies[actor] = movies
            actor = None
            movies = []
            continue

        try:
            fields = line.split('\t')
            debug = [idx, line] + fields
            if fields[0]:
                if actor == None:
                    actor = fields.pop(0)
                else:
                    raise Exception('Unexpected actor on line ' + str(idx) +
                                    ':\n     ' + repr(fields))
            while fields and not fields[0]:
                fields = fields[1:]
            if len(fields) > 1 or len(fields) == 0:
                raise Exception('Unable to parse movie title on line ' +
                                str(idx) + ':\n     ' + repr(fields) )
            movie_title = parse_title(fields[0])
            if movie_title and movie_title not in movies:
                movies.append(movie_title)
        except Exception as ex:
            log(repr(debug), file=sys.stderr)
            summarize()
            raise ex
    return actors_to_movies


def output_gml_actors_as_nodes_movies_as_nodes():
    print('graph')
    print('[')
    print('  directed 0')
    for actor in actors_to_movies.keys():
        print('  node')
        print('  [')
        print('  id ' + actors_to_ids[actor])
        print('  label "' + actor + '"')
        print('  ]')

    for movie, actor_list in movies_to_actors.items():
        print('  node')
        print('  [')
        print('  id ' + movies_to_ids[movie])
        print('  label "' + movie + '"')
        print('  ]')
        for actor in actor_list:
            print('  edge')
            print('  [')
            print('  source ' + actors_to_ids[actor])
            print('  target ' + movies_to_ids[movie])
            print('  ]')
    print(']')


def output_gml_actors_as_nodes_movies_as_edges():
    print('graph')
    print('[')
    print('  directed 0')
    for actor in actors_to_movies.keys():
        print('  node')
        print('  [')
        print('  id ' + actors_to_ids[actor])
        print('  label "' + actor + '"')
        print('  ]')

    for movie, actor_list in movies_to_actors.items():
        for actor1, actor2 in combinations(actor_list, 2):
            print('  edge')
            print('  [')
            print('  source ' + actors_to_ids[actor1])
            print('  target ' + actors_to_ids[actor2])
            print('  label "' + movie + '"')
            print('  ]')
    print(']')

if __name__ == '__main__':
    actors_to_movies = parse_stdin()

    # Restrict to actors appearing in more than one movie
    actors_to_movies = {k:v for k,v in actors_to_movies.items() if len(v) > 1}

    movies_to_actors = {}
    for actor, movie_set in actors_to_movies.items():
        for movie in movie_set:
            if movie not in movies_to_actors:
                movies_to_actors[movie] = []
            if actor not in movies_to_actors[movie]:
                movies_to_actors[movie].append(actor)

    actors_to_ids = {name : 'A'+str(idx) for idx, name in enumerate(actors_to_movies.keys())}
    movies_to_ids = {name : 'M'+str(idx) for idx, name in enumerate(movies_to_actors.keys())}

    output_gml_actors_as_nodes_movies_as_nodes()
