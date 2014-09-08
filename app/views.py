
# The views are the handlers that respond to requests from web browsers.
from flask import render_template, flash, request, redirect, url_for, request
from flask.ext.login import login_user, logout_user
from flask.ext.login import current_user, login_required
from app import app, lm, oid, session, ordered_defaultdict
from app.forms import ProfileForm, RegistrationForm, LoginForm
from app.models.association import *
from app.models.foodlog import *
from app.models.user import *
from app.models.usda import *
import json
from sqlalchemy import or_
from app.constants import food_nutrient_dictionary, food_groups_dictionary
from collections import OrderedDict, defaultdict

@app.route('/')
@app.route('/index')
# def index():
#      user = { 'nickname': 'Linda' } # fake user
#      return render_template("index.html",
#          title = 'Home',
#          user = user)


#next assignment: use food_log as an example.
@app.route('/profile', methods=['GET'])
def profile_get():
    form = ProfileForm(request.form)
    return render_template('profile.html',
        #title is the name of the page for Profile: Nutrition
        title='Profile',
        #make a variable in the template called form. 
        #The value of the form should be
        #equal to the variable form in the local function.
        form=form)


@app.route('/profile', methods=['POST'])
def profile_post():
    form = ProfileForm(request.form)
    #print request.form

    if form.validate():

        #get the user from the database session
        user = session.query(User).filter_by(email="happy").first()
        # do not store the results of calculations using variable defined in
        # models.py That is what models.py is for.
        user.calorie_goal = form.calorie_goal.data
        user.protein_goal = form.protein_goal.data

        user.carbohydrate_goal = form.carbohydrate_goal.data
        user.fat_goal = form.fat_goal.data
        #user.nutrient_goal = form.nutrient_goal.data
        user.birthday = form.birthday.data
        user.set_weight(form.weight.data, form.weight_unit.data)
        user.set_weight_goal(form.weight_goal.data, form.weight_unit.data)
        user.set_height(form.height.data, form.height_unit.data)
        user.gender = form.gender.data    
        user.activity_level = form.activity_level.data
        user.set_weekly_weight_change(form.weekly_change_level.data)
        session.commit()
        #Here we need to save the information enterred by the User.
        #need access to the user object.
        #return redirect(url_for('profile_get'))
        return render_template(
            'profile.html', title='Profile',
            form=form)

# @app.route('/profile', methods=['GET', 'POST'])
# def profile():
#     request contains all the completed information 
#     that the user's browser sends to the host's server.
#     request.form contains all the filled-in information.
#     form = ProfileForm(request.form)
#     #print request.form
    
#     if request.method == 'POST' and form.validate():

#         #get the user from the database session
#         user = session.query(User).filter_by(email="happy").first()
#         # do not store the results of calculations using variable defined in
#         # models.py That is what models.py is for.
#         user.calorie_goal = form.calorie_goal.data
#         user.protein_goal = form.protein_goal.data

#         user.carbohydrate_goal = form.carbohydrate_goal.data
#         user.fat_goal = form.fat_goal.data
#         #user.nutrient_goal = form.nutrient_goal.data
#         user.birthday = form.birthday.data
#         user.set_weight(form.weight.data, form.weight_unit.data)
#         user.set_weight_goal(form.weight_goal.data, form.weight_unit.data)
#         user.set_height(form.height.data, form.height_unit.data)
#         user.gender = form.gender.data       
#         user.activity_level = form.activity_level.data
#         user.set_weekly_weight_change(form.weekly_change_level.data)
#         session.commit()
#         #Here we need to save the information enterred by the User.
#         #need access to the user object.
#         #return redirect(url_for('profile'))
#     return render_template('profile.html', 
#         #title is the name of the page for Profile: Nutrition
#         title = 'Profile',
#         #make a variable in the template called form. The value of the form should be
#         #equal to the variable form in the local function.
#         form=form)


def get_food_log(user):
    #pass the user as a parameter
    
    food_log = session.query(FoodLog).filter_by(user=user).first()   
    if food_log is None:
        food_log = FoodLog()
        food_log.user = user      
        session.add(food_log)
        #session.commit(food_log)
        #session.add()
        session.commit()
    return food_log

