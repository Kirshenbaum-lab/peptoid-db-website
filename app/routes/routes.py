# importing important route-related flask functions, form for searching database, database models, blueprint for routes
from flask import render_template, redirect, url_for, abort, flash, make_response
from app.routes.forms import SearchForm
from app.models import Peptoid, Author, Residue
from app.routes import bp
from app import app
from flask import request

# function for creating all gallery views


def renderGallery(peptoids, title, page, next_url, prev_url, view, var):
    if view not in ['3d', '2d']:
        flash(f'INVALID VIEW ARGUMENT: {view}. Must be \'3d\' or \'2d\'','danger')
        abort(400)
    
    sequence_max = 128  # sequence cap

    # lists passed to generate gallery
    peptoid_codes = []
    peptoid_urls = []
    peptoid_titles = []
    peptoid_sequences = []
    data = []
    publications = []

    # populating lists with properties from peptoids passed by route function
    for p in peptoids.items:
        peptoid_codes.append(p.code)
        peptoid_titles.append(p.title)
        peptoid_urls.append(url_for('routes.peptoid', code=p.code))

        # creating peptoid sequence string according adhering to the max sequence characters (either full sequence or first 3 residues and ...)
        if len(p.sequence) < sequence_max:
            peptoid_sequences.append(p.sequence)
        else:
            l = [pos for pos, char in enumerate(p.sequence) if char == ',']
            peptoid_sequences.append(p.sequence[:l[2]] + " ...")

        # if structure doi exists add doi links for structure doi and pub doi, else use empty string for struct doi link
        if p.struct_doi:
            data.append("https://www.doi.org/{}".format(p.struct_doi))
            publications.append("https://www.doi.org/{}".format(p.pub_doi))
        else:
            data.append("")
            publications.append("https://www.doi.org/{}".format(p.pub_doi))

    # return gallery.html template with properties
    return render_template('gallery.html',
                           title=title,
                           pages=peptoids.pages,
                           total=peptoids.total,
                           next_url=next_url,
                           prev_url=prev_url,
                           page=page,
                           view=view,
                           var=var,
                           peptoid_codes=peptoid_codes,
                           peptoid_urls=peptoid_urls,
                           peptoid_titles=peptoid_titles,
                           peptoid_sequences=peptoid_sequences,
                           data=data,
                           publications=publications
                           )


@bp.route('/')
@bp.route('/home')
def home():
    return render_template('home.html', title="Peptoid Data Bank")

# route for baseline gallery, passes var=False because no var argument


@bp.route('/gallery')
def gallery():
    title = 'Gallery'
    # page number argument for pagination
    page = request.args.get('page', 1, type=int)
    # view argument for 3d vs 2d
    view = request.args.get('view', '2d', type=str)

    # paginated peptoids
    peptoids = Peptoid.query.order_by(Peptoid.release.desc()).paginate(
        page, app.config['PEPTOIDS_PER_PAGE'], True)
    next_url = url_for(
        'routes.gallery', page=peptoids.next_num, view=view) if peptoids.has_next else None
    prev_url = url_for(
        'routes.gallery', page=peptoids.prev_num, view=view) if peptoids.has_prev else None

    return renderGallery(peptoids, title, page, next_url, prev_url, view, var=False)

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
        var = form.search.data
        if '/' in var:
            var = var.replace('/', '$')
        return redirect(url_for('routes.'+form.option.data, var=var))
    return render_template('search.html',
                           title='Search',
                           form=form,
                           info='Filter database of peptoids by any property from the choices below.',
                           description='Peptoid Data Bank - Explore by property')

# individual peptoid page for peptoid specified by code


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

# popout for residues of peptoid


@bp.route('/residue/<var>/popout')
def residue_popout(var):
    residue = Residue.query.filter((Residue.long_name == var) | (
        Residue.short_name == var)).first_or_404()
    return render_template('residue_popout.html', residue=residue, title='Popout')

@bp.route('/peptoid/<code>/citation')
def citation(code):
    peptoid = Peptoid.query.filter_by(code=code).first_or_404()
    response = make_response(peptoid.citation, 200)
    response.mimetype = "text/plain"
    return response


# residue route for residue, name = var
@bp.route('/residue/<var>')
def residue(var):
    page = request.args.get('page', 1, type=int)
    view = request.args.get('view', '2d', type=str)
    title = 'Filtered by Residue: ' + var
    # get residue(s) and related peptoids codes
    residues = Residue.query.filter((Residue.long_name == var) | (
            Residue.short_name == var)).all()
    if len(residues) == 0:
        flash(f'NO RESIDUES for: <{var}>','danger')
        abort(404)
    peptoids = []
    for r in residues:
        peptoids.extend(r.peptoids)
    codes = [p.code for p in peptoids]
    peptoids = Peptoid.query.filter(Peptoid.code.in_(codes)).order_by(Peptoid.release.desc()).paginate(
        page, app.config['PEPTOIDS_PER_PAGE'], True)  # querying for peptoids based on list of codes
    next_url = url_for('routes.residue', page=peptoids.next_num,
                       var=var, view=view) if peptoids.has_next else None
    prev_url = url_for('routes.residue', page=peptoids.prev_num,
                       var=var, view=view) if peptoids.has_prev else None
    return renderGallery(peptoids, title, page, next_url, prev_url, view, var)

