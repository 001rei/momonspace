import os
import pymysql
import re
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, database, split_list, readable_list, toString, lookup, lookup_gym

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


if not os.getenv("API_KEY_RECIPE"):
    raise RuntimeError("API_KEY not set")
elif not os.getenv("API_ID_RECIPE"):
    raise RuntimeError("API_ID not set")


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Dictionary buat nanti hit ke API

dietlabels = {
    "balanced": "Balanced",
    "high-fiber": "High Fiber",
    "high-protein": "High Protein",
    "low-carb": "Low Carb",
    "low-fat": "Low Fat",
    "low-sodium": "Low Sodium",
}

healthlabels = {
    "pescatarian": "Pescatarian",
    "shellfish-free": "Shellfish-Free",
    "alcohol-free": "Alcohol-Free",
    "celery-free": "Celery-Free",
    "soy-free": "Soy-Free",
    "sugar-free": "Sugar-Free",
    "pork-free": "Pork-Free",
    "red-meat-free": "Red-Meat-Free",
    "sesame-free": "Sesame-Free",
    "sulfite-free": "Sulfite-Free",
    "tree-nut-free": "Tree-Nut-Free",
    "vegan": "Vegan",
    "sugar-conscious": "Sugar-Conscious",
    "vegetarian": "Vegetarian",
    "wheat-free": "Wheat-Free",
    "alcohol-cocktail": "Alcohol-Cocktail",
    "crustacean-free": "Crustacean-Free",
    "dairy-free": "Dairy-Free",
    "lupine-free": "Lupine-Free",
    "mediterranean": "Mediterranean",
    "dash": "DASH",
    "kidney-friendly": "Kidney-Friendly",
    "egg-free": "Egg-Free",
    "fish-free": "Fish-Free",
    "fodmap-free": "FODMAP-Free",
    "gluten-free": "Gluten-Free",
    "mollusk-free": "Mollusk-Free",
    "peanut-free": "Peanut-Free",
    "immuno-supportive": "Immuno-Supportive",
    "keto-friendly": "Keto-Friendly",
    "low-sugar": "Low-Sugar",
    "mustard-free": "Mustard-Free",
    "kosher": "Kosher",
    "low-potassium": "Low-Potassium",
    "no-oil-added": "No oil added",
    "paleo": "Paleo",
}

cuisinetype = {
    "chinese": "Chinese",
    "eastern europe": "Eastern Europe",
    "british": "British",
    "caribbean": "Caribbean",
    "asian": "Asian",
    "central europe": "Central Europe",
    "american": "American",
    "french": "French",
    "kosher": "Kosher",
    "indian": "Indian",
    "korean": "Korean",
    "italian": "Italian",
    "greek": "Greek",
    "japanese": "Japanese",
    "mediterranean": "Mediterranean",
    "south east asian": "South East Asian",
    "mexican": "Mexican",
    "south american": "South American",
    "world": "World",
    "nordic": "Nordic",
    "middle eastern": "Middle Eastern",
}

dishtype = {
    "starter": "Starter",
    "main course": "Main Course",
    "side dish": "Side Dish",
    "drinks": "Drinks",
    "desserts": "Desserts",
    'alcohol cocktail': 'Alcohol Cocktail',
    'biscuits and cookies': 'Biscuit and Cookies',
    'bread': 'Bread',
    'cereals': 'Cereals',
    'condiments and sauces': 'Condiments and Sauces',
    'desserts': 'Desserts',
    'drinks': 'Drinks',
    'egg': 'Egg',
    'ice cream and custard': 'Ice Cream and Custard',
    'main course': 'Main Course',
    'pancake': 'Pancake',
    'pasta': 'Pasta',
    'pastry': 'Pastry',
    'pies and tarts': 'Pies and Tarts',
    'pizza': 'Pizza',
    'preps': 'Preps',
    'preserve': 'Preserve',
    'salad': 'Salad',
    'sandwiches': 'Sandwiches',
    'seafood': 'Seafood',
    'side dish': 'Side Dish',
    'soup': 'Soup',
    'special occasions': 'Special Occasions',
    'starter': 'Starter',
    'sweets': 'Sweets'
}


