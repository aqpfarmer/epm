from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for, flash, session, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from base64 import b64encode
import requests
import json
from sqlalchemy import or_, desc
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://chris:funkytown@192.168.1.106/evesde1'
app.debug = True # disable this in production!
app.config['SECRET_KEY'] = 'super-secret-foolish-fool112'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['POOL_SIZE'] = 100
app.config['MAX_OVERFLOW'] = 0
app.config['ISOLATION_LEVEL'] = 'READ UNCOMMITTED'
app.config['POOL_RECYCLE'] = 3600

db = SQLAlchemy(app)

class users(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    character_id = db.Column(db.String(100))
    character_name = db.Column(db.String(100))
    refresh_token = db.Column(db.String(255))
    expiration = db.Column(db.DateTime())
    auth_code = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    last_logged_in = db.Column(db.DateTime())
    home_station_id = db.Column(db.String(100))
    structure_role_bonus = db.Column(db.Numeric())
    default_bp_me = db.Column(db.Numeric())
    corp_id = db.Column(db.String(100))

    def __init__(self, character_id, character_name, refresh_token, expiration, auth_code, active, last_logged_in, home_station_id, structure_role_bonus, default_bp_me, corp_id):
        self.character_id = character_id
        self.character_name = character_name
        self.refresh_token = refresh_token
        self.expiration = expiration
        self.auth_code = auth_code
        self.active = active
        self.last_logged_in = last_logged_in
        self.home_station_id = home_station_id
        self.structure_role_bonus = structure_role_bonus
        self.default_bp_me = default_bp_me
        self.corp_id = corp_id

class eve_sso(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    client_id = db.Column(db.String(100))
    secret_key = db.Column(db.String(100))
    scope = db.Column(db.String(100))

    def __init__(self, client_id, secret_key, scope):
        self.client_id = client_id
        self.secret_key = secret_key
        self.scope = scope

class job_journal(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    job_id = db.Column(db.String(100))
    user_id = db.Column(db.String(100))
    product_id = db.Column(db.Integer())
    activity_id = db.Column(db.Integer())
    facility_id = db.Column(db.String(100))
    station_id = db.Column(db.String(100))
    licensed_runs = db.Column(db.Integer())
    runs = db.Column(db.Integer())
    blueprint_location_id = db.Column(db.String(100))
    output_location_id = db.Column(db.String(100))
    start_date = db.Column(db.DateTime())
    end_date = db.Column(db.DateTime())
    status = db.Column(db.String(50))
    job_cost = db.Column(db.Numeric())

    def __init__(self, job_id, user_id, product_id, activity_id, facility_id, station_id, licensed_runs, runs, blueprint_location_id, output_location_id, start_date, end_date, status, job_cost):
        self.job_id = job_id
        self.user_id = user_id
        self.product_id = product_id
        self.activity_id = activity_id
        self.facility_id = facility_id
        self.station_id = station_id
        self.licensed_runs = licensed_runs
        self.runs = runs
        self.blueprint_location_id = blueprint_location_id
        self.output_location_id = output_location_id
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.job_cost = job_cost

class wallet_journal(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String(100))
    amount = db.Column(db.Numeric())
    date_transaction = db.Column(db.DateTime())
    transaction_id = db.Column(db.String(100))
    ref_type = db.Column(db.String(100))

    def __init__(self, user_id, amount, date_transaction, transaction_id, ref_type):
        self.user_id = user_id
        self.amount = amount
        self.date_transaction = date_transaction
        self.transaction_id = transaction_id
        self.ref_type = ref_type

class wallet_transactions(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String(100))
    amount = db.Column(db.Numeric())
    date_transaction = db.Column(db.DateTime())
    transaction_id = db.Column(db.String(100))
    client_id = db.Column(db.String(100))
    location_id = db.Column(db.String(100))
    qty = db.Column(db.Integer())
    product_id = db.Column(db.Integer())

    def __init__(self, user_id, amount, date_transaction, transaction_id, client_id, location_id, qty, product_id):
        self.user_id = user_id
        self.amount = amount
        self.date_transaction = date_transaction
        self.transaction_id = transaction_id
        self.client_id = client_id
        self.location_id = location_id
        self.qty = qty
        self.product_id = product_id

class assets_onhand(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String(100))
    product_id = db.Column(db.Integer())
    item_id = db.Column(db.String(100))
    location_flag = db.Column(db.String(100))
    location_type = db.Column(db.String(100))
    location_id = db.Column(db.String(100))
    qty = db.Column(db.Integer())
    is_singleton = db.Column(db.Boolean())

    def __init__(self, user_id, product_id, item_id, location_flag, location_type, location_id, qty, is_singleton):
        self.user_id = user_id
        self.product_id = product_id
        self.item_id = item_id
        self.location_flag = location_flag
        self.location_type = location_type
        self.location_id = location_id
        self.qty = qty
        self.is_singleton = is_singleton

class invTypes(db.Model):
    __tablename__ = 'invTypes'
    typeID = db.Column(db.Integer(), primary_key=True)
    groupID = db.Column(db.Integer())
    typeName = db.Column(db.String(100))
    description = db.Column(db.Text())
    mass = db.Column(db.Numeric())
    volume = db.Column(db.Numeric())
    capacity = db.Column(db.Numeric())
    marketGroupID = db.Column(db.Integer())
    portionSize = db.Column(db.Integer())

    def __init__(self, groupID, typeName, description, mass, volume, capacity, marketGroupID, portionSize):
        self.groupID = marketGroupID
        self.typeName = str(typeName)
        self.description = str(description)
        self.mass = mass
        self.volume = volume
        self.capacity = capacity
        self.marketGroupID = marketGroupID
        self.portionSize = portionSize

class invVolumes(db.Model):
    typeID = db.Column(db.Integer(), primary_key=True)
    volume = db.Column(db.Integer())

    def __init__(self, volume):
        self.volume = volume

class ship_fittings(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    build_id = db.Column(db.Integer())
    user_id = db.Column(db.Integer())
    ship_id = db.Column(db.Integer())
    ship_name = db.Column(db.String(100))
    fitting_name = db.Column(db.String(100))
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

    def __init__(self, build_id, user_id, ship_id, ship_name, fitting_name, qty, num_rigslots, num_lowslots, num_medslots, num_highslots, component_id, component_qty, component_cost, component, component_slot, contract_sell_price, build_cost, jita_buy, rollup):
        self.build_id = build_id
        self.user_id = user_id
        self.ship_id = ship_id
        self.ship_name = ship_name
        self.fitting_name = fitting_name
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
    material_vol = db.Column(db.Numeric())
    portion_size = db.Column(db.Integer())

    def __init__(self, user_id, product_id, blueprint_id, runs, material_id, material_qty, material_cost, product_name, material, group_id, build_or_buy, jita_sell_price, local_sell_price, build_cost, material_comp_id, status, material_vol, portion_size):
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
        self.material_vol = material_vol
        self.portion_size = portion_size

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
    datacore_vol = db.Column(db.Numeric())
    status = db.Column(db.Integer())

    def __init__(self, user_id, product_id, blueprint_id, runs, product_name, datacore_id, datacore_qty, datacore_cost, datacore, datacore_vol, status):
        self.user_id = user_id
        self.product_id = product_id
        self.blueprint_id = blueprint_id
        self.runs = runs
        self.product_name = product_name
        self.datacore_id = datacore_id
        self.datacore_qty = datacore_qty
        self.datacore_cost = datacore_cost
        self.datacore = datacore
        self.datacore_vol = datacore_vol
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
    fitting_name = db.Column(db.String())
    user_id = db.Column(db.Integer())
    contract_sell_price = db.Column(db.Numeric())
    qty = db.Column(db.Integer())
    rollup = db.Column(db.Integer())
    jita_buy = db.Column(db.Numeric())

    def __init__(ship_id, ship_name, fitting_name, user_id, contract_sell_price, qty, rollup, jita_buy):
        self.ship_id = ship_id
        self.ship_name = ship_name
        self.fitting_name = fitting_name
        self.user_id = user_id
        self.contract_sell_price = contract_sell_price
        self.qty = qty
        self.rollup = rollup
        self.jita_buy = jita_buy

class v_buildable_fittings(db.Model):
    build_id = db.Column(db.Integer(), primary_key=True)
    ship_id = db.Column(db.Integer())
    ship_name = db.Column(db.String())
    fitting_name = db.Column(db.String())
    jita_buy = db.Column(db.Numeric())
    qty = db.Column(db.Integer())
    id = db.Column(db.Integer())
    component = db.Column(db.String())
    component_cost = db.Column(db.Numeric())
    component_qty = db.Column(db.Integer())
    build_cost = db.Column(db.Numeric())
    meta = db.Column(db.Integer())
    rollup = db.Column(db.Integer())
    user_id = db.Column(db.Integer())
    bp_id = db.Column(db.Integer())

    def __init__(ship_id, ship_name, fitting_name, jita_buy, qty, component_id, component, component_cost, component_qty, build_cost, meta, rollup, user_id, bp_id):
        self.ship_id = ship_id
        self.ship_name = ship_name
        self.fitting_name = fitting_name
        self.jita_buy = jita_buy
        self.qty = qty
        self.id = component_id
        self.component = component
        self.component_cost = component_cost
        self.component_qty = component_qty
        self.build_cost = build_cost
        self.meta = meta
        self.rollup = rollup
        self.user_id = user_id
        self.bp_id = bp_id

class v_buildable_fittings_all(db.Model):
    build_id = db.Column(db.Integer(), primary_key=True)
    ship_id = db.Column(db.Integer())
    ship_name = db.Column(db.String())
    fitting_name = db.Column(db.String())
    jita_buy = db.Column(db.Numeric())
    qty = db.Column(db.Integer())
    id = db.Column(db.Integer())
    component = db.Column(db.String())
    component_cost = db.Column(db.Numeric())
    component_qty = db.Column(db.Integer())
    build_cost = db.Column(db.Numeric())
    meta = db.Column(db.Integer())
    rollup = db.Column(db.Integer())
    user_id = db.Column(db.Integer())
    bp_id = db.Column(db.Integer())

    def __init__(ship_id, ship_name, fitting_name, jita_buy, qty, component_id, component, component_cost, component_qty, build_cost, meta, rollup, user_id, bp_id):
        self.ship_id = ship_id
        self.ship_name = ship_name
        self.fitting_name = fitting_name
        self.jita_buy = jita_buy
        self.qty = qty
        self.id = component_id
        self.component = component
        self.component_cost = component_cost
        self.component_qty = component_qty
        self.build_cost = build_cost
        self.meta = meta
        self.rollup = rollup
        self.user_id = user_id
        self.bp_id = bp_id

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
    group_id = db.Column(db.Integer())

    def __init__(material, material_id, quantity, group_id):
        self.material = str(material)
        self.material_id = material_id
        self.quantity = quantity
        self.group_id = group_id

class v_build_requirements(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    material = db.Column(db.String(100))
    material_id= db.Column(db.Integer())
    group_id = db.Column(db.Integer())
    qty = db.Column(db.Integer())
    product_id = db.Column(db.Integer())
    vol = db.Column(db.Numeric())
    portion_size = db.Column(db.Integer())

    def __init__(material, material_id, group_id, qty, product_id, vol, portion_size):
        self.material = str(material)
        self.material_id = material_id
        self.group_id = group_id
        self.qty = quantity
        self.product_id = product_id
        self.vol = vol
        self.portion_size = portion_size

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
    portion_size = db.Column(db.Integer())

    def __init__(product_name, user_id, blueprint_id, product_id, runs, jita_sell_price, local_sell_price, build_cost, status, portion_size):
        self.product_name = str(product_name)
        self.user_id = user_id
        self.blueprint_id = blueprint_id
        self.product_id = product_id
        self.runs = runs
        self.jita_sell_price = jita_sell_price
        self.local_sell_price = local_sell_price
        self.build_cost = build_cost
        self.status = status
        self.portion_size = portion_size

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
    vol = db.Column(db.Numeric())

    def __init__(datacore, quantity, dc_id, vol):
        self.datacore = str(datacore)
        self.quantity = quantity
        self.dc_id = dc_id
        self.vol = vol

class v_invention_product(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    t2_blueprint = db.Column(db.String(100))
    t2_id = db.Column(db.Integer())

    def __init__(t2_blueprint, t2_id):
        self.t2_blueprint = str(t2_blueprint)
        self.t2_id = t2_id

class v_my_invention_product(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    t2_blueprint = db.Column(db.String(100))
    t2_id = db.Column(db.Integer())
    location_id = db.Column(db.String(100))
    qty = db.Column(db.Integer())

    def __init__(user_id, t2_blueprint, t2_id, location_id, qty):
        self.user_id - user_id
        self.t2_blueprint = str(t2_blueprint)
        self.t2_id = t2_id
        self.location_id = location_id
        self.qty = qty

class v_my_build_product(db.Model):
    id = db.Column(db.Integer())
    user_id = db.Column(db.Integer())
    t2_blueprint = db.Column(db.String(100))
    t2_id = db.Column(db.Integer(), primary_key=True)
    location_id = db.Column(db.String(100))
    qty = db.Column(db.Integer())

    def __init__(id, user_id, t2_blueprint, t2_id, location_id, qty):
        self.user_id - user_id
        self.t2_blueprint = t2_blueprint
        self.t2_id = t2_id
        self.location_id = location_id
        self.qty = qty

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

class v_sales(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    type_id = db.Column(db.Integer())
    product_name = db.Column(db.String())
    qty = db.Column(db.Integer())
    amount = db.Column(db.Numeric())
    date_transaction = db.Column(db.DateTime())

    def __init__(user_id, type_id, product_name, qty, amount, date_transaction):
        self.group = group

class v_purchases(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    type_id = db.Column(db.Integer())
    product_name = db.Column(db.String())
    qty = db.Column(db.Integer())
    amount = db.Column(db.Numeric())
    date_transaction = db.Column(db.DateTime())

    def __init__(user_id, type_id, product_name, qty, amount, date_transaction):
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
    def __init__(self, datacore_id, datacore, datacore_qty, datacore_cost, runs, datacore_vol):
        self.datacore_id = datacore_id
        self.datacore = datacore
        self.datacore_qty = datacore_qty
        self.datacore_cost = datacore_cost
        self.runs = runs
        self.datacore_vol = datacore_vol

class BomShipFittings():
    def __init__(self, id, component, component_qty, component_cost, qty, bp_id):
        self.id = id
        self.component = component
        self.component_qty = component_qty
        self.component_cost = component_cost
        self.qty = qty
        self.bp_id = bp_id

class BomMaterial():
    def __init__(self, material_id, material, material_qty, material_cost, runs, id, build_or_buy, blueprint_id, material_vol, portion_size):
        self.material_id = material_id
        self.material = material
        self.material_qty = material_qty
        self.material_cost = material_cost
        self.runs = runs
        self.id = id
        self.build_or_buy = build_or_buy
        self.blueprint_id = blueprint_id
        self.material_vol = material_vol
        self.portion_size = portion_size

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
    def __init__(self, id, component, component_qty, component_cost, qty):
        self.id = id
        self.component = component
        self.component_qty = component_qty
        self.component_cost = component_cost
        self.qty = qty

class FittingShips():
    def __init__(self, ship_id, ship_name, qty, jita_buy, bp_id):
        self.ship_id = ship_id
        self.ship_name = ship_name
        self.qty = qty
        self.jita_buy = jita_buy
        self.bp_id = bp_id

class FittingList():
    def __init__(self, build_id, name):
        self.build_id = build_id
        self.name = name

class Jobs():
    def __init__(self, product_id, product_name, job_type, status, runs, start_date, finish_date, job_cost, remainder):
        self.product_id = product_id
        self.product_name = product_name
        self.job_type = job_type
        self.status = status
        self.runs = runs
        self.start_date = start_date
        self.finish_date =  finish_date
        self.job_cost = job_cost
        self.remainder = remainder

@app.route("/")
def index():
    if 'myUser_id' in session:
        session['wallet_balance'] = get_wallet_balance()

    return render_template('home.html')

@app.route("/purchases", methods=['GET','POST'])
def purchases():
    if 'myUser_id' in session:

        grand_total = 0.0

        if request.args.get('range_start'):
            current_range_start = datetime.strptime(request.args.get('range_start'),'%Y-%m-%d')
            current_range_end = datetime.strptime(request.args.get('range_end'),'%Y-%m-%d')

        if request.form.get('action')=='prev':
            myDate = datetime.strptime(request.form.get('range_start'),'%Y-%m-%d')
            range_start = str(myDate.year) + '-' + str(myDate.month-1) + '-1'
            range_end = datetime.strftime(myDate - relativedelta(days=1),'%Y-%-m-%-d')
        elif request.form.get('action')=='next':
            myDate = datetime.strptime(request.form.get('range_end'),'%Y-%m-%d')
            range_start = str(myDate.year) + '-' + str(myDate.month+1) + '-1'
            range_end = datetime.strftime(myDate + relativedelta(months=1),'%Y-%-m-%-d')
        else:
            range_start = str(current_range_start).split(" ")[0]
            range_end = str(current_range_end).split(" ")[0]

        myPurchases = db.session.query(v_purchases).filter(v_purchases.user_id==session['myUser_id']).filter(v_purchases.date_transaction >= range_start).filter(v_purchases.date_transaction <= range_end).all()
        for item in myPurchases:
            grand_total += float(item.qty) * float(item.amount)


        return render_template('sales.html', mySales=myPurchases, grand_total=grand_total, range_start=range_start, range_end=range_end, report_type='Purchases')

    else:
        flash('You must be logged in to see purchase transactions', 'danger')
        return redirect(url_for('index'))

@app.route("/sales", methods=['GET','POST'])
def sales():
    if 'myUser_id' in session:

        grand_total = 0.0

        if request.args.get('range_start'):
            current_range_start = datetime.strptime(request.args.get('range_start'),'%Y-%m-%d')
            current_range_end = datetime.strptime(request.args.get('range_end'),'%Y-%m-%d')

        if request.form.get('action')=='prev':
            myDate = datetime.strptime(request.form.get('range_start'),'%Y-%m-%d')
            range_start = str(myDate.year) + '-' + str(myDate.month-1) + '-1'
            range_end = datetime.strftime(myDate - relativedelta(days=1),'%Y-%-m-%-d')
        elif request.form.get('action')=='next':
            myDate = datetime.strptime(request.form.get('range_end'),'%Y-%m-%d')
            range_start = str(myDate.year) + '-' + str(myDate.month+1) + '-1'
            range_end = datetime.strftime(myDate + relativedelta(months=1),'%Y-%-m-%-d')
        else:
            range_start = str(current_range_start).split(" ")[0]
            range_end = str(current_range_end).split(" ")[0]

        mySales = db.session.query(v_sales).filter(v_sales.user_id==session['myUser_id']).filter(v_sales.date_transaction >= range_start).filter(v_sales.date_transaction <= range_end).all()
        for item in mySales:
            grand_total += float(item.qty) * float(item.amount)


        return render_template('sales.html', mySales=mySales, grand_total=grand_total, range_start=range_start, range_end=range_end, report_type='Sales')

    else:
        flash('You must be logged in to see sales transactions', 'danger')
        return redirect(url_for('index'))

@app.route("/options", methods=['GET','POST'])
def options():
    if 'myUser_id' in session:
        home_station_id = request.form.get('home_station_id')
        structure_role_bonus = request.form.get('structure_role_bonus')
        default_bp_me = request.form.get('default_bp_me')

        myUser = db.session.query(users).filter_by(character_id=session['myUser_id']).one()
        myUser.home_station_id = home_station_id
        myUser.structure_role_bonus = structure_role_bonus
        myUser.default_bp_me = default_bp_me
        db.session.add(myUser)
        db.session.commit()

        session['home_station_id'] = home_station_id
        session['structure_role_bonus'] = structure_role_bonus
        session['default_bp_me'] = default_bp_me
        flash('Successfully updated global options', 'success')
    else:
        flash('You must be logged in to update options', 'danger')

    return redirect(url_for('index'))

@app.route("/fetch_assets")
def fetch_assets():
    if 'myUser_id' in session:
        existing = db.session.query(assets_onhand).filter_by(user_id=session['myUser_id']).delete()
        db.session.commit()

        myAssets = get_assets_onhand()
        for item in myAssets:
            #print item['type_id']
            if item =='error' or item=='timeout':
                flash ('Problem fetching assets from EVE.', 'danger')
                break
            else:
                #print item['location_flag']
                if item['location_flag'] == 'HangarAll' or item['location_flag'] == 'Hangar' or item['location_flag'] == 'Unlocked' or item['location_flag'] == 'AutoFit':
                    entry = assets_onhand(session['myUser_id'], item['type_id'], item['item_id'], item['location_flag'], item['location_type'], item['location_id'], item['quantity'], item['is_singleton'])
                    db.session.add(entry)
                    db.session.commit()

        flash('Seccessfully pulled on hand assets for '+session['name'], 'success')

    return redirect(url_for('bom'))

@app.route("/invent_jobs")
def invent_jobs():
    if 'myUser_id' in session:
        myAssets = get_job_journal()
        for item in myAssets:
            #print item
            if item =='error' or item=='timeout':
                flash ('Problem fetching job status from EVE.', 'danger')
                break
            else:
                result = import_jobs(item)
        inventJobs = []
        current_day = datetime.now().day
        current_month = datetime.now().month
        current_year = datetime.now().year
        myDay = str(current_year) + '-' + str(current_month) + '-' + str(current_day)
        now = datetime.utcnow()

        myJobs = db.session.query(job_journal).filter(job_journal.user_id==session['myUser_id']).filter(or_(job_journal.activity_id==5, job_journal.activity_id==8)).order_by(desc('end_date')).all()
        for job in myJobs:
            #print job.activity_id
            print days_between(myDay, job.end_date.strftime('%Y-%m-%d'))
            if days_between(myDay, job.end_date.strftime('%Y-%m-%d')) >=0:
                myProduct = db.session.query(invTypes).filter_by(typeID = int(job.product_id)).one()
                start_date = datetime.strftime(job.start_date, '%b %d %Y .. %H:%M')
                end_date = datetime.strftime(job.end_date, '%b %d %Y .. %H:%M')
                #remain = '{0:0>2}:{1:0>2}'.format((job.end_date - now).seconds%3600//60, (job.end_date - now).seconds%60)
                if job.activity_id==5:
                    job_type="Copying"
                elif job.activity_id==8:
                    job_type="Invention"

                jobx = Jobs(job.product_id, myProduct.typeName, job_type, job.status, job.runs, start_date, end_date, job.job_cost, str(job.end_date - now).split(".")[0])
                inventJobs += [jobx]


        myDay = datetime.strftime(now, '%b %d %Y at %H:%M')
        return render_template('invent_jobs.html', myJobs=inventJobs, myDay=myDay, action='Invention')

    else:
        flash('You must be logged in to use the Job checker.', 'danger')
        return redirect(url_for('invent'))

@app.route("/build_jobs")
def build_jobs():
    if 'myUser_id' in session:
        myAssets = get_job_journal()
        for item in myAssets:
            #print item
            if item =='error' or item=='timeout':
                flash ('Problem fetching job status from EVE.', 'danger')
                break
            else:
                result = import_jobs(item)
        buildJobs = []
        current_day = datetime.now().day
        current_month = datetime.now().month
        current_year = datetime.now().year
        myDay = str(current_year) + '-' + str(current_month) + '-' + str(current_day)
        now = datetime.utcnow()

        myJobs = db.session.query(job_journal).filter(job_journal.user_id==session['myUser_id']).filter(job_journal.activity_id==1).order_by(desc('end_date')).all()
        for job in myJobs:
            #print job.activity_id
            #print days_between(myDay, job.end_date.strftime('%Y-%m-%d'))
            if days_between(myDay, job.end_date.strftime('%Y-%m-%d')) >=0:
                myProduct = db.session.query(invTypes).filter_by(typeID = int(job.product_id)).one()
                start_date = datetime.strftime(job.start_date, '%b %d %Y .. %H:%M')
                end_date = datetime.strftime(job.end_date, '%b %d %Y .. %H:%M')
                if job.activity_id==1:
                    job_type="Manufacturing"

                jobx = Jobs(job.product_id, myProduct.typeName, job_type, job.status, job.runs, start_date, end_date, job.job_cost, str(job.end_date - now).split(".")[0])
                buildJobs += [jobx]

        myDay = datetime.strftime(now, '%b %d %Y at %H:%M')
        return render_template('invent_jobs.html', myJobs=buildJobs, myDay=myDay, action='Build')

    else:
        flash('You must be logged in to use the Job checker.', 'danger')
        return redirect(url_for('build'))

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return (d2 - d1).days

@app.route("/fetch_fittings")
def fetch_fittings():
    if 'myUser_id' in session:
        myAssets = get_fittings()
        for item in myAssets:
            #print item
            if item =='error' or item=='timeout':
                flash ('Problem fetching fitting from EVE.', 'danger')
                break
            else:
                result = import_fitting(item)

        flash('Seccessfully pulled all ship fittings for '+session['name'], 'success')

    return redirect(url_for('fittings'))

@app.route("/financial", methods=['GET','POST'])
def financial():
    if 'myUser_id' in session:
        if request.form.get('fetch'):
            journal = get_wallet_journal()
            transactions = get_wallet_transactions()

            for item in journal:
                #print item
                if item =='error' or item=='timeout':
                    flash ('Problem fetching financial data from EVE.', 'danger')
                    break
                else:
                    #print item['ref_type'] + ' - ' + str(item['amount'])
                    existing = db.session.query(wallet_journal).filter_by(user_id=session['myUser_id'], transaction_id=str(item['id'])).all()
                    if not existing:
                        entry = wallet_journal(session['myUser_id'], item['amount'], item['date'], item['id'], item['ref_type'])
                        db.session.add(entry)
                        db.session.commit()

            for item in transactions:
                #print item
                if item =='error' or item=='timeout':
                    flash ('Problem fetching financial data from EVE.', 'danger')
                    break
                else:
                    existing = db.session.query(wallet_transactions).filter_by(transaction_id=str(item['transaction_id'])).all()
                    if not existing:
                        entry = wallet_transactions(session['myUser_id'], item['unit_price'], item['date'], item['transaction_id'], item['client_id'], item['location_id'], item['quantity'], item['type_id'])
                        db.session.add(entry)
                        db.session.commit()

            return redirect(url_for('financial'))

        total_transaction_taxes = 0.0
        total_broker_fees = 0.0
        total_pi = 0.0
        total_donations_out = 0.0
        total_purchases = 0.0
        total_contract_buys = 0.0
        total_insurance_fees = 0.0
        total_donations_in = 0.0
        total_sales = 0.0
        total_bounties = 0.0
        total_contract_sales = 0.0
        total_insurance_payouts = 0.0
        total_bounty_tax = 0.0
        total_contract_broker_fees = 0.0
        range_start = ''
        range_end = ''
        total_expenses = 0.0
        total_income = 0.0
        total_industry_costs = 0.0

        current_day = datetime.now().day
        current_month = datetime.now().month
        current_year = datetime.now().year
        current_range_start = str(current_year) + '-' + str(current_month)+ '-1'
        current_range_end = str(current_year) + '-' + str(current_month) + '-' + str(current_day)
        #current_range_end = str(current_year) + '-' + str(current_month) + '-30'
        if request.form.get('action')=='prev':
            myDate = datetime.strptime(request.form.get('range_start'),'%Y-%m-%d')
            if str(myDate.month)=='1':
                range_start = str(myDate.year-1) + '-' + str(12) + '-1'
            else:
                range_start = str(myDate.year) + '-' + str(myDate.month-1) + '-1'
            range_end = datetime.strftime(myDate - relativedelta(days=1),'%Y-%-m-%-d')
        elif request.form.get('action')=='next':
            myDate = datetime.strptime(request.form.get('range_end'),'%Y-%m-%d')
            if str(myDate.month)=='12':
                range_start = str(myDate.year+1) + '-' + str(1) + '-1'
            else:
                range_start = str(myDate.year) + '-' + str(myDate.month+1) + '-1'

            range_end = datetime.strftime(myDate + relativedelta(months=1),'%Y-%-m-%-d')
        else:
            range_start = current_range_start
            range_end = current_range_end


        print range_start
        print range_end
        myQuery = db.session.query(wallet_journal).filter(wallet_journal.user_id==session['myUser_id']).filter(wallet_journal.date_transaction >= range_start).filter(wallet_journal.date_transaction <= range_end).all()
        for item in myQuery:
            #print item.ref_type + ' date: ' + str(item.date_transaction)
            if item.ref_type=='transaction_tax' or item.ref_type=='asset_safety_recovery_tax' or item.ref_type=='contract_sales_tax':
                total_transaction_taxes += float(item.amount)
            elif item.ref_type=='market_transaction':
                total_sales += float(item.amount)
            elif item.ref_type=='brokers_fee' or item.ref_type=='clone_transfer' or item.ref_type=='contract_brokers_fee':
                total_broker_fees += float(item.amount)
            elif item.ref_type=='bounty_prizes':
                total_bounties += float(item.amount)
            elif item.ref_type=='player_donation':
                if item.amount < 0 :
                    total_donations_out += float(item.amount)
                else:
                    total_donations_in += float(item.amount)
            elif item.ref_type=='contract_reward':
                total_donations_in += float(item.amount)
            elif item.ref_type=='contract_reward_deposited':
                total_donations_out += float(item.amount)
            elif item.ref_type=='market_escrow':
                total_purchases += float(item.amount)
            elif item.ref_type=='contract_price' or item.ref_type=='contract_price_payment_corp':
                if item.amount < 0 :
                    total_contract_buys += float(item.amount)
                else:
                    total_contract_sales += float(item.amount)
            elif item.ref_type=='insurance':
                if item.amount < 0 :
                    total_insurance_fees += float(item.amount)
                else:
                    total_insurance_payouts += float(item.amount)
            elif item.ref_type=='planetary_export_tax' or item.ref_type=='planetary_import_tax' or item.ref_type=='planetary_construction':
                total_pi += float(item.amount)
            elif item.ref_type=='bounty_prizes_corporate_tax':
                total_bounty_tax += float(item.amount)
            elif item.ref_type=='copying' or item.ref_type=='manufacturing' or item.ref_type=='researching_technology' or item.ref_type=='industry_job_tax' or item.ref_type=='reprocessing_tax':
                total_industry_costs += float(item.amount)

        total_income = total_donations_in + total_sales + total_bounties + total_contract_sales + total_insurance_payouts
        total_expenses = total_transaction_taxes + total_broker_fees + total_contract_broker_fees + total_pi + total_donations_out + total_purchases + total_contract_buys + total_insurance_fees + total_bounty_tax + total_industry_costs

        #print 'income: ' + str(total_income)
        #print 'expenses: ' + str(abs(total_expenses))

        return render_template('financial.html',total_transaction_taxes=total_transaction_taxes,total_broker_fees=total_broker_fees,total_pi=total_pi,total_donations_out=total_donations_out,total_purchases=total_purchases,total_contract_buys=total_contract_buys,total_insurance_fees=total_insurance_fees,total_donations_in=total_donations_in,total_sales=total_sales,total_bounties=total_bounties,total_contract_sales=total_contract_sales,total_insurance_payouts=total_insurance_payouts,total_bounty_tax=total_bounty_tax,total_contract_broker_fees=total_contract_broker_fees,range_start=range_start,range_end=range_end, total_income=total_income, total_expenses=abs(total_expenses), total_industry_costs=total_industry_costs)

    else:
        flash('You must be logged in to use the financial report.', 'danger')
        return redirect(url_for('index'))

@app.route("/fittings", methods=['GET','POST'])
def fittings():
    if 'myUser_id' in session:
        #try:
        build_id = 0
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
        nonBuildableFittings = []
        nonBuildablefittingRollup = []
        nonBuildableTotal = 0.0
        buildableFittings = []
        buildablefittingRollup = []
        buildableTotal = 0.0
        fittingCost = 0.0
        fittingPM = 0.0
        fitting_list = []
        subtract_oh_assets = 'None'

        myFittingsCount = db.session.query(v_count_fittings).filter_by(user_id=user_id).order_by('ship_name').count()
        myFittings = db.session.query(v_count_fittings).filter_by(user_id=user_id).order_by('build_id').all()

        if request.form.get('ship_id'):
            ship_id = int(request.form.get('ship_id'))

        if request.args.get('build_id'):
            build_id = request.args.get('build_id')
            #print 'build args id = ' + str(build_id)

        if request.form.get('build_id'):
            build_id = request.form.get('build_id')
            #print 'build form id = ' + str(build_id)

        if myFittingsCount > 0:
            if request.form.get('fittingIndex'): fittingIndex = int(request.form.get('fittingIndex'))
            if request.args.get('fittingIndex'): fittingIndex = int(request.args.get('fittingIndex'))

            if request.form.get('action') == 'prev':
                fittingIndex = int(request.form.get('fittingIndex')) -1
            elif request.form.get('action') == 'next':
                fittingIndex = int(request.form.get('fittingIndex')) +1
            if fittingIndex < 0:
                build_id = myFittings[0].build_id
                fittingIndex = 0
                #print 'build id index0= ' + str(build_id)
            elif fittingIndex > myFittingsCount-1:
                build_id = myFittings[-1].build_id
                fittingIndex -= 1
                #print 'build id indexmax= ' + str(build_id)

            if build_id == 0:
                build_id = myFittings[0].build_id
                #print 'myfittings build id at index0 = ' + str(build_id)
            else:
                build_id = myFittings[fittingIndex].build_id
                #print 'build id from myFittings (default) = ' + str(build_id)

            if request.form.get('newBuild'):
                build_id = myFittings[-1].build_id +1
                #print 'build id last+1 = ' + str(build_id)
            else:
                if request.form.get('action') <> 'new': ship_id = myFittings[fittingIndex].ship_id
                shipFittings = db.session.query(ship_fittings).filter_by(user_id=user_id, build_id=build_id).order_by('ship_name').all()
                nonBuildableFittings = db.session.query(v_buildable_fittings).filter(v_buildable_fittings.meta <> 2).filter(v_buildable_fittings.rollup==1).filter(v_buildable_fittings.user_id==user_id).with_entities('ship_id', 'ship_name', 'jita_buy', 'qty', 'id', 'component', 'component_cost', 'component_qty', 'build_cost', 'meta', 'rollup','user_id', 'bp_id').all()

                nonBuildablefittingRollup = fitting_rollup_qty(nonBuildableFittings)
                for nbf in nonBuildableFittings:
                    nonBuildableTotal += (float(nbf.qty) * float(nbf.component_qty) * float(nbf.component_cost))

                buildableFittings = db.session.query(v_buildable_fittings_all).filter_by(rollup=1, user_id=user_id).with_entities('ship_id', 'ship_name', 'jita_buy', 'qty', 'id', 'component', 'component_cost', 'component_qty', 'build_cost', 'meta', 'rollup', 'user_id', 'bp_id').all()

                buildablefittingRollup = fitting_rollup_qty(buildableFittings)
                for bf in buildableFittings:
                    buildableTotal += (float(bf.qty) * float(bf.component_qty) * float(bf.component_cost))


                fittingCost = fitting_rollup_cost(shipFittings)
                if fittingCost > 0: fittingPM = ((float(shipFittings[fittingIndex].qty) * float(shipFittings[fittingIndex].contract_sell_price)) / float(fittingCost)) -1.0

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

        #print request.method
        if request.method == 'POST':
            #print request.form.get('action')
            if request.form.get('fetch'):
                myAssets = get_fittings()
                for item in myAssets:
                    #print item
                    if item =='error' or item=='timeout':
                        flash ('Problem fetching fittings from EVE.', 'danger')
                        break
                    else:
                        my_import = FittingList(item['fitting_id'], item['name'])
                        fitting_list += [my_import]

            if request.form.get('import'):
                fitting_selection = int(request.form.get('fitting_selection'))
                myAssets = get_fittings()
                for item in myAssets:
                    #print item
                    if item =='error' or item=='timeout':
                        flash ('Problem fetching this fitting from EVE.', 'danger')
                        break
                    else:
                        if item['fitting_id'] == fitting_selection:
                            result = import_fitting(item)
                            return redirect(url_for('fittings'))

            if request.form.get('action') == 'new':
                if ship_id > 0 :
                    item = db.session.query(v_ships).filter_by(id = ship_id).one()
                    ship_name = item.ship
                    if myFittings:
                        build_id = myFittings[-1].build_id + 1
                    else:
                        build_id = 1
                    #print 'new build id: ' + str(build_id)

                    return render_template('fittings.html', ships=ships, myFittingsCount=myFittingsCount, ship_id=ship_id, build_id=build_id, ship_name=ship_name, num_rigslots=num_rigslots, num_lowslots=num_lowslots, num_medslots=num_medslots, num_highslots=num_highslots, rig_modules=rig_modules, low_modules=low_modules, med_modules=med_modules, high_modules=high_modules,ammos=ammos, drones=drones, myFittings=myFittings, fittingIndex=fittingIndex, fittingCost=fittingCost, fittingPM=fittingPM, newBuild=True)
                else:
                    flash('Pick a ship to build.', 'danger')

            elif request.form.get('action') == 'delete':
                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id']).all()
                for fit in existingFitting:
                    db.session.delete(fit)
                    db.session.commit()

                flash('Successfully deleted fitting.', 'success')
                return redirect(url_for('fittings'))

            elif request.form.get('build'):
                for bfr in buildablefittingRollup:
                    myMaterialCost = []
                    myBuildCost = 0
                    myBuildRequirements = db.session.query(v_build_requirements).filter_by(id = bfr.bp_id, product_id=bfr.id).with_entities('id','material','material_id','group_id','qty','product_id', 'vol').all()

                    for requirements in myBuildRequirements:
                        myBuildCost += (get_marketValue(requirements.material_id, 'sell') * requirements.qty)

                    for requirements in myBuildRequirements:
                        #myCost = get_marketValue(requirements.material_id, 'sell') * requirements.qty
                        myCost = 0
                        pipeline = build_pipeline(session['myUser_id'], bfr.id, bfr.bp_id, bfr.component_qty * bfr.qty, requirements.material_id, requirements.qty, myCost, bfr.component, requirements.material, requirements.group_id, 0, bfr.component_cost, 0, myBuildCost, 0, 2, requirements.vol, 1)
                        
                        db.session.add(pipeline)
                        db.session.commit()

                flash('Successfully added to build pipeline.','success')
                return redirect(url_for('pipeline'))

            elif request.form.get('action') == 'edit':
                item = db.session.query(v_ships).filter_by(id = ship_id).one()
                ship_name = item.ship
                ship_jita_buy = get_marketValue(ship_id,'buy')
                myRollup = 0

                if request.args.get('build_id'):
                    build_id = request.args.get('build_id')
                    myContractPrice = float(request.args.get('contract_sell_price').replace(',', ''))
                    fitting_name = request.args.get('fitting_name')
                    myQty = int(request.args.get('qty'))
                    if request.args.get('rollup') == 'on':
                        myRollup = 1
                    else:
                        myRollup = 0
                else:
                    build_id = request.form.get('build_id')
                    myContractPrice = float(request.form.get('contract_sell_price').replace(',', ''))
                    fitting_name = request.form.get('fitting_name')
                    myQty = int(request.form.get('qty'))

                    if request.form.get('rollup') == 'on':
                        myRollup = 1
                    else:
                        myRollup = 0

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='ship').all()
                if existingFitting:
                    existingFitting[0].qty = myQty
                    existingFitting[0].component_id = ship_id
                    existingFitting[0].component_qty = 1
                    existingFitting[0].component_cost = ship_jita_buy
                    existingFitting[0].component = ship_name
                    existingFitting[0].fitting_name = fitting_name
                    existingFitting[0].contract_sell_price = myContractPrice
                    existingFitting[0].rollup = myRollup
                    db.session.add(existingFitting[0])
                    db.session.commit()
                    #print ('update existing. Contract price: ' + str(myContractPrice))
                else:
                    if build_id == 0: build_id = 1
                    myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, fitting_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, ship_id, 1, ship_jita_buy, ship_name, 'ship', myContractPrice, 0, ship_jita_buy, myRollup)
                    db.session.add(myFittings)
                    db.session.commit()

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='high').all()
                if num_highslots > 0:
                    for n in range(1, num_highslots+1):
                        if request.form.get('hi'+str(n)) > 0:
                            comp_id  = request.form.get('hi'+str(n))
                            #print comp_id
                            if comp_id > 0:
                                #comp_jita_buy = get_marketValue(comp_id,'buy')
                                comp = db.session.query(invTypes).filter(invTypes.typeID==comp_id).with_entities('"typeName"').one()

                            if existingFitting:
                                #print 'rollup = ' + str(myRollup)
                                fit = existingFitting[n-1]
                                fit.qty = myQty
                                fit.component_id = comp_id
                                fit.component_qty = 1
                                #fit.component_cost = comp_jita_buy
                                fit.component = comp[0]
                                fit.fitting_name = fitting_name
                                fit.contract_sell_price = myContractPrice
                                fit.rollup = myRollup
                                db.session.add(fit)
                                db.session.commit()
                            else:
                                if build_id == 0: build_id = 1
                                comp_jita_buy = get_marketValue(comp_id,'buy')
                                myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, fitting_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, 1, comp_jita_buy, comp[0], 'high', myContractPrice, 0, ship_jita_buy, myRollup)
                                db.session.add(myFittings)
                                db.session.commit()

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='med').all()
                if num_medslots > 0:
                    for n in range(1, num_medslots+1):
                        if request.form.get('med'+str(n)) > 0:
                            comp_id  = request.form.get('med'+str(n))
                            if comp_id > 0:
                                #comp_jita_buy = get_marketValue(comp_id,'buy')
                                comp = db.session.query(invTypes).filter(invTypes.typeID==comp_id).with_entities('"typeName"').one()

                            if existingFitting:
                                fit = existingFitting[n-1]
                                fit.qty = myQty
                                fit.component_id = comp_id
                                fit.component_qty = 1
                                #fit.component_cost = comp_jita_buy
                                fit.component = comp[0]
                                fit.fitting_name = fitting_name
                                fit.contract_sell_price = myContractPrice
                                fit.rollup = myRollup
                                db.session.add(fit)
                                db.session.commit()
                            else:
                                if build_id == 0: build_id = 1
                                comp_jita_buy = get_marketValue(comp_id,'buy')
                                myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, fitting_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, 1, comp_jita_buy, comp[0], 'med', myContractPrice, 0, ship_jita_buy, myRollup)
                                db.session.add(myFittings)
                                db.session.commit()

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='low').all()
                if num_lowslots > 0:
                    for n in range(1, num_lowslots+1):
                        if request.form.get('low'+str(n)) > 0:
                            comp_id  = request.form.get('low'+str(n))
                            if comp_id > 0:
                                #comp_jita_buy = get_marketValue(comp_id,'buy')
                                comp = db.session.query(invTypes).filter(invTypes.typeID==comp_id).with_entities('"typeName"').one()

                            if existingFitting:
                                fit = existingFitting[n-1]
                                fit.qty = myQty
                                fit.component_id = comp_id
                                fit.component_qty = 1
                                #fit.component_cost = comp_jita_buy
                                fit.component = comp[0]
                                fit.fitting_name = fitting_name
                                fit.contract_sell_price = myContractPrice
                                fit.rollup = myRollup
                                db.session.add(fit)
                                db.session.commit()
                            else:
                                if build_id == 0: build_id = 1
                                comp_jita_buy = get_marketValue(comp_id,'buy')
                                myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, fitting_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, 1, comp_jita_buy, comp[0], 'low', myContractPrice, 0, ship_jita_buy, myRollup)
                                db.session.add(myFittings)
                                db.session.commit()

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='rig').all()
                if num_rigslots > 0:
                    for n in range(1, num_rigslots+1):
                        if request.form.get('rig'+str(n)) > 0:
                            comp_id  = request.form.get('rig'+str(n))
                            if comp_id > 0:
                                #comp_jita_buy = get_marketValue(comp_id,'buy')
                                comp = db.session.query(invTypes).filter(invTypes.typeID==comp_id).with_entities('"typeName"').one()

                            if existingFitting:
                                fit = existingFitting[n-1]
                                fit.qty = myQty
                                fit.component_id = comp_id
                                fit.component_qty = 1
                                #fit.component_cost = comp_jita_buy
                                fit.component = comp[0]
                                fit.fitting_name = fitting_name
                                fit.contract_sell_price = myContractPrice
                                fit.rollup = myRollup
                                db.session.add(fit)
                                db.session.commit()
                            else:
                                if build_id == 0: build_id = 1
                                comp_jita_buy = get_marketValue(comp_id,'buy')
                                myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, fitting_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, 1, comp_jita_buy, comp[0], 'rig', myContractPrice, 0, ship_jita_buy, myRollup)
                                db.session.add(myFittings)
                                db.session.commit()

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='ammo').all()
                for n in range(1, 10):
                    if request.form.get('ammo'+str(n)) > 0:
                        comp_qty = request.form.get('ammo_qty'+str(n))
                        comp_id  = request.form.get('ammo'+str(n))
                        if comp_id > 0:
                            #comp_jita_buy = get_marketValue(comp_id,'buy')
                            comp = db.session.query(invTypes).filter(invTypes.typeID==comp_id).with_entities('"typeName"').one()

                        if existingFitting:
                            fit = existingFitting[n-1]
                            fit.qty = myQty
                            fit.component_id = comp_id
                            fit.component_qty = comp_qty
                            #fit.component_cost = comp_jita_buy
                            fit.component = comp[0]
                            fit.fitting_name = fitting_name
                            fit.contract_sell_price = myContractPrice
                            fit.rollup = myRollup
                            db.session.add(fit)
                            db.session.commit()
                        else:
                            if build_id == 0: build_id = 1
                            comp_jita_buy = get_marketValue(comp_id,'buy')
                            myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, fitting_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, comp_qty, comp_jita_buy, comp[0], 'ammo', myContractPrice, 0, ship_jita_buy, myRollup)
                            db.session.add(myFittings)
                            db.session.commit()

                existingFitting = db.session.query(ship_fittings).filter_by(build_id = build_id, user_id=session['myUser_id'], component_slot='drone').all()
                for n in range(1, 10):
                    if request.form.get('drone'+str(n)) > 0:
                        comp_qty = request.form.get('drone_qty'+str(n))
                        comp_id  = request.form.get('drone'+str(n))
                        if comp_id > 0:
                            #comp_jita_buy = get_marketValue(comp_id,'buy')
                            comp = db.session.query(invTypes).filter(invTypes.typeID==comp_id).with_entities('"typeName"').one()

                        if existingFitting:
                            fit = existingFitting[n-1]
                            fit.qty = myQty
                            fit.component_id = comp_id
                            fit.component_qty = comp_qty
                            #fit.component_cost = comp_jita_buy
                            fit.component = comp[0]
                            fit.fitting_name = fitting_name
                            fit.contract_sell_price = myContractPrice
                            fit.rollup = myRollup
                            db.session.add(fit)
                            db.session.commit()
                        else:
                            if build_id == 0: build_id = 1
                            comp_jita_buy = get_marketValue(comp_id,'buy')
                            myFittings = ship_fittings(build_id, session['myUser_id'], ship_id, ship_name, fitting_name, myQty, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, comp_qty, comp_jita_buy, comp[0], 'drone', myContractPrice, 0, ship_jita_buy, myRollup)
                            db.session.add(myFittings)
                            db.session.commit()

                flash('Successfully updated fitting.', 'success')
                return redirect(url_for('fittings', fittingIndex=fittingIndex, build_id=build_id))


        if myFittingsCount > 0:
            myFittingsHigh = db.session.query(ship_fittings).filter_by(user_id=user_id, ship_id=ship_id, component_slot='high').all()
            myFittingsMed = db.session.query(ship_fittings).filter_by(user_id=user_id, ship_id=ship_id, component_slot='med').all()
            myFittingsLow = db.session.query(ship_fittings).filter_by(user_id=user_id, ship_id=ship_id, component_slot='low').all()
            myFittingsRig = db.session.query(ship_fittings).filter_by(user_id=user_id, ship_id=ship_id, component_slot='rig').all()
            myFittingsAmmo = db.session.query(ship_fittings).filter_by(user_id=user_id, ship_id=ship_id, component_slot='ammo').all()
            myFittingsDrone = db.session.query(ship_fittings).filter_by(user_id=user_id, ship_id=ship_id, component_slot='drone').all()

            return render_template('fittings.html', ships=ships, ship_id=ship_id, ship_name=ship_name, num_rigslots=num_rigslots, num_lowslots=num_lowslots, num_medslots=num_medslots, num_highslots=num_highslots, rig_modules=rig_modules, low_modules=low_modules, med_modules=med_modules, high_modules=high_modules,ammos=ammos, drones=drones, myFittingsCount=myFittingsCount, myFittings=myFittings, myFittingsHigh=myFittingsHigh, myFittingsMed=myFittingsMed, myFittingsLow=myFittingsLow, myFittingsRig=myFittingsRig, myFittingsAmmo=myFittingsAmmo, myFittingsDrone=myFittingsDrone, fittingIndex=fittingIndex, fittingCost=fittingCost, fittingPM=fittingPM, buildableFittings=buildableFittings, nonBuildableFittings=nonBuildableFittings, nonBuildableTotal=nonBuildableTotal, buildableTotal=buildableTotal, build_id=build_id, nonBuildablefittingRollup=nonBuildablefittingRollup, buildablefittingRollup=buildablefittingRollup, fitting_list=fitting_list)

        return render_template('fittings.html', ships=ships, myFittingsCount=0, ship_id=0, build_id=build_id, myFittings=myFittings, fittingCost=fittingCost, fitting_list=fitting_list)

        #except Exception as e:
        #    flash('Problem with Ship Fittings - see log.', 'danger')
        #    app.logger.info(str(e))
        #    return redirect(url_for('fittings'))
    else:
        flash('You must be logged in to use Ship Fittings.', 'danger')
        return redirect(url_for('index'))

