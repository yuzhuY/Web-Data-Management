import os.path

import psycopg2

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.escape import url_unescape
from tornado.options import define, options

conn = psycopg2.connect(dbname="webData", user="postgres")
cur = conn.cursor()

define('port', default=8000, help='run on the given port', type=int)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('search.html')


class movieHandler(tornado.web.RequestHandler):
    def get(self):
        idmovies = self.get_argument('movieId')
        title = tornado.escape.url_unescape(self.get_argument('title'), plus=True)

        if idmovies != '':
            try:
                idmovies = int(idmovies)
            except:
                self.render('return.html', returnInfo='Wrong input.')
                return

        if idmovies != '' and title != '':
            cur.execute('SELECT * FROM movies WHERE type=3 AND idmovies=%s AND title~*%s', (idmovies, title))
        elif idmovies != '':
            cur.execute('SELECT * FROM movies WHERE type=3 AND idmovies=%s', (idmovies,))
        elif title != '':
            cur.execute('SELECT * FROM movies WHERE type=3 AND title~*%s', (title,))
        else:
            self.render('return.html', returnInfo='Wrong input.')
            return

        movies = cur.fetchall()

        if len(movies) == 0:
            self.render('return.html', returnInfo='No result.')
            return

        moviesList = []
        for movie in movies:
            movieInfoList = [str(movie[0]), str(movie[1]), str(movie[2])]
            sql = 'SELECT name FROM series WHERE idmovies = %s' % (movie[0],)
            cur.execute(sql)
            seriesList = cur.fetchall()
            movieInfoList.append(seriesList)
            sql = 'SELECT genre FROM genres WHERE idgenres = ' \
                  'ANY(SELECT idgenres FROM movies_genres WHERE idmovies = %s)' % (movie[0],)
            cur.execute(sql)
            genersList = cur.fetchall()
            movieInfoList.append(genersList)
            sql = 'SELECT keyword FROM keywords WHERE idkeywords = ' \
                  'ANY(SELECT idkeywords FROM movies_keywords WHERE idmovies = %s)' % (movie[0],)
            cur.execute(sql)
            keywordsList = cur.fetchall()
            movieInfoList.append(keywordsList)
            sql = 'SELECT idactors, "character" FROM acted_in WHERE idmovies = %s' % (movie[0],)
            cur.execute(sql)
            actorsIdRoleList = cur.fetchall()
            actorsNameRoleList = []
            for actor in actorsIdRoleList:
                sql = 'SELECT fname, mname, lname FROM actors WHERE idactors = %s' % (actor[0],)
                cur.execute(sql)
                actorNameList = cur.fetchall()
                if actorNameList[0][1] is None:
                    actorName = '%s %s' % (actorNameList[0][0], actorNameList[0][2])
                else:
                    actorName = '%s %s %s' % (actorNameList[0][0], actorNameList[0][1], actorNameList[0][2])
                actorsNameRoleList.append((actorName, actor[1]))
            movieInfoList.append(actorsNameRoleList)
            moviesList.append(movieInfoList)

        self.render('movie.html', moviesList=moviesList)


class actorDetailHandler(tornado.web.RequestHandler):
    def get(self):
        idactors = str(self.get_argument('actorId'))
        fname = tornado.escape.url_unescape(self.get_argument('fname'), plus=False)
        lname = tornado.escape.url_unescape(self.get_argument('lname'), plus=False)

        if idactors == '' and fname == '' and lname == '':
            self.render('return.html', returnInfo='Wrong input.')
            return
        if idactors != '':
            try:
                idactors = int(idactors)
            except:
                self.render('return.html', returnInfo='Wrong input.')
                return

        sql = 'SELECT * FROM actors'
        first = True
        if idactors != '':
                sql = "%s WHERE idactors=%s" % (sql, idactors)
                first = False
        if fname != '':
            if first:
                sql = "%s WHERE fname~*'%s'" % (sql, fname)
                first = False
            else:
                sql = "%s AND fname~*'%s'" % (sql, fname)
        if lname != '':
            if first:
                sql = "%s WHERE lname~*'%s'" % (sql, lname)
            else:
                sql = "%s AND lname~*'%s'" % (sql, lname)

        cur.execute(sql)
        actors = cur.fetchall()
        if len(actors) == 0:
            self.render('return.html', returnInfo='No result.')
            return

        actorsList = []
        for actor in actors:
            actorInfoList = [actor[0]]
            if actor[3] is None:
                actorName = '%s %s' % (actor[2], actor[1])
            else:
                actorName = '%s %s %s' % (actor[2], actor[3], actor[1])
            actorInfoList.append(actorName)
            if actor[4] is None:
                actorInfoList.append('Female')
            else:
                actorInfoList.append('Male')

            sql = 'SELECT title, year FROM movies WHERE type=3 AND idmovies = ' \
                  'ANY(SELECT idmovies FROM acted_in WHERE idactors = %s) ORDER BY year DESC' % (actor[0],)
            cur.execute(sql)
            moviesList = cur.fetchall()
            actorInfoList.append(moviesList)
            actorsList.append(actorInfoList)

        self.render('actorDetail.html', actorsList=actorsList)


