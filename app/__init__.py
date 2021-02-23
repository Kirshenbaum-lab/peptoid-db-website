#importing essential modules for instantiating application and extensions
from flask import Flask
from flask.views import View
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask import Blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_graphql import GraphQLView
from flask_moment import Moment
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth

#instantiating app, database, config, limiter, bootstrap, moment, and basic_auth
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
limiter = Limiter(app, key_func=get_remote_address)
moment = Moment(app)
basic_auth = BasicAuth(app)

#setting up admin
from app.admin import admin

#registering blueprints
from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.routes import bp as routes_bp
app.register_blueprint(routes_bp)

#importing models from app module
from app import models
from .schema import schema

class myGraphQLView(GraphQLView):
    decorators = [limiter.limit('1000 per minute')]
    def dispatch_request(self):
        return GraphQLView.dispatch_request(self)

app.add_url_rule('/graphql', view_func=myGraphQLView.as_view('graphql', schema=schema, graphiql=True))