@app.route("/mining", methods=['GET','POST'])
def mining():
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

                return render_template('mining.html', asteroid_groups=asteroid_groups, calcs=calcs, min_id1=min_id1, min_id2=min_id2, min_id3=min_id3, min_id4=min_id4, group_id1=group_id1, group_id2=group_id2, group_id3=group_id3, group_id4=group_id4, asteroid_name1=asteroid_name1, asteroid_name2=asteroid_name2, asteroid_name3=asteroid_name3, asteroid_name4=asteroid_name4, mined_mins=mined_mins)

            calcs = db.session.query(mining_calc).filter_by(user_id=session['myUser_id']).all()

            return render_template('mining.html', asteroid_groups=asteroid_groups, calcs=calcs)

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
    if 'myUser_id' in session:
        #try:
        inv_pipeline = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id']).with_entities('product_name','user_id','runs','blueprint_id','status').order_by('product_name').all()

        bld_pipeline = db.session.query(v_build_pipeline_products).filter_by(user_id= session['myUser_id']).with_entities('product_name','user_id','blueprint_id','product_id','runs','jita_sell_price','local_sell_price','build_cost','status', 'portion_size').order_by('status').all()

        if request.method == 'POST':
            if request.form.get('action') == 'Delete All':
                pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id']).all()
                for item in pipeline:
                    db.session.delete(item)
                    db.session.commit()
                flash('Successfully deleted all pipeline products.', 'success')

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
                        myBuildRequirements = db.session.query(v_build_requirements).filter_by(id = product_id, product_id=selected_product.t2_id ).with_entities('id', 'material', 'material_id', 'group_id', 'qty', 'product_id', 'vol').all()
                        myProduct = db.session.query(invTypes).filter_by(typeID = int(selected_product.t2_id)).one()

                        myBuildCost = 0
                        myMaterialCost = []
                        for requirements in myBuildRequirements:
                            myMaterialCost += [get_marketValue(requirements.material_id, 'sell') * requirements.qty]

                        for cost in myMaterialCost:
                            myBuildCost = myBuildCost + cost

                        for requirements in myBuildRequirements:
                            myCost = get_marketValue(requirements.material_id, 'sell') * requirements.qty

                            pipeline = build_pipeline(session['myUser_id'],  selected_product.t2_id, product_id, runs, requirements.material_id, requirements.qty, myCost, product_name, requirements.material, requirements.group_id, 0, querySell, 0, myBuildCost, 0, 2, requirements.vol, myProduct.portionSize)

                            db.session.add(pipeline)
                            db.session.commit()

                        flash('Successfully converted invention to build product.', 'success')
                        return redirect(url_for('pipeline'))

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
                    local_sell_price = float(request.form.get('local_sell').replace(',', ''))

                    #pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id'], blueprint_id = bp_id).all()
                    pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id'], blueprint_id = bp_id).delete()
                    db.session.commit()

                    selected_bp = db.session.query(v_build_product).filter_by(id = bp_id).one()
                    myProduct = db.session.query(invTypes).filter_by(typeID = int(selected_bp.t2_id)).one()
                    querySell = get_marketValue(str(myProduct.typeID),'buy')
                    myBuildRequirements = db.session.query(v_build_requirements).filter_by(id = bp_id, product_id=myProduct.typeID).with_entities('id','material','material_id','group_id','qty','product_id', 'vol').all()

                    myBuildCost = 0
                    myMaterialCost = []
                    for requirements in myBuildRequirements:
                        myMaterialCost += [get_marketValue(requirements.material_id, 'sell') * requirements.qty]

                    for cost in myMaterialCost:
                        myBuildCost = myBuildCost + cost

                    for requirements in myBuildRequirements:
                        myCost = get_marketValue(requirements.material_id, 'sell') * requirements.qty * int(runs)
                        compQty = calc_comp_efficiency(requirements.qty, runs)
                        compQty = (compQty * int(runs)) / 10

                        pipeline = build_pipeline(session['myUser_id'], myProduct.typeID, bp_id, int(runs), requirements.material_id, compQty, myCost, myProduct.typeName, requirements.material, requirements.group_id, 0, querySell, local_sell_price, myBuildCost, 0, status, requirements.vol, myProduct.portionSize)

                        db.session.add(pipeline)
                        db.session.commit()
                    flash('Successfully updated bill of materials.', 'success')

                if request.form.get('action') == 'DEL':
                    bp_id = request.form.get('blueprint_id')

                    pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id'], blueprint_id = bp_id).all()
                    for item in pipeline:
                        db.session.delete(item)
                        db.session.commit()
                    flash('Successfully deleted pipeline product.', 'success')

                bld_pipeline = db.session.query(v_build_pipeline_products).filter_by(user_id= session['myUser_id']).with_entities('product_name','user_id','blueprint_id','product_id','runs','jita_sell_price','local_sell_price','build_cost','status', 'portion_size').order_by('product_name').all()

        return render_template('pipeline.html', inv_pipeline=inv_pipeline, bld_pipeline=bld_pipeline)

        #except Exception as e:
        #    flash('Problem with Pipeline. - see log.', 'danger')
        #    app.logger.info(str(e))
        #    return redirect(url_for('pipeline'))
    else:
        flash('You must be logged in to view the pipeline', 'danger')
        return redirect(url_for('index'))

