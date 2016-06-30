import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

import pymongo

client = pymongo.MongoClient('localhost', 27017)
db = client.webData

define("port", default=8000, help="run on the given port", type=int)


class searchHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('search.html')


class movieHandler(tornado.web.RequestHandler):
    def get(self):
        idmovies = self.get_argument('movieId')
        title = tornado.escape.url_unescape(self.get_argument('title'), plus=True)

        if not isinstance(idmovies, int) and idmovies != '':
            self.write('Wrong input.')
            return

        moviesColl = db['movies']
        actorsColl = db['actors']

        if idmovies != '' and title != '':
            movies = moviesColl.find({'_id': int(idmovies), 'title': {"$regex": title, "$options": "$i"}})
        elif idmovies != '':
            movies = moviesColl.find({'_id': int(idmovies)})
        elif title != '':
            movies = moviesColl.find({'title': {"$regex": title, "$options": "$i"}}) \
                .sort('year', pymongo.DESCENDING)
        else:
            self.write('Wrong input.')
            return

        if movies is None:
            self.write('No result.')
            return
        moviesList = []
        for movie in movies:
            movieDict = movie
            if movie['idactors'] is None:
                movieDict['actors'] = None
            else:
                actorRoleList = []
                for idactor in movie['idactors']:
                    actor = actorsColl.find_one({'_id': idactor})
                    if actor['mname'] is None:
                        actorName = '%s %s' % (actor['fname'], actor['lname'])
                    else:
                        actorName = '%s %s %s' % (actor['fname'], actor['mname'], actor['lname'])
                    for actorMovie in actor['movies']:
                        if actorMovie['title'] == movie['title']:
                            actorRoleList.append((actorName, actorMovie['role']))
                            continue
                movieDict['actors'] = actorRoleList
            moviesList.append(movieDict)

        self.render('movie.html', moviesList=moviesList)


class actorDetailHandler(tornado.web.RequestHandler):
    def get(self):
        idactors = self.get_argument('actorId')
        fname = tornado.escape.url_unescape(self.get_argument('fname'), plus=True)
        lname = tornado.escape.url_unescape(self.get_argument('lname'), plus=True)

        actorsColl = db['actors']

        if (idactors == '' and fname == '' and lname == '') or \
                (not isinstance(idactors, int) and idactors != ''):
            self.write('Wrong input!')
            return

        if idactors != '' and fname == '' and lname == '':
            actors = actorsColl.find({'_id': idactors})
        elif idactors == '' and fname != '' and lname == '':
            actors = actorsColl.find({'fname': {"$regex": fname, "$options": "$i"}})
        elif idactors == '' and fname == '' and lname != '':
            actors = actorsColl.find({'lname': {"$regex": lname, "$options": "$i"}})
        elif idactors == '' and fname != '' and lname != '':
            actors = actorsColl.find({'fname': {"$regex": fname, "$options": "$i"},
                                       'lname': {"$regex": lname, "$options": "$i"}})
        elif idactors != '' and fname == '' and lname != '':
            actors = actorsColl.find({'_id': idactors,
                                       'lname': {"$regex": lname, "$options": "$i"}})
        elif idactors != '' and fname != '' and lname == '':
            actors = actorsColl.find({'_id': idactors,
                                       'fname': {"$regex": fname, "$options": "$i"}})
        elif idactors != '' and fname != '' and lname != '':
            actors = actorsColl.find({'_id': idactors,
                                       'fname': {"$regex": fname, "$options": "$i"},
                                       'lname': {"$regex": lname, "$options": "$i"}})

        if actors is None:
            self.write('No result.')
            return
        self.render('actorDetail.html', actorsList=actors)


class actorBriefHandler(tornado.web.RequestHandler):
    def get(self):
        idactors = self.get_argument('actorId')
        fname = tornado.escape.url_unescape(self.get_argument('fname'), plus=True)
        lname = tornado.escape.url_unescape(self.get_argument('lname'), plus=True)

        actorsColl = db['actors']

        if (idactors == '' and fname == '' and lname == '') or \
                (not isinstance(idactors, int) and idactors != ''):
            self.write('Wrong input!')
            return

        if idactors != '' and fname == '' and lname == '':
            actors = actorsColl.find({'_id': idactors})
        elif idactors == '' and fname != '' and lname == '':
            actors = actorsColl.find({'fname': {"$regex": fname, "$options": "$i"}})
        elif idactors == '' and fname == '' and lname != '':
            actors = actorsColl.find({'lname': {"$regex": lname, "$options": "$i"}})
        elif idactors == '' and fname != '' and lname != '':
            actors = actorsColl.find({'fname': {"$regex": fname, "$options": "$i"},
                                       'lname': {"$regex": lname, "$options": "$i"}})
        elif idactors != '' and fname == '' and lname != '':
             actors = actorsColl.find({'_id': idactors,
                                       'lname': {"$regex": lname, "$options": "$i"}})
        elif idactors != '' and fname != '' and lname == '':
            actors = actorsColl.find({'_id': idactors,
                                       'fname': {"$regex": fname, "$options": "$i"}})
        elif idactors != '' and fname != '' and lname != '':
            actors = actorsColl.find({'_id': idactors,
                                       'fname': {"$regex": fname, "$options": "$i"},
                                       'lname': {"$regex": lname, "$options": "$i"}})

        if actors is None:
            self.write('No result.')
            return
        actorsList = []
        for actor in actors:
            actorDict = {}
            if actor['mname'] is None:
                actorDict['name'] = '%s %s' % (actor['fname'], actor['lname'])
            else:
                actorDict['name'] = '%s %s %s' % (actor['fname'], actor['mname'], actor['lname'])
            actorDict['movieNum'] = len(actor['movies'])
            actorsList.append(actorDict)
        self.render('actorBrief.html', actorsList=actorsList)


class genreExplHandler(tornado.web.RequestHandler):
    def get(self):
        genre = self.get_argument('genre')
        year = self.get_argument('year')
        endYear = self.get_argument('endYear')

        # if (not isinstance(year, int) and year != '') or \
        #         (not isinstance(endYear, int) and endYear != ''):
        #     self.write('Wrong input.')
        #     return

        moviesColl = db['movies']

        if endYear == '':
            movies = moviesColl.find({'genre': genre, 'year': year})
        else:
            movies = moviesColl.find({'genre': genre, 'year': {'$gte': year, '$lte': endYear}})

        if movies is None:
            self.write('No result.')
            return

        self.render('genreExpl.html', moviesList=movies)






if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r'/', searchHandler),
                                            (r'/movie', movieHandler),
                                            (r'/actorDetail', actorDetailHandler),
                                            (r'/actorBrief', actorBriefHandler),
                                            (r'/genreExpl', genreExplHandler)
                                            ],
                                  template_path=os.path.join(os.path.dirname(__file__), "templates"),
                                  static_path=os.path.join(os.path.dirname(__file__), "static")
                                  #debug=True
                                  )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
