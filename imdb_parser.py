#!/usr/bin/env python3

from collections import defaultdict
from itertools import combinations
import pickle
import io
import re
import sys
import json

from model import Actor, Graph, Movie, UnknownMovieException

sys.setrecursionlimit(10000)

def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def parse_movie_title(string):
    # Ignore TV shows
    if re.search('#[0-9]+\\.[0-9]+', string):
        return None

    parsed = re.match('"([^"]*)" \\(([0-9]+)\\)', string)
    if not parsed:
        # Backup regex
        parsed = re.match('(.*) \\(([0-9]+)\\)', string)

    if parsed:
        name = parsed.group(1)
        year = parsed.group(2)
        if '?' in year:
            return None
        return name, year
    return None
    #raise Exception('Unable to parse movie: ' + string)

def parse_movies(graph, filename):
    #            distr.      votes       rating        title        year
    REGEX = '[ ]+[*.0-9]+[ ]+([0-9]+)[ ]+([.0-9]+)  \\"?(.*)\\"? \\(([0-9]+)\\)'
    parse_fail_count = 0
    with open(filename, encoding='latin-1', mode='r') as infile:
        for idx, line in enumerate(infile, 1):
            parsed = re.match(REGEX, line)
            if parsed is not None:
                votes, stars, title, year = parsed.groups()
                if int(votes) >= 1000:
                    movie = Movie(title, int(year), float(stars), int(votes))
                    graph.add_movie(movie)
            else:
                #print('Failed to parse',line)
                parse_fail_count += 1
        #log('Parse failed for ', parse_fail_count, 'out of', idx)


def parse_actors(graph, filename):
    actor = None
    with open(filename, encoding='latin-1', mode='r') as infile:
        for idx, line in enumerate(infile, 1):
            # Remove trailing whitespace
            line = line.rstrip()
            if not line:
                if actor is not None and actor.movies:
                    graph.add_actor(actor)
                actor = None
                continue

            try:
                fields = line.split('\t')
                debug = [idx, line] + fields
                if fields[0]:
                    if actor == None:
                        actor = Actor(fields.pop(0))
                    else:
                        raise Exception('Unexpected actor on line ' + str(idx) +
                                        ':\n     ' + repr(fields))

                # Strip leading blank fields
                while fields and not fields[0]:
                    fields = fields[1:]

                # More than one field
                if len(fields) > 1 or len(fields) == 0:
                    raise Exception('Unable to parse movie title on line ' +
                                    str(idx) + ':\n     ' + repr(fields) )


                result = parse_movie_title(fields[0])
                if not result:
                    continue
                movie_title, year = result
                try:
                    m = graph.get_movie(movie_title, year)
                    actor.add_role(m)
                except UnknownMovieException as ex:
                    pass


            except Exception as ex:
                log(repr(debug))
                raise ex


if __name__ == '__main__':
    graph = Graph()
    actor_file, movie_file = sys.argv[1:]
    parse_movies(graph, movie_file)
    parse_actors(graph, actor_file)
    graph.store()
    with open('data.bin', 'wb') as out:
        pickle.dump(graph, out)