@app.route("/bom", methods=['GET','POST'])
def bom():
    if 'myUser_id' in session:
        #try:
        build_or_buy = 0
        build_or_buy_all = 99
        build_or_buy_all_t1 = 99

        subtract_oh_assets = request.form.get('subtract_oh_assets')
        #print subtract_oh_assets
        if request.method == 'POST':
            if request.form.get('build_or_buy') == 'buy':
                build_or_buy = 0
            elif request.form.get('build_or_buy') == 'build':
                build_or_buy = 1

            if request.form.get('build_or_buy_all'):
                if request.form.get('build_or_buy_all') == 'buy':
                    build_or_buy = 0
                    build_or_buy_all = 0
                    flash('Buying all Advanced Components.', 'success')
                elif request.form.get('build_or_buy_all') == 'build':
                    build_or_buy = 1
                    build_or_buy_all = 1
                    flash('Building all Advanced Components.', 'success')

                pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id'],group_id=334, status=2).all()
                for item in pipeline:
                    item.build_or_buy = build_or_buy
                    db.session.add(item)
                    db.session.commit()

            if request.form.get('build_or_buy_all_t1'):
                if request.form.get('build_or_buy_all_t1') == 'buy':
                    build_or_buy = 0
                    build_or_buy_all_t1 = 0
                    flash('Buying all Tech 1 components.', 'success')
                elif request.form.get('build_or_buy_all_t1') == 'build':
                    build_or_buy = 1
                    build_or_buy_all_t1 = 1
                    flash('Building all Tech 1 components.', 'success')

                pipeline = db.session.query(build_pipeline).filter(build_pipeline.status==2).filter(build_pipeline.user_id == session['myUser_id']).filter(build_pipeline.group_id <> 334).filter(build_pipeline.group_id <> 18).filter(build_pipeline.group_id <> 1034).filter(build_pipeline.group_id <> 332).filter(build_pipeline.group_id <> 1040).filter(build_pipeline.group_id <> 429).all()

                for item in pipeline:
                    item.build_or_buy = build_or_buy
                    db.session.add(item)
                    db.session.commit()

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
                    materialCost = build_pipeline_rollup_cost(newcost_pipeline, subtract_oh_assets)
                    for item1 in newcost_pipeline:
                        comp = db.session.query(build_pipeline).filter_by(id=item1.id).one()
                        comp.build_cost = materialCost / comp.runs
                        db.session.add(comp)
                        db.session.commit()

        inv_pipeline = db.session.query(invent_pipeline).filter_by(user_id = session['myUser_id'],status=3).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','datacore_id','datacore_qty','datacore_cost','datacore', 'datacore_vol','status').order_by('datacore').all()

        planetary_pipeline = db.session.query(build_pipeline).filter(build_pipeline.status==2).filter(build_pipeline.user_id == session['myUser_id'], (or_(build_pipeline.group_id==1034, build_pipeline.group_id==1040, build_pipeline.group_id==1041, build_pipeline.group_id==1042, build_pipeline.group_id==1033, build_pipeline.group_id==1035))).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').order_by('material').all()

        salvage_pipeline = db.session.query(build_pipeline).filter(build_pipeline.status==2).filter(build_pipeline.user_id == session['myUser_id'], (or_(build_pipeline.group_id==754))).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').order_by('material').all()

        component_pipeline = db.session.query(build_pipeline).filter(build_pipeline.status==2).filter(build_pipeline.user_id == session['myUser_id'], (or_(build_pipeline.group_id==334, build_pipeline.group_id==964, build_pipeline.group_id==754, build_pipeline.group_id==536))).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').order_by('material').all()

        #component_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=334, status=2).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').order_by('material').all()

        comp_blueprint_id = 0 
        for component in component_pipeline:
            #print 'comp build or buy=' + str(component.build_or_buy)
            #print 'comp material cost=' + str(component.material_cost)
            if component.build_or_buy == 1 and component.material_cost > 0:
                comp = db.session.query(build_pipeline).filter_by(id=component.id).one()
                comp.material_cost = 0.0
                db.session.add(comp)
                db.session.commit()

                myBuildComponents = db.session.query(v_build_components).filter_by(id = component.material_id).with_entities('id','material','material_id','quantity','vol', 'group_id').all()
                comp_blueprint_id = component.blueprint_id

                for requirements in myBuildComponents:
                    myCost = get_marketValue(requirements.material_id, 'sell') * requirements.quantity * component.material_qty
                    matQty = calc_mat_efficiency(component.material_qty, requirements.quantity)

                    if requirements.group_id == 18 or requirements.group_id == 1034 or requirements.group_id == 1040 or requirements.group_id == 1033 or requirements.group_id == 1035 or requirements.group_id == 1041 or requirements.group_id == 1042:
                        pipeline = build_pipeline(session['myUser_id'],  component.product_id, component.blueprint_id, component.runs, requirements.material_id, matQty, myCost, component.product_name, requirements.material, requirements.group_id, 0, component.jita_sell_price, component.local_sell_price, component.build_cost, component.material_id, component.status, requirements.vol, component.portion_size)
                    else:
                        pipeline = build_pipeline(session['myUser_id'],  component.product_id, component.blueprint_id, component.runs, requirements.material_id, matQty, myCost, component.product_name, requirements.material, 429, 0, component.jita_sell_price, component.local_sell_price, component.build_cost, component.material_id, component.status, requirements.vol, component.portion_size)

                    db.session.add(pipeline)
                    db.session.commit()

                newcost_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],blueprint_id=comp_blueprint_id).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').all()
                materialCost = build_pipeline_rollup_cost(newcost_pipeline, subtract_oh_assets)
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

                if build_or_buy_all == 0:
                    mats_all = db.session.query(build_pipeline).filter(build_pipeline.user_id==session['myUser_id']).filter(build_pipeline.group_id==429).filter(build_pipeline.status==2).filter(build_pipeline.material_comp_id > 0).all()
                    for mat1 in mats_all:
                        db.session.delete(mat1)
                        db.session.commit()


                newcost_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],blueprint_id=comp_blueprint_id).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').all()
                materialCost = build_pipeline_rollup_cost(newcost_pipeline, subtract_oh_assets)
                for item in newcost_pipeline:
                    comp = db.session.query(build_pipeline).filter_by(id=item.id).one()
                    comp.build_cost = materialCost / comp.runs
                    db.session.add(comp)
                    db.session.commit()

        component_pipeline = db.session.query(build_pipeline).filter(build_pipeline.status==2).filter(build_pipeline.user_id == session['myUser_id'], (or_(build_pipeline.group_id==334, build_pipeline.group_id==964, build_pipeline.group_id==536))).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol','portion_size').order_by('material').all()

        material_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=429, status=2).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol','portion_size').order_by('material').all()

        tech1_pipeline = db.session.query(build_pipeline).filter(build_pipeline.status==2).filter(build_pipeline.user_id == session['myUser_id']).filter(build_pipeline.group_id <> 536).filter(build_pipeline.group_id <> 964).filter(build_pipeline.group_id <> 334).filter(build_pipeline.group_id <> 18).filter(build_pipeline.group_id <> 1034).filter(build_pipeline.group_id <> 332).filter(build_pipeline.group_id <> 1040).filter(build_pipeline.group_id <> 429).filter(build_pipeline.group_id <> 1041).filter(build_pipeline.group_id <> 1042).filter(build_pipeline.group_id <> 754).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').order_by('material').all()

        for component1 in tech1_pipeline:
            if component1.build_or_buy == 1 and component1.material_cost > 0:
                comp = db.session.query(build_pipeline).filter_by(id=component1.id).one()
                comp.material_cost = 0.0
                db.session.add(comp)
                db.session.commit()

                myBuildComponents = db.session.query(v_build_components).filter_by(id = component1.material_id).with_entities('id','material','material_id','quantity', 'vol', 'group_id').all()
                comp_blueprint_id = component1.blueprint_id

                for requirements in myBuildComponents:
                    myCost = get_marketValue(requirements.material_id, 'sell') * requirements.quantity * component1.material_qty

                    pipeline = build_pipeline(session['myUser_id'],  component1.product_id, component1.blueprint_id, component1.runs, requirements.material_id, requirements.quantity * component1.material_qty, myCost, component1.product_name, requirements.material, 18, 0, component1.jita_sell_price, component1.local_sell_price, component1.build_cost, component1.product_id, component1.status, requirements.vol, component1.portion_size)

                    db.session.add(pipeline)
                    db.session.commit()

                newcost_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],blueprint_id=comp_blueprint_id).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').all()
                materialCost = build_pipeline_rollup_cost(newcost_pipeline, subtract_oh_assets)
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

                if build_or_buy_all_t1 == 0:
                    mats_all = db.session.query(build_pipeline).filter(build_pipeline.user_id==session['myUser_id']).filter(build_pipeline.group_id==18).filter(build_pipeline.material_comp_id > 0).filter(build_pipeline.status==2).all()
                    for mat1 in mats_all:
                        db.session.delete(mat1)
                        db.session.commit()

                newcost_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],blueprint_id=comp_blueprint_id).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id', 'build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').all()
                materialCost = build_pipeline_rollup_cost(newcost_pipeline, subtract_oh_assets)
                for item in newcost_pipeline:
                    comp = db.session.query(build_pipeline).filter_by(id=item.id).one()
                    comp.build_cost = materialCost / comp.runs
                    db.session.add(comp)
                    db.session.commit()

        tech1_pipeline = db.session.query(build_pipeline).filter(build_pipeline.status==2).filter(build_pipeline.user_id == session['myUser_id']).filter(build_pipeline.group_id <> 536).filter(build_pipeline.group_id <> 964).filter(build_pipeline.group_id <> 334).filter(build_pipeline.group_id <> 18).filter(build_pipeline.group_id <> 1034).filter(build_pipeline.group_id <> 332).filter(build_pipeline.group_id <> 1040).filter(build_pipeline.group_id <> 1041).filter(build_pipeline.group_id <> 1042).filter(build_pipeline.group_id <> 429).filter(build_pipeline.group_id <> 754).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').order_by('material').all()

        ram_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=332,status=2).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').order_by('material').all()

        for component2 in ram_pipeline:
            if component2.build_or_buy == 1 and component2.material_cost > 0:
                comp = db.session.query(build_pipeline).filter_by(id=component2.id).one()
                comp.material_cost = 0.0
                db.session.add(comp)
                db.session.commit()

                myBuildComponents = db.session.query(v_build_components).filter_by(id = component2.material_id).with_entities('id','material','material_id','quantity', 'vol', 'group_id').all()

                for requirements in myBuildComponents:
                    myCost = get_marketValue(requirements.material_id, 'sell') * requirements.quantity * component2.material_qty

                    pipeline = build_pipeline(session['myUser_id'],  component2.product_id, component2.blueprint_id, component2.runs, requirements.material_id, requirements.quantity * component2.material_qty, myCost, component2.product_name, requirements.material, 18, 0, component2.jita_sell_price, component2.local_sell_price, component2.build_cost, component2.product_id,component2.status, requirements.vol)

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

        ram_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=332, status=2).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').order_by('material').all()

        mineral_pipeline = db.session.query(build_pipeline).filter_by(user_id= session['myUser_id'],group_id=18, status=2).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','material_id','material_qty','material_cost','material','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','jita_sell_price','local_sell_price','build_cost','material_comp_id','status','material_vol', 'portion_size').order_by('material_id').all()

        calcs = db.session.query(mining_calc).filter_by(user_id=session['myUser_id']).all()
        mineralInPipeline = build_pipeline_rollup_qty(mineral_pipeline, subtract_oh_assets)
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

            for mins in mineralInPipeline:
                if mins.material_id == 34:
                    trit_required += mins.material_qty
                elif mins.material_id == 35:
                    pye_required += mins.material_qty
                elif mins.material_id == 36:
                    mex_required += mins.material_qty
                elif mins.material_id == 37:
                    iso_required += mins.material_qty
                elif mins.material_id == 38:
                    nox_required += mins.material_qty
                elif mins.material_id == 39:
                    zyd_required += mins.material_qty
                elif mins.material_id == 40:
                    meg_required += mins.material_qty
                elif mins.material_id == 11399:
                    morph_required += mins.material_qty

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

        component_vol_total = 0
        tech1_vol_total = 0
        calcs = db.session.query(mining_calc).filter_by(user_id=session['myUser_id']).all()
        datacoresInPipeline = invent_pipeline_rollup_qty(inv_pipeline, subtract_oh_assets)
        dc_total = invent_pipeline_rollup_cost(inv_pipeline, subtract_oh_assets)
        vol_total = invent_pipeline_rollup_vol(inv_pipeline, subtract_oh_assets)
        planetaryInPipeline = build_pipeline_rollup_qty(planetary_pipeline, subtract_oh_assets)
        planet_total = build_pipeline_rollup_cost(planetary_pipeline, subtract_oh_assets)
        planet_vol_total = build_pipeline_rollup_vol(planetary_pipeline, subtract_oh_assets)
        salvageInPipeline = build_pipeline_rollup_qty(salvage_pipeline, subtract_oh_assets)
        salvage_total = build_pipeline_rollup_cost(salvage_pipeline, subtract_oh_assets)
        salvage_vol_total = build_pipeline_rollup_vol(salvage_pipeline, subtract_oh_assets)
        componentInPipeline = build_pipeline_rollup_qty(component_pipeline, subtract_oh_assets)
        component_total = build_pipeline_rollup_cost(component_pipeline, subtract_oh_assets)
        if component_total > 0:
            component_vol_total = build_pipeline_rollup_vol(component_pipeline, subtract_oh_assets)
        materialInPipeline = build_pipeline_rollup_qty(material_pipeline, subtract_oh_assets)
        material_total = build_pipeline_rollup_cost(material_pipeline, subtract_oh_assets)
        material_vol_total = build_pipeline_rollup_vol(material_pipeline, subtract_oh_assets)
        tech1InPipeline = build_pipeline_rollup_qty(tech1_pipeline, subtract_oh_assets)
        tech1_total = build_pipeline_rollup_cost(tech1_pipeline, subtract_oh_assets)
        if tech1_total > 0:
            tech1_vol_total = build_pipeline_rollup_vol(tech1_pipeline, subtract_oh_assets)
        ramInPipeline = build_pipeline_rollup_qty(ram_pipeline, subtract_oh_assets)
        ram_total = build_pipeline_rollup_cost(ram_pipeline, subtract_oh_assets)
        ram_vol_total = build_pipeline_rollup_vol(ram_pipeline, subtract_oh_assets)
        mineralInPipeline = build_pipeline_rollup_qty(mineral_pipeline, subtract_oh_assets)
        mineral_total = build_pipeline_rollup_cost(mineral_pipeline, subtract_oh_assets)
        mineral_vol_total = build_pipeline_rollup_vol(mineral_pipeline, subtract_oh_assets)
        total_volume = ram_vol_total + tech1_vol_total + material_vol_total + component_vol_total + planet_vol_total + vol_total

        bom_total = 0
        bom_total += dc_total
        bom_total += planet_total
        bom_total += salvage_total
        bom_total += component_total
        bom_total += material_total
        bom_total += tech1_total
        bom_total += ram_total
        bom_total += mineral_total

        return render_template('shopping_list.html', datacoresInPipeline=datacoresInPipeline, planetaryInPipeline=planetaryInPipeline, salvageInPipeline=salvageInPipeline, componentInPipeline=componentInPipeline, materialInPipeline=materialInPipeline, tech1InPipeline=tech1InPipeline, ramInPipeline=ramInPipeline, mineralInPipeline=mineralInPipeline, bom_total=bom_total, dc_total=dc_total, planet_total=planet_total, salvage_total=salvage_total, component_total=component_total, material_total=material_total, tech1_total=tech1_total, ram_total=ram_total, mineral_total=mineral_total,calcs=calcs, vol_total=vol_total, planet_vol_total=planet_vol_total, salvage_vol_total=salvage_vol_total, component_vol_total=component_vol_total, material_vol_total=material_vol_total, tech1_vol_total=tech1_vol_total, ram_vol_total=ram_vol_total, mineral_vol_total=mineral_vol_total, total_volume=total_volume, subtract_oh_assets=subtract_oh_assets)

        #except Exception as e:
        #    flash('Problem with B.o.M. - see log.', 'danger')
        #    app.logger.info(str(e))
        #    return redirect(url_for('bom'))
    else:
        flash('You must be logged in to view B.O.M.', 'danger')
        return redirect(url_for('index'))