# Route

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/home')
@login_required
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():

    session.clear()
    
    if request.method == "GET":
        return render_template("login.html")
    else:

        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not username or not password:
            message = "Please enter a valid password and username!"
            return render_template("login.html", message=message)
        

        try:
            connect, cursor = database()

            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            rows = cursor.fetchall()

            if len(rows) != 1:
                message = "Invalid username or password."
                return render_template("login.html", message=message)

            validate_password = check_password_hash(rows[0]["hash"], password)

            if not validate_password:
                message = "Invalid username or password."
                return render_template("login.html", message=message)

            session["user_id"] = rows[0]["id"]
            cursor.close()
            connect.close()

            return redirect("/home")
        except Exception as e:

            print("DB error:", str(e))
            message = "Error occurred while processing your request. Please try again later."
            return render_template("login.html", message=message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == "GET":
        return render_template("register.html")
    else:

        name = request.form.get("name").strip()
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        confirmation = request.form.get("confirmation").strip()

        if not name or not username or not password or not confirmation:
            message = "Please complete the form!"
            return render_template("register.html", message=message)
        
        if len(name) < 2:
            message = "Name should be a minimum of three characters!"
            return render_template("register.html", message=message)
        
        if len(username) < 4 or not re.match("^[a-zA-Z0-9]+$", username):
            message = "Username should be a minimum of four alphanumeric (A-z, 0-9) characters!"
            return render_template("register.html", message=message)
        
        if len(password) < 8:
                message = "Password should be a minimum of eight characters!"
                return render_template("register.html", message=message)
        
        if password != confirmation:
            message = "Your password does not match."
            return render_template("register.html", message=message)
        
        hashed_pass = generate_password_hash(password, method="pbkdf2", salt_length=16)

        try:
            connect, cursor = database()
            cursor.execute("INSERT INTO users (name, username, hash) VALUES (%s, %s, %s)", (name, username, hashed_pass))
            connect.commit()

            user_id = cursor.lastrowid
            session["user_id"] = user_id

            return redirect("/home")

        except pymysql.IntegrityError as e:
            message = "Username already exists."
            return render_template("register.html", message=message)
        
        except Exception as e:
            message = f"Error : {str(e)}"
            return render_template("register.html", message=message)
        
        finally:
            cursor.close()
            connect.close()

@app.route('/intake-tracker', methods=['GET', 'POST'])
@login_required
def intake_tracker():
    if request.method == "GET":
        return render_template("intake_track.html")
    
    else:
        foodName = request.form.get("foodName").strip()
        quantityFood = request.form.get("quantityFood")
        calories = request.form.get("calories")
        protein = request.form.get("protein")
        carbs = request.form.get("carbs")
        fats = request.form.get("fats")
        mealTime = request.form.get("mealTime")

        connect, cursor = database()
        cursor.execute("INSERT INTO food_intake (user_id, food_name, quantity_food, calories, protein, carbohydrates, fats, meal_time) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)", 
                       (
                           session["user_id"],
                           foodName,
                           quantityFood,
                           calories,
                           protein,
                           carbs,
                           fats,
                           mealTime,
                       ))
        connect.commit()
        connect.close()
        cursor.close()

        return redirect("/intake-history")
    
@app.route('/intake-history', methods=['GET', 'POST'])
@login_required
def intake_history():
    if request.method == "GET":
        connect, cursor = database()
        cursor.execute("SELECT * FROM food_intake WHERE user_id = %s ORDER BY food_date DESC", (session["user_id"]))
        datas = cursor.fetchall()
        cursor.close()
        connect.close()

        return render_template("intake_history.html", datas=datas)
    
@app.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete(entry_id):
    
    connect, cursor = database()
    cursor.execute("DELETE FROM food_intake WHERE user_id = %s AND id = %s",
                   (
                        session["user_id"],
                        entry_id
                   ))
    connect.commit()
    cursor.close()
    connect.close()

    return redirect("/intake-history")

@app.route('/recipe', methods=['GET', 'POST'])
@login_required
def recipe():

    if request.method == "GET":

        connect, cursor = database()
        cursor.execute("SELECT name FROM users WHERE id = %s", (session["user_id"]))

        data = cursor.fetchall()
        name = data[0]["name"]
        cursor.close()
        connect.close()

        health_labels = split_list(healthlabels, 3)
        cuisine_type = split_list(cuisinetype, 3)
        dish_type = split_list(dishtype, 3)

        return render_template("recipe.html", 
                               name=name,
                               dishtype = dish_type,
                               dietlabels = dietlabels,
                               healthlabels = health_labels,
                               cuisinetype = cuisine_type,
                               dishtype_length = len(dish_type),
                               healthlabels_length = len(health_labels),
                               cuisinetype_length = len(cuisine_type)
                               )
    

@app.route('/result')
@login_required
def result():
    
    get_ingredients_list = request.args.getlist("ingredients")
    ingredients_list = [i.lower().strip() for i in (filter(None, get_ingredients_list))]

    readable_ingredients = readable_list(ingredients_list) # untuk title di result

    ingredients = str(",".join(ingredients_list)) # untuk param api

    dietLabels = toString("dietLabels", "&diet=")
    dishType = toString("dishType", "&dishType=")
    healthLabels = toString("healthLabels", "&health=")
    cuisineType = toString("cuisineType", "&cuisineType=")

    # gabung semua parameter
    param = "".join(ingredients + dietLabels[1] + dishType[1] + healthLabels[1] + cuisineType[1])

    recipes_list = lookup(param)

    conect, cursor = database()
    cursor.execute("SELECT link FROM bookmarks WHERE user_id = %s",
        (session["user_id"],)
    )
    saved_recipes_link = cursor.fetchall()
    cursor.close()
    conect.close()


    return render_template("result.html",
            readable_ingredients=readable_ingredients,
            recipes_list=recipes_list,
            dish_list=dishType[0],
            diet_list=dietLabels[0],
            health_list=healthLabels[0],
            cuisine_list=cuisineType[0],
            saved_recipes_link=saved_recipes_link,
            dishtype=dishtype,
            )

@app.route('/result-gym')
async def result_gym():

    if request.args.get("bodygroup"):
        param = request.args.get("bodygroup")
        method = "bodyPart"
        gym_list = await lookup_gym(param, method)

        return render_template("result_gym.html", gym_list = gym_list, bodygroup_name = param, method = method)

    if request.args.get("nameExcercises"):
        param = request.args.get("nameExcercises").strip()
        print(param)
        method = "name"
        gym_list = await lookup_gym(param, method)

        return render_template("result_gym.html", gym_list = gym_list, excercises_name = param, method = method)



@app.route('/guide')
@login_required
def guide():
    return render_template("guide.html")

@app.route('/weightcheck')
@login_required
def weightcheck():
    return render_template("weight-status.html")

@app.route('/calorieneeds')
def calorieneeds():
    return render_template("calorie_needs.html")

@app.route('/progress', methods=['GET', 'POST'])
@login_required
def progress():
    if request.method == "GET":

        connect, cursor = database()
        cursor.execute("SELECT name FROM users WHERE id = %s", (session["user_id"]))
        row = cursor.fetchall()
        name = row[0]["name"]

        cursor.execute("SELECT * FROM progress WHERE user_id = %s ORDER BY date DESC", (session["user_id"]))
        datas = cursor.fetchall()

        cursor.execute("SELECT * FROM set_intake WHERE user_id = %s AND date = (SELECT MAX(date) FROM set_intake)", (session["user_id"]))
        row = cursor.fetchall()
        if row:
            calories = row[0]["calories"]
        else:
            calories = 0

        cursor.execute("SELECT SUM(calories) AS sum FROM food_intake WHERE user_id = %s AND DATE(food_date) = CURRENT_DATE", (session["user_id"]))
        row = cursor.fetchone()
        sum = row["sum"] if row and "sum" in row else 0

        cursor.close()
        connect.close()

        return render_template('progress.html', name = name, datas = datas, calories = calories, sum_calories = sum)
    
    else:
        sessionTypes = request.form.getlist('sessionType')
        sessionTypeString = ','.join(sessionTypes) if sessionTypes else None
        sessionDuration = request.form.get('sessionDuration')

        connect, cursor = database()
        cursor.execute("INSERT INTO progress (user_id, sessionType, sessionDuration) VALUES (%s, %s, %s)",(
                            session["user_id"],
                            sessionTypeString,
                            sessionDuration
                        ))
        
        connect.commit()
        connect.close()
        cursor.close()

        return "Success"
    
@app.route('/set-intake', methods=['POST'])
def set_intake():
    program = request.form.get("program")
    connect, cursor = database()
    cursor.execute("INSERT INTO set_intake (user_id, calories) VALUES (%s, %s)",(session["user_id"], program))

    connect.commit()
    cursor.close()
    connect.close()

    return "success"
    
@app.route('/gym-guide', methods=['GET', 'POST'])
def gym_guide():
    if request.method == "GET":
        return render_template("gym_guide.html")
        
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():

    connect, cursor = database()
    cursor.execute("SELECT name, username,hash FROM users WHERE id = %s", (session["user_id"]))
    row = cursor.fetchall()

    currentName = row[0]["name"]
    currentUsername = row[0]["username"]

    active_tab = "name"
    
    if request.method == "GET":
        return render_template("settings.html", name=currentName, username=currentUsername, active_tab=active_tab)
    
    else:
        name = request.form.get("change_name").strip()
        if name:
            active_tab = "name"
            if len(name) < 2:
                message1 = "Name should be a minimum of three characters!"
                return render_template("settings.html", message1=message1, name=currentName , username=currentUsername, active_tab=active_tab)

            try:
                cursor.execute("UPDATE users SET name = %s WHERE id = %s", (name, session["user_id"]))
                connect.commit()

                currentName = name

                message1 = "Name has succesfully changed!"
                
                return render_template("settings.html", message1=message1, name=currentName , username=currentUsername, active_tab=active_tab)
            
            except Exception as e:
                message1 = f"Error : {str(e)}"
                return render_template("settings.html", message1=message1, name=currentName , username=currentUsername, active_tab=active_tab)
         
        username = request.form.get("change_username")
        if username:
            active_tab = "username"
            if len(username) < 4 or not re.match("^[a-zA-Z0-9]+$", username):
                message2 = "Username should be a minimum of four alphanumeric (A-z, 0-9) characters!"
                return render_template("settings.html", message2=message2, name=currentName , username=currentUsername, active_tab=active_tab)

            try:
                cursor.execute("UPDATE users SET username = %s WHERE id = %s", (username, session["user_id"]))
                connect.commit()

                currentUsername = username

                message2 = "Username has succesfully changed!"
                
                return render_template("settings.html", message2=message2, name=currentName , username=currentUsername, active_tab=active_tab)
            
            except pymysql.IntegrityError as e:
                message2 = "Username already exists."
                return render_template("settings.html", message2=message2, name=currentName , username=currentUsername, active_tab=active_tab)
            
            except Exception as e:
                message2 = f"Error : {str(e)}"
                return render_template("settings.html", message2=message2, name=currentName , username=currentUsername, active_tab=active_tab)
            
        current_password = request.form.get("old_pass")
        new_password = request.form.get("new_pass")
        confirmation = request.form.get("confirmation")

        hashed_new_pass = generate_password_hash(new_password, method="pbkdf2", salt_length=16)

        if current_password and new_password and confirmation:
            active_tab = "password"
            if len(new_password) < 8:
                message3 = "Password should be a minimum of eight characters!"
                return render_template("settings.html", message3=message3, name=currentName , username=currentUsername, active_tab=active_tab)
            
            if not check_password_hash(row[0]["hash"], current_password):
                message3 = "Current password is incorrect!"
                return render_template("settings.html", message3=message3, name=currentName , username=currentUsername, active_tab=active_tab)
            
            if not check_password_hash(hashed_new_pass, confirmation):
                message3 = "New password and confirmation password does not match!"
                return render_template("settings.html", message3=message3, name=currentName , username=currentUsername, active_tab=active_tab)
            
            try:
                cursor.execute("UPDATE users SET hash = %s WHERE id = %s", (hashed_new_pass, session["user_id"]))
                connect.commit()

                message3 = "Password Succesfully Changed!"
                return render_template("settings.html", message3=message3, name=currentName , username=currentUsername, active_tab=active_tab)
            except Exception as e:
                message3 = f"Error : {str(e)}"
                return render_template("settings.html", message3=message3, name=currentName , username=currentUsername, active_tab=active_tab)
            
        connect.close()
        return redirect("/home")

            
@app.route('/bookmarks')
@login_required
def bookmarks():

    connect, cursor = database()
    cursor.execute("SELECT * FROM bookmarks WHERE user_id = %s", (session["user_id"]))
    data = cursor.fetchall()
    cursor.close()
    connect.close()

    return render_template("bookmarks.html", bookmarks=data, dishtype=dishtype)

@app.route('/add', methods=['POST'])
@login_required
def add():
    
     # String
    link = request.form.get("link")
    label = request.form.get("label")
    image = request.form.get("image")
    source = request.form.get("source")
    url = request.form.get("url")
    calories = request.form.get("calories")
    totalTime = request.form.get("totalTime")

    # List
    dishType = request.form.get("dishType").strip("[]").strip(",")
    dietLabels = request.form.get("dietLabels").strip("[]").strip(",")
    healthLabels = request.form.get("healthLabels").strip("[]").strip(",")
    cuisineType = request.form.get("cuisineType").strip("[]").strip(",")
    ingredientLines = request.form.get("ingredientLines").strip("[]")


    connect, cursor = database()
    cursor.execute("INSERT INTO bookmarks (user_id, link, label, image, source, url, calories, totaltime, dishtype, dietlabels, healthlabels, cuisinetype, ingredientlines) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                   (session["user_id"],
                    link,
                    label,
                    image,
                    source,
                    url,
                    calories,
                    totalTime,
                    dishType,
                    dietLabels,
                    healthLabels,
                    cuisineType,
                    ingredientLines)
                )
    connect.commit()
    connect.close()
    cursor.close()

    return redirect("/bookmarks")

@app.route('/remove', methods=['POST'])
@login_required
def remove():
    
    link = request.form.get("link")

    connect, cursor = database()
    cursor.execute("DELETE FROM bookmarks WHERE user_id = %s AND link = %s",
                   (session["user_id"], link)
                   )
    connect.commit()
    cursor.close()
    connect.close()

    return redirect("/bookmarks")

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)