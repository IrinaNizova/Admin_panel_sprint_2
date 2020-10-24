import backoff
import json
import logging
from typing import List
from urllib.parse import urljoin

import requests
import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from state import JsonFileStorage
import sql_request
import config


logging.basicConfig(filename='loader.log', level=logging.INFO)


def coroutine(f):
    def wrap(*args, **kwargs):
        gen = f(*args, **kwargs)
        gen.send(None)
        return gen
    return wrap


class ESLoader:
    def __init__(self, url: str):
        self.url = url
        self.storage = JsonFileStorage()

    def _get_es_bulk_query(self, rows: List[dict]) -> List[str]:
        '''
        Подготавливает bulk-запрос в Elasticsearch
        '''
        prepared_query = []
        for row in rows:
            prepared_query.extend([
                json.dumps({'index': {'_index': row['id'], '_id': row['id']}}),
                json.dumps(row)
            ])
        return prepared_query

    @coroutine
    def load_to_es(self):
        '''
        Отправка запроса в ES и разбор ошибок сохранения данных
        '''
        while values := (yield):
            records, _type, last_time = values
            prepared_query = self._get_es_bulk_query(records)
            str_query = '\n'.join(prepared_query) + '\n'

            response = requests.post(
                urljoin(self.url, '_bulk'),
                data=str_query,
                headers={'Content-Type': 'application/x-ndjson'}
            )
            logging.info("Post {} records in url {}".format(len(str_query), urljoin(self.url, '_bulk')))
            json_response = json.loads(response.content.decode())
            for item in json_response['items']:
                error_message = item['index'].get('error')
                if error_message:
                    logging.error(error_message)

            self.storage.save_state(_type, last_time)


class ETL:

    def __init__(self, conn: _connection, es_loader: ESLoader):
        self.es_loader = es_loader
        self.conn = conn
        self.cursor = conn.cursor()
        self.storage = JsonFileStorage()

    @coroutine
    def _transform_row(self, target) -> dict:
        while results := (yield):
            data, _type, last_time = results
            items = []
            for result in data:
                _id, title, description, rating, _, created, modified, actors, writers, directors, genres = result
                actors_names = ", ".join([actor.split(";")[1] for actor in actors])
                actors = [{"id": actor.split(";")[0], "name": actor.split(";")[1]}
                          for actor in actors]
                writers_names = ", ".join([writer.split(";")[1] for writer in writers])
                writers = [{"id": writer.split(";")[0], "name": writer.split(";")[1]}
                           for writer in writers]
                director_names = ", ".join([director.split(";")[1] for director in directors])
                items.append({
                    'id': _id,
                    'genre': genres,
                    'writers': writers,
                    'actors': actors,
                    'actors_names': actors_names,
                    'writers_names': writers_names,
                    'rating': rating,
                    'title': title,
                    'director': director_names,
                    'description': description
                })
            target.send((items, _type, last_time))

    @backoff.on_exception(backoff.expo, psycopg2.DatabaseError, max_tries=8)
    def get_genre_ids(self, target):
        last_time = self.storage.get_state('genre')
        self.cursor.execute(sql_request.SQL_GENRE.format(last_time))
        genre_ids = self.cursor.fetchall()
        if not genre_ids:
            return
        genre_ids = "'" + "', '".join([_id for _id, time in genre_ids]) + "'"
        self.cursor.execute(sql_request.SQL_GENRE_FILM.format(last_time, genre_ids))
        genre_data = self.cursor.fetchall()
        target.send((genre_data, 'genre', str(genre_data[-1][-1])))

    @backoff.on_exception(backoff.expo, psycopg2.DatabaseError, max_tries=8)
    def get_person_ids(self, target):
        last_time = self.storage.get_state('person')
        self.cursor.execute(sql_request.SQL_PERSON.format(last_time))
        persons = self.cursor.fetchall()
        if not persons:
            return
        person_ids = "'" + "', '".join([_id for _id, time in persons]) + "'"
        self.cursor.execute(sql_request.SQL_PERSON_FILM.format(last_time, person_ids))
        person_data = self.cursor.fetchall()
        target.send((person_data, 'person', str(person_data[-1][-1])))

    @backoff.on_exception(backoff.expo, psycopg2.DatabaseError, max_tries=8)
    def get_film_ids(self, target):
        last_time = self.storage.get_state('film')
        self.cursor.execute(sql_request.SQL_FILM_IDS.format(last_time))
        film_data = self.cursor.fetchall()
        if not film_data:
            return
        target.send((film_data, 'film', str(film_data[-1][-1])))

    @backoff.on_exception(backoff.expo, psycopg2.DatabaseError, max_tries=8)
    @coroutine
    def get_films_data(self, target):
        while value := (yield):
            film_ids, _type, last_time = value
            ids = "'" + "', '".join([_id for _id, time in film_ids]) + "'"
            self.cursor.execute(sql_request.SQL_FILMS.format(ids))
            films_results = self.cursor.fetchall()
            logging.info("Get {} films from {}".format(len(films_results), _type))
            target.send((films_results, _type, last_time))

    def load(self):
        '''
        Основной метод для вашего ETL.
        Обязательно используйте метод load_to_es — это будет проверяться
        :param index_name: название индекса, в который будут грузиться данные
        '''
        loader = self.es_loader.load_to_es()
        transform = self._transform_row(loader)
        result = self.get_films_data(transform)
        self.get_genre_ids(result)
        self.get_person_ids(result)
        self.get_film_ids(result)


etl = ETL(psycopg2.connect(**config.postgres_dsl, cursor_factory=DictCursor),
          ESLoader(config.ETL_URL))
while True:
    etl.load()