@app.route('/build', methods=['GET','POST'])
def build():
    myBlueprints = []
    subtract_oh_assets = 'None'
    #try:
    myBlueprints = db.session.query(v_build_product).all()
    bp_all = True

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
        if request.args.get('bp_collection') == 'all':
            myBlueprints = db.session.query(v_build_product).all()
            bp_all = True
        elif request.args.get('bp_collection') == 'mine':
            myBlueprints = db.session.query(v_my_build_product).filter_by(user_id=session['myUser_id']).all()
            bp_all = False

        pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id'],status=2).with_entities('id','user_id','product_id','blueprint_id','runs','material_id','material_qty','material_cost','product_name','material','material_vol','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','jita_sell_price','local_sell_price','build_cost','material_comp_id','status', 'portion_size').order_by('material').all()

        pipeline_products = db.session.query(v_build_pipeline_products).filter_by(user_id = session['myUser_id'],status=2).with_entities('product_name', 'user_id', 'blueprint_id', 'product_id', 'runs', 'jita_sell_price','local_sell_price','build_cost','status')

        materialInPipeline = build_pipeline_rollup_qty(pipeline, subtract_oh_assets)
        materialCost = build_pipeline_rollup_cost(pipeline, subtract_oh_assets)

        return render_template('build.html', blueprints=myBlueprints, bp_id=0, pipeline=pipeline, materialInPipeline=materialInPipeline, pipelineCost=materialCost, pipeline_products=pipeline_products, bp_all=bp_all)
    else:
        return render_template('build.html', blueprints=myBlueprints, bp_id=0, bp_all=True)

    #except Exception as e:
    #    flash('Problem with blueprint - see log.', 'danger')
    #    app.logger.info(str(e))
    #    return redirect(url_for('build'))