class actorBriefHandler(tornado.web.RequestHandler):
    def get(self):
        idactors = str(self.get_argument('actorId'))
        fname = tornado.escape.url_unescape(self.get_argument('fname'), plus=False)
        lname = tornado.escape.url_unescape(self.get_argument('lname'), plus=False)

        if idactors == '' and fname == '' and lname == '':
            self.render('return.html', returnInfo='Wrong input.')
            return
        if idactors != '':
            try:
                idactors = int(idactors)
            except:
                self.render('return.html', returnInfo='Wrong input.')
                return

        sql = 'SELECT * FROM actors'
        first = True
        if idactors != '':
                sql = "%s WHERE idactors=%s" % (sql, idactors)
                first = False
        if fname != '':
            if first:
                sql = "%s WHERE fname~*'%s'" % (sql, fname)
                first = False
            else:
                sql = "%s AND fname~*'%s'" % (sql, fname)
        if lname != '':
            if first:
                sql = "%s WHERE lname~*'%s'" % (sql, lname)
            else:
                sql = "%s AND lname~*'%s'" % (sql, lname)

        cur.execute(sql)
        actors = cur.fetchall()
        if len(actors) == 0:
            self.render('return.html', returnInfo='No result.')
            return

        actorsList = []
        for actor in actors:
            actorInfoList = [actor[0]]
            if actor[3] is None:
                actorName = '%s %s' % (actor[2], actor[1])
            else:
                actorName = '%s %s %s' % (actor[2], actor[3], actor[1])
            actorInfoList.append(actorName)

            sql = 'SELECT COUNT(idmovies) FROM acted_in WHERE idactors = %s' % (actor[0],)
            cur.execute(sql)
            movieNum = cur.fetchone()
            actorInfoList.append(movieNum[0])
            actorsList.append(actorInfoList)

        self.render('actorBrief.html', actorsList=actorsList)


class genreExplHandler(tornado.web.RequestHandler):
    def get(self):
        genre = self.get_argument('genre')
        year = str(self.get_argument('year'))
        endYear = str(self.get_argument('endYear'))

        if year != '':
            try:
                year = int(year)
            except:
                self.render('return.html', returnInfo='Wrong input.')
                return
        if endYear != '':
            try:
                endYear = int(endYear)
            except:
                self.render('return.html', returnInfo='Wrong input.')
                return

        if year == '' and endYear != '':
            self.render('return.html', returnInfo='Wrong input.')
            return
        elif endYear != '' and endYear < year:
            self.render('return.html', returnInfo='Wrong input.')
            return

        if year == '':
            sql = "SELECT idmovies, title, year FROM movies WHERE type=3 AND idmovies = " \
                  "ANY(SELECT idmovies FROM movies_genres WHERE idgenres = " \
                  "ANY(SELECT idgenres FROM genres WHERE genre = '%s')) ORDER BY year DESC" % (genre,)
        elif endYear != '':
            sql = "SELECT idmovies, title, year FROM movies WHERE type=3 AND year >= %s AND year <= %s AND idmovies = " \
                  "ANY(SELECT idmovies FROM movies_genres WHERE idgenres = " \
                  "ANY(SELECT idgenres FROM genres WHERE genre = '%s')) ORDER BY year DESC" % (year, endYear, genre)
        else:
            sql = "SELECT idmovies, title, year FROM movies WHERE type=3 AND year = %s AND idmovies = " \
                  "ANY(SELECT idmovies FROM movies_genres WHERE idgenres = " \
                  "ANY(SELECT idgenres FROM genres WHERE genre = '%s')) ORDER BY year DESC" % (year, genre)

        cur.execute(sql)
        moviesList = cur.fetchall()
        if len(moviesList) == 0:
            self.render('return.html', returnInfo='No result.')
            return

        self.render('genreExpl.html', moviesList=moviesList)


class genreStatHandler(tornado.web.RequestHandler):
    def get(self):
        year = self.get_argument('year')
        endYear = self.get_argument('endYear')

        if year == '':
            self.render('return.html', returnInfo='Wrong input.')
            return
        else:
            try:
                year = int(year)
            except:
                self.render('return.html', returnInfo='Wrong input.')
                return
        if endYear != '':
            try:
                endYear = int(endYear)
            except:
                self.render('return.html', returnInfo='Wrong input.')
                return

        if endYear != '' and endYear < year:
            self.render('return.html', returnInfo='Wrong input.')
            return

        genres = ['Documentary', 'Reality', 'Horror', 'Short',
                  'Thriller', 'Drama', 'Comedy', 'Musical',
                  'Talk', 'Crime', 'Mystery', 'News', 'Sport',
                  'Sci', 'Romance', 'Family', 'Biography', 'Music',
                  'Game', 'Adventure', 'War', 'Fantasy', 'Animation',
                  'Action', 'History', 'Adult', 'Western', 'Lifestyle',
                  'Film', '_', 'Experimental', 'Commercial', 'Erotica']

        numList = []
        for i in range(1, 34):
            if endYear == '':
                sql = 'SELECT COUNT(idmovies) FROM movies WHERE type=3 AND year=%s AND idmovies=' \
                      'ANY(SELECT idmovies FROM movies_genres WHERE idgenres=%s)' % (year, i)
            else:
                sql = 'SELECT COUNT(idmovies) FROM movies WHERE type=3 AND year>=%s AND year <= %s AND idmovies=' \
                      'ANY(SELECT idmovies FROM movies_genres WHERE idgenres=%s)' % (year, endYear, i)
            cur.execute(sql)
            numTuple = cur.fetchone()
            numList.append((genres[i-1], numTuple[0]))

        self.render('genreStat.html', genresList=numList)



if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r'/', IndexHandler),
            (r'/movie', movieHandler),
            (r'/actorDetail', actorDetailHandler),
            (r'/actorBrief', actorBriefHandler),
            (r'/genreExpl', genreExplHandler),
            (r'/genreStat', genreStatHandler)
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()