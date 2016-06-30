import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

from py2neo import Graph, authenticate

authenticate("localhost:7474", "neo4j", "jingle")
graph = Graph()

define("port", default=8000, help="run on the given port", type=int)

class searchHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('search.html')

class movieHandler(tornado.web.RequestHandler):
    def get(self):
        idmovies = self.get_argument('movieId')
        title = tornado.escape.url_unescape(self.get_argument('title'), plus=True)

        if idmovies == '' and title == '':
            self.write('Wrong input.')
            return

        if idmovies != '':
            try:
                idmovies = int(idmovies)
            except:
                self.write('Wrong input.')
                return

        if idmovies != '':
            if title != '':
                query = ('\n'
                         '        MATCH (a:ACTOR)-[r:acted_in]->(m:MOVIE{id:"%s",type:"3"})\n'
                         '        WHERE m.title CONTAINS "%s"\n'
                         ) % (idmovies, title)
                query_g = ('\n'
                           '        MATCH (g:GENRE)<-[:has_genre]-(m:MOVIE{id:"%s",type:"3"})\n'
                           '        WHERE m.title CONTAINS "%s"\n'
                           '        RETURN g.genre\n'
                           ) % (idmovies, title)
                query_k = ('\n'
                           '        MATCH (k:KEYWORD)<-[:has_keyword]-(m:MOVIE{id:"%s",type:"3"})\n'
                           '        WHERE m.title CONTAINS "%s"\n'
                           '        RETURN k.keyword\n'
                           ) % (idmovies, title)
                # query_s = ('\n'
                #            '        MATCH (s:SERIES)<-[:has_series]-(m:MOVIE{id:"%s",type:"3"})\n'
                #            '        WHERE m.title CONTAINS "%s"\n'
                #            '        RETURN s.series\n'
                #            ) % (idmovies, title)
            else:
                query = ('\n'
                         '        MATCH (a:ACTOR)-[r:acted_in]->(m:MOVIE{id:"%s",type:"3"})\n'
                         ) % (idmovies,)
                query_g = ('\n'
                           '        MATCH (g:GENRE)<-[:has_genre]-(m:MOVIE{id:"%s",type:"3"})\n'
                           '        RETURN g.genre\n'
                           ) % (idmovies,)
                query_k = ('\n'
                           '        MATCH (k:KEYWORD)<-[:has_keyword]-(m:MOVIE{id:"%s",type:"3"})\n'
                           '        RETURN k.keyword\n'
                           ) % (idmovies,)
                # query_s = ('\n'
                #            '        MATCH (s:SERIES)<-[:has_series]-(m:MOVIE{id:"%s",type:"3"})\n'
                #            '        RETURN s.series\n'
                #            ) % (idmovies, title)

            query_return = (
            'RETURN m.id,m.title,m.year,collect(distinct (a.fname + " " + a.lname + "--" + r.character)),r.billing_address\n')

            genres = graph.cypher.execute(query_g)
            if genres:
                query = query + (
                    'MATCH (g:GENRE)<-[:has_genre]-(m)\n')
                query_return = query_return + (',collect(distinct g.genre)\n')
            else:
                query_return = query_return + (',0\n')

            keywords = graph.cypher.execute(query_k)
            if keywords:
                query = query + (
                    'MATCH (k:KEYWORD)<-[:has_keyword]-(m)\n')
                query_return = query_return + (',collect(distinct k.keyword)\n')
            else:
                query_return = query_return + (',1\n')

            # series = graph.cypher.execute(query_s)
            # if series:
            #     query = query + (
            #         'MATCH (s:SERIES)<-[:has_series]-(m)\n')
            #     query_return = query_return + (',collect(distinct s.series)\n')
            # else:
            #     query_return = query_return + (',1\n')

            query_return = query_return + (
                'ORDER BY r.billing_address ASC;\n'
            )
            query = query + query_return
            movies = graph.cypher.execute(query)
        elif idmovies == '' and title != '':
            query_vague = ('\n'
                     '        MATCH (m:MOVIE{type:"3"})\n'
                     '        WHERE m.title CONTAINS "%s"\n'
                     '        RETURN m.id,m.title,m.year,92,93,90,91\n'
                     '        ORDER BY m.year\n'
                     ) % (title, )
            movies = graph.cypher.execute(query_vague)

        self.render('movie.html', moviesList=movies)