@app.route('/build_selected', methods=['POST','GET'])
def build_selected():
    id = 0
    myBlueprints = []
    selected_bp = 0
    subtract_oh_assets = 'None'
    runs = 1
    bp_all = True
    #if request.form.get('build_product') is not None:
    #    id = int(request.form.get('build_product'))
    #if request.args.get('build_product') is not None:
    id = int(request.args.get('build_product'))
    #if request.args.get('runs'):
    runs = int(request.args.get('runs'))

    myBlueprints = db.session.query(v_build_product).all()
    if request.form.get('bp_all') == 'False':
        myBlueprints = db.session.query(v_my_build_product).filter_by(user_id=session['myUser_id']).all()
        bp_all = False

    #try:
    #print id
    #myBlueprints = db.session.query(v_build_product).all()
    try:
        selected_bp = db.session.query(v_build_product).filter_by(id = id).one()
    except Exception as e:
        #id +=1
        flash('Can\'t find that build info.', 'danger')
        print 'Not getting anything for item: ' + str(id)
        return redirect(url_for('build'))

    myProduct = db.session.query(invTypes).filter_by(typeID = int(selected_bp.t2_id)).one()
    querySell = get_marketValue(str(myProduct.typeID),'buy')
    mySellMedian = "{:,.0f}".format(querySell)
    buildTime = db.session.query(v_build_time).filter_by(id = id).one()
    myTime = "{:,}".format(buildTime.time/60)
    myBuildRequirements = db.session.query(v_build_requirements).filter_by(id = id, product_id = selected_bp.t2_id ).with_entities('id', 'material', 'material_id', 'group_id', 'qty', 'product_id', 'vol').all()

    myBuildCost = 0
    myMaterialCost = []
    for requirements in myBuildRequirements:
        myMaterialCost += [get_marketValue(requirements.material_id, 'sell') * requirements.qty]

    for cost in myMaterialCost:
        myBuildCost = myBuildCost + cost

    if 'myUser_id' in session:
        #myBlueprints = db.session.query(v_my_build_product).filter_by(user_id=session['myUser_id']).all()
        #if not myBlueprints:
        #    myBlueprints = db.session.query(v_build_product).all()
        #    bp_all = True

        pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id'],status=2).with_entities('id','user_id','product_id','blueprint_id','runs','material_id','material_qty','material_cost','product_name','material','material_vol','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','status', 'portion_size').order_by('material').all()

        pipeline_products = db.session.query(v_build_pipeline_products).filter_by(user_id = session['myUser_id'],status=2).with_entities('product_name', 'user_id', 'blueprint_id', 'product_id','runs','jita_sell_price','local_sell_price','build_cost','status', 'portion_size')

        materialInPipeline = build_pipeline_rollup_qty(pipeline, subtract_oh_assets)
        materialCost = build_pipeline_rollup_cost(pipeline, subtract_oh_assets)

        return render_template('build.html', blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, sell_median=querySell, time=myTime, buildRequirements = myBuildRequirements, buildCost = myBuildCost, materialCost = myMaterialCost, pipeline=pipeline, materialInPipeline=materialInPipeline, pipelineCost=materialCost, pipeline_products=pipeline_products, runs=runs, bp_all=bp_all)

    else:
        return render_template('build.html', blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, sell_median=querySell, time=myTime, buildRequirements = myBuildRequirements, buildCost = myBuildCost, materialCost = myMaterialCost, runs=runs, bp_all=bp_all)

    #except Exception as e:
    #    flash('Problem querying blueprint. See log', 'danger')
    #    app.logger.info(str(e))
    #    return redirect(url_for('build'))

