from flask import Flask, render_template, request, flash, redirect, session,url_for,abort
import requests
from models import Cocktail


from models import db, connect_db, User
from forms import UserAddForm, LoginForm,SearchForm



app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nobpa2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"
CURR_USER_KEY = "curr_user"



@app.route("/", methods=["GET", "POST"])
def home():
    """Home page"""
    search_form=SearchForm()
    
    if search_form.validate_on_submit():
        search_term=search_form.search.data
        return redirect(url_for("search_cocktails", term=search_term))
    return render_template("home.html", search_form=search_form)

@app.route("/search/<term>")
def search_cocktails(term):
    """Search cocktails based on the given term"""
    response = requests.get(f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={term}")
    data = response.json()
    cocktails = data["drinks"] if data["drinks"] else []
    processed_coctails=[]
    
    
    
    for cocktail in cocktails:
        processed_coctail = {}
        processed_coctail['id'] = cocktail['idDrink']
        processed_coctail['name'] = cocktail['strDrink']
        processed_coctail['instructions'] = cocktail['strInstructions']
        processed_coctail['image'] = cocktail['strDrinkThumb']
        processed_coctail['ingredients'] = []
        
        for i in range(1,16):
            ingredient_key = f'strIngredient{i}'
            measure_key = f'strMeasure{i}'
            
            if cocktail[ingredient_key] and cocktail[measure_key]:
                ingredient = cocktail[ingredient_key]
                measure = cocktail[measure_key]
                processed_coctail['ingredients'].append((ingredient, measure))
        
        processed_coctails.append(processed_coctail)
    
                
    return render_template("search.html", term=term, cocktails=processed_coctails)


@app.route("/random-cocktail")
def random_cocktail():
    """Get a random cocktail"""
    response = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php")
    data = response.json()
    cocktail = data["drinks"][0]
    return render_template("cocktail.html", cocktail=cocktail)



@app.route("/cocktail")
def cocktaill():
    # Logic to fetch the cocktail data, such as fetching a random cocktail
    response = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php")
    data = response.json()
    cocktail = data["drinks"][0]
    

    return render_template("cocktail.html", cocktail=cocktail) 

@app.route("/cocktail/<id>")
def cocktail(id):
    response = requests.get(f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={id}")
    data = response.json()
    cocktails = data["drinks"][0]
    processed_coctails=[]
    
    for cocktail in cocktails:
        processed_coctail = {}
        processed_coctail['id'] = cocktail['idDrink']
        processed_coctail['name'] = cocktail['strDrink']
        processed_coctail['instructions'] = cocktail['strInstructions']
        processed_coctail['image'] = cocktail['strDrinkThumb']
        processed_coctail['ingredients'] = []
        
        for i in range(1,16):
            ingredient_key = f'strIngredient{i}'
            measure_key = f'strMeasure{i}'
            
            if cocktail[ingredient_key] and cocktail[measure_key]:
                ingredient = cocktail[ingredient_key]
                measure = cocktail[measure_key]
                processed_coctail['ingredients'].append((ingredient, measure))
        
        processed_coctails.append(processed_coctail)

    return render_template("cocktail.html", cocktail=processed_coctail) 

   








































@app.route("/login", methods=["GET", "POST"])
def login_user():
    """User login handling"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session[CURR_USER_KEY] = user.id
            return redirect("/")
        else:
            form.username.errors = ["Invalid Username/Passwords"]

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register_user():
    """User register handling"""
    form = UserAddForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User.register(username, password, first_name, last_name)
        db.session.add(user)
        db.session.commit()
        session[CURR_USER_KEY] = user.id
        flash("User Created", "success")
        return redirect("/")
    else:
        return render_template("register.html", form=form)


@app.route("/logout")
def logout():
    session.pop(CURR_USER_KEY)
    flash("You have logged out successfully", "success")
    return redirect("/")
