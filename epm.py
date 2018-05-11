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
app.config['POOL_SIZE'] = 20
app.config['MAX_OVERFLOW'] = 0

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

class ship_fittings(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    build_id = db.Column(db.Integer())
    user_id = db.Column(db.Integer())
    ship_id = db.Column(db.Integer())
    ship_name = db.Column(db.String(100))
    qty = db.Column(db.Integer())
    num_rigslots = db.Column(db.Integer())
    num_lowslots = db.Column(db.Integer())
    num_medslots = db.Column(db.Integer())
    num_highslots = db.Column(db.Integer())
    component_id = db.Column(db.Integer())
    component_qty = db.Column(db.Integer())
    component_cost = db.Column(db.Numeric())
    component = db.Column(db.String(100))
    component_slot = db.Column(db.String(20))
    contract_sell_price = db.Column(db.Numeric())
    build_cost = db.Column(db.Numeric())
    jita_buy = db.Column(db.Numeric())
    rollup = db.Column(db.Integer())

    def __init__(self, build_id, user_id, ship_id, ship_name, qty, num_rigslots, num_lowslots, num_medslots, num_highslots, component_id, component_qty, component_cost, component, component_slot, contract_sell_price, build_cost, jita_buy, rollup):
        self.build_id = build_id
        self.user_id = user_id
        self.ship_id = ship_id
        self.ship_name = ship_name
        self.qty = qty
        self.num_rigslots = num_rigslots
        self.num_lowslots = num_lowslots
        self.num_medslots = num_medslots
        self.num_highslots = num_highslots
        self.component_id = component_id
        self.component_qty = component_qty
        self.component_cost = component_cost
        self.component = component
        self.component_slot = component_slot
        self.contract_sell_price = contract_sell_price
        self.build_cost = build_cost
        self.jita_buy = jita_buy
        self.rollup = rollup

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
    status = db.Column(db.Integer())

    def __init__(self, user_id, product_id, blueprint_id, runs, material_id, material_qty, material_cost, product_name, material, group_id, build_or_buy, jita_sell_price, local_sell_price, build_cost, material_comp_id, status):
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
        self.status = status

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
    status = db.Column(db.Integer())

    def __init__(self, user_id, product_id, blueprint_id, runs, product_name, datacore_id, datacore_qty, datacore_cost, datacore, status):
        self.user_id = user_id
        self.product_id = product_id
        self.blueprint_id = blueprint_id
        self.runs = runs
        self.product_name = product_name
        self.datacore_id = datacore_id
        self.datacore_qty = datacore_qty
        self.datacore_cost = datacore_cost
        self.datacore = datacore
        self.status = status

class mining_calc(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    m3_per_cycle = db.Column(db.Integer())
    cycle_time = db.Column(db.Integer())
    num_cycles = db.Column(db.Integer())
    refinery = db.Column(db.Numeric())
    trit_required = db.Column(db.Integer())
    pye_required = db.Column(db.Integer())
    mex_required = db.Column(db.Integer())
    iso_required = db.Column(db.Integer())
    nox_required = db.Column(db.Integer())
    zyd_required = db.Column(db.Integer())
    meg_required = db.Column(db.Integer())
    morph_required = db.Column(db.Integer())
    asteroid1_id = db.Column(db.Integer())
    asteroid2_id = db.Column(db.Integer())
    asteroid3_id = db.Column(db.Integer())
    asteroid4_id = db.Column(db.Integer())

    def __init__(self, user_id, m3_per_cycle, cycle_time, num_cycles, refinery, trit_required, pye_required, mex_required, iso_required, nox_required, zyd_required, meg_required, morph_required, asteroid1_id, asteroid2_id, asteroid3_id, asteroid4_id):
        self.user_id = user_id
        self.m3_per_cycle = m3_per_cycle
        self.cycle_time = cycle_time
        self.num_cycles = num_cycles
        self.refinery = refinery
        self.trit_required = trit_required
        self.pye_required = pye_required
        self.mex_required = mex_required
        self.iso_required = iso_required
        self.nox_required = nox_required
        self.zyd_required = zyd_required
        self.meg_required = meg_required
        self.morph_required = morph_required
        self.asteroid1_id = asteroid1_id
        self.asteroid2_id = asteroid2_id
        self.asteroid3_id = asteroid3_id
        self.asteroid4_id = asteroid4_id

class v_ships(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    ship = db.Column(db.String(100))

    def __init__(ship):
        self.ship = str(ship)

class v_count_fittings(db.Model):
    build_id = db.Column(db.Integer(), primary_key=True)
    ship_id = db.Column(db.Integer())
    ship_name = db.Column(db.String())
    user_id = db.Column(db.Integer())
    contract_sell_price = db.Column(db.Numeric())
    qty = db.Column(db.Integer())
    rollup = db.Column(db.Integer())
    jita_buy = db.Column(db.Numeric())

    def __init__(ship_id, ship_name, user_id, contract_sell_price, qty, rollup, jita_buy):
        self.ship_id = ship_id
        self.ship_name = ship_name
        self.user_id = user_id
        self.contract_sell_price = contract_sell_price
        self.qty = qty
        self.rollup = rollup
        self.jita_buy = jita_buy

class v_buildable_fittings(db.Model):
    build_id = db.Column(db.Integer(), primary_key=True)
    ship_id = db.Column(db.Integer())
    ship_name = db.Column(db.String())
    jita_buy = db.Column(db.Numeric())
    qty = db.Column(db.Integer())
    id = db.Column(db.Integer())
    component = db.Column(db.String())
    component_cost = db.Column(db.Numeric())
    component_qty = db.Column(db.Integer())
    build_cost = db.Column(db.Numeric())
    meta = db.Column(db.Integer())
    rollup = db.Column(db.Integer())

    def __init__(ship_id, ship_name, jita_buy, qty, component_id, component, component_cost, component_qty, build_cost, meta, rollup):
        self.ship_id = ship_id
        self.ship_name = ship_name
        self.jita_buy = jita_buy
        self.qty = qty
        self.id = component_id
        self.component = component
        self.component_cost = component_cost
        self.component_qty = component_qty
        self.build_cost = build_cost
        self.meta = meta
        self.rollup = rollup

class v_shipslots(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    ship_id = db.Column(db.Integer())
    valint = db.Column(db.Integer())
    valfloat = db.Column(db.Numeric())

    def __init__(ship_id, valint, valfloat):
        self.ship_id = ship_id
        self.valint = valint
        self.valfloat - valfloat

class v_modules(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    item = db.Column(db.String(100))
    category = db.Column(db.Integer())

    def __init__(item, category):
        self.item = item
        self.category = category

class v_rigs(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    item = db.Column(db.String(100))
    size = db.Column(db.Numeric())

    def __init__(item, size):
        self.item = item
        self.size = size

class v_item_by_cat(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    item = db.Column(db.String(100))
    category = db.Column(db.Integer())

    def __init__(item, category):
        self.item = item
        self.category = category

class v_build_components(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    material = db.Column(db.String(100))
    material_id= db.Column(db.Integer())
    quantity = db.Column(db.Integer())

    def __init__(material, material_id, quantity):
        self.material = str(material)
        self.material_id = material_id
        self.quantity = quantity

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

class v_build_pipeline_products(db.Model):
    product_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer(), primary_key=True)
    blueprint_id = db.Column(db.Integer())
    product_id = db.Column(db.Integer())
    runs = db.Column(db.Integer())
    jita_sell_price = db.Column(db.Numeric())
    local_sell_price = db.Column(db.Numeric())
    build_cost = db.Column(db.Numeric())
    status = db.Column(db.Integer())

    def __init__(product_name, user_id, blueprint_id, product_id, runs, jita_sell_price, local_sell_price, build_cost, status):
        self.product_name = str(product_name)
        self.user_id = user_id
        self.blueprint_id = blueprint_id
        self.product_id = product_id
        self.runs = runs
        self.jita_sell_price = jita_sell_price
        self.local_sell_price = local_sell_price
        self.build_cost = build_cost
        self.status = status

class v_invent_pipeline_products(db.Model):
    product_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer(), primary_key=True)
    blueprint_id = db.Column(db.Integer())
    runs = db.Column(db.Integer())
    status = db.Column(db.Integer())

    def __init__(product_name, user_id, blueprint_id, runs, status):
        self.product_name = str(product_name)
        self.user_id = user_id
        self.blueprint_id = blueprint_id
        self.runs = runs
        self.status = status

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

class v_asteroids(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    group_id = db.Column(db.Integer())
    asteroid = db.Column(db.String())
    vol = db.Column(db.Numeric())
    portion = db.Column(db.Integer())

    def __init__(group_id, asteroid, vol, portion):
        self.group_id = group_id
        self.asteroid = asteroid
        self.vol = vol
        self.portion = portion

class v_asteroid_groups(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    group = db.Column(db.String())

    def __init__(group):
        self.group = group

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

class MinedMinerals():
    def __init__(self, trit, pye, mex, iso, nox, zyd, meg, morph):
        self.trit = trit
        self.pye = pye
        self.mex = mex
        self.iso = iso
        self.nox = nox
        self.zyd = zyd
        self.meg = meg
        self.morph = morph

class FittingRigs():
    def __init__(self, id, component, component_qty, component_cost):
        self.id = id
        self.component = component
        self.component_qty = component_qty
        self.component_cost = component_cost

@app.route("/")
def index():
    form = LoginForm(request.form)
    return render_template('home.html', form=form)

@app.route("/fittings", methods=['GET','POST'])
def fittings():
    form = LoginForm(request.form)
    if 'myUser_id' in session:
        #try:
        build_id = 1
        user_id = session['myUser_id']
        ships = db.session.query(v_ships).all()
        ship_name = ''
        num_rigslots = 0
        num_lowslots = 0
        num_medslots = 0
        num_highslots = 0
        rigsize = 0
        fittingIndex = 0
        ship_id = 0
        myFittings = []
        nonBuildableFittings = []
        rigRollup = []
        nonBuildableTotal = 0.0
        buildableFittings = []
        buildableTotal = 0.0
        fittingCost = 0
        fittingPM = 0.0
        if request.form.get('ship_id'):
            ship_id = request.form.get('ship_id')
        if request.form.get('build_id'):
            build_id = request.form.get('build_id')

        myFittingsCount = db.session.query(v_count_fittings).filter_by(user_id=user_id).order_by('ship_name').count()
        if myFittingsCount > 0:
            myFittings = db.session.query(v_count_fittings).filter_by(user_id=user_id).order_by('ship_name').all()
            if request.form.get('fittingIndex') > 0 :
                fittingIndex = request.form.get('fittingIndex')
            ship_id = myFittings[fittingIndex].ship_id
            shipFittings = db.session.query(ship_fittings).filter_by(user_id=user_id, build_id=build_id).order_by('ship_name').all()
            fittingCost = fitting_rollup_cost(shipFittings)
            fittingPM = ((float(shipFittings[0].qty) * float(shipFittings[0].contract_sell_price)) / float(fittingCost)) -1.0

            nonBuildableFittings = db.session.query(v_buildable_fittings).filter(v_buildable_fittings.meta <> 2).filter(v_buildable_fittings.rollup==1).with_entities('ship_id', 'ship_name', 'jita_buy', 'qty', 'id', 'component', 'component_cost', 'component_qty', 'build_cost', 'meta', 'rollup').all()
            for nbf in nonBuildableFittings:
                nonBuildableTotal += (float(nbf.qty) * float(nbf.component_qty) * float(nbf.component_cost))
            for fitting in shipFittings:
                if fitting.component_slot == 'rig' and fitting.rollup==1:
                    rig = FittingRigs(fitting.component_id, fitting.component, fitting.component_qty, fitting.component_cost)
                    rigRollup += [rig]
                    nonBuildableTotal += (float(nonBuildableFittings[0].qty) * float(fitting.component_qty) * float(fitting.component_cost))

            buildableFittings = db.session.query(v_buildable_fittings).filter_by(meta=2, rollup=1).with_entities('ship_id', 'ship_name', 'jita_buy', 'qty', 'id', 'component', 'component_cost', 'component_qty', 'build_cost', 'meta', 'rollup').all()
            for bf in buildableFittings:
                buildableTotal += (float(bf.qty) * float(bf.component_qty) * float(bf.component_cost))
            if buildableFittings:
                buildableTotal += float(buildableFittings[0].qty) * float(buildableFittings[0].jita_buy)

        if ship_id > 0 :
            rigs = db.session.query(v_shipslots).filter_by(id=1137, ship_id=ship_id).one()
            rigsize = db.session.query(v_shipslots).filter_by(id=1547, ship_id=ship_id).one()
            myRigSize = rigsize.valfloat
            rig_modules = db.session.query(v_rigs).filter_by(size=myRigSize).all()
            lows = db.session.query(v_shipslots).filter_by(id=12, ship_id=ship_id).one()
            low_modules = db.session.query(v_modules).filter_by(category=11).all()
            meds = db.session.query(v_shipslots).filter_by(id=13, ship_id=ship_id).one()
            med_modules = db.session.query(v_modules).filter_by(category=13).all()
            highs = db.session.query(v_shipslots).filter_by(id=14, ship_id=ship_id).one()
            high_modules = db.session.query(v_modules).filter_by(category=12).all()
            ammos = db.session.query(v_item_by_cat).filter_by(category=8).all()
            drones = db.session.query(v_item_by_cat).filter_by(category=18).all()
            if rigs.valfloat:
                num_rigslots = rigs.valfloat
            else:
                num_rigslots = rigs.valint
            if rigsize.valfloat:
                rigsize = rigs.valfloat
            else:
                rigsize = rigs.valint
            if lows.valfloat:
                num_lowslots = lows.valfloat
            else:
                num_lowslots = lows.valint
            if meds.valfloat:
                num_medslots = meds.valfloat
            else:
                num_medslots = meds.valint
            if highs.valfloat:
                num_highslots = highs.valfloat
            else:
                num_highslots = highs.valint



        if request.method == 'POST':
            #print request.form.get('action')
            if request.form.get('action') == 'new':
                item = db.session.query(v_ships).filter_by(id = ship_id).one()
                ship_name = item.ship
                #print ship_name

                return render_template('fittings.html', form=form, ships=ships, ship_id=ship_id, ship_name=ship_name, num_rigslots=num_rigslots, num_lowslots=num_lowslots, num_medslots=num_medslots, num_highslots=num_highslots, rig_modules=rig_modules, low_modules=low_modules, med_modules=med_modules, high_modules=high_modules,ammos=ammos, drones=drones, myFittingsCount=myFittingsCount, myFittings=myFittings, fittingIndex=fittingIndex)

            elif request.form.get('action') == 'delete':
                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id']).all()
                for fit in existingFitting:
                    db.session.delete(fit)
                    db.session.commit()

                flash('Successfully deleted fitting.', 'success')
                return redirect(url_for('fittings'))

            elif request.form.get('action') == 'edit':
                item = db.session.query(v_ships).filter_by(id = ship_id).one()
                ship_name = item.ship
                ship_jita_buy = get_marketValue(ship_id,'buy')
                myQty = int(request.form.get('qty'))
                myContractPrice = float(request.form.get('contract_sell_price').replace(',', ''))
                myRollup = 0
                if request.form.get('rollup'):
                    myRollup = 1

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='high').all()
                for n in range(1, num_highslots+1):
                    #print  request.form.get('hi'+str(n))
                    if request.form.get('hi'+str(n)) > 0:
                        comp_id  = request.form.get('hi'+str(n))
                        #print comp_id
                        if comp_id > 0:
                            comp_jita_buy = get_marketValue(comp_id,'buy')
                            comp = db.session.query(invtypes).filter_by(typeID=comp_id).one()

                        if existingFitting:
                            fit = existingFitting[n-1]
                            fit.qty = myQty
                            fit.component_id = comp_id
                            fit.component_qty = 1
                            fit.component_cost = comp_jita_buy
                            fit.component = comp.typeName
                            fit.contract_sell_price = myContractPrice
                            fit.rollup = myRollup
                            db.session.add(fit)
                            db.session.commit()
                        else:
                            myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, 1, comp_jita_buy, comp.typeName, 'high', myContractPrice, 0, ship_jita_buy, myRollup)
                            db.session.add(myFittings)
                            db.session.commit()

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='med').all()
                for n in range(1, num_medslots+1):
                    if request.form.get('med'+str(n)):
                        comp_id  = request.form.get('med'+str(n))
                        if comp_id > 0:
                            comp_jita_buy = get_marketValue(comp_id,'buy')
                            comp = db.session.query(invtypes).filter_by(typeID=comp_id).one()

                        if existingFitting:
                            fit = existingFitting[n-1]
                            fit.qty = myQty
                            fit.component_id = comp_id
                            fit.component_qty = 1
                            fit.component_cost = comp_jita_buy
                            fit.component = comp.typeName
                            fit.contract_sell_price = myContractPrice
                            fit.rollup = myRollup
                            db.session.add(fit)
                            db.session.commit()
                        else:
                            myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, 1, comp_jita_buy, comp.typeName, 'med', myContractPrice, 0, ship_jita_buy, myRollup)
                            db.session.add(myFittings)
                            db.session.commit()

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='low').all()
                for n in range(1, num_lowslots+1):
                    if request.form.get('low'+str(n)):
                        comp_id  = request.form.get('low'+str(n))
                        if comp_id > 0:
                            comp_jita_buy = get_marketValue(comp_id,'buy')
                            comp = db.session.query(invtypes).filter_by(typeID=comp_id).one()

                        if existingFitting:
                            fit = existingFitting[n-1]
                            fit.qty = myQty
                            fit.component_id = comp_id
                            fit.component_qty = 1
                            fit.component_cost = comp_jita_buy
                            fit.component = comp.typeName
                            fit.contract_sell_price = myContractPrice
                            fit.rollup = myRollup
                            db.session.add(fit)
                            db.session.commit()
                        else:
                            myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, 1, comp_jita_buy, comp.typeName, 'low', myContractPrice, 0, ship_jita_buy, myRollup)
                            db.session.add(myFittings)
                            db.session.commit()

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='rig').all()
                for n in range(1, num_rigslots+1):
                    if request.form.get('rig'+str(n)):
                        comp_id  = request.form.get('rig'+str(n))
                        if comp_id > 0:
                            comp_jita_buy = get_marketValue(comp_id,'buy')
                            comp = db.session.query(invtypes).filter_by(typeID=comp_id).one()

                        if existingFitting:
                            fit = existingFitting[n-1]
                            fit.qty = myQty
                            fit.component_id = comp_id
                            fit.component_qty = 1
                            fit.component_cost = comp_jita_buy
                            fit.component = comp.typeName
                            fit.contract_sell_price = myContractPrice
                            fit.rollup = myRollup
                            db.session.add(fit)
                            db.session.commit()
                        else:
                            myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, 1, comp_jita_buy, comp.typeName, 'rig', myContractPrice, 0, ship_jita_buy, myRollup)
                            db.session.add(myFittings)
                            db.session.commit()

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='ammo').all()
                for n in range(1, 6):
                    if request.form.get('ammo'+str(n)):
                        comp_qty = request.form.get('ammo_qty'+str(n))
                        comp_id  = request.form.get('ammo'+str(n))
                        if comp_id > 0:
                            comp_jita_buy = get_marketValue(comp_id,'buy')
                            comp = db.session.query(invtypes).filter_by(typeID=comp_id).one()

                        if existingFitting:
                            fit = existingFitting[n-1]
                            fit.qty = myQty
                            fit.component_id = comp_id
                            fit.component_qty = comp_qty
                            fit.component_cost = comp_jita_buy
                            fit.component = comp.typeName
                            fit.contract_sell_price = myContractPrice
                            fit.rollup = myRollup
                            db.session.add(fit)
                            db.session.commit()
                        else:
                            myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, 1, comp_jita_buy, comp.typeName, 'ammo', myContractPrice, 0, ship_jita_buy, myRollup)
                            db.session.add(myFittings)
                            db.session.commit()

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='drone').all()
                for n in range(1, 6):
                    if request.form.get('drone'+str(n)):
                        comp_qty = request.form.get('drone_qty'+str(n))
                        comp_id  = request.form.get('drone'+str(n))
                        if comp_id > 0:
                            comp_jita_buy = get_marketValue(comp_id,'buy')
                            comp = db.session.query(invtypes).filter_by(typeID=comp_id).one()

                        if existingFitting:
                            fit = existingFitting[n-1]
                            fit.qty = myQty
                            fit.component_id = comp_id
                            fit.component_qty = comp_qty
                            fit.component_cost = comp_jita_buy
                            fit.component = comp.typeName
                            fit.contract_sell_price = myContractPrice
                            fit.rollup = myRollup
                            db.session.add(fit)
                            db.session.commit()
                        else:
                            myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, 1, comp_jita_buy, comp.typeName, 'drone', myContractPrice, 0, ship_jita_buy, myRollup)
                            db.session.add(myFittings)
                            db.session.commit()

                #myFittingsCount = db.session.query(v_count_fittings).filter_by(user_id=user_id).order_by('ship_name').count()
                #myFittings = db.session.query(ship_fittings).filter_by(user_id=user_id).order_by('ship_name').all()
                return redirect(url_for('fittings'))


        if myFittingsCount > 0:
            myFittingsHigh = db.session.query(ship_fittings).filter_by(user_id=user_id, ship_id=ship_id, component_slot='high').all()
            myFittingsMed = db.session.query(ship_fittings).filter_by(user_id=user_id, ship_id=ship_id, component_slot='med').all()
            myFittingsLow = db.session.query(ship_fittings).filter_by(user_id=user_id, ship_id=ship_id, component_slot='low').all()
            myFittingsRig = db.session.query(ship_fittings).filter_by(user_id=user_id, ship_id=ship_id, component_slot='rig').all()
            myFittingsAmmo = db.session.query(ship_fittings).filter_by(user_id=user_id, ship_id=ship_id, component_slot='ammo').all()
            myFittingsDrone = db.session.query(ship_fittings).filter_by(user_id=user_id, ship_id=ship_id, component_slot='drone').all()

            return render_template('fittings.html', form=form, ships=ships, ship_id=ship_id, ship_name=ship_name, num_rigslots=num_rigslots, num_lowslots=num_lowslots, num_medslots=num_medslots, num_highslots=num_highslots, rig_modules=rig_modules, low_modules=low_modules, med_modules=med_modules, high_modules=high_modules,ammos=ammos, drones=drones, myFittingsCount=myFittingsCount, myFittings=myFittings, myFittingsHigh=myFittingsHigh, myFittingsMed=myFittingsMed, myFittingsLow=myFittingsLow, myFittingsRig=myFittingsRig, myFittingsAmmo=myFittingsAmmo, myFittingsDrone=myFittingsDrone, fittingIndex=fittingIndex, fittingCost=fittingCost, fittingPM=fittingPM, buildableFittings=buildableFittings, nonBuildableFittings=nonBuildableFittings, nonBuildableTotal=nonBuildableTotal, buildableTotal=buildableTotal, build_id=build_id, rigRollup=rigRollup)

        return render_template('fittings.html', form=form, ships=ships, myFittingsCount=0, ship_id=0)

        #except Exception as e:
        #    flash('Problem with Ship Fittings - see log.', 'danger')
        #    app.logger.info(str(e))
        #    return redirect(url_for('fittings'))
    else:
        flash('You must be logged in to use Ship Fittings.', 'danger')
        return redirect(url_for('index'))