@app.route('/build_add_pipeline', methods=['POST'])
def build_add_pipeline():
    id = request.form.get('bp_id')
    if 'myUser_id' in session:
        #try:
        if id > 0:
            subtract_oh_assets = 'None'
            myBlueprints = db.session.query(v_build_product).all()
            selected_bp = db.session.query(v_build_product).filter_by(id = id).one()
            myProduct = db.session.query(invTypes).filter_by(typeID = int(selected_bp.t2_id)).one()
            querySell = get_marketValue(str(myProduct.typeID),'buy')
            buildTime = db.session.query(v_build_time).filter_by(id = id).one()
            myTime = "{:,}".format(buildTime.time/60)
            myBuildRequirements = db.session.query(v_build_requirements).filter_by(id = id, product_id=myProduct.typeID).with_entities('id','material','material_id','group_id','qty','product_id', 'vol').all()
            myBuildCost = 0
            myMaterialCost = []
            for requirements in myBuildRequirements:
                myMaterialCost += [get_marketValue(requirements.material_id, 'sell') * requirements.qty]

            for cost in myMaterialCost:
                myBuildCost = myBuildCost + cost

            pipeline = db.session.query(build_pipeline).filter_by(user_id = session['myUser_id'],status=2).with_entities('id','user_id','product_id','blueprint_id','runs','material_id','material_qty','material_cost','product_name','material','material_vol','group_id','build_or_buy','jita_sell_price','local_sell_price','build_cost','jita_sell_price','local_sell_price','build_cost','material_comp_id','status', 'portion_size').order_by('material').all()

            pipeline_products = db.session.query(v_build_pipeline_products).filter_by(user_id = session['myUser_id'],status=2).with_entities('product_name', 'user_id', 'blueprint_id', 'product_id','runs','jita_sell_price','local_sell_price','build_cost','status')

            materialInPipeline = build_pipeline_rollup_qty(pipeline, subtract_oh_assets)
            materialCost = build_pipeline_rollup_cost(pipeline, subtract_oh_assets)

            if request.form.get('job_runs') <> '':
                for requirements in myBuildRequirements:
                    myCost = get_marketValue(requirements.material_id, 'sell') * requirements.qty * float(request.form.get('job_runs'))
                    compQty = calc_comp_efficiency(requirements.qty, request.form.get('job_runs'))
                    compQty = (compQty * float(request.form.get('job_runs'))) / 10

                    pipeline = build_pipeline(session['myUser_id'], myProduct.typeID, id, request.form.get('job_runs'), requirements.material_id, compQty, myCost, myProduct.typeName, requirements.material, requirements.group_id, 0, querySell, 0, myBuildCost, 0, 2, requirements.vol, myProduct.portionSize)

                    db.session.add(pipeline)
                    db.session.commit()

                flash('Successfully added to pipeline using blueprint and station efficiencies (set in options).','success')
                return redirect(url_for('build'))
            else:
                flash('Enter a quantity in job runs field.', 'danger')
                return render_template('build.html', blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, sell_median=querySell, time=myTime, buildRequirements = myBuildRequirements, buildCost = myBuildCost, materialCost = myMaterialCost, pipeline=pipeline, materialInPipeline=materialInPipeline, pipelineCost=materialCost, pipeline_products=pipeline_products)

        else:
            flash('Choose a product to build.', 'danger')
            return redirect(url_for('build'))

        #except Exception as e:
        #    flash('Problem adding to pipeline. See log.', 'danger')
    #        app.logger.info(str(e))
    #        return redirect(url_for('build'))

    else:
        flash('You must be logged in to add to pipeline.', 'danger')
        return redirect(url_for('build'))

@app.route('/invent', methods=['POST','GET'])
def invent():
    runs = 20
    myBlueprints = []
    subtract_oh_assets = 'None'

    try:
        myBlueprints = db.session.query(v_invention_product).all()
        bp_all = True

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
            if request.args.get('bp_collection') == 'all':
                myBlueprints = db.session.query(v_invention_product).all()
                bp_all = True
            elif request.args.get('bp_collection') == 'mine':
                myBlueprints = db.session.query(v_my_invention_product).filter_by(user_id=session['myUser_id']).all()
                bp_all = False

            pipeline = db.session.query(invent_pipeline).filter_by(user_id = session['myUser_id'],status=3).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','datacore_id','datacore_qty','datacore_cost','datacore','datacore_vol','status').order_by('datacore').all()

            pipeline_products = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id'],status=3).with_entities('product_name', 'user_id', 'runs','status')

            materialInPipeline = invent_pipeline_rollup_qty(pipeline, subtract_oh_assets)
            materialCost = invent_pipeline_rollup_cost(pipeline, subtract_oh_assets)

            return render_template('invent.html', blueprints=myBlueprints, bp_id=0, pipeline=pipeline, materialInPipeline=materialInPipeline, pipeline_products=pipeline_products, materialCost=materialCost, runs=runs, bp_all=bp_all)
        else:
            return render_template('invent.html', blueprints=myBlueprints, bp_id=0, bp_all=True)

    except Exception as e:
        flash('Problem with blueprint - see log.', 'danger')
        app.logger.info(str(e))
        return redirect(url_for('invent'))

