# importing important route-related flask functions, form for searching database, database models, blueprint for routes
from flask import render_template, flash, redirect, url_for, abort
from app.routes.forms import SearchForm, ApiRequest
from app.models import Peptoid, Author, Residue
from app.routes import bp
from app import app
from flask import request


def get_home(peptoids):
    peptoid_codes = []
    peptoid_urls = []
    peptoid_titles = []
    sequence_max = 128
    peptoid_sequences = []
    data = []
    publications = []

    for p in peptoids:
        peptoid_codes.append(p.code)
        peptoid_titles.append(p.title)
        peptoid_urls.append(url_for('routes.peptoid', code=p.code))
        if len(p.sequence) < sequence_max:
            peptoid_sequences.append(p.sequence)
        else:
            l = [pos for pos, char in enumerate(p.sequence) if char == ',']
            peptoid_sequences.append(p.sequence[:l[2]] + " ...")
        if p.experiment == 'X-Ray Diffraction':
            data.append("https://www.doi.org/{}".format(p.struct_doi))
            publications.append("https://www.doi.org/{}".format(p.pub_doi))
        else:
            data.append("")
            publications.append("https://www.doi.org/{}".format(p.pub_doi))

    return [peptoid_codes, peptoid_urls, peptoid_titles, peptoid_sequences, data, publications]

# base route
@bp.route('/')

@bp.route('/home')
def home():
    return render_template('home.html', title="PeptoidDB")

# gallery route displaying all petoids in reverse chron order using gallery.html template
@bp.route('/gallery')
def gallery():
    # paginated peptoids
    page = request.args.get('page', 1, type=int)
    peptoids = Peptoid.query.order_by(Peptoid.release.desc()).paginate(
        page, app.config['PEPTOIDS_PER_PAGE'], True)
    properties = get_home(peptoids.items)
    next_url = url_for(
        'routes.gallery', page=peptoids.next_num) if peptoids.has_next else None
    prev_url = url_for(
        'routes.gallery', page=peptoids.prev_num) if peptoids.has_prev else None
    return render_template('gallery.html',
                           title='Gallery',
                           pages=peptoids.pages,
                           total=peptoids.total,
                           next_url=next_url,
                           prev_url=prev_url,
                           peptoid_codes=properties[0],
                           peptoid_urls=properties[1],
                           peptoid_titles=properties[2],
                           peptoid_sequences=properties[3],
                           data=properties[4],
                           publications=properties[5]
                           )

# route for all residues renders residues.html


@bp.route('/residues')
def residues():
    title = 'Residues'
    residues = [r for r in Residue.query.all()]
    return render_template('residues.html', title=title, residues=residues)
# search route renders the form using the search.html template and the SearchForm() from forms.py
# if the user has submitted the form they are redirected to the route for the serial choice with
# var = their search box input


@bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        flash('{cat} search for <{term}>'.format(cat=form.option.data.upper(), term=form.search.data),
              'success')
        var = form.search.data
        if '/' in var:
            var = var.replace('/', '$')
        return redirect(url_for('routes.'+form.option.data, var=var))
    return render_template('search.html',
                           title='Search',
                           form=form,
                           info='Filter database of peptoids by any property from the choices below.',
                           description='Peptoid Data Bank - Explore by property')


