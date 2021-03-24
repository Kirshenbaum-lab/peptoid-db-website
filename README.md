# Peptoid Data Bank
# How to install and run locally
## Prerequisites
- Install Python version >=3.6 and <3.8 ([Need help?](https://realpython.com/installing-python/))
- Install required packages using the command `pip install -r requirements.txt`

## Run application locally
Run the application locally (access on port 5000) with the command
```
flask run
```
Access the flask shell, where you can make query the database using
```
flask shell
```

## Application structure
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
