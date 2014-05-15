
# The views are the handlers that respond to requests from web browsers.
from flask import render_template, flash, request, redirect, url_for, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, lm, oid, session
from forms import ProfileForm, RegistrationForm, LoginForm
from models import *
import json
from sqlalchemy import or_


#refer to page 9 of the USDA database
food_nutrient_dictionary = {
    "Calorie Information": {
        "Energy_KCAL": 208,
        #"Energy_KJ": 268,

    },

    "Carbohydrates": {
        "Carbohydrate, by difference": 205, 
        "Fiber, total dietary": 291, 
        "Starch": 209, 
        "Sugars, total": 269, 
        "Sucrose": 210, 
        "Glucose(dextrose)": 211, 
        "Fructose": 212,         
        "Lactose": 213, 
        "Maltose": 214, 
        "Galactose": 287,       

    },

    "Fats & Fatty Acids": {
        "Total lipid (fat)": 204, 
        "Fatty acids, total saturated": 606, 
        "4:0": 607, 
        "6:0": 608, 
        "8:0": 609,
        "10:0": 610, 
        "12:0": 611, 
        "13:0": 696,
        "14:0": 612, 
        "15:0": 652, 
        "16:0": 613, 
        "17:0": 653 , 
        "18:0": 614, 
        "20:0": 615, 
        "22:0": 624, 
        "24:0": 654, 

    
        "Fatty acids, total monounsaturated": 645, 
        "14:1": 625, 
        "15:1": 697, 
        "16:1 undifferentiated": 626, 
        "16:1 c": 673, 
        "16:1 t": 662,
        "17:1": 687,
        "18:1 undifferentiated": 617, 
        "18:1 c": 674,
        "18:1 t": 663, 
        "18:1-11t (18:1tn-7)": 859,
        "20:1": 628,
        "22:1 undifferentiated": 630,
        "22:1 c": 676, 
        "22:1 t": 664, 
        "24:1 c": 671, 

        "Fatty acids, total polyunsaturated ": 646, 
        "18:2 undifferentiated": 618, 
        "18:2 n-6 c,c": 675, 
        "18:2 CLAs": 670, 
        "18:2 t,t": 669, 
        "18:2 i": 666, 
        "18:2 t not further defined": 665, 
        "18:3 undifferentiated": 619, 
        "18:3 n-3 c,c,c (ALA)": 851, 
        "18:3 n-6 c,c,c": 685,
        "18:3i": 856, 
        "18:4": 627, 
        "20:2 n-6 c,c": 672, 
        "20:3 undifferentiated": 689, 
        "20:3 n-3": 852, 
        "20:3 n-6": 853, 
        "20:4 undifferentiated": 620, 
        "20:4 n-6": 855, 
        "20:5 n-3 (EPA)": 629, 
        "21:5": 857, 
        "22:4": 858, 
        "22:5 n-3 (DPA)": 631, 
        "22:6 n-3 (DHA)": 621, 

        "Fatty acids, total trans": 605, 
        "Fatty acids, total trans-monoenoic": 693, 
        "Fatty acids, total trans-polyenoic": 695, 

    },

    "Protein & Amino Acids": {
        "Protein": 203, 
        "Adjusted Protein": 257,
        "Tryptophan": 501, 
        "Threonine": 502, 
        "Isoleucine": 503, 
        "Leucine": 504, 
        "Lysine": 505, 
        "Methionine": 506, 
        "Cystine": 507, 
        "Phenylalanine": 508, 
        "Tyrosine": 509, 
        "Valine": 510, 
        "Arginine": 511, 
        "Histidine": 512, 
        "Alanine": 513, 
        "Aspartic acid": 514, 
        "Glutamic acid": 515, 
        "Glycine": 516, 
        "Proline": 517, 
        "Serine": 518, 
        "Hydroxyproline": 521, 

    },

    "Vitamins": {
        "Vitamin A, IU": 318, 
        "Vitamin A, RAE": 320,
        "Retinol": 319, 
        "Carotene, beta": 321, 
        "Carotene, alpha": 322, 
        "Cryptoxanthin, beta": 334, 
        "Vitamin A, IU": 318, 
        "Lycopene": 337, 
        "Lutein + Zeaxanthin": 338, 

        "Vitamin C, total ascorbic acid": 401, 

        "Vitamin D(D2 + D3)": 328, 
        "Vitamin D2 (ergocalciforol)": 325, 
        "Vitamin D3(cholecalciferol)": 326, 
        "Vitamin D": 324, 

        "Vitamin E(alpha-tocopherol)": 323, 

        "Vitamin E, added": 573, 
        "Tocopherol, beta": 341, 
        "Tocopherol, gamma": 342, 
        "Tocopherol, delta": 343, 
        "Tocotrienol, alpha": 344, 
        "Tocotrienol, beta": 345, 
        "Tocotrienol, gamma": 346, 
        "Tocotrienol, delta": 347, 

        "Vitamin K (phylloquinone)": 430, 
        "Dihydrophylloquinone": 429, 
        "Menaquinone-4": 428, 
        "Vitamin B1(Thiamin)": 404, 
        "Vitamin B2(Riboflavin)": 405, 
        "Vitamin B3(Niacin)": 406, 
        "Vitamin B5(Pantothenic Acid)": 410,
        "Vitamin B-6(Pyridoxine)": 415, 
        "Folate, total": 417, 
        "Folic acid": 431, 
        "Folate, food": 432,
        "Folate, DFE": 435,


        "Vitamin B-12(Cobalamin)": 418, 
        "Vitamin B-12(Cobalamin), added": 578, 
        

        "Choline, total": 421, 
        "Betaine": 435, 


    },

    "Minerals": {
        "Calcium, Ca": 301, 
        "Iron, Fe": 303, 
        "Magnesium, Mg": 304, 
        "Phosphorus, P": 305, 
        "Potassium, K": 306, 
        "Sodium, Na": 307, 
        "Zinc, Zn": 309, 
        "Copper, Cu": 312, 
        "Manganese, Mn": 315, 
        "Selenium, Se": 317,  
        "Flouride, F": 313, 

    },

    "Sterols": {
        "Cholesterol": 601,         
        "Phytosterols": 636, 
        "Stigmasterol": 638, 
        "Campesterol": 639, 
        "Beta-sitosterol" : 641, 


    },

    
    "Other": {
        "Water": 255, 
        "Alcohol, ethyl": 221, 
        "Caffeine": 262,
        "Theobromine": 263,
        "Ash": 207,
    }
}

