from flask import *
import os
from datetime import datetime
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from things import *
from database import *
import json


api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)


def remove_sa(d):
    d.pop('_sa_instance_state', None)
    return d


class NewsList(Resource):
        
    def get(self):
        news = News.query.all()
        return jsonify(news = [remove_sa(n.__dict__) for n in news])
        
         
    def post(self):
        args = parser.parse_args()
        news_item = News(title=args['title'], 
                         content=args['content'])
        db.session.add(news_item)
        db.session.commit()
        return jsonify({'success': 'OK'})
    
    
class NewsItem(Resource):
        
    def get(self, id):
        news = News.query.filter_by(id=id).first()
        return jsonify(news = remove_sa(news.__dict__))


class ContestList(Resource):
    
    def get(self):
        contests = Contest.query.all()
        return jsonify(contests = [remove_sa(c.__dict__) for c in contests]) 


class SolutionList(Resource):
    
    def get(self):
        solutions = Solution.query.all()
        return jsonify(solutions = [remove_sa(s.__dict__) for s in solutions])     


api.add_resource(NewsList, '/api/news')
api.add_resource(ContestList, '/api/contests')
api.add_resource(NewsItem, '/api/news/<int:id>')
api.add_resource(SolutionList, '/api/solutions')
