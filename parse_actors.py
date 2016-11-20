#!/usr/bin/env python3

from collections import defaultdict
import io
import re
import sys


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
    print('Parsed ', len(data), 'actors')
    print('Parsed ', len(data_r), 'movies')

top250 = [line.strip() for line in open('top250.txt', 'r', encoding='latin-1')]
REGEX = re.compile('|'.join(x.replace('(', '\\(').replace(')', '\\)')
                    for x in top250))

print('parsed top 250', len(top250))

actor = None
movies = set()

data = defaultdict(set)

#stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='latin-1')

for idx, line in enumerate(stdin, 1):
    # Remove trailing whitespace
    line = line.rstrip()
    if idx < 240 or idx >= 20494549:
        # Actual data starts on line 240 and ends on
        continue
    if not line:
        if movies:
            data[actor] |= movies
            print(actor, repr(movies))
        actor = None
        movies = set()
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
        if movie_title:
            movies.add(movie_title)
    except Exception as ex:
        print(repr(debug))
        summarize()
        raise ex

data_r = defaultdict(set)
for actor, movie_set in data.items():
    for movie in movie_set:
        data_r[movie].add(actor)

summarize()