food_groups_dictionary = {
    "Dairy and Egg Products": 100, 
    "Spices and Herbs": 200, 
    "Baby Foods": 300, 
    "Fats and Oils": 400, 
    "Poultry Products": 0500, 
    "Soups, Sauces, and Gravies": 600, 
    "Sausages and Luncheon Meats": 700, 
    "Breakfast Cereals": 800, 
    "Fruit and Fruit Juices": 900, 
    "Pork Products": 1000, 
    "Vegetables and Vegetable Products": 1100, 
    "Nut and Seed Products": 1200, 
    "Beef Products": 1300, 
    "Beverages": 1400, 
    "Finfish and Shellfish Products": 1500, 
    "Legumes and Legume Products": 1600, 
    "Lamb, Veal, and Game Products": 1700, 
    "Baked Products": 1800, 
    "Sweets": 1900, 
    "Cereal Grains and Pasta": 2000, 
    "Fast Foods": 2100, 
    "Meals, Entrees, and Side Dishes": 2200, 
    "Snacks": 2500, 
    "American Indian/Alaska Native Foods": 3500, 
    "Restaurant Foods": 3600,
}
    


@app.route('/')
@app.route('/index')
def index():
    user = { 'nickname': 'Linda' } # fake user
    return render_template("index.html",
        title = 'Home',
        user = user)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = ProfileForm(request.form)
    if request.method == 'POST' and form.validate():
        #need to set up salalchemy and reset the redirect to a
        #different url_fo()
        return redirect(url_for('profile'))
    return render_template('profile.html', form=form)