@bp.route('/peptoid/<code>')
def peptoid(code):
    # data passed to front end
    peptoid = Peptoid.query.filter_by(code=code).first_or_404()
    title = peptoid.title
    code = peptoid.code
    release = str(peptoid.release.month) + "/" + \
        str(peptoid.release.day) + "/" + str(peptoid.release.year)
    experiment = peptoid.experiment

    # lists of objects also passed to front end
    authors = []
    residues = []

    for author in peptoid.peptoid_author:
        authors.append(author)

    for residue in peptoid.peptoid_residue:
        residues.append(residue)

    sequence = peptoid.sequence
    author_list = ", ".join(
        [a.first_name + " " + a.last_name for a in authors])
    # rendering html template
    if experiment == 'X-Ray Diffraction':
        data = peptoid.struct_doi
        publication = peptoid.pub_doi

        return render_template('peptoid.html',
                               peptoid=peptoid,
                               title=title,
                               code=code,
                               release=release,
                               experiment=experiment,
                               data=data,
                               publication=publication,
                               authors=authors,
                               residues=residues,
                               sequence=sequence,
                               author_list=author_list
                               )
    else:
        publication = peptoid.pub_doi

        return render_template('peptoid.html',
                               peptoid=peptoid,
                               title=title,
                               code=code,
                               release=release,
                               data='',
                               experiment=experiment,
                               publication=publication,
                               authors=authors,
                               residues=residues,
                               sequence=sequence,
                               author_list=author_list
                               )

#popout for residues of peptoid
@bp.route('/residue/<var>/popout')
def residue_popout(var):
    residue = Residue.query.filter((Residue.long_name == var) | (Residue.short_name == var)).first_or_404()
    return render_template('residue_popout.html',residue=residue,title='Popout')


# residue route for residue, name = var, returns gallery.html (gallery view)
@bp.route('/residue/<var>')
def residue(var):
    page = request.args.get('page', 1, type=int)  # setting page number

    # retrieving peptoids from residue input
    if var == 'null':
        return render_template('404.html')
    residue = Residue.query.filter((Residue.long_name == var) | (
        Residue.short_name == var)).first_or_404()
    codes = [p.code for p in residue.peptoids]

    # pagination
    peptoids = Peptoid.query.filter(Peptoid.code.in_(codes)).order_by(Peptoid.release.desc()).paginate(
        page, app.config['PEPTOIDS_PER_PAGE'], True)
    properties = get_home(peptoids.items)
    next_url = url_for('routes.residue', page=peptoids.next_num,
                       var=var) if peptoids.has_next else None
    prev_url = url_for('routes.residue', page=peptoids.prev_num,
                       var=var) if peptoids.has_prev else None

    return render_template('gallery.html',
                           title='Filtered by Residue: ' + var,
                           pages=peptoids.pages,
                           total=peptoids.total,
                           next_url=next_url,
                           prev_url=prev_url,
                           peptoid_codes=properties[0],
                           peptoid_urls=properties[1],
                           peptoid_titles=properties[2],
                           peptoid_sequences=properties[3],
                           data=properties[4],
                           publications=properties[5]
                           )

# author route for author. If name entered has a space search by both words for first name and last name.
# if name entered is just one word check if it is an author's first name or last name
# returns gallery.html (gallery view)


@bp.route('/author/<var>')
def author(var):
    page = request.args.get('page', 1, type=int)  # setting page number

    # retrieving peptoids from author according to input var
    if "," in var:
        name_split = var.split(', ')
        last_name = name_split[0]
        first_name = name_split[1]
        author = Author.query.filter_by(
            first_name=first_name, last_name=last_name).first_or_404()
    else:
        author = Author.query.filter((Author.first_name == var) | (
            Author.last_name == var)).first_or_404()
    codes = [p.code for p in author.peptoids]

    # generating peptoids according to sorted list date keys
    peptoids = Peptoid.query.filter(Peptoid.code.in_(codes)).order_by(Peptoid.release.desc()).paginate(
        page, app.config['PEPTOIDS_PER_PAGE'], True)
    properties = get_home(peptoids.items)
    next_url = url_for('routes.author', page=peptoids.next_num,
                       var=var) if peptoids.has_next else None
    prev_url = url_for('routes.author', page=peptoids.prev_num,
                       var=var) if peptoids.has_prev else None

    return render_template('gallery.html',
                           title='Filtered by Author: ' + var,
                           pages=peptoids.pages,
                           total=peptoids.total,
                           next_url=next_url,
                           prev_url=prev_url,
                           peptoid_codes=properties[0],
                           peptoid_urls=properties[1],
                           peptoid_titles=properties[2],
                           peptoid_sequences=properties[3],
                           data=properties[4],
                           publications=properties[5]
                           )

