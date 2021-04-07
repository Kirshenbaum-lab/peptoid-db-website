# from the app module imports db instance of SQLAlchemy application
from enum import unique
from app import db
import datetime
from flask import url_for
from sqlalchemy import event

# peptoid-author helper table
peptoid_author = db.Table('peptoid-author',
                          db.Column('peptoid_id', db.String(16), db.ForeignKey(
                              'peptoid.code'), unique=False),
                          db.Column('author_id', db.Integer, db.ForeignKey(
                              'author.id'), unique=False)
                          )

# peptoid-residue helper table
peptoid_residue = db.Table('peptoid-residue',
                           db.Column('peptoid_id', db.String(16), db.ForeignKey(
                               'peptoid.code'), unique=False),
                           db.Column('residue_id', db.Integer, db.ForeignKey(
                               'residue.id'), unique=False)
                           )

# peptoid table: image file name, title to display on page, data base code, release date,
# experimental technique, doi of publication, relationship with the author and residue


class Peptoid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), unique=True)
    title = db.Column(db.Text, unique=False)
    release = db.Column(db.DateTime, unique=False)
    experiment = db.Column(db.Text, unique=False)
    pub_doi = db.Column(db.String(32), unique=False)
    struct_doi = db.Column(db.String(32), unique=False)
    topology = db.Column(db.String(1), unique=False)
    sequence = db.Column(db.String(1024), unique=False)
    n_term = db.Column(db.String(32), unique=False)
    c_term = db.Column(db.String(32), unique=False)
    cyclization_points = db.Column(db.String(8), unique=False)
    struct_smiles = db.Column(db.String(128),unique=False)

    peptoid_author = db.relationship('Author', secondary=peptoid_author, lazy='dynamic',
                                     backref=db.backref('peptoids', order_by='Peptoid.release.desc()'))
    peptoid_residue = db.relationship('Residue', secondary=peptoid_residue, lazy='dynamic',
                                      backref=db.backref('peptoids', order_by='Peptoid.release.desc()'))

    def to_dict(self):
        data = {
            'title': self.title,
            'release': self.release,
            'experiment': self.experiment,
            'pub_doi': self.pub_doi,
            'struct_doi': self.struct_doi,
            'topology': self.topology,
            'sequence':self.sequence,
            'n_term':self.n_term,
            'c_term':self.c_term,
            'cyc_points':self.cyclization_points,
            'struct_smiles':self.struct_smiles,
            '_links': {
                'self': url_for('api.get_peptoid', code=self.code),
                'residues': url_for('api.get_pep_residues', code=self.code),
                'authors': url_for('api.get_pep_authors', code=self.code),
                '3d_image': url_for('static', filename='peptoids/'+self.code[:5]+'.png'),
                '2d_image': url_for('static', filename='peptoids/'+self.code+'_2d.png')
            }
        }
        return data

    def __repr__(self):
        return '<Peptoid {}>'.format(self.title)

# authors table: first name and last name
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, unique=False)
    last_name = db.Column(db.Text, unique=False)

    def to_dict(self):
        data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'peptoids': {}
        }
        for p in self.peptoids:
            data['peptoids'][p.code] = url_for('api.get_peptoid', code=p.code)
        return data

    def __repr__(self):
        return '<Author {}>'.format(self.last_name)

# residues table: nomenclature


class Residue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_name = db.Column(db.Text, unique=False)
    short_name = db.Column(db.Text, unique=False)
    pep_type = db.Column(db.Text, unique=False)
    monomer_structure = db.Column(db.Text, unique=False)
    SMILES = db.Column(db.Text, unique=False)

    def to_dict(self):
        data = {
            'full_nomenclature': self.long_name,
            'short_name': self.short_name,
            'type': self.pep_type,
            'monomer_structure': self.monomer_structure,
            'SMILES': self.SMILES,
            'peptoids': {}
        }
        for p in self.peptoids:
            data['peptoids'][p.code] = url_for('api.get_peptoid', code=p.code)
        return data

    def __repr__(self):
        return '<Residue {}>'.format(self.long_name)
