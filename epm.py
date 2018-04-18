from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for, flash, session, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from datetime import datetime
import requests
import json
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://chris:funkytown@catfish/evesde'
app.debug = True # disable this in production!
app.config['SECRET_KEY'] = 'super-secret-foolish-fool'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    name = db.Column(db.String(255), unique=False)
    last_logged_in = db.Column(db.DateTime())
    api_key = db.Column(db.String(100), unique=False)
    api_code = db.Column(db.String(255), unique=False)

    def __init__(self, name, email, password, active, last_logged_in, api_key, api_code):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.last_logged_in = last_logged_in
        self.api_key = api_key
        self.api_code = api_code

class invtypes(db.Model):
    typeID = db.Column(db.Integer(), primary_key=True)
    groupID = db.Column(db.Integer())
    typeName = db.Column(db.String(100))
    description = db.Column(db.Text())
    mass = db.Column(db.Numeric())
    volume = db.Column(db.Numeric())
    capacity = db.Column(db.Numeric())
    marketGroupID = db.Column(db.Integer())

    def __init__(self, groupID, typeName, description, mass, volume, capacity, marketGroupID):
        self.groupID = marketGroupID
        self.typeName = str(typeName)
        self.description = str(description)
        self.mass = mass
        self.volume = volume
        self.capacity = capacity
        self.marketGroupID = marketGroupID