@app.route('/food_log', methods=['GET'])
def food_log_get():
   
    user = session.query(User).filter_by(email="happy").first()
    #gets the food groups list from the database
    #session.query(FoodGroupDescription) is a function that returns a variable.
    if user.protein_goal == None:
        return redirect(url_for('profile_get'))

    food_groups_list = session.query(FoodGroupDescription).order_by(
        FoodGroupDescription.FdGrp_Desc).all()
    #pylint suggested FdGrp_Cd
    #food_groups_list = session.query(FoodGroupDescription).order_by(
    #    FoodGroupDescription.FdGrp_Cd).all()
    food_log = get_food_log(user)
    
    # The food_log contains a list of associations between foods and quantities.
    #creating a list of dictionaries
    food_nutrient_list = []
    for association in food_log.foods:
        nutrients = session.query(NutrientData).filter_by(
            NDB_No=association.food.NDB_No).all()
        weights = session.query(Weight).filter_by(
            NDB_No=association.food.NDB_No).all()
            
        
        
        
        #get the nutrient values associated with the food
        #food_nutrient_dictionary is a dictionary with 
        #   a key called nutrient_category_name, and 
        #   a value called OrderedDictionary 
        #nutrient_category_name is the key in food_nutrient_dictionary which is a string
        #nutrient_category_dic is the value in food_nutrient_dictionary which is an Ordered Dictionary
        #values_nutrient_category is an empty dictionary
        #contains the amount of values of each food
        values_nutrient_dictionary = {}
        #find the OrderedDict() for each nutrient_category_dictionary
        for nutrient_category_name in food_nutrient_dictionary:
            nutrient_category_dictionary = food_nutrient_dictionary[nutrient_category_name]
            values_nutrient_category_dictionary = values_nutrient_dictionary[nutrient_category_name] = OrderedDict()
            for nutrient_name in nutrient_category_dictionary:              
                nutrient_number = nutrient_category_dictionary[nutrient_name]
                try:
                    nutrient_value = next(
                        x.Nutr_Val for x in nutrients if int(x.Nutr_No) == nutrient_number)                   
                    values_nutrient_category_dictionary[nutrient_name] = float(nutrient_value) * association.quantity
                except StopIteration:
                    values_nutrient_category_dictionary[nutrient_name] = "N/A"
         
        #example           
        #values_nutrient_dictionary["Carbohydrates"]["Fiber"]


        food_nutrient_list.append({
            "name": association.food.Long_Desc,
            "nutrients": values_nutrient_dictionary,
            "quantities": association.quantity,
            #"unit": association.unit
            })
        #create a new dictionary totalling the amount of nutrients consumed.
        #make the dictionary a nested dictionary to show the category_name
    totals = defaultdict(lambda: ordered_defaultdict.OrderedDefaultdict(float))
    for food_dictionary in food_nutrient_list:
        nutrient_category_dictionary = food_dictionary["nutrients"]
        for nutrient_category_name in nutrient_category_dictionary:
            nutrient_dictionary = nutrient_category_dictionary[nutrient_category_name]
            for nutrient_name in nutrient_dictionary:
                if nutrient_dictionary[nutrient_name] != "N/A":
                    totals[nutrient_category_name][nutrient_name] += nutrient_dictionary[nutrient_name]
    # for nutrient_category_name in totals:
    #     nutrient_dictionary = totals[nutrient_category_name]
    #     for nutrient_name in nutrient_dictionary:  
    #         print "{}: {}: {}".format(nutrient_category_name, nutrient_name, nutrient_dictionary[nutrient_name])  


    food_nutrient_list.append({
        "name": "Totals",
        "nutrients": totals,
        })

    return render_template(
        'food_log.html', title="FoodLog",
        food_nutrient_list=food_nutrient_list,
        food_groups_list=food_groups_list,
        # pass the user into the template. 
        # need a user object to display something in python on views.
        user=user
        )
    

@app.route('/food_log', methods=['POST'])
def food_log_post():
    user = session.query(User).filter_by(email="happy").first()
    foods = request.form.getlist('food')
    quantities = request.form.getlist('quantity')
    food_log = get_food_log(user)
    
    for food_name, food_quantity in zip(foods, quantities):
        food = session.query(FoodDescription).filter(
            FoodDescription.Long_Desc.ilike('%{}%'.format(food_name))).first()
        
        #weight = session.query(Weight.NDB_No == association.food.NDB_No)
        
        if food is None:
            print 'The item %s you enterred is not a proper food. \
            Please try again.' % food_name
            continue
        
        
        association = Association()
        #quantity is an attribute of a class
        association.quantity = float(food_quantity)
        #the association will contain one food and one food_log
        association.food = food
        #unit = session.query()
        association.unit = unit
        weight = session.query(Weight.NDB_No == association.food.NDB_No)
        food_log.foods.append(association)
        
    session.commit()


    #after adding the requests, want to take a look at the food log
    return redirect(url_for('food_log_get'))
    
    
@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        #user = session.query(User).filter_by(email="happy").first()
        #login = session.query(LoginForm).filter_by(user=user).first()
        user = User(form.openid.data, form.remember_me.data)
        db_session.add(user)
    
        return redirect(url_for('index'))
    return render_template(
        'login.html', title='Sign In',
    form=form,
        providers=app.config['OPENID_PROVIDERS'])


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        #user = session.query(User).filter_by(email="happy").first()
        #register = session.query(RegistrationForm).filter_by(user=user).first()
        user = User(form.username.data, form.email.data, 
            form.password.data)
        db_session.add(User)
        return redirect(url_for('login'))
    return render_template(
        'register.html', title="Register",
        form=form)


@lm.user_loader
def load_user(id):  
    return User.query.get(int(id))()

@app.route('/queries/<query_string>.json', methods=['GET'])
def query(query_string):

    food_list = []
    # construct a list of all the groups that we want to use as filters.
    groups = request.args.getlist("group")
    group_filters = [FoodDescription.FdGrp_Cd == group for group in groups]
    foods = session.query(FoodDescription)
    foods = foods.filter(FoodDescription.Long_Desc.ilike('%{}%'.format(query_string)))
    foods = foods.filter(or_(*group_filters))
    foods = foods.all()
    food_list = []
    for food in foods:
        unit_query = session.query(Weight).filter(Weight.NDB_No == \
        food.NDB_No).all()
        unit_list = []
        for unit in unit_query:
            unit_list.append({
                "name": unit.Msre_Desc,
                #"gram weight": units
                "units": units
                #add more relevant columns for the weights
                })
        food_list.append({
            "value": food.Long_Desc,
            "units": unit_list
            })

    return json.dumps(food_list)
    