class actorDetailHandler(tornado.web.RequestHandler):
    def get(self):
        idactors = self.get_argument('actorId')
        fname = tornado.escape.url_unescape(self.get_argument('fname'), plus=True)
        lname = tornado.escape.url_unescape(self.get_argument('lname'), plus=True)

        if (idactors == '' and fname == '' and lname == ''): #or \
                # (not isinstance(idactors, int) and idactors != ''):
            self.write('Wrong input!')
            return

        if idactors != '':
            try:
                idactors = int(idactors)
            except:
                self.write('Wrong input.')
                return

        if idactors != '':
            query = """
            MATCH (m:MOVIE)<-[r:acted_in]-(a:ACTOR{id:"%s"})
            WHERE a.fname CONTAINS "%s" AND a.lname CONTAINS "%s"
            RETURN a.fname,a.lname,a.gender,collect(distinct m.title),m.year
            ORDER BY m.year ASC;
            """ % (idactors, fname, lname)
        else:
            query = """
            MATCH (m:MOVIE)<-[r:acted_in]-(a:ACTOR)
            WHERE a.fname CONTAINS "%s" AND a.lname CONTAINS "%s"
            RETURN a.fname,a.lname,a.gender,collect(distinct m.title),m.year
            ORDER BY m.year ASC;
            """ % (fname, lname)


        actors = graph.cypher.execute(query)

        self.render('actorDetail.html', actorsList=actors)


class actorBriefHandler(tornado.web.RequestHandler):
    def get(self):
        idactors = self.get_argument('actorId')
        fname = tornado.escape.url_unescape(self.get_argument('fname'), plus=True)
        lname = tornado.escape.url_unescape(self.get_argument('lname'), plus=True)

        if (idactors == '' and fname == '' and lname == ''): #or \
                # (not isinstance(idactors, int) and idactors != ''):
            self.write('Wrong input!')
            return

        if idactors != '':
            try:
                idactors = int(idactors)
            except:
                self.write('Wrong input.')
                return

        if idactors != '':
            query = """
            MATCH (m:MOVIE)<-[r:acted_in]-(a:ACTOR{id:"%s"})
            WHERE a.fname CONTAINS "%s" AND a.lname CONTAINS "%s"
            RETURN a.fname,a.lname,collect(distinct m.title),count(distinct m.title)
            """ % (idactors, fname, lname)
        else:
            query = """
            MATCH (m:MOVIE)<-[r:actor_acted_in]-(a:ACTOR)
            WHERE a.fname CONTAINS "%s" AND a.lname CONTAINS "%s"
            RETURN a.fname,a.lname,collect(distinct m.title),count(distinct m.title)
            """ % (fname, lname)

        actors = graph.cypher.execute(query)

        self.render('actorBrief.html', actorsList=actors)


class genreExplHandler(tornado.web.RequestHandler):
    def get(self):
        genre = self.get_argument('genre')
        year = self.get_argument('year')
        endYear = self.get_argument('endYear')

        if endYear == '':
            endYear = year

        if (year == '' and endYear == ''):
            self.write('Wrong input!')
            return

        query = """
        MATCH (g:GENRE{genre:"%s"})<-[:has_genre]-(m:MOVIE)
        WHERE m.year >= "%s" AND m.year <= "%s"
        MATCH (a:ACTOR)-[:acted_in]->(m)
        RETURN DISTINCT collect(distinct(a.fname + " " + a.lname)),collect(distinct m.title),g.genre,m.year,a.fname
        ORDER BY m.year,a.fname ASC;
        """ % (genre, year, endYear)

        actors = graph.cypher.execute(query)

        self.render('genreExpl.html', actorsList=actors)



class genreStatHandler(tornado.web.RequestHandler):
    def get(self):
        year = self.get_argument('year')
        endYear = self.get_argument('endYear')

        if endYear == '':
            endYear = year

        if (year == '' and endYear == ''):
            self.write('Wrong input!')
            return

        query = """
        MATCH (g:GENRE)<-[r:has_genre]-(m:MOVIE{type:"3"})
        WHERE m.year >= "%s" AND m.year <= "%s"
        RETURN g.genre,count(DISTINCT m.title),m.year
        ORDER BY m.year ASC;
        """ % (year, endYear)

        genres = graph.cypher.execute(query)

        self.render('genreStat.html', genreList=genres)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r'/', searchHandler),
                                            (r'/movie', movieHandler),
                                            (r'/actorDetail', actorDetailHandler),
                                            (r'/actorBrief', actorBriefHandler),
                                            (r'/genreExpl', genreExplHandler),
                                            (r'/genreStat', genreStatHandler)
                                            ],
                                  template_path=os.path.join(os.path.dirname(__file__), "templates"),
                                  static_path=os.path.join(os.path.dirname(__file__), "static")
                                  #debug=True
                                  )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
