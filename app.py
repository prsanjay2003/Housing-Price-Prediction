from flask import Flask, request, render_template, jsonify
from flask_cors import cross_origin
from flask import Flask, render_template,request,flash,redirect,url_for,session
import sqlite3

import PricePrediction as tm

app = Flask(__name__)
app.secret_key="123"

con=sqlite3.connect("database.db")
con.execute("create table if not exists customer(pid integer primary key,name text,address text,contact integer,mail text)")
con.close()

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        name=request.form['name']
        password=request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from customer where name=? and mail=?",(name,password))
        data=cur.fetchone()

        if data:
            session["name"]=data["name"]
            session["mail"]=data["mail"]
            return redirect("dashboard")
        else:
            flash("Username and Password Mismatch","danger")
    return redirect(url_for("index"))
@app.route('/dashboard',methods=["GET","POST"])
def dashboard():
    return render_template("dashboard.html")

@app.route('/studentname', methods=["GET","POST"])
def studentname():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customer')
    data = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    conn.close()
    return render_template('studentdetails.html', column_names=column_names, data=data)

@app.route('/student',methods=["POST"])
def student():
    return render_template("index.html")

@app.route('/admin',methods=["POST"])
def admin():
    return render_template("register.html")

@app.route('/home',methods=["POST"])
def home3():
    return render_template("home.html")

@app.route('/index',methods=["POST"])
def home4():
    return render_template("main.html")

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
            name=request.form['name']
            address=request.form['address']
            contact=request.form['contact']
            mail=request.form['mail']
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            cur.execute("insert into customer(name,address,contact,mail)values(?,?,?,?)",(name,address,contact,mail))
            con.commit()
            flash("Record Added  Successfully","success")
        except:
            flash("Error in Insert Operation","danger")
        finally:
            return redirect(url_for("index"))
            con.close()

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/get_location_names', methods=['GET'])
def get_location_names():
    response = jsonify({
        'locations': tm.get_location_names()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/get_area_names', methods=['GET'])
def get_area_names():
    response = jsonify({
        'area': tm.get_area_values()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/get_availability_names', methods=['GET'])
def get_availability_names():
    response = jsonify({
        'availability': tm.get_availability_values()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/")
@cross_origin()
def home():
    return render_template("home.html")


@app.route("/predict", methods=["GET", "POST"])
#@cross_origin()
def predict():
    if request.method == "POST":
        sqft = float(request.form['sqft'])
        bhk = int(request.form['bhk'])
        bath = int(request.form['bath'])
        loc = request.form.get('loc')
        area = request.form.get('area')
        availability = request.form.get('avail')

        prediction = round(float(tm.predict_house_price(loc, area, availability, sqft, bhk, bath)), 2)

        return render_template('home.html', prediction_text="The house price is Rs. {} lakhs".format(prediction))

    return render_template("home.html")


if __name__ == "__main__":
    tm.load_saved_attributes()
    app.run(debug = True)