import copy
import itertools

class Actor:

    def __init__(self, name, gender='M'):
        self.name = name
        self.gender = gender
        self.movies = set()

    def add_role(self, movie):
        self.movies.add(movie)
        movie.actors.add(self)

    def __str__(self):
        return 'Actor<{}>'.format(self.name)

class Movie:
    def __init__(self, name, year, stars, votes):
        self.name = name
        self.year = year
        self.stars = stars
        self.votes = votes
        self.actors = set()

    def __str__(self):
        return 'Movie<{} {} {} {}>'.format(
                self.name, self.year, self.stars, self.votes)

class Graph:
    def __init__(self):
        self.movies = set()
        self.actors = set()
        self.actors_by_name = {}
        self.movies_by_name = {}

    def add_movie(self, m):
        if not m.name:
            raise Exception('Movies need names')
        self.movies.add(m)
        m.id = 'M' + str(len(self.movies))
        self.movies_by_name[(m.name, m.year)] = m

    def add_actor(self, a):
        if not a.name:
            raise Exception('Actors need names')
        self.actors.add(a)
        a.id = 'A' + str(len(self.actors))
        self.actors_by_name[a.name] = a

    def get_actor(self, name):
        if name not in self.actors_by_name:
            raise Exception('Unknown actor: ' + name)
        return self.actors_by_name[name]

    def get_movie(self, name, year):
        try:
            year = int(year)
        except:
            raise Exception('Non-integer year? ' + name + ' >'+str(year) + '<')
        if (name, year) not in self.movies_by_name:
            raise UnknownMovieException('Unknown movie: ' + name + ' ' + str(year))
        return self.movies_by_name[(name, year)]

    @staticmethod
    def subgraph_containing_actor(actor):
        actors_seen = set()
        movies_seen = set()

        actor_queue = set([actor])
        movie_queue = set()

        while actor_queue or movie_queue:
            while actor_queue:
                a = actor_queue.pop()
                if a not in actors_seen:
                    actors_seen.add(a)
                    for m in a.movies:
                        movie_queue.add(m)

            while movie_queue:
                m = movie_queue.pop()
                if m not in movies_seen:
                    movies_seen.add(m)
                    for a in m.actors:
                        actor_queue.add(a)
        subgraph = Graph()
        subgraph.actors = actors_seen
        subgraph.movies = movies_seen
        subgraph.actors_by_name = {a.name: a for a in actors_seen}
        subgraph.movies_by_name = {m.name: m for m in movies_seen}
        return subgraph

    def clone(self):
        self.store()
        g = copy.deepcopy(self)
        self.restore()
        g.restore()
        return g

    def cleanup(self):
        changed = True
        mod = lambda: sum([
                len(self.actors),
                len(self.movies),
                sum(len(a.movies) for a in self.actors),
                sum(len(m.actors) for m in self.movies)
        ])

        while changed:
            before = mod()

            for a in self.actors:
                a.movies &= self.movies
            for m in self.movies:
                m.actors &= self.actors
            self.movies = set(m for m in self.movies if m.actors)
            self.actors = set(a for a in self.actors if a.movies)

            changed = mod() != before

    def store(self):
        # Replace object references with string ids to remove cycles
        actors_by_id = {a.id : a for a in self.actors}
        movies_by_id = {m.id : m for m in self.movies}
        for a in self.actors:
            a.movies = set(m.id for m in a.movies)
        for m in self.movies:
            m.actors = set(a.id for a in m.actors)

    def restore(self):
        # Restore object references
        actors_by_id = {a.id : a for a in self.actors}
        movies_by_id = {m.id : m for m in self.movies}
        for a in self.actors:
            a.movies = set(movies_by_id[m_id] for m_id in a.movies)
        for m in self.movies:
            m.actors = set(actors_by_id[a_id] for a_id in m.actors)


class UnknownMovieException(Exception):
    pass
