from distutils.log import debug
from flask import Flask, render_template, flash, request,redirect,session,Response,url_for
from flask_sqlalchemy import SQLAlchemy
from extensions import db,login_manager
from model import User,Manager
from flask_login import login_required
from werkzeug.utils import secure_filename
from datetime import datetime
import cv2 ,csv
import face_recognition
import urllib.parse
import os 
import numpy as np



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
            now = datetime.now()
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

    @login_required
    @app.route('/punchout',methods=['GET','POST'])
    def punchout():
        email=session['user']
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        found = False
        with open('attendance_2-2023.csv', 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
            for row in data:
                if row[0] == email :
                    found = True
                    if row[1] == '':
                        row[1] = current_time
                    else:
                        row[1] = current_time
                    break
            if not found:
                return redirect('/punchin')
        with open('attendance_2-2023.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        return redirect("/index")
            

    @login_required
    @app.route('/video')
    def video():
        """Video streaming home page."""
        return render_template('video.html')


    def gen():
        IMAGE_FILES = []
        filename = []
        dir_path = app.config['UPLOAD_FOLDER']
        print(dir_path)

        for imagess in os.listdir(dir_path):
            img_path = os.path.join(dir_path, imagess)
            img_path = face_recognition.load_image_file(img_path)  # reading image and append to list
            IMAGE_FILES.append(img_path)
            filename.append(imagess.split(".", 1)[0])

        def encoding_img(IMAGE_FILES):
            encodeList = []
            for img in IMAGE_FILES:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            return encodeList

        def takeAttendence(name):
            with open('attendence.csv', 'r+') as f:
                name = filename[matchindex].upper()

                mypeople_list = f.readlines()
                nameList = []
                for line in mypeople_list:
                    entry = line.split(',')
                    nameList.append(entry[0])
                if name not in nameList:
                    now = datetime.now()
                    datestring = now.strftime('%H:%M:%S')
                    f.writelines(f'\n{name},{datestring}')

        encodeListknown = encoding_img(IMAGE_FILES)
        # print(len('sucesses'))

        cap = cv2.VideoCapture(0)

        while True:
            success, img = cap.read()
            imgc = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            # converting image to RGB from BGR
            imgc = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            fasescurrent = face_recognition.face_locations(imgc)
            encode_fasescurrent = face_recognition.face_encodings(imgc, fasescurrent)

            # faceloc- one by one it grab one face location from fasescurrent
            # than encodeFace grab encoding from encode_fasescurrent
            # we want them all in same loop so we are using zip
            for encodeFace, faceloc in zip(encode_fasescurrent, fasescurrent):
                matches_face = face_recognition.compare_faces(encodeListknown, encodeFace)
                face_distence = face_recognition.face_distance(encodeListknown, encodeFace)
                # print(face_distence)
                # finding minimum distence index that will return best match
                matchindex = np.argmin(face_distence)

                if matches_face[matchindex]:
                    name = filename[matchindex].upper()
                    # print(name)
                    y1, x2, y2, x1 = faceloc
                    # multiply locations by 4 because we above we reduced our webcam input image by 0.25
                    # y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 0, 0), 2, cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    takeAttendence(name)  # taking name for attendence function above

            # cv2.imshow("campare", img)
            # cv2.waitKey(0)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            key = cv2.waitKey(20)
            if key == 27:
                break

    @login_required           
    @app.route('/video_feed')
    def video_feed():
        """Video streaming route. Put this in the src attribute of an img tag."""
       
        return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

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

