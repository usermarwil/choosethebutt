import random
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Custom Jinja filter to find intersection of lists
@app.template_filter('intersection')
def filter_intersection(list1, list2):
    return set(list1).intersection(set(list2))

# Liste der Essensoptionen
food_options = ["Pizza", "Sushi", "Burger", "Pasta", "Reis", "Indisch", "Thai", "Gebratene Nudeln", "Salat", "Curry", "Kebab"]

# Datenbank initialisieren
def init_db():
    conn = sqlite3.connect('food_choices.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS choices (
                    user_id TEXT,
                    food TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    # Reset results if both have submitted
    if request.args.get('reset') == 'true':
        conn = sqlite3.connect('food_choices.db')
        c = conn.cursor()
        c.execute('DELETE FROM choices')
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    # Handle form submission
    if request.method == "POST":
        user_id = request.form.get("user_id", "1")
        foods = request.form.getlist("food")
        
        conn = sqlite3.connect('food_choices.db')
        c = conn.cursor()
        c.execute('DELETE FROM choices WHERE user_id = ?', (user_id,))
        for food in foods:
            c.execute('INSERT INTO choices (user_id, food) VALUES (?, ?)', (user_id, food))
        conn.commit()
        conn.close()
    
    # Check if both users have made choices
    result = None
    user1_choices = get_user_choices("1")
    user2_choices = get_user_choices("2")
    
    if user1_choices and user2_choices:
        # Find common choices
        common_choices = set(user1_choices).intersection(set(user2_choices))
        
        if common_choices:
            result = f"Ihr habt übereinstimmende Essensoptionen gefunden: {', '.join(common_choices)}! Guten Appetit! 🍽️"
        else:
            # Suggest a random choice from either user's selections
            all_choices = user1_choices + user2_choices
            suggested_food = random.choice(all_choices)
            result = f"Keine Übereinstimmung! Zufälliger Vorschlag: {suggested_food}?"
    
    return render_template("index.html", 
                          food_options=food_options, 
                          result=result, 
                          user1_choices=user1_choices, 
                          user2_choices=user2_choices)

@app.route("/random_choice", methods=["POST"])
def random_choice():
    user1_choices = get_user_choices("1")
    user2_choices = get_user_choices("2")
    
    if user1_choices and user2_choices:
        all_choices = user1_choices + user2_choices
        suggested_food = random.choice(all_choices)
        result = f"Zufällige Auswahl: {suggested_food}! Guten Appetit! 🍽️"
        return render_template("index.html", 
                              food_options=food_options, 
                              result=result, 
                              user1_choices=user1_choices, 
                              user2_choices=user2_choices)
    
    return redirect(url_for('index'))

@app.route("/user/<user_id>")
def user_view(user_id):
    current_choices = get_user_choices(user_id)
    return render_template("user.html", user_id=user_id, food_options=food_options, current_choices=current_choices)

def get_user_choices(user_id):
    conn = sqlite3.connect('food_choices.db')
    c = conn.cursor()
    c.execute('SELECT food FROM choices WHERE user_id = ?', (user_id,))
    choices = [row[0] for row in c.fetchall()]
    conn.close()
    return choices

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)