# experiment route for Peptoid.experimet = var, returns gallery.html (gallery view), if no peptoid found returns a 404


@bp.route('/experiment/<var>')
def experiment(var):
    page = request.args.get('page', 1, type=int)  # setting page number

    # paginated peptoids filtered by experimental technique input var
    peptoids = Peptoid.query.order_by(Peptoid.release.desc()).filter_by(
        experiment=var).paginate(page, app.config['PEPTOIDS_PER_PAGE'], True)
    properties = get_home(peptoids.items)
    next_url = url_for('routes.experiment', page=peptoids.next_num,
                       var=var) if peptoids.has_next else None
    prev_url = url_for('routes.experiment', page=peptoids.prev_num,
                       var=var) if peptoids.has_prev else None

    if len(properties[0]) == 0:
        abort(404)

    return render_template('gallery.html',
                           title='Filtered by Experiment: ' + var,
                           pages=peptoids.pages,
                           total=peptoids.total,
                           next_url=next_url,
                           prev_url=prev_url,
                           peptoid_codes=properties[0],
                           peptoid_urls=properties[1],
                           peptoid_titles=properties[2],
                           peptoid_sequences=properties[3],
                           data=properties[4],
                           publications=properties[5]
                           )

# doi route for Peptoid.doi = var, returns gallery.html (gallery view), if no peptoid found returns a 404


@bp.route('/doi/<var>')
def doi(var):
    page = request.args.get('page', 1, type=int)  # setting page number
    var = var.replace('$', '/')

    # paginated peptoids filtered by doi input var
    peptoids = Peptoid.query.order_by(Peptoid.release.desc()).filter(
        (Peptoid.struct_doi == var) | (Peptoid.pub_doi == var)).paginate(page, app.config['PEPTOIDS_PER_PAGE'], True)
    properties = get_home(peptoids.items)
    next_url = url_for('routes.doi', page=peptoids.next_num,
                       var=var) if peptoids.has_next else None
    prev_url = url_for('routes.doi', page=peptoids.prev_num,
                       var=var) if peptoids.has_prev else None

    if len(properties[0]) == 0:
        abort(404)

    return render_template('gallery.html',
                           title='Filtered by DOI: ' + var,
                           pages=peptoids.pages,
                           total=peptoids.total,
                           next_url=next_url,
                           prev_url=prev_url,
                           peptoid_codes=properties[0],
                           peptoid_urls=properties[1],
                           peptoid_titles=properties[2],
                           peptoid_sequences=properties[3],
                           data=properties[4],
                           publications=properties[5]
                           )

# filtering according to topology


@bp.route('/top/<var>')
def topology(var):
    page = request.args.get('page', 1, type=int)  # setting page number

    # paginated peptoids filtered by doi input var
    peptoids = Peptoid.query.order_by(Peptoid.release.desc()).filter_by(
        topology=var).paginate(page, app.config['PEPTOIDS_PER_PAGE'], True)
    properties = get_home(peptoids.items)
    next_url = url_for('routes.topology', page=peptoids.next_num,
                       var=var) if peptoids.has_next else None
    prev_url = url_for('routes.topology', page=peptoids.prev_num,
                       var=var) if peptoids.has_prev else None

    if len(properties[0]) == 0:
        abort(404)

    return render_template('gallery.html',
                           title='Filtered by Topology: ' + var,
                           pages=peptoids.pages,
                           total=peptoids.total,
                           next_url=next_url,
                           prev_url=prev_url,
                           peptoid_codes=properties[0],
                           peptoid_urls=properties[1],
                           peptoid_titles=properties[2],
                           peptoid_sequences=properties[3],
                           data=properties[4],
                           publications=properties[5]
                           )


# api route returns api.html template


@bp.route('/api', methods=['GET', 'POST'])
def api():
    return render_template('api.html', title="PeptoidDB API")