@app.route('/invent_selected', methods=['POST','GET'])
def invent_selected():
    subtract_oh_assets = 'None'
    queryByName = False
    runs = 20
    if request.form.get('bp_all'): bp_all = request.form.get('bp_all')
    id = request.form.get('invent_product')

    myBlueprints = db.session.query(v_invention_product).all()
    bp_all = True

    if request.args.get('invent_productName'):
        queryByName = True
        runs = int(request.args.get('runs'))

    try:
        if queryByName == True:
            productName = request.args.get('invent_productName')
            selected_bp = db.session.query(v_invention_product).filter_by(t2_blueprint = productName).first()
            id = selected_bp.id
        else:
            selected_bp = db.session.query(v_invention_product).filter_by(id = id).one()

        selected_product = db.session.query(v_product).filter_by(id = selected_bp.t2_id).one()
        myProduct = db.session.query(invTypes).filter_by(typeID = int(selected_product.t2_id)).one()
        myProbability = db.session.query(v_probability).filter_by(id = id).one()
        myProbPercent = "{:.2%}".format(myProbability.probability)
        querySell = get_marketValue(str(myProduct.typeID),'buy')
        mySellMedian = "{:,.0f}".format(querySell)
        inventTime = db.session.query(v_invent_time).filter_by(id = id).one()
        myTime = "{:,}".format((inventTime.time/60)/60)
        myDatacoreRequirements = db.session.query(v_datacore_requirements).filter_by(id = id).with_entities('id','datacore','quantity','dc_id', 'vol').all()
        myDatacoresCost = 0
        for datacore in myDatacoreRequirements:
            myDatacoresCost = myDatacoresCost + get_marketValue(datacore.dc_id, 'sell') * datacore.quantity

        myBaseProduct = db.session.query(v_build_requirements).filter_by(id = selected_bp.t2_id).filter(v_build_requirements.group_id <> 334).filter(v_build_requirements.group_id <> 18).filter(v_build_requirements.group_id <> 1034).filter(v_build_requirements.group_id <> 332).filter(v_build_requirements.group_id <> 1040).one()

        if 'myUser_id' in session:
            myBlueprints = db.session.query(v_my_invention_product).filter_by(user_id=session['myUser_id']).all()
            if not myBlueprints:
                myBlueprints = db.session.query(v_invention_product).all()
                bp_all = True

            pipeline = db.session.query(invent_pipeline).filter_by(user_id = session['myUser_id'],status=3).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','datacore_id','datacore_qty','datacore_cost','datacore','datacore_vol','status').order_by('datacore').all()

            pipeline_products = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id'],status=3).with_entities('product_name', 'user_id', 'runs','status')

            materialInPipeline = invent_pipeline_rollup_qty(pipeline, subtract_oh_assets)
            materialCost = invent_pipeline_rollup_cost(pipeline, subtract_oh_assets)

            return render_template('invent.html', blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, probability=myProbPercent, sell_median=mySellMedian, time=myTime, datacoreRequirements = myDatacoreRequirements, datacoresCost=myDatacoresCost, baseProduct = myBaseProduct.material, pipeline=pipeline, materialInPipeline=materialInPipeline, materialCost=materialCost, pipeline_products=pipeline_products, runs=runs, bp_all=bp_all)

        else:
            return render_template('invent.html', blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, probability=myProbPercent, sell_median=mySellMedian, time=myTime, datacoreRequirements=myDatacoreRequirements, datacoresCost = myDatacoresCost, baseProduct = myBaseProduct.material, runs=runs, bp_all=True)

    except Exception as e:
        flash('Problem querying blueprint. See log', 'danger')
        app.logger.info(str(e))
        return redirect(url_for('invent'))

@app.route('/invent_add_pipeline', methods=['POST'])
def invent_add_pipeline():
    id = request.form.get('bp_id')

    if 'myUser_id' in session:
        try:
            if id > 0:
                subtract_oh_assets = 'None'
                myBlueprints = db.session.query(v_invention_product).all()
                selected_bp = db.session.query(v_invention_product).filter_by(id = id).one()
                selected_product = db.session.query(v_product).filter_by(id = selected_bp.t2_id).one()
                myProduct = db.session.query(invTypes).filter_by(typeID = int(selected_bp.t2_id)).one()
                querySell = get_marketValue(str(myProduct.typeID),'buy')
                inventTime = db.session.query(v_invent_time).filter_by(id = id).one()
                myTime = "{:,}".format((inventTime.time/60)/60)
                myDatacoreRequirements = db.session.query(v_datacore_requirements).filter_by(id = id).with_entities('id','datacore','quantity','dc_id', 'vol').all()
                myInventCost = 0
                myDatacoreCost = []
                for requirements in myDatacoreRequirements:
                    myDatacoreCost += [get_marketValue(requirements.dc_id, 'sell') * requirements.quantity]

                for cost in myDatacoreCost:
                    myInventCost += cost

                pipeline = db.session.query(invent_pipeline).filter_by(user_id = session['myUser_id'],status=3).with_entities('id','user_id','product_id','blueprint_id','runs','product_name','datacore_id','datacore_qty','datacore_cost','datacore','datacore_vol','status').order_by('datacore').all()

                pipeline_products = db.session.query(v_invent_pipeline_products).filter_by(user_id = session['myUser_id'],status=3).with_entities('product_name', 'user_id', 'runs','status')

                materialInPipeline = invent_pipeline_rollup_qty(pipeline, subtract_oh_assets)
                materialCost = invent_pipeline_rollup_cost(pipeline, subtract_oh_assets)

                if request.form.get('job_runs') <> '':
                    for requirements in myDatacoreRequirements:
                        myCost = get_marketValue(requirements.dc_id, 'sell') * requirements.quantity

                        pipeline = invent_pipeline(session['myUser_id'],  myProduct.typeID, id, request.form.get('job_runs'), selected_bp.t2_blueprint, requirements.dc_id, requirements.quantity, myCost, requirements.datacore, requirements.vol, 3)

                        db.session.add(pipeline)
                        db.session.commit()

                    flash('Successfully added to pipeline.','success')
                    return redirect(url_for('invent'))
                else:
                    flash('Enter a quantity in job runs field.', 'danger')
                    return render_template('invent.html', blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, sell_median=querySell, time=myTime, datacoreRequirements = myDatacoreRequirements, inventCost = myInventCost, datacoreCost = myDatacoreCost, pipeline=pipeline, materialInPipeline=materialInPipeline, materialCost=materialCost, pipeline_products=pipeline_products)

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
        return render_template('register.html')

@app.route('/logout')
def logout():
    user_id = session['myUser_id']
    session.clear()
    myUser = db.session.query(users).filter_by(character_id=user_id).all()
    if myUser:
        myUser[0].active = False
        db.session.add(myUser[0])
        db.session.commit()
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

def calc_comp_efficiency(qty, runs):
    wasteval = (1 - (float(session['structure_role_bonus']))/100) * (1 - (float(session['default_bp_me']))/100)
    if runs >= 10:
        myQty = math.ceil(round(qty * wasteval * 10, 2))
    else:
        myQty = math.ceil(round(qty * wasteval, 2))

    return myQty

def calc_mat_efficiency(compQty, matQty):
    if matQty > 1:
        myQty = math.ceil(round(matQty * 0.891 * compQty, 2))
    elif matQty == 1:
        myQty = math.ceil(round(matQty * compQty, 2))
    else:
        matQty = 0

    return myQty

def build_pipeline_rollup_cost(pipeline, subtract_oh_assets):
    buildCost = 0.0
    mat_oh = 0
    for item in pipeline:
        mat_oh = 0
        if subtract_oh_assets == 'true':
            mat_oh = search_assets(session['myUser_id'], item.material_id)

        if mat_oh == 0:
            buildCost += item.material_cost

    return buildCost



def fitting_rollup_cost(myFittings):
    buildCost = 0.0
    for item in myFittings:
        if item.component_qty > 0:
            buildCost += float(item.component_cost) * float(item.qty) * float(item.component_qty)

    return buildCost

def build_pipeline_rollup_qty(pipeline, subtract_oh_assets):
    materialInPipeline = []
    matchFound1 = False

    for item in pipeline:
        mat_oh = 0
        for mat in materialInPipeline:
            if mat.material_id == item.material_id:
                if subtract_oh_assets == 'true':
                    mat_oh = search_assets(session['myUser_id'], item.material_id)
                mat_qty = (item.material_qty) - mat_oh
                if mat_qty < 0: mat_qty = 0
                mat.material_qty += mat_qty
                mat.material_cost += item.material_cost
                matchFound1 = True

        if matchFound1 == True:
            matchFound1 = False
        else:
            if subtract_oh_assets == 'true':
                mat_oh = search_assets(session['myUser_id'], item.material_id)

            mat_qty = (item.material_qty) - mat_oh
            if mat_qty < 0: mat_qty = 0
            my_bom = BomMaterial(item.material_id, item.material, mat_qty, item.material_cost, item.runs, item.id, item.build_or_buy, item.blueprint_id, item.material_vol, item.portion_size)
            materialInPipeline += [my_bom]

    return materialInPipeline

def invent_pipeline_rollup_cost(pipeline, subtract_oh_assets):
    buildCost = 0.0
    dc_oh = 0
    for item in pipeline:
        if subtract_oh_assets == 'true':
            dc_oh = search_assets(session['myUser_id'], item.datacore_id)

        if dc_oh == 0:
            buildCost += (item.datacore_cost * item.runs)

    return buildCost

def build_pipeline_rollup_vol(pipeline, subtract_oh_assets):
    vol = 0.0
    mat_oh = 0

    for item in pipeline:
        mat_oh = 0
        if subtract_oh_assets == 'true':
            mat_oh = search_assets(session['myUser_id'], item.material_id)
            #print 'mat oh = ' + str(mat_oh)

        mat_vol = (item.material_vol * item.material_qty) - (mat_oh * item.material_vol)

        if mat_vol > 0:
            #print 'mat vol = ' + str(mat_vol)
            vol += mat_vol

    return vol

def invent_pipeline_rollup_vol(pipeline, subtract_oh_assets):
    vol = 0.0
    dc_oh = 0
    for item in pipeline:
        dc_oh = 0
        if subtract_oh_assets == 'true':
            dc_oh = search_assets(session['myUser_id'], item.datacore_id)

        dc_vol = (item.datacore_vol * item.datacore_qty * item.runs) - (dc_oh * item.datacore_vol)
        if dc_vol > 0:
            vol += dc_vol

    return vol

def invent_pipeline_rollup_qty(pipeline, subtract_oh_assets):
    materialInPipeline = []
    matchFound1 = False

    for item in pipeline:
        dc_oh = 0
        for mat in materialInPipeline:
            if mat.datacore_id == item.datacore_id:
                mat.datacore_qty += (item.datacore_qty * item.runs)
                mat.datacore_cost += item.datacore_cost
                matchFound1 = True

        if matchFound1 == True:
            matchFound1 = False
        else:
            if subtract_oh_assets == 'true':
                dc_oh = search_assets(session['myUser_id'], item.datacore_id)

            dc_qty = (item.datacore_qty * item.runs) - dc_oh
            if dc_qty < 0: dc_qty = 0
            my_bom = BomDatacores(item.datacore_id, item.datacore, dc_qty, item.datacore_cost, item.runs, item.datacore_vol)
            materialInPipeline += [my_bom]

    return materialInPipeline

def fitting_rollup_qty(shipFittings):
    shipFittingsRollup = []
    matchFound1 = False

    for item in shipFittings:
        for mat in shipFittingsRollup:
            if mat.id == item.id:
                mat.component_qty += item.component_qty
                matchFound1 = True

        if matchFound1 == True:
            matchFound1 = False
        else:
            my_bom = BomShipFittings(item.id, item.component, item.component_qty, item.component_cost, item.qty, item.bp_id)
            shipFittingsRollup += [my_bom]

    return shipFittingsRollup

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

@app.route('/login', methods=['GET','POST'])
def login():
    sso = db.session.query(eve_sso).all()
    client_id = sso[0].client_id
    secret_key = sso[0].secret_key
    code = request.args.get('code')
    state = request.args.get('state')
    auth = b64encode("{0}:{1}".format(client_id, secret_key))

    headers = {'Authorization': 'Basic ' + auth}
    payload = {'grant_type':'authorization_code', 'code':code}

    response = requests.post('https://login.eveonline.com/oauth/token', headers=headers, params=payload)
    jsonData = json.loads(response.text)

    if jsonData:
        #print jsonData
        refresh_token = jsonData['refresh_token']
        auth_code = jsonData['access_token']
        headers1 = {'Authorization': 'Bearer ' + auth_code}
        response1 = requests.get('https://esi.evetech.net/verify/', headers=headers1)
        jsonData1 = json.loads(response1.text)
        #print jsonData1

        if jsonData1:
            character_id = str(jsonData1['CharacterID'])
            #print character_id
            payload = {'datasource':'tranquility'}
            response2 = requests.get('https://esi.evetech.net/latest/characters/'+character_id, params=payload)
            jsonData2 = json.loads(response2.text)
            #print jsonData2
            corp_id = str(jsonData2['corporation_id'])
            response3 = requests.get('https://esi.evetech.net/latest/corporations/'+corp_id, params=payload)
            jsonData3 = json.loads(response3.text)
            corp_name = jsonData3['name']
            character_name = jsonData1['CharacterName']
            new_expiration = jsonData1['ExpiresOn']
            myUser = db.session.query(users).filter_by(character_id=character_id).all()
            home_station_id = '0'
            structure_role_bonus = 1.0
            default_bp_me = 2.0

            if myUser:
                lli = myUser[0].last_logged_in.strftime('%b %d, %Y')
                myUser[0].auth_code = auth_code
                myUser[0].expiration = new_expiration
                myUser[0].last_logged_in = datetime.now()
                myUser[0].active = True
                myUser[0].refresh_token = refresh_token
                home_station_id = myUser[0].home_station_id
                structure_role_bonus = float(myUser[0].structure_role_bonus)
                default_bp_me = float(myUser[0].default_bp_me)
                db.session.add(myUser[0])
                db.session.commit()

                flash('Successful login. '+character_name+' last logged in on: ' + lli,  'success')
            else:
                myUser = users(character_id, character_name, refresh_token, new_expiration, auth_code, True, datetime.now(), home_station_id, structure_role_bonus, default_bp_me, corp_id)
                db.session.add(myUser)
                db.session.commit()

                flash('Successfully created new login. Welcome, '+character_name+ '!',  'success')

            session['logged_in'] = True
            session['name'] = character_name
            session['myUser_id'] = character_id
            session['access_token'] = auth_code
            session['expiration'] = new_expiration
            session['corp_id'] = corp_id
            session['home_station_id'] = home_station_id
            session['structure_role_bonus'] = structure_role_bonus
            session['default_bp_me'] = default_bp_me
            session['corp_name'] = corp_name


    return redirect(url_for('index'))

