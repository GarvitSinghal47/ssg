from distutils.log import debug
from flask import Flask, render_template, flash, request,redirect,session
from flask_sqlalchemy import SQLAlchemy
from extensions import db,login_manager
from model import User,Manager
from flask_login import login_required
from werkzeug.utils import secure_filename
import datetime

import urllib.parse
import os 



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
def create_app():
    app = Flask(__name__)
    # server = 'logidb.database.windows.net'
    # database = 'logiDB'
    # username = 'login'
    # port ='1433'
    # password = '{Admin@123}'
    # driver= '{ODBC Driver 18 for SQL Server}'

    # params=urllib.parse.quote_plus('Driver='+driver+';Server=tcp:'+server+','+port+';Database='+ database +';UID='+ username +';Pwd='+password)
    # app.secret_key = "super secret key"
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc:///?odbc_connect=%s'% params
    # app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

    app.secret_key = "super secret key"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'Images')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///manager.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # db = SQLAlchemy(app)
    db.init_app(app)
    # For managing sessions during login
    login_manager.init_app(app)
    from auth import auth

    app.register_blueprint(auth)




    @login_manager.user_loader
    def load_user(user_id):
        # using the user id as primary key as id for session
        return User.query.get(int(user_id))

   
    @app.route('/')
    def homepage():
        return render_template('login.html')

    @login_required
    @app.route('/index')
    def enter():
        return render_template('index.html')

    
    @login_required
    @app.route('/upload',methods=['GET','POST'])
    def upload():

        if request.method == "POST":
                if 'file' not in request.files:
            # flash('No file part')
                    return render_template('upload.html')
                file = request.files['file']

                if file.filename == '':
            # flash('No image selected for uploading')
                    return render_template('upload.html')

                if file and allowed_file(file.filename):
                     filename = secure_filename(file.filename)
                     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # print('upload_image filename: ' + filename)
            # flash('Image successfully uploaded and displayed below')
                     return render_template('upload.html')
        else:
            # flash('Allowed image types are -> png, jpg, jpeg, gif')
            return render_template('upload.html')

    @login_required
    @app.route('/punchin',methods=['GET','POST'])
    def punchin():
            email =session["user"]
            now = datetime.datetime.now()
            month_year = f'{now.month}-{now.year}'
            filename = f'attendance_{month_year}.csv'
            
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    f.write('Name,Date Time\n')
            
            with open(filename, 'r+') as f:
                mypeople_list = f.readlines()
                nameList = []
                for line in mypeople_list:
                    entry = line.split(',')
                    nameList.append(entry[0])
                if email not in nameList:
                    datestring = now.strftime('%d-%m-%Y %H:%M:%S')
                    f.write(f'{email},{datestring}\n')        
            return render_template('punchin.html')


    # @login_required
    # @app.route('/manage', methods=['GET', 'POST'])
    # def manager() :
    #     email = session['user']
    #     alldata = Manager.query.filter_by(emailid=email).all()

    #     if request.method == "POST":
    #         website = request.form['website']
    #         email = request.form['email']
    #         password = request.form['password']

            
    #         manageinstance=Manager(website=website,emailid=email,password=password)
    #         db.session.add(manageinstance)
    #         db.session.commit()
    #         email = session['user']
    #         alldata = Manager.query.filter_by(emailid=email).all()

    #         print(website)

    #         return render_template('manager.html', data=alldata,value=1)
        
    #     else:
            
    #         return render_template('manager.html',value=1,data=alldata)

    # @login_required
    # @app.route('/delete/<int:sno>')
    # def delete(sno):
    #     todelete=Manager.query.filter_by(sno=sno).first()
    #     db.session.delete(todelete)
    #     db.session.commit()
    #     return redirect("/manage")
        

    # @login_required
    # @app.route('/update/<int:sno>', methods=['GET', 'POST'])
    # def update(sno):
    #     if request.method == "POST":
    #         website = request.form["website"]
    #         email = request.form['email']
    #         password = request.form['password']
    #         toupdate = Manager.query.filter_by(sno=sno).first()
    #         toupdate.website=website
    #         toupdate.emailid=email
    #         toupdate.password=password
            
    #         db.session.add(toupdate)
    #         db.session.commit()
    #         return redirect("/manage")


    #     toupdate = Manager.query.filter_by(sno=sno).first()
    #     return render_template('update.html',toupdate=toupdate)
    return app

if __name__ == "__main__":
    app=create_app()
    app.app_context().push()

    app.run(debug=True)

