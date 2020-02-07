import pymysql
import sys
from app import app
from db_config import mysql
from flask import flash, session, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib


@app.route('/')
def index():
    if 'email' in session:
        username = session['email']

        return "<h2>HOME PAGE</h2>"'<strong>Logged in as ' + username + '</strong><br>' + \
               "<b><a href = '/logout'>click here to logout</a></b>" + \
               "<p><form action='/run' method='POST'><input type='submit' value='Run Program'></form></p>"

    return redirect('/login')


@app.route('/run', methods=['GET', 'POST'])
def foo():
    import mysql.connector
    from mysql.connector import Error
    def main():
        import numpy as np
        import cv2
        import imutils
        import sys
        import pytesseract
        import pandas as pd
        import time
        import cv2
        import glob
        with open("/home/mahrukh/output.txt", "w") as f:
            f.write("")
        camera = cv2.VideoCapture(0)
        i = 0
        while i < 1:
            return_value, image = camera.read()
            cv2.imwrite('/home/mahrukh/images/img' + str(i) + '.png', image)
            i += 1
            # del(camera)
            #Add this line to assert the path. Else TesseractNotFoundError will be raised.
            #Read the original image.
          #  img = cv2.imread("/home/mustufa/Downloads/immm/car2.jpg")
            path = "/home/mahrukh/images/*.*"
            for file in glob.glob(path):
                print(file)
                img = cv2.imread(file)
                #   print(img)
                # %%%%%%%%%%%%%%%%%%%%%
                # conversion numpy array into rgb image to show
                c = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
             #   cv2.imshow('Color image', c)
                # wait for 1 second
                k = cv2.waitKey(1000)
                # destroy the window
                cv2.destroyAllWindows()
                #Using imutils to resize the image.
                img = imutils.resize(img, width=500)
               # cv2.imshow("Original Image", img)  #Show the original image
                cv2.waitKey(0)
                #Convert from colored to Grayscale.
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                #cv2.imshow("Preprocess 1 - Grayscale Conversion", gray_img)        #Show modification.
                cv2.waitKey(0)
                #Applying Bilateral Filter on the grayscale image.
                '''Bilateral Filter : A bilateral filter is a non-linear, edge-preserving,
                and noise-reducing smoothing filter for images.
                It replaces the intensity of each pixel with a weighted average of intensity values from nearby pixels.'''
                #It will remove noise while preserving the edges. So, the number plate remains distinct.
                gray_img = cv2.bilateralFilter(gray_img, 11, 17, 17)
                #cv2.imshow("Preprocess 2 - Bilateral Filter", gray_img)    #Showing the preprocessed image.
                cv2.waitKey(0)
                '''Canny Edge detector : The Process of Canny edge detection algorithm can be broken down to 5 different steps:
                1. Apply Gaussian filter to smooth the image in order to remove the noise
                2. Find the intensity gradients of the image
                3. Apply non-maximum suppression to get rid of spurious response to edge detection
                4. Apply double threshold to determine potential edges
                5. Track edge by hysteresis: Finalize the detection of edges by suppressing all the other edges that are weak and not connected to strong edges.'''
                #Finding edges of the grayscale image.
                c_edge = cv2.Canny(gray_img, 170, 200)
                #cv2.imshow("Preprocess 3 - Canny Edges", c_edge)        #Showing the preprocessed image.
                cv2.waitKey(0)
                #Finding contours based on edges detected.
                cnt, new = cv2.findContours(c_edge, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                #Storing the top 30 edges based on priority
                cnt = sorted(cnt, key = cv2.contourArea, reverse = True)[:30]
                NumberPlateCount = None
                im2 = img.copy()
                cv2.drawContours(im2, cnt, -1, (0,255,0), 3)
                #cv2.imshow("Top 30 Contours", im2)          #Show the top 30 contours.
                cv2.waitKey(0)
                count = 0
                for c in cnt:
                    perimeter = cv2.arcLength(c, True)      #Getting perimeter of each contour
                    approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
                    if len(approx) == 4:            #Selecting the contour with 4 corners/sides.
                        NumberPlateCount = approx
                        break
                '''A picture can be stored as a numpy array. Thus to mask the unwanted portions of the
                picture, we simply convert it to a zeros array.'''
                #Masking all other parts, other than the number plate.
                masked = np.zeros(gray_img.shape,np.uint8)
                new_image = cv2.drawContours(masked,[NumberPlateCount],0,255,-1)
                new_image = cv2.bitwise_and(img,img,mask=masked)
                #cv2.imshow("4 - Final_Image",new_image)     #The final image showing only the number plate.
                cv2.waitKey(0)
                #Configuration for tesseract
                configr = ('-l eng --oem 1 --psm 3')
                #Running Tesseract-OCR on final image.
                text_no = pytesseract.image_to_string(new_image, config=configr)
                #The extracted data is stored in a data file.
             #   data = {'Date': [time.asctime(time.localtime(time.time()))],
              #      'Vehicle_number': [text_no]}
             #   df = pd.DataFrame(data, columns = ['Date', 'Vehicle_number'])
             #   df.to_csv('Dataset_VehicleNo.csv')
              #  print(text_no)
                #Printing the recognized text as output.
                if not text_no:
                    return redirect('/')
                with open("/home/mahrukh/output.txt", "a") as f:
                    print(text_no, file=f)
                    cv2.waitKey(0)
        try:
            connection = mysql.connector.connect(host='localhost',
                                                 database='flask_login',
                                                 user='root',
                                                 password='Root@123')
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                mySql_insert_query = """LOAD DATA LOCAL INFILE '/home/mahrukh/output.txt' INTO TABLE car_info(plate_number); """
                cursor = connection.cursor()
                cursor.execute(mySql_insert_query)
                connection.commit()
                print(cursor.rowcount, "Record inserted successfully into license_plate table")
                cursor.close()
        except Error as e:
            print("error jbcjb", e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")
    if __name__ == '__main__':
        main()
    return redirect('/')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/submit', methods=['POST'])
def login_submit():
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    # validate the received values
    if _email and _password:
        # check user exists
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT * FROM tbl_user WHERE user_email=%s"
        sql_where = (_email,)
        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        if row:
            test = hashlib.md5()
            test.update(_password.encode('utf-8'))
            if (test.hexdigest() == row[3]):
                session['email'] = row[1]
                cursor.close()
                conn.close()
                return redirect('/')
            # if check_password_hash(row[3], _password.decode('utf-8')):
            #     session['email'] = row[1]
            #     cursor.close()
            #     conn.close()
            #     return redirect('/')
            else:
                flash('Invalid password!')
                return redirect('/login')
        else:
            flash('Invalid email/password!')
            return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')


if __name__ == "__main__":
    app.run(port=5001)