# author route for author. If name entered has a space search by both words for first name and last name.
# if name entered is just one word check if it is an author's first name or last name


@bp.route('/author/<var>')
def author(var):
    page = request.args.get('page', 1, type=int)
    view = request.args.get('view', '2d', type=str)

    # retrieving peptoids from author according to input var, processed for comma separated name
    if "," in var:
        name_split = var.split(', ')
        last_name = name_split[0]
        first_name = name_split[1]
        authors = Author.query.filter_by(
            first_name=first_name, last_name=last_name).all()
    else:
        authors = Author.query.filter((Author.first_name == var) | (
            Author.last_name == var)).all()
    if len(authors) == 0:
        flash(f'NO AUTHORS for: <{var}>','danger')
        abort(404)
    peptoids = []
    for a in authors:
        peptoids.extend(a.peptoids)
    codes = [p.code for p in peptoids]
    title = 'Filtered by Author: ' + var
    peptoids = Peptoid.query.filter(Peptoid.code.in_(codes)).order_by(Peptoid.release.desc()).paginate(
        page, app.config['PEPTOIDS_PER_PAGE'], True)
    next_url = url_for('routes.author', page=peptoids.next_num,
                       var=var, view=view) if peptoids.has_next else None
    prev_url = url_for('routes.author', page=peptoids.prev_num,
                       var=var, view=view) if peptoids.has_prev else None
    return renderGallery(peptoids, title, page, next_url, prev_url, view, var)

# experiment route for Peptoid.experimet = var, returns gallery.html (gallery view), if no peptoid found returns a 404


@bp.route('/experiment/<var>')
def experiment(var):
    page = request.args.get('page', 1, type=int)
    view = request.args.get('view', '2d', type=str)
    title = 'Filtered by Experiment: ' + var
    peptoids = Peptoid.query.order_by(Peptoid.release.desc()).filter_by(
        experiment=var).paginate(page, app.config['PEPTOIDS_PER_PAGE'], True)
    if len(peptoids.items) == 0:
        abort(404)
    next_url = url_for('routes.experiment', page=peptoids.next_num,
                       var=var, view=view) if peptoids.has_next else None
    prev_url = url_for('routes.experiment', page=peptoids.prev_num,
                       var=var, view=view) if peptoids.has_prev else None
    return renderGallery(peptoids, title, page, next_url, prev_url, view, var)

# doi route for Peptoid.doi = var, returns gallery.html (gallery view), if no peptoid found returns a 404


@bp.route('/doi/<var>')
def doi(var):
    page = request.args.get('page', 1, type=int)
    var = var.replace('$', '/') #making doi into doi that fits database
    view = request.args.get('view', '2d', type=str)
    title = 'Filtered by DOI: ' + var
    peptoids = Peptoid.query.order_by(Peptoid.release.desc()).filter(
        (Peptoid.struct_doi == var) | (Peptoid.pub_doi == var)).paginate(page, app.config['PEPTOIDS_PER_PAGE'], True)
    if len(peptoids.items) == 0:
        abort(404)
    var = var.replace('/', '$') #making doi fit url
    next_url = url_for('routes.doi', page=peptoids.next_num,
                       var=var, view=view) if peptoids.has_next else None
    prev_url = url_for('routes.doi', page=peptoids.prev_num,
                       var=var, view=view) if peptoids.has_prev else None
    return renderGallery(peptoids, title, page, next_url, prev_url, view, var)

# filtering according to topology


@bp.route('/top/<var>')
def topology(var):
    page = request.args.get('page', 1, type=int)
    view = request.args.get('view', '2d', type=str)
    title = 'Filtered by Topology: ' + var
    peptoids = Peptoid.query.order_by(Peptoid.release.desc()).filter_by(
        topology=var).paginate(page, app.config['PEPTOIDS_PER_PAGE'], True)
    if len(peptoids.items) == 0:
        abort(404)
    next_url = url_for('routes.topology', page=peptoids.next_num,
                       var=var, view=view) if peptoids.has_next else None
    prev_url = url_for('routes.topology', page=peptoids.prev_num,
                       var=var, view=view) if peptoids.has_prev else None
    return renderGallery(peptoids, title, page, next_url, prev_url, view, var)


# api route returns api.html template
@bp.route('/api', methods=['GET', 'POST'])
def api():
    return render_template('api.html', title="PeptoidDB API")
