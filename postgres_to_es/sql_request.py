SQL_PERSON = """SELECT id, modified FROM content.person
WHERE modified > '{}'
ORDER BY modified
LIMIT 100; """

SQL_PERSON_FILM = """
SELECT fw.id, fw.modified
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
WHERE fw.modified > '{}' AND pfw.person_id IN ({})
ORDER BY fw.modified
LIMIT 100; """

SQL_GENRE = """SELECT id, modified FROM content.genre
WHERE modified > '{}'
ORDER BY modified
LIMIT 100; """

SQL_GENRE_FILM = """
SELECT fw.id, fw.modified
FROM content.film_work fw
LEFT JOIN content.genre_film_work gfw ON gfw.filmwork_id = fw.id
WHERE fw.modified > '{}' AND gfw.genre_id IN ({})
ORDER BY fw.modified
LIMIT 100; """

SQL_FILM_IDS = """
SELECT id, modified FROM content.film_work
WHERE modified > '{}'
ORDER BY modified
LIMIT 100; """

SQL_FILMS = """
SELECT fw.id, fw.title, fw.description, fw.rating, fw.type, fw.created, 
    fw.modified, p_a.actors, p_w.writers, p_d.directors, g.genres
FROM content.film_work fw,
LATERAL (
   SELECT ARRAY (
      SELECT p.id || ';' || p.full_name
      FROM   person p
      LEFT JOIN   person_film_work pfw  ON p.id = pfw.person_id
      WHERE  pfw.film_work_id = fw.id AND pfw.role = 'actor'
      ) AS actors
   ) p_a,
LATERAL (
   SELECT ARRAY (
      SELECT p.id || ';' || p.full_name
      FROM   person p
      LEFT JOIN   person_film_work pfw  ON p.id = pfw.person_id
      WHERE  pfw.film_work_id = fw.id AND pfw.role = 'writer'
      ) AS writers
   ) p_w,
LATERAL (
   SELECT ARRAY (
      SELECT p.id || ';' || p.full_name
      FROM   person p
      LEFT JOIN   person_film_work pfw  ON p.id = pfw.person_id
      WHERE  pfw.film_work_id = fw.id AND pfw.role = 'director'
      ) AS directors
   ) p_d,
LATERAL (
   SELECT ARRAY (
      SELECT g.name
      FROM   genre g
      LEFT JOIN   genre_film_work gf  ON g.id = gf.genre_id
      WHERE  gf.filmwork_id = fw.id
      ) AS genres
   ) g
WHERE fw.id IN ({}); """
