import psycopg2
from writeJson import writeJson
from compiler.ast import flatten

conn = psycopg2.connect(dbname='webData', user='postgres')
cur = conn.cursor()

sql = 'SELECT idmovies, title, year, type FROM movies'
cur.execute(sql)
movieResults = cur.fetchall()
total = len(movieResults)
count = 0.0
lastProgress = 0
print 'Progress: 0.00000000000'
for movie in movieResults:
    count += 1
    progress = count/total
    if progress == 1:
        print 'Complete!'
    if progress - lastProgress >= 0.01:
        print 'Progress: %s' % (str(100*progress),)
        lastProgress = progress

    if movie[3] != 3:
        continue
    rowDict = {'_id': movie[0], 'title': movie[1]}
    if movie[2] == '':
        rowDict['year'] = None
    else:
        rowDict['year'] = movie[2]
    sql = 'SELECT name FROM series WHERE idmovies = %s' % (str(movie[0]),)
    cur.execute(sql)
    seriesName = cur.fetchall()
    if not seriesName:
        rowDict['series'] = None
    else:
        rowDict['series'] = flatten(seriesName)

    sql = 'SELECT genre FROM genres WHERE idgenres = ' \
          'ANY(SELECT idgenres FROM movies_genres WHERE idmovies = %s)' % (str(movie[0]))
    cur.execute(sql)
    genreLables = cur.fetchall()
    if not genreLables:
        rowDict['genre'] = None
    else:
        rowDict['genre'] = flatten(genreLables)

    sql = 'SELECT keyword FROM keywords WHERE idkeywords = ' \
          'ANY(SELECT idkeywords FROM movies_keywords WHERE idmovies = %s)' % (str(movie[0]))
    cur.execute(sql)
    keywords = cur.fetchall()
    if not keywords:
        rowDict['keywords'] = None
    else:
        rowDict['keywords'] = flatten(keywords)

    sql = 'SELECT DISTINCT idactors FROM acted_in WHERE idmovies = %s' % (str(movie[0]))
    cur.execute(sql)
    actorIds = cur.fetchall()
    if not actorIds:
        rowDict['idactors'] = None
    else:
        rowDict['idactors'] = flatten(actorIds)

    writeJson('./movies.json', rowDict)

    progress = count/total
    if progress == 1:
        print 'Complete!'
    if progress - lastProgress >= 0.01:
        print 'Progress: %s' % (str(100*progress),)
        lastProgress = progress