class build_pipeline(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    product_id = db.Column(db.Integer())
    blueprint_id = db.Column(db.Integer())
    runs = db.Column(db.Integer())
    material_id = db.Column(db.Integer())
    material_qty = db.Column(db.Integer())
    material_cost = db.Column(db.Numeric())
    product_name = db.Column(db.String(100))
    material = db.Column(db.String(100))
    group_id = db.Column(db.Integer())
    build_or_buy = db.Column(db.Integer())
    jita_sell_price = db.Column(db.Numeric())
    local_sell_price = db.Column(db.Numeric())
    build_cost = db.Column(db.Numeric())
    material_comp_id = db.Column(db.Integer())

    def __init__(self, user_id, product_id, blueprint_id, runs, material_id, material_qty, material_cost, product_name, material, group_id, build_or_buy, jita_sell_price, local_sell_price, build_cost, material_comp_id):
        self.user_id = user_id
        self.product_id = product_id
        self.blueprint_id = blueprint_id
        self.runs = runs
        self.material_id = material_id
        self.material_qty = material_qty
        self.material_cost = material_cost
        self.product_name = product_name
        self.material = material
        self.group_id = group_id
        self.build_or_buy = build_or_buy
        self.jita_sell_price = jita_sell_price
        self.local_sell_price = local_sell_price
        self.build_cost = build_cost
        self.material_comp_id = material_comp_id

class invent_pipeline(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    product_id = db.Column(db.Integer())
    blueprint_id = db.Column(db.Integer())
    product_name = db.Column(db.String(100))
    runs = db.Column(db.Integer())
    datacore_id = db.Column(db.Integer())
    datacore_qty = db.Column(db.Integer())
    datacore_cost = db.Column(db.Numeric())
    datacore = db.Column(db.String(100))

    def __init__(self, user_id, product_id, blueprint_id, runs, product_name, datacore_id, datacore_qty, datacore_cost, datacore):
        self.user_id = user_id
        self.product_id = product_id
        self.blueprint_id = blueprint_id
        self.runs = runs
        self.product_name = product_name
        self.datacore_id = datacore_id
        self.datacore_qty = datacore_qty
        self.datacore_cost = datacore_cost
        self.datacore = datacore

class v_build_requirements(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    material = db.Column(db.String(100))
    material_id= db.Column(db.Integer())
    group_id = db.Column(db.Integer())
    qty = db.Column(db.Integer())
    product_id = db.Column(db.Integer())

    def __init__(material, material_id, group_id, qty, product_id):
        self.material = str(material)
        self.material_id = material_id
        self.group_id = group_id
        self.qty = quantity
        self.product_id = product_id

class v_build_components(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    material = db.Column(db.String(100))
    material_id= db.Column(db.Integer())
    quantity = db.Column(db.Integer())

    def __init__(material, material_id, quantity):
        self.material = str(material)
        self.material_id = material_id
        self.quantity = quantity

class v_build_pipeline_products(db.Model):
    product_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer(), primary_key=True)
    blueprint_id = db.Column(db.Integer())
    product_id = db.Column(db.Integer())
    runs = db.Column(db.Integer())
    jita_sell_price = db.Column(db.Numeric())
    local_sell_price = db.Column(db.Numeric())
    build_cost = db.Column(db.Numeric())

    def __init__(product_name, user_id, blueprint_id, product_id, runs, jita_sell_price, local_sell_price, build_cost):
        self.product_name = str(product_name)
        self.user_id = user_id
        self.blueprint_id = blueprint_id
        self.product_id = product_id
        self.runs = runs
        self.jita_sell_price = jita_sell_price
        self.local_sell_price = local_sell_price
        self.build_cost = build_cost

class v_invent_pipeline_products(db.Model):
    product_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer(), primary_key=True)
    blueprint_id = db.Column(db.Integer())
    runs = db.Column(db.Integer())

    def __init__(product_name, user_id, blueprint_idruns):
        self.product_name = str(product_name)
        self.user_id = user_id
        self.blueprint_id = blueprint_id
        self.runs = runs

class v_datacore_requirements(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    datacore = db.Column(db.String(100))
    quantity = db.Column(db.Integer())
    dc_id = db.Column(db.Integer())

    def __init__(datacore, quantity, dc_id):
        self.datacore = str(datacore)
        self.quantity = quantity
        self.dc_id = dc_id

class v_invention_product(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    t2_blueprint = db.Column(db.String(100))
    t2_id = db.Column(db.Integer())

    def __init__(t2_blueprint, t2_id):
        self.t2_blueprint = str(t2_blueprint)
        self.t2_id = t2_id

class v_build_product(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    t2_blueprint = db.Column(db.String(100))
    t2_id = db.Column(db.Integer())

    def __init__(t2_blueprint, t2_id):
        self.t2_blueprint = str(t2_blueprint)
        self.t2_id = t2_id

class v_probability(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    probability = db.Column(db.Numeric())

    def __init__(probability):
        self.probability = probability

class v_product(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    t2_id = db.Column(db.Integer())

    def __init__(t2_id):
        self.t2_id = t2_id

class v_invent_time(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    time = db.Column(db.Integer())

    def __init__(time):
        self.time = time

class v_build_time(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    time = db.Column(db.Integer())

    def __init__(time):
        self.time = time

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

class LoginForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired()])

class BomDatacores():
    def __init__(self, datacore_id, datacore, datacore_qty, datacore_cost, runs):
        self.datacore_id = datacore_id
        self.datacore = datacore
        self.datacore_qty = datacore_qty
        self.datacore_cost = datacore_cost
        self.runs = runs

class BomMaterial():
    def __init__(self, material_id, material, material_qty, material_cost, runs, id, build_or_buy, blueprint_id):
        self.material_id = material_id
        self.material = material
        self.material_qty = material_qty
        self.material_cost = material_cost
        self.runs = runs
        self.id = id
        self.build_or_buy = build_or_buy
        self.blueprint_id = blueprint_id

@app.route("/")
def index():
    form = LoginForm(request.form)
    return render_template('home.html', form=form)

@app.route("/pipeline", methods=['GET','POST'])
def pipeline():
    form = LoginForm(request.form)
    if 'myUser_id' in session:
        myBlueprints = db.session.query(v_build_product).all()

        inv_pipeline = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id']).with_entities('product_name','user_id','runs','blueprint_id').order_by('product_name').all()

        bld_pipeline = db.session.query(v_build_pipeline_products).filter_by(user_id= session['myUser_id']).with_entities('product_name','user_id','blueprint_id','product_id','runs','jita_sell_price','local_sell_price','build_cost').order_by('product_name').all()

        return render_template('pipeline.html', form=form, blueprints=myBlueprints, inv_pipeline=inv_pipeline, bld_pipeline=bld_pipeline)

    else:
        flash('You must be logged in to view the pipeline', 'danger')
        return redirect(url_for('index'))

@app.route("/bom", methods=['GET','POST'])
def bom():
    form = LoginForm(request.form)
    if 'myUser_id' in session:
        try:
            build_or_buy = 0
            if request.method == 'POST':
                if request.form.get('build_or_buy') == 'buy':
                    build_or_buy = 0

                elif request.form.get('build_or_buy') == 'build':
                    build_or_buy = 1

                material_id = request.form.get('material_id')
                pipeline = db.session.query(build_pipeline).filter_by(material_id = material_id).all()
                for item in pipeline:
                    item.build_or_buy = build_or_buy
                    db.session.add(item)
                    db.session.commit()

            inv_pipeline = db.session.query(invent_pipeline).filter_by(user_id = session['myUser_id']).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','datacore_id','datacore_qty','datacore_cost','datacore').order_by('datacore').all()

            planetary_pipeline = db.session.query(build_pipeline).filter(build_pipeline.user_id == session['myUser_id'], (or_(build_pipeline.group_id==1034, build_pipeline.group_id==1040))).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id').order_by('material').all()

            component_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=334).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id').order_by('material').all()

            for component in component_pipeline:
                if component.build_or_buy == 1 and component.material_cost > 0:
                    comp = db.session.query(build_pipeline).filter_by(id=component.id).one()
                    comp.material_cost = 0.0
                    db.session.add(comp)
                    db.session.commit()

                    myBuildComponents = db.session.query(v_build_components).filter_by(id = component.material_id).with_entities('id','material','material_id','quantity').all()

                    for requirements in myBuildComponents:
                        myCost = get_marketValue(requirements.material_id, 'sell') * requirements.quantity * component.material_qty

                        pipeline = build_pipeline(session['myUser_id'],  component.product_id, component.blueprint_id, component.runs, requirements.material_id, requirements.quantity * component.material_qty, myCost, component.product_name, requirements.material, 429, 0, component.jita_sell_price, component.local_sell_price, component.build_cost, component.product_id)

                        db.session.add(pipeline)
                        db.session.commit()

                elif component.build_or_buy == 0 and component.material_cost == 0:
                    comp = db.session.query(build_pipeline).filter_by(id=component.id).one()
                    comp.material_cost = get_marketValue(component.material_id, 'sell') * component.material_qty
                    db.session.add(comp)
                    db.session.commit()
                    mat_id = comp.product_id

                    mats = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'], group_id=429, material_comp_id=mat_id).all()
                    for mat in mats:
                        db.session.delete(mat)
                        db.session.commit()

            component_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=334).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id').order_by('material').all()

            material_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=429).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id').order_by('material').all()

            tech1_pipeline = db.session.query(build_pipeline).filter(build_pipeline.user_id == session['myUser_id']).filter(build_pipeline.group_id <> 334).filter(build_pipeline.group_id <> 18).filter(build_pipeline.group_id <> 1034).filter(build_pipeline.group_id <> 332).filter(build_pipeline.group_id <> 1040).filter(build_pipeline.group_id <> 429).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id').order_by('material').all()

            for component1 in tech1_pipeline:
                if component1.build_or_buy == 1 and component1.material_cost > 0:
                    comp = db.session.query(build_pipeline).filter_by(id=component1.id).one()
                    comp.material_cost = 0.0
                    db.session.add(comp)
                    db.session.commit()

                    myBuildComponents = db.session.query(v_build_components).filter_by(id = component1.material_id).with_entities('id','material','material_id','quantity').all()

                    for requirements in myBuildComponents:
                        myCost = get_marketValue(requirements.material_id, 'sell') * requirements.quantity * component1.material_qty

                        pipeline = build_pipeline(session['myUser_id'],  component1.product_id, component1.blueprint_id, component1.runs, requirements.material_id, requirements.quantity * component1.material_qty, myCost, component1.product_name, requirements.material, 18, 0, component.jita_sell_price, component.local_sell_price, component.build_cost, component.product_id)

                        db.session.add(pipeline)
                        db.session.commit()

                elif component1.build_or_buy == 0 and component1.material_cost == 0:
                    comp = db.session.query(build_pipeline).filter_by(id=component1.id).one()
                    comp.material_cost = get_marketValue(component1.material_id, 'sell') * component1.material_qty
                    db.session.add(comp)
                    db.session.commit()
                    mat_id = comp.product_id

                    mats = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'], group_id=18, material_comp_id=mat_id).all()
                    for mat in mats:
                        db.session.delete(mat)
                        db.session.commit()

            tech1_pipeline = db.session.query(build_pipeline).filter(build_pipeline.user_id == session['myUser_id']).filter(build_pipeline.group_id <> 334).filter(build_pipeline.group_id <> 18).filter(build_pipeline.group_id <> 1034).filter(build_pipeline.group_id <> 332).filter(build_pipeline.group_id <> 1040).filter(build_pipeline.group_id <> 429).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id').order_by('material').all()

            ram_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=332).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id').order_by('material').all()

            for component2 in ram_pipeline:
                if component2.build_or_buy == 1 and component2.material_cost > 0:
                    comp = db.session.query(build_pipeline).filter_by(id=component2.id).one()
                    comp.material_cost = 0.0
                    db.session.add(comp)
                    db.session.commit()

                    myBuildComponents = db.session.query(v_build_components).filter_by(id = component2.material_id).with_entities('id','material','material_id','quantity').all()

                    for requirements in myBuildComponents:
                        myCost = get_marketValue(requirements.material_id, 'sell') * requirements.quantity * component2.material_qty

                        pipeline = build_pipeline(session['myUser_id'],  component2.product_id, component2.blueprint_id, component2.runs, requirements.material_id, requirements.quantity * component2.material_qty, myCost, component2.product_name, requirements.material, 18, 0, component.jita_sell_price, component.local_sell_price, component.build_cost, component.product_id)

                        db.session.add(pipeline)
                        db.session.commit()

                elif component2.build_or_buy == 0 and component2.material_cost == 0:
                    comp = db.session.query(build_pipeline).filter_by(id=component2.id).one()
                    comp.material_cost = get_marketValue(component2.material_id, 'sell') * component2.material_qty
                    db.session.add(comp)
                    db.session.commit()
                    mat_id = comp.product_id

                    mats = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'], group_id=18, material_comp_id=mat_id).all()
                    for mat in mats:
                        db.session.delete(mat)
                        db.session.commit()

            ram_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=332).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','jita_sell_price','local_sell_price','build_cost','material_comp_id').order_by('material').all()

            mineral_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=18).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','jita_sell_price','local_sell_price','build_cost','material_comp_id').order_by('material_id').all()

            datacoresInPipeline = invent_pipeline_rollup_qty(inv_pipeline)
            dc_total = invent_pipeline_rollup_cost(inv_pipeline)
            planetaryInPipeline = build_pipeline_rollup_qty(planetary_pipeline)
            planet_total = build_pipeline_rollup_cost(planetary_pipeline)
            componentInPipeline = build_pipeline_rollup_qty(component_pipeline)
            component_total = build_pipeline_rollup_cost(component_pipeline)
            materialInPipeline = build_pipeline_rollup_qty(material_pipeline)
            material_total = build_pipeline_rollup_cost(material_pipeline)
            tech1InPipeline = build_pipeline_rollup_qty(tech1_pipeline)
            tech1_total = build_pipeline_rollup_cost(tech1_pipeline)
            ramInPipeline = build_pipeline_rollup_qty(ram_pipeline)
            ram_total = build_pipeline_rollup_cost(ram_pipeline)
            mineralInPipeline = build_pipeline_rollup_qty(mineral_pipeline)
            mineral_total = build_pipeline_rollup_cost(mineral_pipeline)

            bom_total = 0
            bom_total += dc_total
            bom_total += planet_total
            bom_total += component_total
            bom_total += material_total
            bom_total += tech1_total
            bom_total += ram_total
            bom_total += mineral_total

            return render_template('shopping_list.html', form=form, datacoresInPipeline=datacoresInPipeline, planetaryInPipeline=planetaryInPipeline, componentInPipeline=componentInPipeline, materialInPipeline=materialInPipeline, tech1InPipeline=tech1InPipeline, ramInPipeline=ramInPipeline, mineralInPipeline=mineralInPipeline, bom_total=bom_total, dc_total=dc_total, planet_total=planet_total, component_total=component_total, material_total=material_total, tech1_total=tech1_total, ram_total=ram_total, mineral_total=mineral_total)

        except Exception as e:
            flash('Problem with B.o.M. - see log.', 'danger')
            app.logger.info(str(e))
            return redirect(url_for('bom'))
    else:
        flash('You must be logged in to view B.O.M.', 'danger')
        return redirect(url_for('index'))


@app.route('/build', methods=['GET','POST'])
def build():
    form = LoginForm(request.form)
    try:
        myBlueprints = db.session.query(v_build_product).all()
        if request.method == 'POST':
            if request.form['action'] == 'edit':
                if request.form.get('product_id'):
                    product_id = request.form.get('product_id')
                    runs = request.form['runs']
                    pipeline = db.session.query(build_pipeline).filter_by(blueprint_id = product_id).all()
                    for item in pipeline:
                        item.runs = runs
                        db.session.add(item)
                        db.session.commit()

                    flash('Successfully updated pipeline runs.', 'success')
            elif request.form.get('action') == 'delete':
                if request.form.get('product_id'):
                    product_id = request.form.get('product_id')
                    pipeline = db.session.query(build_pipeline).filter_by(blueprint_id = product_id).all()
                    for item in pipeline:
                        db.session.delete(item)
                        db.session.commit()

                    flash('Successfully deleted pipeline product.', 'success')

        if 'myUser_id' in session:
            pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id']).with_entities('id','user_id','product_id','blueprint_id','runs','material_id','material_qty','material_cost','product_name','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','jita_sell_price','local_sell_price','build_cost','material_comp_id').order_by('material').all()

            pipeline_products = db.session.query(v_build_pipeline_products).filter_by(user_id = session['myUser_id']).with_entities('product_name', 'user_id', 'blueprint_id', 'product_id', 'runs', 'jita_sell_price','local_sell_price','build_cost')

            materialInPipeline = build_pipeline_rollup_qty(pipeline)
            materialCost = build_pipeline_rollup_cost(pipeline)

            return render_template('build.html', form=form, blueprints=myBlueprints, bp_id=0, pipeline=pipeline, materialInPipeline=materialInPipeline, pipelineCost=materialCost, pipeline_products=pipeline_products)
        else:
            return render_template('build.html', form=form, blueprints=myBlueprints, bp_id=0)

    except Exception as e:
        flash('Problem with blueprint - see log.', 'danger')
        app.logger.info(str(e))
        return redirect(url_for('build'))

@app.route('/build_selected', methods=['POST','GET'])
def build_selected():
    runs = 1
    id = request.form.get('build_product')
    if id == 'None':
        id = request.args.get('build_product')
    if request.args.get('build_product'):
        id = request.args.get('build_product')
    if request.args.get('runs'):
        runs = int(request.args.get('runs'))

    form = LoginForm(request.form)
    try:
        myBlueprints = db.session.query(v_build_product).all()
        selected_bp = db.session.query(v_build_product).filter_by(id = id).one()
        myProduct = db.session.query(invtypes).filter_by(typeID = int(selected_bp.t2_id)).one()
        querySell = get_marketValue(str(myProduct.typeID),'buy')
        mySellMedian = "{:,.0f}".format(querySell)
        buildTime = db.session.query(v_build_time).filter_by(id = id).one()
        myTime = "{:,}".format(buildTime.time/60)
        myBuildRequirements = db.session.query(v_build_requirements).filter_by(id = id, product_id = selected_bp.t2_id ).with_entities('id', 'material', 'material_id', 'group_id', 'qty', 'product_id').all()

        myBuildCost = 0
        myMaterialCost = []
        for requirements in myBuildRequirements:
            myMaterialCost += [get_marketValue(requirements.material_id, 'sell') * requirements.qty]

        for cost in myMaterialCost:
            myBuildCost = myBuildCost + cost

        if 'myUser_id' in session:
            pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id']).with_entities('id','user_id','product_id','blueprint_id','runs','material_id','material_qty','material_cost','product_name','material', 'group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost').order_by('material').all()

            pipeline_products = db.session.query(v_build_pipeline_products).filter_by(user_id = session['myUser_id']).with_entities('product_name', 'user_id', 'blueprint_id', 'product_id','runs','jita_sell_price','local_sell_price','build_cost')

            materialInPipeline = build_pipeline_rollup_qty(pipeline)
            materialCost = build_pipeline_rollup_cost(pipeline)

            return render_template('build.html', form=form, blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, sell_median=querySell, time=myTime, buildRequirements = myBuildRequirements, buildCost = myBuildCost, materialCost = myMaterialCost, pipeline=pipeline, materialInPipeline=materialInPipeline, pipelineCost=materialCost, pipeline_products=pipeline_products, runs=runs)

        else:
            return render_template('build.html', form=form, blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, sell_median=querySell, time=myTime, buildRequirements = myBuildRequirements, buildCost = myBuildCost, materialCost = myMaterialCost)

    except Exception as e:
        flash('Problem querying blueprint. See log', 'danger')
        app.logger.info(str(e))
        return redirect(url_for('build'))

@app.route('/build_add_pipeline', methods=['POST'])
def build_add_pipeline():
    id = request.form.get('bp_id')
    form = LoginForm(request.form)
    if 'myUser_id' in session:
        try:
            if id > 0:
                myBlueprints = db.session.query(v_build_product).all()
                selected_bp = db.session.query(v_build_product).filter_by(id = id).one()
                myProduct = db.session.query(invtypes).filter_by(typeID = int(selected_bp.t2_id)).one()
                querySell = get_marketValue(str(myProduct.typeID),'buy')
                buildTime = db.session.query(v_build_time).filter_by(id = id).one()
                myTime = "{:,}".format(buildTime.time/60)
                myBuildRequirements = db.session.query(v_build_requirements).filter_by(id = id, product_id=myProduct.typeID).with_entities('id','material','material_id','group_id','qty','product_id').all()
                myBuildCost = 0
                myMaterialCost = []
                for requirements in myBuildRequirements:
                    myMaterialCost += [get_marketValue(requirements.material_id, 'sell') * requirements.qty]

                for cost in myMaterialCost:
                    myBuildCost = myBuildCost + cost

                pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id']).with_entities('id','user_id','product_id','blueprint_id','runs','material_id','material_qty','material_cost','product_name','material', 'group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','jita_sell_price','local_sell_price','build_cost','material_comp_id').order_by('material').all()

                pipeline_products = db.session.query(v_build_pipeline_products).filter_by(user_id = session['myUser_id']).with_entities('product_name', 'user_id', 'blueprint_id', 'product_id','runs','jita_sell_price','local_sell_price','build_cost')

                materialInPipeline = build_pipeline_rollup_qty(pipeline)
                materialCost = build_pipeline_rollup_cost(pipeline)

                if request.form.get('job_runs') <> '':
                    for requirements in myBuildRequirements:
                        myCost = get_marketValue(requirements.material_id, 'sell') * requirements.qty

                        pipeline = build_pipeline(session['myUser_id'],  myProduct.typeID, id, request.form.get('job_runs'), requirements.material_id, requirements.qty, myCost, myProduct.typeName, requirements.material, requirements.group_id, 0, querySell, 0, myBuildCost, 0)

                        db.session.add(pipeline)
                        db.session.commit()

                    flash('Successfully added to pipeline.','success')
                    return redirect(url_for('build'))
                else:
                    flash('Enter a quantity in job runs field.', 'danger')
                    return render_template('build.html', form=form, blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, sell_median=querySell, time=myTime, buildRequirements = myBuildRequirements, buildCost = myBuildCost, materialCost = myMaterialCost, pipeline=pipeline, materialInPipeline=materialInPipeline, pipelineCost=materialCost, pipeline_products=pipeline_products)

            else:
                flash('Choose a product to build.', 'danger')
                return redirect(url_for('build'))

        except Exception as e:
            flash('Problem adding to pipeline. See log.', 'danger')
            app.logger.info(str(e))
            return redirect(url_for('build'))

    else:
        flash('You must be logged in to add to pipeline.', 'danger')
        return redirect(url_for('build'))

@app.route('/invent', methods=['GET','POST'])
def invent():
    runs = 20
    form = LoginForm(request.form)
    try:
        myBlueprints = db.session.query(v_invention_product).all()
        if request.method == 'POST':
            if request.form['action'] == 'edit':
                if request.form['product_name']:
                    product_name = request.form['product_name']
                    runs = request.form['runs']
                    pipeline = db.session.query(invent_pipeline).filter_by(product_name = product_name).all()
                    for item in pipeline:
                        item.runs = runs
                        db.session.add(item)
                        db.session.commit()

                    flash('Successfully updated pipeline runs.', 'success')
            elif request.form.get('action') == 'delete':
                if request.form.get('product_name'):
                    product_name = request.form.get('product_name')
                    pipeline = db.session.query(invent_pipeline).filter_by(product_name = product_name).all()
                    for item in pipeline:
                        db.session.delete(item)
                        db.session.commit()

                    flash('Successfully deleted pipeline product.', 'success')

        if 'myUser_id' in session:
            pipeline = db.session.query(invent_pipeline).filter_by(user_id = session['myUser_id']).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','datacore_id','datacore_qty','datacore_cost','datacore').order_by('datacore').all()

            pipeline_products = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id']).with_entities('product_name', 'user_id', 'runs')

            materialInPipeline = invent_pipeline_rollup_qty(pipeline)
            materialCost = invent_pipeline_rollup_cost(pipeline)

            return render_template('invent.html', form=form, blueprints=myBlueprints, bp_id=0, pipeline=pipeline, materialInPipeline=materialInPipeline, pipeline_products=pipeline_products, materialCost=materialCost, runs=runs)
        else:
            return render_template('invent.html', form=form, blueprints=myBlueprints, bp_id=0)

    except Exception as e:
        flash('Problem with blueprint - see log.', 'danger')
        app.logger.info(str(e))
        return redirect(url_for('invent'))

@app.route('/invent_selected', methods=['POST','GET'])
def invent_selected():
    queryByName = False
    runs = 20
    id = request.form.get('invent_product')
    if request.args.get('invent_productName'):
        queryByName = True
        runs = int(request.args.get('runs'))

    form = LoginForm(request.form)
    try:
        myBlueprints = db.session.query(v_invention_product).all()
        if queryByName == True:
            productName = request.args.get('invent_productName')
            selected_bp = db.session.query(v_invention_product).filter_by(t2_blueprint = productName).first()
            id = selected_bp.id
        else:
            selected_bp = db.session.query(v_invention_product).filter_by(id = id).one()

        selected_product = db.session.query(v_product).filter_by(id = selected_bp.t2_id).one()
        myProduct = db.session.query(invtypes).filter_by(typeID = int(selected_product.t2_id)).one()
        myProbability = db.session.query(v_probability).filter_by(id = id).one()
        myProbPercent = "{:.2%}".format(myProbability.probability)
        querySell = get_marketValue(str(myProduct.typeID),'buy')
        mySellMedian = "{:,.0f}".format(querySell)
        inventTime = db.session.query(v_invent_time).filter_by(id = id).one()
        myTime = "{:,}".format((inventTime.time/60)/60)
        myDatacoreRequirements = db.session.query(v_datacore_requirements).filter_by(id = id).with_entities('id','datacore','quantity','dc_id').all()
        myDatacoresCost = 0
        for datacore in myDatacoreRequirements:
            myDatacoresCost = myDatacoresCost + get_marketValue(datacore.dc_id, 'sell') * datacore.quantity

        myBaseProduct = db.session.query(v_build_requirements).filter_by(id = selected_bp.t2_id).filter(v_build_requirements.group_id <> 334).filter(v_build_requirements.group_id <> 18).filter(v_build_requirements.group_id <> 1034).filter(v_build_requirements.group_id <> 332).filter(v_build_requirements.group_id <> 1040).one()

        if 'myUser_id' in session:

            pipeline = db.session.query(invent_pipeline).filter_by(user_id = session['myUser_id']).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','datacore_id','datacore_qty','datacore_cost','datacore').order_by('datacore').all()

            pipeline_products = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id']).with_entities('product_name', 'user_id', 'runs')

            materialInPipeline = invent_pipeline_rollup_qty(pipeline)
            materialCost = invent_pipeline_rollup_cost(pipeline)

            return render_template('invent.html', form=form, blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, probability=myProbPercent, sell_median=mySellMedian, time=myTime, datacoreRequirements = myDatacoreRequirements, datacoresCost=myDatacoresCost, baseProduct = myBaseProduct.material, pipeline=pipeline, materialInPipeline=materialInPipeline, materialCost=materialCost, pipeline_products=pipeline_products, runs=runs)

        else:
            return render_template('invent.html', form=form, blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, probability=myProbPercent, sell_median=mySellMedian, time=myTime, datacoreRequirements=myDatacoreRequirements, datacoresCost = myDatacoresCost, baseProduct = myBaseProduct.material)

    except Exception as e:
        flash('Problem querying blueprint. See log', 'danger')
        app.logger.info(str(e))
        return redirect(url_for('invent'))

@app.route('/invent_add_pipeline', methods=['POST'])
def invent_add_pipeline():
    id = request.form.get('bp_id')
    form = LoginForm(request.form)

    if 'myUser_id' in session:
        try:
            if id > 0:
                myBlueprints = db.session.query(v_invention_product).all()
                selected_bp = db.session.query(v_invention_product).filter_by(id = id).one()
                selected_product = db.session.query(v_product).filter_by(id = selected_bp.t2_id).one()
                myProduct = db.session.query(invtypes).filter_by(typeID = int(selected_bp.t2_id)).one()
                querySell = get_marketValue(str(myProduct.typeID),'buy')
                inventTime = db.session.query(v_invent_time).filter_by(id = id).one()
                myTime = "{:,}".format((inventTime.time/60)/60)
                myDatacoreRequirements = db.session.query(v_datacore_requirements).filter_by(id = id).with_entities('id','datacore','quantity','dc_id').all()
                myInventCost = 0
                myDatacoreCost = []
                for requirements in myDatacoreRequirements:
                    myDatacoreCost += [get_marketValue(requirements.dc_id, 'sell') * requirements.quantity]

                for cost in myDatacoreCost:
                    myInventCost += cost

                pipeline = db.session.query(invent_pipeline).filter_by(user_id = session['myUser_id']).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','datacore_id','datacore_qty','datacore_cost','datacore').order_by('datacore').all()

                pipeline_products = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id']).with_entities('product_name', 'user_id', 'runs')

                materialInPipeline = invent_pipeline_rollup_qty(pipeline)
                materialCost = invent_pipeline_rollup_cost(pipeline)

                if request.form.get('job_runs') <> '':
                    for requirements in myDatacoreRequirements:
                        myCost = get_marketValue(requirements.dc_id, 'sell') * requirements.quantity

                        pipeline = invent_pipeline(session['myUser_id'],  myProduct.typeID, id, request.form.get('job_runs'), selected_bp.t2_blueprint, requirements.dc_id, requirements.quantity, myCost, requirements.datacore)

                        db.session.add(pipeline)
                        db.session.commit()

                    flash('Successfully added to pipeline.','success')
                    return redirect(url_for('invent'))
                else:
                    flash('Enter a quantity in job runs field.', 'danger')
                    return render_template('invent.html', form=form, blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, sell_median=querySell, time=myTime, datacoreRequirements = myDatacoreRequirements, inventCost = myInventCost, datacoreCost = myDatacoreCost, pipeline=pipeline, materialInPipeline=materialInPipeline, materialCost=materialCost, pipeline_products=pipeline_products)

            else:
                flash('Choose a product to invent.', 'danger')
                return redirect(url_for('invent'))

        except Exception as e:
            flash('Problem adding to pipeline. See log.', 'danger')
            app.logger.info(str(e))
            return redirect(url_for('invent'))

    else:
        flash('You must be logged in to add to pipeline.', 'danger')
        return redirect(url_for('invent'))


@app.route('/updateBuilder', methods=['POST'])
def updateBuilder():
    if request.method == 'POST':
        try:
            if 'email' in session:
                email = session['email']
                editedBuilder = db.session.query(User).filter_by(email = email).one()
                if request.form['name']:
                    editedBuilder.name = request.form['name']
                if request.form['email']:
                    editedBuilder.email = request.form['email']
                if request.form['password']:
                    editedBuilder.password = sha256_crypt.encrypt(str(request.form['password']))
                if request.form['api_key']:
                    editedBuilder.api_key = request.form['api_key']
                if request.form['api_code']:
                    editedBuilder.api_code = request.form['api_code']

                editedBuilder.last_logged_in = datetime.now()
                db.session.add(editedBuilder)
                db.session.commit()
                flash('Builder details successfully updated.', 'success')
                session['logged_in'] = True
                session['name'] = editedBuilder.name
                session['email'] = editedBuilder.email
                session['api_key'] = editedBuilder.api_key
                session['api_code'] = editedBuilder.api_code

                app.logger.info(editedBuilder.name + ' successfully updated.')

            return redirect(url_for('index'))
        except Exception as e:
            flash('Builder update failed. See log', 'danger')
            app.logger.info(str(e))
            return redirect(url_for('index'))


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password_candidate = form.password.data
        try:
            myUser = db.session.query(User).filter_by(email = email).one()
            lli = myUser.last_logged_in.strftime('%b %d, %Y')
            if sha256_crypt.verify(password_candidate, myUser.password):
                session['logged_in'] = True
                session['name'] = myUser.name
                session['myUser_id'] = myUser.id
                session['email'] = myUser.email
                session['api_key'] = myUser.api_key
                session['api_code'] = myUser.api_code

                myUser.last_logged_in = datetime.now()
                db.session.add(myUser)
                db.session.commit()
                flash('Successful login. You last logged in on: ' + lli,  'success')
                return redirect(url_for('index'))
            else:
                flash('Login denied. Wrong password. Try again', 'danger')
                return render_template('login.html', form=form, error=error)
        except Exception as e:
            app.logger.info(str(e))
            flash('Problem logging in. See log', 'danger')
            return render_template('login.html', form=form, error=error)
    else:
        return render_template('login.html', form=form)

@app.route('/registration', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User('{'+ form.name.data +'}',  form.email.data, sha256_crypt.encrypt(str(form.password.data)), True, datetime.now())
        db.session.add(user)
        db.session.commit()
        flash('Successful Registration. Please login.')
        return redirect(url_for('index'))
    else:
        return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have logged out.', 'success')
    return redirect(url_for('index'))

def get_marketValue(typeID, buyOrSell):
    payload = {'typeid':typeID, 'regionlimit':10000002}
    try:
        response = requests.get('https://api.evemarketer.com/ec/marketstat/json', params=payload)
        jsonData = response.json()
        if buyOrSell == 'buy':
            return jsonData[0]['buy']['median']
        else:
            return jsonData[0]['sell']['median']

    except Exception as e:
        app.logger.info(str(e))
        flash('Problem with Market API. See log', 'danger')
        return 0


def build_pipeline_rollup_cost(pipeline):
    buildCost = 0.0
    for item in pipeline:
        buildCost += item.material_cost * item.runs

    return buildCost

def build_pipeline_rollup_qty(pipeline):
    materialInPipeline = []
    matchFound1 = False

    for item in pipeline:
        for mat in materialInPipeline:
            if mat.material_id == item.material_id:
                mat.material_qty += item.material_qty * item.runs
                mat.material_cost += item.material_cost
                matchFound1 = True

        if matchFound1 == True:
            matchFound1 = False
        else:
            my_bom = BomMaterial(item.material_id, item.material, (item.material_qty*item.runs), item.material_cost, item.runs, item.id, item.build_or_buy, item.blueprint_id)
            materialInPipeline += [my_bom]

    return materialInPipeline

def invent_pipeline_rollup_cost(pipeline):
    buildCost = 0.0
    for item in pipeline:
        buildCost += item.datacore_cost * item.runs

    return buildCost

def invent_pipeline_rollup_qty(pipeline):
    materialInPipeline = []
    matchFound1 = False

    for item in pipeline:
        for mat in materialInPipeline:
            if mat.datacore_id == item.datacore_id:
                mat.datacore_qty += item.datacore_qty
                matchFound1 = True

        if matchFound1 == True:
            matchFound1 = False
        else:
            my_bom = BomDatacores(item.datacore_id, item.datacore, item.datacore_qty, item.datacore_cost, item.runs)
            materialInPipeline += [my_bom]

    return materialInPipeline

if __name__ == "__main__":
   app.run()
