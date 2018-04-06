from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for, flash, session, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from datetime import datetime
import requests
import json

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

class invention_pipeline(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    product_id = db.Column(db.Integer())
    blueprint_id = db.Column(db.Integer())
    runs = db.Column(db.Integer())
    datacore1_id = db.Column(db.Integer())
    datacore2_id = db.Column(db.Integer())
    datacore1_cost = db.Column(db.Numeric())
    datacore2_cost = db.Column(db.Numeric())
    product_name = db.Column(db.String(100))
    datacore1 = db.Column(db.String(100))
    datacore2 = db.Column(db.String(100))

    def __init__(self, user_id, product_id, blueprint_id, runs, datacore1_id, datacore2_id, datacore1_cost, datacore2_cost, product_name, datacore1, datacore2):
        self.user_id = user_id
        self.product_id = product_id
        self.blueprint_id = blueprint_id
        self.runs = runs
        self.datacore1_id = datacore1_id
        self.datacore2_id = datacore2_id
        self.datacore1_cost = datacore1_cost
        self.datacore2_cost = datacore2_cost
        self.product_name = product_name
        self.datacore1 = datacore1
        self.datacore2 = datacore2

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


@app.route("/")
def index():
    form = LoginForm(request.form)
    return render_template('home.html', form=form)

@app.route('/invent', methods=['GET'])
def invent():
    form = LoginForm(request.form)
    try:
        myBlueprints = db.session.query(v_invention_product).all()

        if 'myUser_id' in session:
            pipeline = db.session.query(invention_pipeline).filter_by(user_id = session['myUser_id']).with_entities('id','user_id','product_id','blueprint_id','runs','datacore1_id','datacore2_id','datacore1_cost','datacore2_cost','product_name','datacore1','datacore2').all()

            datacoresInPipeline = invention_pipeline_rollup(pipeline)
            datacoreQtyInPipeline = invention_pipeline_rollup_qty(pipeline)
            datacoreCost = invention_pipeline_rollup_cost(pipeline)

            #print datacoresInPipeline
            return render_template('invent.html', form=form, blueprints=myBlueprints, bp_id=0, pipeline=pipeline, datacores=datacoresInPipeline, datacoreQty=datacoreQtyInPipeline, datacoreCost=datacoreCost)
        else:
            return render_template('invent.html', form=form, blueprints=myBlueprints, bp_id=0)

    except Exception as e:
        flash('Couldn\'t get blueprint list. See log', 'danger')
        app.logger.info(str(e))
        return redirect(url_for('invent'))

@app.route('/invent_selected', methods=['POST','GET'])
def invent_selected():
    id = request.form.get('invent_product')
    form = LoginForm(request.form)
    try:
        myBlueprints = db.session.query(v_invention_product).all()
        selected_bp = db.session.query(v_invention_product).filter_by(id = id).one()
        selected_product = db.session.query(v_product).filter_by(id = selected_bp.t2_id).one()
        myProduct = db.session.query(invtypes).filter_by(typeID = int(selected_product.t2_id)).one()
        myProbability = db.session.query(v_probability).filter_by(id = id).one()
        myProbPercent = "{:.2%}".format(myProbability.probability)
        querySell = get_marketValue(str(myProduct.typeID),'sell')
        mySellMedian = "{:,.2f}".format(querySell)
        inventTime = db.session.query(v_invent_time).filter_by(id = id).one()
        myTime = "{:,}".format((inventTime.time/60)/60)
        myDatacores = db.session.query(v_datacore_requirements).filter_by(id = id).with_entities('id','datacore','quantity','dc_id').all()
        myDatacoresCost = 0
        for datacore in myDatacores:
            myDatacoresCost = myDatacoresCost + get_marketValue(datacore.dc_id, 'buy') * datacore.quantity

        myBaseProduct = db.session.query(v_build_requirements).filter_by(id = selected_bp.t2_id).filter(v_build_requirements.group_id <> 334).filter(v_build_requirements.group_id <> 18).filter(v_build_requirements.group_id <> 1034).filter(v_build_requirements.group_id <> 332).filter(v_build_requirements.group_id <> 1040).one()

        if 'myUser_id' in session:
            pipeline = db.session.query(invention_pipeline).filter_by(user_id = session['myUser_id']).with_entities('id','user_id','product_id','blueprint_id','runs','datacore1_id','datacore2_id','datacore1_cost','datacore2_cost','product_name','datacore1','datacore2').all()
            return render_template('invent.html', form=form, blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, probability=myProbPercent, sell_median=mySellMedian, time=myTime, datacores = myDatacores, datacoresCost = myDatacoresCost, baseProduct = myBaseProduct.material, pipeline=pipeline)
        else:
            return render_template('invent.html', form=form, blueprints=myBlueprints, bp_id=id, selected_bp=selected_bp, product=myProduct, probability=myProbPercent, sell_median=mySellMedian, time=myTime, datacores = myDatacores, datacoresCost = myDatacoresCost, baseProduct = myBaseProduct.material)

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
            myBlueprints = db.session.query(v_invention_product).all()
            selected_bp = db.session.query(v_invention_product).filter_by(id = id).one()
            selected_product = db.session.query(v_product).filter_by(id = selected_bp.t2_id).one()
            myProduct = db.session.query(invtypes).filter_by(typeID = int(selected_product.t2_id)).one()
            myDatacores = db.session.query(v_datacore_requirements).filter_by(id = id).with_entities('id','datacore','quantity','dc_id').all()
            datacore1_cost = get_marketValue(myDatacores[0].dc_id, 'buy') * myDatacores[0].quantity
            datacore2_cost = get_marketValue(myDatacores[1].dc_id, 'buy') * myDatacores[1].quantity
            pipeline = invention_pipeline(session['myUser_id'],  myProduct.typeID, id, request.form.get('job_runs'), myDatacores[0].dc_id, myDatacores[1].dc_id, datacore1_cost, datacore2_cost, myProduct.typeName, myDatacores[0].datacore, myDatacores[1].datacore)

            db.session.add(pipeline)
            db.session.commit()
            msg = 'Successful added to pipeline.'

            pipeline = db.session.query(invention_pipeline).filter_by(user_id = session['myUser_id']).with_entities('id','user_id','product_id','blueprint_id','runs','datacore1_id','datacore2_id','datacore1_cost','datacore2_cost','product_name','datacore1','datacore2').all()

            return render_template('invent.html', form=form, blueprints=myBlueprints, bp_id=0, pipeline=pipeline)

        except Exception as e:
            error = 'Problem adding to pipeline. See log.'
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
                error = 'Login denied. Wrong password. Try again'
                return render_template('login.html', form=form, error=error)
        except Exception as e:
            app.logger.info(str(e))
            error = 'Problem logging in. See log'
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
        error = 'Problem with Market API. See log'
        return 0

def invention_pipeline_rollup(pipeline):
    datacoresInPipeline = []
    matchFound = False

    for item in pipeline:
        if matchFound == False:
            datacoresInPipeline += [item.datacore1]
            datacoresInPipeline += [item.datacore2]
        else:
            matchFound == False

        for dc in datacoresInPipeline:
            if dc == item.datacore1:
                matchFound = True
            elif dc == item.datacore2:
                matchFound = True
            else:
                matchFound = False

        #print ("item1: " + item.datacore1 + " Item2: " + item.datacore2)
        #matchFound = False
        print ("----------------")
        print datacoresInPipeline

    return datacoresInPipeline

def invention_pipeline_rollup_qty(pipeline):
    datacoreQtyInPipeline = []
    datacoresInPipeline = invention_pipeline_rollup(pipeline)
    matchFound = False

    for item in pipeline:
        if matchFound == False:
            datacoreQtyInPipeline += [item.runs]
            datacoreQtyInPipeline += [item.runs]
        else:
            matchFound == False

        for dc in datacoresInPipeline:
            if dc == item.datacore1:
                index = datacoresInPipeline.index(item.datacore1)
                datacoreQtyInPipeline[index] = datacoreQtyInPipeline[index] + item.runs
                matchFound = True
            else:
                matchFound = False

            if dc == item.datacore2:
                index = datacoresInPipeline.index(item.datacore2)
                datacoreQtyInPipeline[index] = datacoreQtyInPipeline[index] + item.runs
                matchFound = True
            else:
                matchFound = False

    return datacoreQtyInPipeline

def invention_pipeline_rollup_cost(pipeline):
    datacoreCost = 0
    for item in pipeline:
        datacoreCost += item.datacore1_cost * item.runs
        datacoreCost += item.datacore2_cost * item.runs

    return datacoreCost

if __name__ == "__main__":
   app.run()
