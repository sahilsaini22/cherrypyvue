from datetime import datetime
from email.policy import default
import os
from pydoc import describe
from telnetlib import SE
from urllib import response
from xmlrpc.client import DateTime

import cherrypy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import String, Float, DateTime, Integer

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import cherrypy_cors

import json

from cp_sqlalchemy import SQLAlchemyTool, SQLAlchemyPlugin

conn_str = os.environ.get('DBBS')

Base = declarative_base()
HERE = os.path.dirname(os.path.abspath(__file__))

cherrypy_cors.install()

cherrypy.config.update(
    {
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080,        
    }
)


conn_str = os.environ['DBBS']

engine = create_engine(conn_str)
Session = sessionmaker(engine)

class LogMessage(Base):

    __tablename__ = 'budget'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    amount = Column(Float)



@cherrypy.expose
class HelloWorld(object):

    @property
    def db(self):        
        return cherrypy.request.db

        
    #@cherrypy.tools.json_out()
    def GET(self):   
        self.session = Session.configure(bind=engine)
        session = Session()    
        statement = "select * from budget"
        tups = session.execute(statement).all()
        session.close()
        res_json = json.dumps([{"id": tup[0], "value": tup[1]} for tup in tups])
        return res_json

    #@cherrypy.tools.json_out()
    def GET(self, id=''):   
        self.session = Session.configure(bind=engine)
        session = Session()  
        if id == '':    
            statement = "select * from budget"
            tups = session.execute(statement).all()
            session.close()            
        else:                
            statement = "select * from budget where id = %s" % id
            tups = session.execute(statement)
        session.close()
        print(tups)    
        (print(tup) for tup in tups)
        res_json = json.dumps([{"id": tup[0], "description": tup[1], "amount": float(tup[2])} for tup in tups])
        return res_json        

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):           
        if cherrypy.request.method == 'OPTIONS':
            cherrypy.response.header["Access-Control-Allow-Origin"] = "*"
            cherrypy_cors.preflight(allowed_methods=['GET', 'POST', 'OPTIONS'])

        msg = LogMessage(
            description = cherrypy.request.json.get('description'),
            amount = cherrypy.request.json.get('amount')
        )
        self.session = Session.configure(bind=engine)
        session = Session()
        session.add(msg)
        session.commit()
        session.close()
        return cherrypy.request.json

    #@cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def PUT(self, id):           
        self.session = Session.configure(bind=engine)
        session = Session()
        item = session.query(LogMessage).filter(LogMessage.id == id).one()
        item.description = cherrypy.request.json.get('description')
        item.amount = cherrypy.request.json.get('amount')
        session.commit()     
        session.close()
        return "success"    



    def DELETE(self, id):   
        self.session = Session.configure(bind=engine)
        session = Session()    
        session.query(LogMessage).filter(LogMessage.id==id).delete()
        session.commit()
        session.close()        
        return "deleted"


    def OPTIONS(self, *args, **kwargs):
        print("preflight")
        if cherrypy.request.method == 'OPTIONS':
            #print("preflight")
            #cherrypy_cors.preflight(allowed_methods=["GET", "DELETE", "PUT"])
            ##self.response.header["Access-Control-Allow-Origin"] = "*"
            ##self.response.headers["Access-Control-Allow-Headers"]= "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            ##self.response.headders["Access-Control-Allow-Methods"] = 'GET', 'POST', 'OPTIONS', 'PUT', 'POST'
            ##print("response:")
            ##print(self.response)
            ##return self.response
            req_head = cherrypy.request.headers
            resp_head = cherrypy.response.headers

            resp = cherrypy.serving.response

            # Always set response headers necessary for 'simple' CORS.
            resp_head['Access-Control-Allow-Origin'] = req_head.get('Origin', '*')
            resp_head['Access-Control-Expose-Headers'] = 'GET, POST'
            resp_head['Access-Control-Allow-Credentials'] = 'true'

            ac_method = req_head.get('Access-Control-Request-Method', None)
  
            allowed_methods = ['GET', 'POST', 'PUT', 'DELETE']
            allowed_headers = [
                'Content-Type',
                'X-Auth-Token',
                'X-Requested-With',
            ]
                
            resp_head['Access-Control-Allow-Methods'] = ', '.join(allowed_methods)
            resp_head['Access-Control-Allow-Headers'] = ', '.join(allowed_headers)    
            resp_head['Connection'] = 'keep-alive'
            resp_head['Access-Control-Max-Age'] = '3600'
    
            # CORS requests should short-circuit the other tools.
            resp.body = ''.encode('utf8')
            resp.status = 200
            resp.header = resp_head
            cherrypy.serving.request.handler = None

            print("down")
            #print(resp)
    
            #return resp
    

if __name__ == '__main__':
    cherrypy.tools.db = SQLAlchemyTool()    
    
    conf = {
        '/': {
            'tools.db.on': True,
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True, 
            'cors.expose.on': True,       
            'tools.response_headers.headers': [('Content-Type', 'text/plain'), ('Allow-Control-Allow_origin', '*')],            
        }
    }



    

    
    

    cherrypy.quickstart(HelloWorld(), '/budget/', conf)
    dbfile = os.path.join(HERE, 'budget.db')

    if not os.path.exists(dbfile):
        open(dbfile, 'w+').close()

    sqlalchemy_plugin = SQLAlchemyPlugin(
        cherrypy.engine, Base, 'sqlite:///%s' % (dbfile),
        echo=True
    )
    sqlalchemy_plugin.subscribe()
    sqlalchemy_plugin.create()


    


    cherrypy.engine.start()
    cherrypy.engine.block()
      