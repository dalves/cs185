movies = ['movie '+str(i) for i in range(1, 1000)]
actors = ['actor '+str(i) for i in range(1, 1000)]

from random import choice
from collections import Counter, defaultdict

acted_in = defaultdict(set)
for i in range(4000):
    print(choice(actors) + ';' +choice(movies))