@app.route("/financial")
def financial():
    form = LoginForm(request.form)
    return render_template('financial.html', form=form)

@app.route("/mining", methods=['GET','POST'])
def mining():
    form = LoginForm(request.form)
    asteroid_groups = db.session.query(v_asteroid_groups).all()
    if 'myUser_id' in session:
        try:
            calcs = db.session.query(mining_calc).filter_by(user_id=session['myUser_id']).all()
            if not calcs:
                calc = mining_calc(session['myUser_id'],  300, 120, 30, .5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                db.session.add(calc)
                db.session.commit()

            if request.method == 'POST':
                if request.form.get('m3_per_cycle'):
                    for calc in calcs:
                        calc.m3_per_cycle = request.form.get('m3_per_cycle',type=int)
                        calc.cycle_time = request.form.get('cycle_time',type=int)
                        calc.num_cycles = request.form.get('num_cycles')
                        calc.refinery = float(request.form.get('refinery'))/100
                        db.session.add(calc)
                        db.session.commit()

                if request.form.get('clear'):
                    for calc in calcs:
                        calc.trit_required = 0
                        calc.pye_required = 0
                        calc.mex_required = 0
                        calc.iso_required = 0
                        calc.nox_required = 0
                        calc.zyd_required = 0
                        calc.meg_required = 0
                        calc.morph_required = 0
                        db.session.add(calc)
                        db.session.commit()

                mined_mins1 = MinedMinerals(0,0,0,0,0,0,0,0)
                mined_mins2 = MinedMinerals(0,0,0,0,0,0,0,0)
                mined_mins3 = MinedMinerals(0,0,0,0,0,0,0,0)
                mined_mins4 = MinedMinerals(0,0,0,0,0,0,0,0)
                min_id1 = 0
                min_id2 = 0
                min_id3 = 0
                min_id4 = 0
                group_id1 = 0
                group_id2 = 0
                group_id3 = 0
                group_id4 = 0
                asteroid_name1 = ''
                asteroid_name2 = ''
                asteroid_name3 = ''
                asteroid_name4 = ''

                if request.form.get('asteroid'):
                    if int(request.form.get('asteroid')) > 0:
                        min_id1 = request.form.get('asteroid')
                        asteroid_stats1 = db.session.query(v_asteroids).filter_by(id=min_id1).one()
                        mined_mins1 = refine_asteroid(min_id1, calcs, asteroid_stats1)
                        group_id1 = asteroid_stats1.group_id
                        asteroid_name1 = asteroid_stats1.asteroid

                if request.form.get('asteroid1'):
                    if int(request.form.get('asteroid1')) > 0:
                        min_id2 = request.form.get('asteroid1')
                        asteroid_stats2 = db.session.query(v_asteroids).filter_by(id=min_id2).one()
                        mined_mins2 = refine_asteroid(min_id2, calcs, asteroid_stats2)
                        group_id2 = asteroid_stats2.group_id
                        asteroid_name2 = asteroid_stats2.asteroid

                if request.form.get('asteroid2'):
                    if int(request.form.get('asteroid2')) > 0:
                        min_id3 = request.form.get('asteroid2')
                        asteroid_stats3 = db.session.query(v_asteroids).filter_by(id=min_id3).one()
                        mined_mins3 = refine_asteroid(min_id3, calcs, asteroid_stats3)
                        group_id3 = asteroid_stats3.group_id
                        asteroid_name3 = asteroid_stats3.asteroid

                if request.form.get('asteroid3'):
                    if int(request.form.get('asteroid3')) > 0:
                        min_id4 = request.form.get('asteroid3')
                        asteroid_stats4 = db.session.query(v_asteroids).filter_by(id=min_id4).one()
                        mined_mins4 = refine_asteroid(min_id4, calcs, asteroid_stats4)
                        group_id4 = asteroid_stats4.group_id
                        asteroid_name4 = asteroid_stats4.asteroid

                mined_mins = MinedMinerals(mined_mins1.trit +mined_mins2.trit +mined_mins3.trit +mined_mins4.trit, mined_mins1.pye +mined_mins2.pye +mined_mins3.pye +mined_mins4.pye, mined_mins1.mex +mined_mins2.mex +mined_mins3.mex +mined_mins4.mex, mined_mins1.iso +mined_mins2.iso +mined_mins3.iso +mined_mins4.iso, mined_mins1.nox +mined_mins2.nox +mined_mins3.nox +mined_mins4.nox, mined_mins1.zyd +mined_mins2.zyd +mined_mins3.zyd +mined_mins4.zyd, mined_mins1.meg +mined_mins2.meg +mined_mins3.meg +mined_mins4.meg, mined_mins1.morph +mined_mins2.morph +mined_mins3.morph +mined_mins4.morph)
                #print group_id1

                return render_template('mining.html', form=form, asteroid_groups=asteroid_groups, calcs=calcs, min_id1=min_id1, min_id2=min_id2, min_id3=min_id3, min_id4=min_id4, group_id1=group_id1, group_id2=group_id2, group_id3=group_id3, group_id4=group_id4, asteroid_name1=asteroid_name1, asteroid_name2=asteroid_name2, asteroid_name3=asteroid_name3, asteroid_name4=asteroid_name4, mined_mins=mined_mins)

            calcs = db.session.query(mining_calc).filter_by(user_id=session['myUser_id']).all()
            return render_template('mining.html', form=form, asteroid_groups=asteroid_groups, calcs=calcs)

        except Exception as e:
            flash('Problem with Mining Calculator - see log.', 'danger')
            app.logger.info(str(e))
            return redirect(url_for('mining'))
    else:
        flash('You must be logged in to use mining calculator.', 'danger')
        return redirect(url_for('index'))


@app.context_processor
def utility_processor():
    def getAsteroids(group_id):
        asteroids = db.session.query(v_asteroids).filter_by(group_id=group_id).all()
        return asteroids

    return dict(getAsteroids=getAsteroids)

@app.route("/pipeline", methods=['GET','POST'])
def pipeline():
    form = LoginForm(request.form)
    if 'myUser_id' in session:
        try:
            inv_pipeline = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id']).with_entities('product_name','user_id','runs','blueprint_id','status').order_by('product_name').all()

            bld_pipeline = db.session.query(v_build_pipeline_products).filter_by(user_id= session['myUser_id']).with_entities('product_name','user_id','blueprint_id','product_id','runs','jita_sell_price','local_sell_price','build_cost','status').order_by('product_name').all()

            if request.method == 'POST':
                if request.form.get('inv_pipeline_select'):
                    if request.form.get('action') == 'UPD':
                        bp_id = request.form.get('blueprint_id')
                        runs = request.form.get('qty')
                        status = request.form.get('inv_pipeline_select')

                        pipeline = db.session.query(invent_pipeline).filter_by(blueprint_id = bp_id).all()
                        for item in pipeline:
                            item.runs = runs
                            item.status = status
                            db.session.add(item)
                            db.session.commit()
                        #print request.form.get('inv_pipeline_select')
                        if request.form.get('inv_pipeline_select') == '2':

                            pipeline = db.session.query(invent_pipeline).filter_by(blueprint_id = bp_id).all()
                            product_id = 0
                            blueprint_id = 0
                            product_name = ''
                            for item in pipeline:
                                product_id = item.product_id
                                blueprint_id = item.blueprint_id
                                product_name = item.product_name
                                db.session.delete(item)
                                db.session.commit()

                            selected_product = db.session.query(v_product).filter_by(id = product_id).one()
                            querySell = get_marketValue(selected_product.t2_id,'buy')
                            myBuildRequirements = db.session.query(v_build_requirements).filter_by(id = product_id, product_id=selected_product.t2_id ).with_entities('id', 'material', 'material_id', 'group_id', 'qty', 'product_id').all()

                            myBuildCost = 0
                            myMaterialCost = []
                            for requirements in myBuildRequirements:
                                myMaterialCost += [get_marketValue(requirements.material_id, 'sell') * requirements.qty]

                            for cost in myMaterialCost:
                                myBuildCost = myBuildCost + cost

                            for requirements in myBuildRequirements:
                                myCost = get_marketValue(requirements.material_id, 'sell') * requirements.qty

                                pipeline = build_pipeline(session['myUser_id'],  selected_product.t2_id, product_id, runs, requirements.material_id, requirements.qty, myCost, product_name, requirements.material, requirements.group_id, 0, querySell, 0, myBuildCost, 0, 2)

                                db.session.add(pipeline)
                                db.session.commit()

                            flash('Successfully converted invention to build product.', 'success')

                    if request.form.get('action') == 'DEL':
                            bp_id = request.form.get('blueprint_id')

                            pipeline = db.session.query(invent_pipeline).filter_by(blueprint_id = bp_id).all()
                            for item in pipeline:
                                db.session.delete(item)
                                db.session.commit()
                            flash('Successfully deleted pipeline product.', 'success')

                    inv_pipeline = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id']).with_entities('product_name','user_id','runs','blueprint_id','status').order_by('product_name').all()

                if request.form.get('bld_pipeline_select'):
                    if request.form.get('action') == 'UPD':
                        bp_id = request.form.get('blueprint_id')
                        runs = request.form.get('qty')
                        status = request.form.get('bld_pipeline_select')
                        local_sell_price = float(request.form.get('local_sell'))
                        pipeline = db.session.query(build_pipeline).filter_by(blueprint_id = bp_id).all()
                        for item in pipeline:
                            item.runs = runs
                            item.status = status
                            item.local_sell_price = local_sell_price
                            db.session.add(item)
                            db.session.commit()

                    if request.form.get('action') == 'DEL':
                        bp_id = request.form.get('blueprint_id')

                        pipeline = db.session.query(build_pipeline).filter_by(blueprint_id = bp_id).all()
                        for item in pipeline:
                            db.session.delete(item)
                            db.session.commit()
                        flash('Successfully deleted pipeline product.', 'success')

                    bld_pipeline = db.session.query(v_build_pipeline_products).filter_by(user_id= session['myUser_id']).with_entities('product_name','user_id','blueprint_id','product_id','runs','jita_sell_price','local_sell_price','build_cost','status').order_by('product_name').all()

            return render_template('pipeline.html', form=form, inv_pipeline=inv_pipeline, bld_pipeline=bld_pipeline)

        except Exception as e:
            flash('Problem with Pipeline. - see log.', 'danger')
            app.logger.info(str(e))
            return redirect(url_for('pipeline'))
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

                if request.form.get('mine_or_buy'):
                    if request.form.get('mine_or_buy') == 'mine':
                        build_or_buy = 1
                    elif request.form.get('mine_or_buy') == 'buy':
                        build_or_buy = 0

                    pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id'],group_id=18, status=2).all()
                    for item in pipeline:
                        item.build_or_buy = build_or_buy
                        if build_or_buy == 1:
                            item.material_cost = 0.0
                        else:
                            item.material_cost = get_marketValue(item.material_id, 'sell') * item.material_qty

                        db.session.add(item)
                        db.session.commit()

                        comp_blueprint_id = item.blueprint_id
                        newcost_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],blueprint_id=comp_blueprint_id).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').all()
                        materialCost = build_pipeline_rollup_cost(newcost_pipeline)
                        for item1 in newcost_pipeline:
                            comp = db.session.query(build_pipeline).filter_by(id=item1.id).one()
                            comp.build_cost = materialCost / comp.runs
                            db.session.add(comp)
                            db.session.commit()

            inv_pipeline = db.session.query(invent_pipeline).filter_by(user_id = session['myUser_id'],status=3).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','datacore_id','datacore_qty','datacore_cost','datacore','status').order_by('datacore').all()

            planetary_pipeline = db.session.query(build_pipeline).filter(build_pipeline.status==2).filter(build_pipeline.user_id == session['myUser_id'], (or_(build_pipeline.group_id==1034, build_pipeline.group_id==1040))).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').order_by('material').all()

            component_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=334, status=2).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').order_by('material').all()

            comp_blueprint_id = 0
            for component in component_pipeline:
                if component.build_or_buy == 1 and component.material_cost > 0:
                    comp = db.session.query(build_pipeline).filter_by(id=component.id).one()
                    comp.material_cost = 0.0
                    db.session.add(comp)
                    db.session.commit()

                    myBuildComponents = db.session.query(v_build_components).filter_by(id = component.material_id).with_entities('id','material','material_id','quantity').all()
                    comp_blueprint_id = component.blueprint_id

                    for requirements in myBuildComponents:
                        myCost = get_marketValue(requirements.material_id, 'sell') * requirements.quantity * component.material_qty

                        pipeline = build_pipeline(session['myUser_id'],  component.product_id, component.blueprint_id, component.runs, requirements.material_id, requirements.quantity * component.material_qty, myCost, component.product_name, requirements.material, 429, 0, component.jita_sell_price, component.local_sell_price, component.build_cost, component.material_id, component.status)

                        db.session.add(pipeline)
                        db.session.commit()

                    newcost_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],blueprint_id=comp_blueprint_id).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').all()
                    materialCost = build_pipeline_rollup_cost(newcost_pipeline)
                    for item in newcost_pipeline:
                        comp = db.session.query(build_pipeline).filter_by(id=item.id).one()
                        comp.build_cost = materialCost / comp.runs
                        db.session.add(comp)
                        db.session.commit()

                elif component.build_or_buy == 0 and component.material_cost == 0:
                    comp = db.session.query(build_pipeline).filter_by(id=component.id).one()
                    comp.material_cost = get_marketValue(component.material_id, 'sell') * component.material_qty
                    db.session.add(comp)
                    db.session.commit()
                    mat_id = comp.material_id
                    comp_blueprint_id = component.blueprint_id

                    mats = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'], group_id=429, material_comp_id=mat_id,status=2).all()
                    for mat in mats:
                        db.session.delete(mat)
                        db.session.commit()

                    newcost_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],blueprint_id=comp_blueprint_id).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').all()
                    materialCost = build_pipeline_rollup_cost(newcost_pipeline)
                    for item in newcost_pipeline:
                        comp = db.session.query(build_pipeline).filter_by(id=item.id).one()
                        comp.build_cost = materialCost / comp.runs
                        db.session.add(comp)
                        db.session.commit()

            component_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=334,status=2).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').order_by('material').all()

            material_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=429,status=2).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').order_by('material').all()

            tech1_pipeline = db.session.query(build_pipeline).filter(build_pipeline.status==2).filter(build_pipeline.user_id == session['myUser_id']).filter(build_pipeline.group_id <> 334).filter(build_pipeline.group_id <> 18).filter(build_pipeline.group_id <> 1034).filter(build_pipeline.group_id <> 332).filter(build_pipeline.group_id <> 1040).filter(build_pipeline.group_id <> 429).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').order_by('material').all()

            for component1 in tech1_pipeline:
                if component1.build_or_buy == 1 and component1.material_cost > 0:
                    comp = db.session.query(build_pipeline).filter_by(id=component1.id).one()
                    comp.material_cost = 0.0
                    db.session.add(comp)
                    db.session.commit()

                    myBuildComponents = db.session.query(v_build_components).filter_by(id = component1.material_id).with_entities('id','material','material_id','quantity').all()
                    comp_blueprint_id = component1.blueprint_id

                    for requirements in myBuildComponents:
                        myCost = get_marketValue(requirements.material_id, 'sell') * requirements.quantity * component1.material_qty

                        pipeline = build_pipeline(session['myUser_id'],  component1.product_id, component1.blueprint_id, component1.runs, requirements.material_id, requirements.quantity * component1.material_qty, myCost, component1.product_name, requirements.material, 18, 0, component1.jita_sell_price, component1.local_sell_price, component1.build_cost, component1.product_id, component1.status)

                        db.session.add(pipeline)
                        db.session.commit()

                    newcost_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],blueprint_id=comp_blueprint_id).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').all()
                    materialCost = build_pipeline_rollup_cost(newcost_pipeline)
                    for item in newcost_pipeline:
                        comp = db.session.query(build_pipeline).filter_by(id=item.id).one()
                        comp.build_cost = materialCost / comp.runs
                        db.session.add(comp)
                        db.session.commit()

                elif component1.build_or_buy == 0 and component1.material_cost == 0:
                    comp = db.session.query(build_pipeline).filter_by(id=component1.id).one()
                    comp.material_cost = get_marketValue(component1.material_id, 'sell') * component1.material_qty
                    db.session.add(comp)
                    db.session.commit()
                    mat_id = comp.product_id
                    comp_blueprint_id = component1.blueprint_id

                    mats = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'], group_id=18, material_comp_id=mat_id, status=2).all()
                    for mat in mats:
                        db.session.delete(mat)
                        db.session.commit()

                    newcost_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],blueprint_id=comp_blueprint_id).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').all()
                    materialCost = build_pipeline_rollup_cost(newcost_pipeline)
                    for item in newcost_pipeline:
                        comp = db.session.query(build_pipeline).filter_by(id=item.id).one()
                        comp.build_cost = materialCost / comp.runs
                        db.session.add(comp)
                        db.session.commit()

            tech1_pipeline = db.session.query(build_pipeline).filter(build_pipeline.status==2).filter(build_pipeline.user_id == session['myUser_id']).filter(build_pipeline.group_id <> 334).filter(build_pipeline.group_id <> 18).filter(build_pipeline.group_id <> 1034).filter(build_pipeline.group_id <> 332).filter(build_pipeline.group_id <> 1040).filter(build_pipeline.group_id <> 429).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').order_by('material').all()

            ram_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=332,status=2).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').order_by('material').all()

            for component2 in ram_pipeline:
                if component2.build_or_buy == 1 and component2.material_cost > 0:
                    comp = db.session.query(build_pipeline).filter_by(id=component2.id).one()
                    comp.material_cost = 0.0
                    db.session.add(comp)
                    db.session.commit()

                    myBuildComponents = db.session.query(v_build_components).filter_by(id = component2.material_id).with_entities('id','material','material_id','quantity').all()

                    for requirements in myBuildComponents:
                        myCost = get_marketValue(requirements.material_id, 'sell') * requirements.quantity * component2.material_qty

                        pipeline = build_pipeline(session['myUser_id'],  component2.product_id, component2.blueprint_id, component2.runs, requirements.material_id, requirements.quantity * component2.material_qty, myCost, component2.product_name, requirements.material, 18, 0, component2.jita_sell_price, component2.local_sell_price, component2.build_cost, component2.product_id,component2.status)

                        db.session.add(pipeline)
                        db.session.commit()

                elif component2.build_or_buy == 0 and component2.material_cost == 0:
                    comp = db.session.query(build_pipeline).filter_by(id=component2.id).one()
                    comp.material_cost = get_marketValue(component2.material_id, 'sell') * component2.material_qty
                    db.session.add(comp)
                    db.session.commit()
                    mat_id = comp.product_id

                    mats = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'], group_id=18, material_comp_id=mat_id,status=2).all()
                    for mat in mats:
                        db.session.delete(mat)
                        db.session.commit()

            ram_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=332, status=2).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').order_by('material').all()

            mineral_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=18, status=2).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').order_by('material_id').all()

            calcs = db.session.query(mining_calc).filter_by(user_id=session['myUser_id']).all()
            if request.form.get('add_mining'):
                trit_required = 0
                pye_required = 0
                mex_required = 0
                iso_required = 0
                nox_required = 0
                zyd_required = 0
                meg_required = 0
                morph_required = 0
                upd_or_add = 0;
                for mins in mineral_pipeline:
                    if mins.material_id == 34:
                        trit_required += mins.material_qty * mins.runs
                    elif mins.material_id == 35:
                        pye_required += mins.material_qty * mins.runs
                    elif mins.material_id == 36:
                        mex_required += mins.material_qty * mins.runs
                    elif mins.material_id == 37:
                        iso_required += mins.material_qty * mins.runs
                    elif mins.material_id == 38:
                        nox_required += mins.material_qty * mins.runs
                    elif mins.material_id == 39:
                        zyd_required += mins.material_qty * mins.runs
                    elif mins.material_id == 40:
                        meg_required += mins.material_qty * mins.runs
                    elif mins.material_id == 11399:
                        morph_required += mins.material_qty * mins.runs

                for calc in calcs:
                    upd_or_add = 1
                    calc.trit_required = trit_required
                    calc.pye_required = pye_required
                    calc.mex_required = mex_required
                    calc.iso_required = iso_required
                    calc.nox_required = nox_required
                    calc.zyd_required = zyd_required
                    calc.meg_required = meg_required
                    calc.morph_required = morph_required
                    db.session.add(calc)
                    db.session.commit()
                    flash('Successfully updated mining calculations.','success')
                    return redirect(url_for('mining'))

                if upd_or_add == 0:
                    calc = mining_calc(session['myUser_id'],  300, 120, 30, trit_required, pye_required, mex_required, iso_required, nox_required, zyd_required, meg_required, morph_required, 0, 0, 0, 0)
                    db.session.add(calc)
                    db.session.commit()
                    flash('Successfully sent mineral requirements to mining calculator.','success')

            calcs = db.session.query(mining_calc).filter_by(user_id=session['myUser_id']).all()
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

            return render_template('shopping_list.html', form=form, datacoresInPipeline=datacoresInPipeline, planetaryInPipeline=planetaryInPipeline, componentInPipeline=componentInPipeline, materialInPipeline=materialInPipeline, tech1InPipeline=tech1InPipeline, ramInPipeline=ramInPipeline, mineralInPipeline=mineralInPipeline, bom_total=bom_total, dc_total=dc_total, planet_total=planet_total, component_total=component_total, material_total=material_total, tech1_total=tech1_total, ram_total=ram_total, mineral_total=mineral_total,calcs=calcs)

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
            pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id'],status=2).with_entities('id','user_id','product_id','blueprint_id','runs','material_id','material_qty','material_cost','product_name','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').order_by('material').all()

            pipeline_products = db.session.query(v_build_pipeline_products).filter_by(user_id = session['myUser_id'],status=2).with_entities('product_name', 'user_id', 'blueprint_id', 'product_id', 'runs', 'jita_sell_price','local_sell_price','build_cost','status')

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
    #try:
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
        pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id'],status=2).with_entities('id','user_id','product_id','blueprint_id','runs','material_id','material_qty','material_cost','product_name','material', 'group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','status').order_by('material').all()

        pipeline_products = db.session.query(v_build_pipeline_products).filter_by(user_id = session['myUser_id'],status=2).with_entities('product_name', 'user_id', 'blueprint_id', 'product_id','runs','jita_sell_price','local_sell_price','build_cost','status')

        materialInPipeline = build_pipeline_rollup_qty(pipeline)
        materialCost = build_pipeline_rollup_cost(pipeline)

        return render_template('build.html', form=form, blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, sell_median=querySell, time=myTime, buildRequirements = myBuildRequirements, buildCost = myBuildCost, materialCost = myMaterialCost, pipeline=pipeline, materialInPipeline=materialInPipeline, pipelineCost=materialCost, pipeline_products=pipeline_products, runs=runs)

    else:
        return render_template('build.html', form=form, blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, sell_median=querySell, time=myTime, buildRequirements = myBuildRequirements, buildCost = myBuildCost, materialCost = myMaterialCost, runs=runs)

    #except Exception as e:
    #    flash('Problem querying blueprint. See log', 'danger')
    #    app.logger.info(str(e))
    #    return redirect(url_for('build'))

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

                pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id'],status=2).with_entities('id','user_id','product_id','blueprint_id','runs','material_id','material_qty','material_cost','product_name','material', 'group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','jita_sell_price','local_sell_price','build_cost','material_comp_id','status').order_by('material').all()

                pipeline_products = db.session.query(v_build_pipeline_products).filter_by(user_id = session['myUser_id'],status=2).with_entities('product_name', 'user_id', 'blueprint_id', 'product_id','runs','jita_sell_price','local_sell_price','build_cost','status')

                materialInPipeline = build_pipeline_rollup_qty(pipeline)
                materialCost = build_pipeline_rollup_cost(pipeline)

                if request.form.get('job_runs') <> '':
                    for requirements in myBuildRequirements:
                        myCost = get_marketValue(requirements.material_id, 'sell') * requirements.qty

                        pipeline = build_pipeline(session['myUser_id'],  myProduct.typeID, id, request.form.get('job_runs'), requirements.material_id, requirements.qty, myCost, myProduct.typeName, requirements.material, requirements.group_id, 0, querySell, 0, myBuildCost, 0, 2)

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
            pipeline = db.session.query(invent_pipeline).filter_by(user_id = session['myUser_id'],status=3).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','datacore_id','datacore_qty','datacore_cost','datacore','status').order_by('datacore').all()

            pipeline_products = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id'],status=3).with_entities('product_name', 'user_id', 'runs','status')

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

            pipeline = db.session.query(invent_pipeline).filter_by(user_id = session['myUser_id'],status=3).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','datacore_id','datacore_qty','datacore_cost','datacore','status').order_by('datacore').all()

            pipeline_products = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id'],status=3).with_entities('product_name', 'user_id', 'runs','status')

            materialInPipeline = invent_pipeline_rollup_qty(pipeline)
            materialCost = invent_pipeline_rollup_cost(pipeline)

            return render_template('invent.html', form=form, blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, probability=myProbPercent, sell_median=mySellMedian, time=myTime, datacoreRequirements = myDatacoreRequirements, datacoresCost=myDatacoresCost, baseProduct = myBaseProduct.material, pipeline=pipeline, materialInPipeline=materialInPipeline, materialCost=materialCost, pipeline_products=pipeline_products, runs=runs)

        else:
            return render_template('invent.html', form=form, blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, probability=myProbPercent, sell_median=mySellMedian, time=myTime, datacoreRequirements=myDatacoreRequirements, datacoresCost = myDatacoresCost, baseProduct = myBaseProduct.material, runs=runs)

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

                pipeline = db.session.query(invent_pipeline).filter_by(user_id = session['myUser_id'],status=3).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','datacore_id','datacore_qty','datacore_cost','datacore','status').order_by('datacore').all()

                pipeline_products = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id'],status=3).with_entities('product_name', 'user_id', 'runs','status')

                materialInPipeline = invent_pipeline_rollup_qty(pipeline)
                materialCost = invent_pipeline_rollup_cost(pipeline)

                if request.form.get('job_runs') <> '':
                    for requirements in myDatacoreRequirements:
                        myCost = get_marketValue(requirements.dc_id, 'sell') * requirements.quantity

                        pipeline = invent_pipeline(session['myUser_id'],  myProduct.typeID, id, request.form.get('job_runs'), selected_bp.t2_blueprint, requirements.dc_id, requirements.quantity, myCost, requirements.datacore, 3)

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
                return render_template('login.html', form=form)
        except Exception as e:
            app.logger.info(str(e))
            flash('Problem logging in. See log', 'danger')
            return render_template('login.html', form=form)
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

