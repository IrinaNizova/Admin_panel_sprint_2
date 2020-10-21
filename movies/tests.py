import random
from time import sleep


def coroutine(f):
    def wrap(*args,**kwargs):
        gen = f(*args,**kwargs)
        gen.send(None)
        return gen
    return wrap


def genre_sql(target):
    value = "SELECT GENRE"
    print(value)
    target.send(value)
    sleep(0.1)


def person_sql(target):
    value = "SELECT PERSON"
    print(value)
    target.send(value)
    sleep(0.1)


def film_sql(target):
    value = "SELECT FILM"
    print(value)
    target.send(value)
    sleep(random.randint(1, 3))

@coroutine
def make_sql(target):
    while value := (yield):
        print(value + " AND FILM")
        target.send(value + " AND FILM")


@coroutine
def transform_sql():
    while value := (yield):
        print(value.split(" "))


printer_sink = transform_sql()
even_filter = make_sql(printer_sink)
while True:
    genre_sql(even_filter)
    person_sql(even_filter)
    film_sql(even_filter)
