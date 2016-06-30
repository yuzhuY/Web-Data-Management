import psycopg2
from writeJson import writeJson
from compiler.ast import flatten

conn = psycopg2.connect(dbname='webData', user='postgres')
cur = conn.cursor()

sql = 'SELECT * FROM actors'
cur.execute(sql)
actorResults = cur.fetchall()
total = len(actorResults)
count = 0.0
lastProgress = 0
print 'Progress: 0.00000000000'
for actor in actorResults:
    count += 1
    progress = count/total
    if progress == 1:
        print 'Complete!'
    if progress - lastProgress >= 0.01:
        print 'Progress: %s' % (str(100*progress),)
        lastProgress = progress

    rowDict = {'_id': actor[0]}
    if actor[1] == '':
        rowDict['lname'] = None
    else:
        rowDict['lname'] = actor[1]
    if actor[2] == '':
        rowDict['fname'] = None
    else:
        rowDict['fname'] = actor[2]
    if actor[3] == '':
        rowDict['mname'] = None
    else:
        rowDict['mname'] = actor[3]
    if actor[4] == '':
        rowDict['gender'] = None
    else:
        rowDict['gender'] = actor[4]

    sql = 'SELECT DISTINCT idmovies, "character" FROM acted_in WHERE idactors = %s' % (actor[0],)
    cur.execute(sql)
    movies = cur.fetchall()
    movieList = []
    for movie in movies:
        sql = 'SELECT title FROM movies WHERE idmovies = %s' % (movie[0])
        cur.execute(sql)
        title = cur.fetchone()
        subDict = {'role': movie[1], 'title': title[0]}
        movieList.append(subDict)
    rowDict['movies'] = movieList

    writeJson('./actors.json', rowDict)

    progress = count/total
    if progress == 1:
        print 'Complete!'
    if progress - lastProgress >= 0.01:
        print 'Progress: %s' % (str(100*progress),)
        lastProgress = progress