def fitting_rollup_cost(myFittings):
    buildCost = 0.0
    for item in myFittings:
        if item.component_qty > 0:
            buildCost += float(item.component_cost) * float(item.qty) * float(item.component_qty)

    buildCost += float(myFittings[0].jita_buy) * float(myFittings[0].qty)
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

def refine_asteroid(min_id, calcs, asteroid_stats):
    asteroid_mins = db.session.query(v_build_components).filter_by(id=min_id).with_entities('id','material','material_id','quantity').all()
    yield1 = calcs[0].m3_per_cycle * calcs[0].num_cycles
    qty = yield1 / asteroid_stats.vol
    #print ' m3 yield = ' +str(yield1) + ' , refinery % = ' + str(calcs[0].refinery)

    mined_mins = MinedMinerals(0,0,0,0,0,0,0,0)
    for mins in asteroid_mins:
        mined = (mins.quantity * qty * calcs[0].refinery) / asteroid_stats.portion
        remain = yield1 % asteroid_stats.portion
        #print 'from ' + str(qty) + ', we refine - ' + str(mins.material) + ', qty = ' + str(mined) + ' , with remainder = ' + str(remain)
        if mins.material_id == 34:
            mined_mins.trit = mined
        elif mins.material_id == 35:
            mined_mins.pye = mined
        elif mins.material_id == 36:
            mined_mins.mex = mined
        elif mins.material_id == 37:
            mined_mins.iso = mined
        elif mins.material_id == 38:
            mined_mins.nox = mined
        elif mins.material_id == 39:
            mined_mins.zyd = mined
        elif mins.material_id == 40:
            mined_mins.meg = mined
        elif mins.material_id == 11399:
            mined_mins.morph = mined
    return mined_mins

if __name__ == "__main__":
   app.run()