def do_refresh_token(character_id):
    sso = db.session.query(eve_sso).all()
    myUser = db.session.query(users).filter_by(character_id=character_id).all()
    if myUser:
        refresh_token = myUser[0].refresh_token
        client_id = sso[0].client_id
        secret_key = sso[0].secret_key
        auth = b64encode("{0}:{1}".format(client_id, secret_key))

        headers = {'Authorization': 'Basic ' + auth}
        payload = {'grant_type':'refresh_token', 'refresh_token':refresh_token}

        response = requests.post('https://login.eveonline.com/oauth/token', headers=headers, params=payload)
        jsonData = json.loads(response.text)
        print jsonData
        auth_code = jsonData['access_token']
        myUser[0].auth_code = auth_code
        myUser[0].active = True
        myUser[0].last_logged_in = datetime.now()
        db.session.add(myUser[0])
        db.session.commit()

        print 'Successfully refreshed '+myUser[0].character_name+'\'s auth token.'
        session['logged_in'] = True
        session['access_token'] = auth_code
        return 0
    else:
        print 'Problem with logged in user.'
        return 1

def check_token(character_id):
    myUser = db.session.query(users).filter_by(character_id=character_id).all()
    if myUser:
        refresh_token = myUser[0].refresh_token
        auth_code = myUser[0].auth_code
        headers1 = {'Authorization': 'Bearer ' + auth_code}
        response1 = requests.get('https://esi.evetech.net/verify/', headers=headers1)
        jsonData1 = json.loads(response1.text)
        print 'Get Check Token - ' + str(response1.status_code)
        print jsonData1

        if response1.status_code <> 200:
            do_refresh_token(character_id)
            return 0
        else:
            print 'No token refresh needed.'
            return 0
    else:
        print 'Problem with logged in user.'
        return 1

def get_wallet_balance():
    payload = {'datasource':'tranquility', 'token':session['access_token']}
    response = requests.get('https://esi.evetech.net/latest/characters/'+session['myUser_id']+'/wallet/', params=payload)
    #print payload
    print 'Get Wallet Balance - ' + str(response.status_code)
    if response.status_code <> 200 and response.status_code <> 504:
        do_refresh_token(session['myUser_id'])
        payload = {'datasource':'tranquility', 'token':session['access_token']}
        response = requests.get('https://esi.evetech.net/latest/characters/'+session['myUser_id']+'/wallet/', params=payload)

    jsonData = json.loads(response.text)
    #print jsonData
    return jsonData

def get_wallet_journal():
    payload = {'datasource':'tranquility', 'token':session['access_token']}
    response = requests.get('https://esi.evetech.net/latest/characters/'+session['myUser_id']+'/wallet/journal/', params=payload)
    print 'Get Wallet Journal - ' + str(response.status_code)
    if response.status_code <> 200 and response.status_code <> 504:
        do_refresh_token(session['myUser_id'])
        payload = {'datasource':'tranquility', 'token':session['access_token']}
        response = requests.get('https://esi.evetech.net/latest/characters/'+session['myUser_id']+'/wallet/journal/', params=payload)

    jsonData = json.loads(response.text)
    return jsonData

def get_wallet_transactions():
    payload = {'datasource':'tranquility', 'token':session['access_token']}
    response = requests.get('https://esi.evetech.net/latest/characters/'+session['myUser_id']+'/wallet/transactions/', params=payload)
    print 'Get Wallet Transactions - ' + str(response.status_code)
    if response.status_code <> 200 and response.status_code <> 504:
        do_refresh_token(session['myUser_id'])
        payload = {'datasource':'tranquility', 'token':session['access_token']}
        response = requests.get('https://esi.evetech.net/latest/characters/'+session['myUser_id']+'/wallet/transactions/', params=payload)

    jsonData = json.loads(response.text)
    return jsonData

def get_assets_onhand():
    jsonData = []
    listLengthPrev = 0
    listLengthCurrent = 0
    for n in range(1, 10):
        payload = {'datasource':'tranquility', 'token':session['access_token'], 'page':n}
        response = requests.get('https://esi.evetech.net/latest/characters/'+session['myUser_id']+'/assets/', params=payload)
        print 'Get Assets On Hand - page: ' + str(n) + ' - ' + str(response.status_code)
        if response.status_code <> 200 and response.status_code <> 504:
            do_refresh_token(session['myUser_id'])
            payload = {'datasource':'tranquility', 'token':session['access_token']}
            response = requests.get('https://esi.evetech.net/latest/characters/'+session['myUser_id']+'/assets/', params=payload)

        jsonData += json.loads(response.text)
        listLengthCurrent = len(jsonData)
        if listLengthCurrent > listLengthPrev:
            listLengthPrev = listLengthCurrent
        else:
            break

            #print 'jsondata count: ' + str(len(jsonData))

    return jsonData

def get_fittings():
    payload = {'datasource':'tranquility', 'token':session['access_token']}
    response = requests.get('https://esi.evetech.net/latest/characters/'+session['myUser_id']+'/fittings/', params=payload)
    #print payload
    print 'Get Fittings - ' + str(response.status_code)
    do_refresh_token(session['myUser_id'])
    if response.status_code <> 200 and response.status_code <> 504:

        payload = {'datasource':'tranquility', 'token':session['access_token']}
        response = requests.get('https://esi.evetech.net/latest/characters/'+session['myUser_id']+'/fittings/', params=payload)

    jsonData = json.loads(response.text)
    return jsonData

def search_assets(user_id, product_id):
    qty = 0
    assets = db.session.query(assets_onhand).filter_by(user_id=user_id, product_id=product_id).all()
    for item in assets:
        qty += item.qty

    return qty

def get_job_journal():
    payload = {'datasource':'tranquility', 'token':session['access_token']}
    response = requests.get('https://esi.evetech.net/latest/characters/'+session['myUser_id']+'/industry/jobs/', params=payload)
    print 'Get Job Journal - ' + str(response.status_code)
    if response.status_code <> 200 and response.status_code <> 504:
        do_refresh_token(session['myUser_id'])
        payload = {'datasource':'tranquility', 'token':session['access_token']}
        response = requests.get('https://esi.evetech.net/latest/characters/'+session['myUser_id']+'/industry/jobs/', params=payload)

    jsonData = json.loads(response.text)
    return jsonData

def import_fitting(item):
    print 'Importing fit: ' + item['name']
    ship_id = item['ship_type_id']
    existingFitting = db.session.query(ship_fittings).filter_by(build_id = item['fitting_id'], user_id=session['myUser_id'], component_slot='ship').all()
    ship_jita_buy = get_marketValue(ship_id, 'buy')
    #ship_jita_buy = 0.0
    ship = db.session.query(v_ships).filter_by(id = ship_id).one()
    ship_name = ship.ship
    rigs = db.session.query(v_shipslots).filter_by(id=1137, ship_id=ship_id).one()
    rigsize = db.session.query(v_shipslots).filter_by(id=1547, ship_id=ship_id).one()
    myRigSize = rigsize.valfloat
    lows = db.session.query(v_shipslots).filter_by(id=12, ship_id=ship_id).one()
    meds = db.session.query(v_shipslots).filter_by(id=13, ship_id=ship_id).one()
    highs = db.session.query(v_shipslots).filter_by(id=14, ship_id=ship_id).one()
    print ship_id
    print highs.valfloat

    if rigs.valfloat:
        num_rigslots = int(rigs.valfloat)
    else:
        num_rigslots = rigs.valint
    rigsize = rigs.valint

    if lows.valfloat:
        num_lowslots = int(lows.valfloat)
    else:
        num_lowslots = lows.valint
    if meds.valfloat:
        num_medslots = int(meds.valfloat)
    else:
        num_medslots = meds.valint
    if highs.valfloat:
        num_highslots = int(highs.valfloat)
    else:
        num_highslots = highs.valint

    if not existingFitting:
        myFittings = ship_fittings(item['fitting_id'], session['myUser_id'], ship_id, ship_name, item['name'], 1, num_rigslots, num_lowslots, num_medslots, num_highslots, ship_id, 1, ship_jita_buy, ship_name, 'ship', 0.0, 0, ship_jita_buy, 0)
        db.session.add(myFittings)
        db.session.commit()

        for idx, slot in enumerate(item['items']):
            if slot['flag'].find("HiSlot") ==0:
                slot_position = 'high'
            elif slot['flag'].find("MedSlot") ==0:
                slot_position = 'med'
            elif slot['flag'].find("LoSlot") ==0:
                slot_position = 'low'
            elif slot['flag'].find("RigSlot") ==0:
                slot_position = 'rig'
            elif slot['flag'].find("Cargo") ==0:
                slot_position = 'ammo'
            elif slot['flag'].find("DroneBay") ==0:
                slot_position = 'drone'
            else:
                slot_position = ''
            #print(slot['flag'])
            #print(slot_position)

            comp_id  = slot['type_id']
            comp_qty = slot['quantity']
            if comp_id > 0:
                comp_jita_buy = get_marketValue(comp_id,'buy')
                comp = db.session.query(invTypes).filter(invTypes.typeID==comp_id).with_entities('"typeName"').one()

            myFittings = ship_fittings(item['fitting_id'], session['myUser_id'], ship_id, ship_name, item['name'], 1, num_rigslots, num_lowslots, num_medslots, num_highslots, comp_id, comp_qty, comp_jita_buy, comp[0], slot_position, 0.0, 0, ship_jita_buy, 0)
            db.session.add(myFittings)
            db.session.commit()


        highCount = db.session.query(ship_fittings).filter_by(build_id = item['fitting_id'], user_id=session['myUser_id'], component_slot='high').count()
        #print 'highcount is ' + str(highCount)
        for n in range(1, (num_highslots+1) - highCount):
            myFittings = ship_fittings(item['fitting_id'], session['myUser_id'], item['ship_type_id'], ship_name, item['name'], 1, num_rigslots, num_lowslots, num_medslots, num_highslots, 0, 1, 0.0, '', 'high', 0.0, 0, ship_jita_buy, 0)
            db.session.add(myFittings)
            db.session.commit()

        medCount = db.session.query(ship_fittings).filter_by(build_id = item['fitting_id'], user_id=session['myUser_id'], component_slot='med').count()

        for n in range(1, (num_medslots+1) -medCount):
            myFittings = ship_fittings(item['fitting_id'], session['myUser_id'], item['ship_type_id'], ship_name, item['name'], 1, num_rigslots, num_lowslots, num_medslots, num_highslots, 0, 1, 0.0, '', 'med', 0.0, 0, ship_jita_buy, 0)
            db.session.add(myFittings)
            db.session.commit()

        lowCount = db.session.query(ship_fittings).filter_by(build_id = item['fitting_id'], user_id=session['myUser_id'], component_slot='low').count()
        for n in range(1, (num_lowslots+1)-lowCount):
            myFittings = ship_fittings(item['fitting_id'], session['myUser_id'], item['ship_type_id'], ship_name, item['name'], 1, num_rigslots, num_lowslots, num_medslots, num_highslots, 0, 1, 0.0, '', 'low', 0.0, 0, ship_jita_buy, 0)
            db.session.add(myFittings)
            db.session.commit()

        rigCount = db.session.query(ship_fittings).filter_by(build_id = item['fitting_id'], user_id=session['myUser_id'], component_slot='rig').count()
        for n in range(1, (num_rigslots+1) -rigCount):
            myFittings = ship_fittings(item['fitting_id'], session['myUser_id'], item['ship_type_id'], ship_name, item['name'], 1, num_rigslots, num_lowslots, num_medslots, num_highslots, 0, 1, 0.0, '', 'rig', 0.0, 0, ship_jita_buy, 0)
            db.session.add(myFittings)
            db.session.commit()

        ammoCount = db.session.query(ship_fittings).filter_by(build_id = item['fitting_id'], user_id=session['myUser_id'], component_slot='ammo').count()
        for n in range(1, (10 - ammoCount)):
            myFittings = ship_fittings(item['fitting_id'], session['myUser_id'], item['ship_type_id'], ship_name, item['name'], 1, num_rigslots, num_lowslots, num_medslots, num_highslots, 0, 1, 0.0, '', 'ammo', 0.0, 0, ship_jita_buy, 0)
            db.session.add(myFittings)
            db.session.commit()

        droneCount = db.session.query(ship_fittings).filter_by(build_id = item['fitting_id'], user_id=session['myUser_id'], component_slot='drone').count()
        for n in range(1, (10 - droneCount)):
            myFittings = ship_fittings(item['fitting_id'], session['myUser_id'], item['ship_type_id'], ship_name, item['name'], 1, num_rigslots, num_lowslots, num_medslots, num_highslots, 0, 1, 0.0, '', 'drone', 0.0, 0, ship_jita_buy, 0)
            db.session.add(myFittings)
            db.session.commit()

    return 0

def import_jobs(item):
    #print 'Importing job: ' + str(item['blueprint_type_id'])
    #print item
    existingJob = db.session.query(job_journal).filter_by(job_id = str(item['job_id']), user_id=session['myUser_id']).all()
    if not existingJob:
        myJob = job_journal(item['job_id'], session['myUser_id'], item['product_type_id'], item['activity_id'], item['facility_id'], item['station_id'], item['licensed_runs'], item['runs'], item['blueprint_location_id'], item['output_location_id'], item['start_date'], item['end_date'], item['status'], item['cost'])
        db.session.add(myJob)
        db.session.commit()

    return 0

if __name__ == "__main__":
   app.run()