#when user goes to local host:  the function executes.
@app.route('/food_log', methods=['GET','POST'])
def food_log():
    user = session.query(User).filter_by(email="happy").first()
    if request.method == 'POST':
        # list comprehension: transforms previous lists iinto a new list n python
        #numbers = [int(x) for x in request.form.getlist('number')]
        #we add multiple foods into the form
        foods = request.form.getlist('food')
        quantities = request.form.getlist('quantity')
        # To get the food log belonging to the existing user, we need to see if it 
        # exists by querying the database/FoodLog Class
        # FoodLog class 

        #this is a single food log
        food_log = session.query(FoodLog).filter_by(user=user).first()
        if food_log is None:
            food_log = FoodLog()

            #user attribute of the FoodLog Class is the user currently logged in.
            food_log.user = user
            session.add(food_log)

        for food_name, food_quantity in zip(foods, quantities):
            food = session.query(FoodDescription).filter(
                FoodDescription.Long_Desc.ilike('%{}%'.format(food_name))).first()
            if food is None:
                print 'The item %s you enterred is not a proper food. Please try again.' % food_name
                continue
            print food.Long_Desc
            
            association = Association()
            #quantity is an attribute of a class
            association.quantity = float(food_quantity)
            #the association will contain one food and one food_log
            association.food = food 
            food_log.foods.append(association)
            #else:
                #to our food_log, we want to get the list of foods and add the desired food to the food_log.
                #food_log.foods.append(food)

        session.commit()
        

        
        # add query for finding food in database called Food. 
        # I want to see if the food exists in the database called Food.
        # Give error if food is not in database.
        # Give affirmation for finding food in database.
        # will need to rexamine relationships in models.py
        # refer to sqlalchemy tutorial

        #after adding the requests, want to take a look at the FoodLog class
        return redirect(url_for('food_log'))

    # put code querying for food groups
    
    food_groups_list = session.query(FoodGroupDescription).all()
    # Now send food group into the template. 
    


    #we are dealing with one food_log at a time    
    food_log = session.query(FoodLog).filter_by(user=user).first()
    print food_log
    if food_log is None:
        food_log = FoodLog()

        #user attribute of the FoodLog Class is the user currently logged in.
        food_log.user = user
        session.add(food_log)

    
    # The food_log contains a list of associations between foods and quantities.
    food_nutrient_list = []
    for association in food_log.foods:
        nutrients = session.query(NutrientData).filter_by(
            NDB_No=association.food.NDB_No).all()
        #print nutrients
        # next allows us to get a single value or raise an error.
        food_log_dictionary = {}
        
        values_nutrient_dictionary = {}
        for nutrient_category_name in food_nutrient_dictionary:

            #print "NUTRIENT_CATEGORY NAME!!!", nutrient_category_name
            nutrient_category = food_nutrient_dictionary[nutrient_category_name]
            #print "NUTRIENT_CATEGORY!!!", nutrient_category

            values_nutrient_category = values_nutrient_dictionary[nutrient_category_name] = {}
                
            #print "VALUES_NUTRIENT_CATEGORY!!!", values_nutrient_category

            for nutrient_name in nutrient_category:
                
                nutrient_number = nutrient_category[nutrient_name]

                try:
                
                    nutrient_value = next(x.Nutr_Val for x in nutrients if int(x.Nutr_No) == 
                        nutrient_number)
                    values_nutrient_category[nutrient_name] = float(nutrient_value) * association.quantity

                    #print nutrient_name, nutrient_category[nutrient_name], nutrient_value
                except StopIteration:
                    pass
    
        food_nutrient_list.append({
            "name": association.food.Long_Desc, 
            "nutrients": values_nutrient_dictionary,
            })
        
    

    return render_template(
        'food_log.html', 
        food_nutrient_list=food_nutrient_list, 
        food_groups_list=food_groups_list,
        )
    


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    #form = LoginForm()
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
    #if form.validate_on_submit():

        #flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        #need to set up sqlalchemy
        #user = User(form.username.data, form.email.data,
                    #form.password.data)
        #need to set up sqlalchemy
        #session.add(user)
        #flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@lm.user_loader
def load_user(id):  
    return User.query.get(int(id))()

@app.route('/queries/<query_string>.json', methods=['GET'])
def query(query_string):
    #FdGrp_Cd=str(1100)
    #food = session.query\
        #(FoodDescription).join(FoodGroupDescription, FoodDescription.FdGrp_Cd==FoodGroupDescription.FdGrp_Cd)
    #food_groups = session.query(FoodGroupDescription).filter(FoodGroupDescription.FdGrp_Desc.ilike('%{Vegetables and Vegetable Products}%')).all()
    #print food_groups
    #foods = session.query(FoodDescription).filter(FoodDescription.Long_Desc.ilike('%{}%'.format(query_string))).all()
    food_list = []
    # construct a list of all the groups that we want to use as filters.
    group_filters = [(FoodDescription.FdGrp_Cd == group) for group in request.args.getlist("group")]
    # query the data base for foods that have the right names.
    #loop for the foods and return them one at a time.
    for food_group, food in session.query(FoodGroupDescription, FoodDescription).\
        filter(FoodDescription.Long_Desc.ilike('%{}%'.format(query_string))).\
        filter(or_(*group_filters)).all():
        #filter(FoodGroupDescription.FdGrp_Cd==FoodDescription.FdGrp_Cd).all():
        
   
        # add food description to the food_list
        food_list.append({"value": food.Long_Desc})
        # send the food_list back as json.
    return json.dumps(food_list)
        #filter(FoodDescription.FdGrp_Cd==1100).all():
    #     print '--', food_groups, foods
    #     for food in foods:
    #         food_dictionary = {"value": food.Long_Desc}
    #         food_list.append(food_dictionary)
    # print 'string', food_list
    # return json.dumps(food_list)


#{% for food_group in food_groups_list %} 
#       <option value ="{{food_group}}">{{ food_group.FdGrp_Desc }}</option>
    
@app.route('/test')
def query_test():
    print request.args.getlist('group')
    return ""
