# Peptoid Data Bank
# How to install and run locally
## Prerequisites
- Install Python version >=3.6 and <3.8 ([Need help?](https://realpython.com/installing-python/))
- Install required packages using the command `pip install -r requirements.txt`

## Run application locally
Run the application locally (access at http://127.0.0.1:5000/) with the command
```
flask run
```

# Application structure
```
├── app
│   ├── __init__.py
│   ├── admin.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   └── peptoids.py
│   ├── errors
│   │   ├── __init__.py
│   │   └── handlers.py
│   ├── models.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── schema.py
│   ├── static
│   │   ├── bootstrap-grid.css
│   │   ├── home.png
│   │   ├── icon.ico
│   │   ├── images.css
│   │   ├── peptoids
│   │   └── residues
│   └── templates
│       ├── 404.html
│       ├── 429.html
│       ├── 500.html
│       ├── admin
│       ├── api.html
│       ├── base.html
│       ├── gallery.html
│       ├── home.html
│       ├── peptoid.html
│       ├── residue_popout.html
│       ├── residues.html
│       └── search.html
├── app.db
├── config.py
├── databank.py
└── requirements.txt
```
# Modules
The application consists of a main "app" module, with submodules for the api, error handling, and the routes. In each of these submodules a Blueprint is made and registerd in the app module's `__init__.py`. The api blueprint defines what JSON will be returned at each API endpoint (found in `app/api/peptoids.py`). The error handling blueprint defines what HTML template will be rendered for a given HTTP error (found in `app/errors/handlers.py`). The routes blueprint defines what HTML template will be rendered for each URL endpoint (found in `app/routes/routes.py`). 

# Additional Files
- `app/admin.py` creates the views for the admin portal and implements HTTP basic authentication to secure the route
- `app/models.py` defines the database models (explained in the [database section](#Database))
- `app/schema.py` creates a GraphQL schema from the SQLAlchemy models
- `app/templates/` contains all of the HTML templates (explained in the [template section](#Templates))
- `app/static/` contains all of the static resources (images and CSS)
- `app.db` is the SQLite database file
- `databank.py` is the top level definition of the flask application
- `config.py` includes essential app configuration variables
- `requirements.txt` includes the required python modules that can be installed with pip

# Database
The database used for this application is SQLite, a relational database that stores all of its contents in one file, which can be as large as 281 TB. The database is connected to the application using SQLAlchemy. Using SQLAlchemy we can define the schema for the database in python. The schema consists of three basic models (Peptoid, Residue, and Author). Each model has columns, which specify what attributes can be recorded for a given entry into the table. The relational model employed is a many-to-many model. This means that each peptoid can have many authors, and each author can be associated with many peptoids. The same is true for residues. This is accomplished by using helper tables called peptoid-residue and peptoid-author. These tables contain two columns, linking foreign keys from the Peptoid and Author or Peptoid and Residue tables together.

# Templates
Templates are made using HTML and jinja. Jinja allows python code to generate the HTML that will be rendered on the page, so certain lines of HTML can be iteratively or conditionally produced, which is taken advantage of in the `gallery.html` template to produce HTML for each peptoid shown iteratively and generate links, images, and text conditionally based on each peptoid's properties. Further, all templates extend from a `base.html` template, which imports the required CSS and defines an essential jQuery script. It also places the navbar at the top of each page.
