try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import argparse
import cv2
import os
import re
import io
import json
import ftfy
import numpy as np
import flask
import time
from flask import Flask,jsonify

app=Flask(__name__)

@app.route('/check_blur')
def check_blur():
     return flask.render_template('index.html')


@app.route('/blur',methods=['POST'])
def blur_img():
    print("Checking blur...")
    data={}
    img1 = flask.request.files['im']
    img1.save(img1.filename)
    img=cv2.imread('./' + img1.filename)
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    if laplacian_var < 50:
           result="Blurry"
           data['Uid']=""
    else:
           result="Not Blurry"
           data=ocr(img)

    return flask.render_template('index.html',laplacian=result,p=data['Uid'])
           
           
    

@app.route('/extract')
def ocr(img):
     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
     gray = cv2.threshold(gray, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
     print("Trying to extract...")
     filename = "{}.png".format(os.getpid())
     cv2.imwrite(filename, gray)
     text = pytesseract.image_to_string(Image.open(filename), lang = 'eng')
     os.remove(filename)
     
     text_output = open('outputbase.txt', 'w', encoding='utf-8')
     text_output.write(text)
     text_output.close()

     file = open('outputbase.txt', 'r', encoding='utf-8')
     text = file.read()

     text = ftfy.fix_text(text)
     text = ftfy.fix_encoding(text)
     name = None
     fname = None
     dob = None
     pan = None
     gender = None
     genderStr = '(Female|Male|emale|male|ale|FEMALE|MALE|EMALE)$'
     yearline = []
     genline = []
     nameline = []
     panline = []
     text0 = []
     text1 = []
     text2 = []

     lines = text.split('\n')
     for lin in lines:
         s = lin.strip()
         s = lin.replace('\n','')
         s = s.rstrip()
         s = s.lstrip()
         text1.append(s)

     text1 = list(filter(None, text1))

     lineno = 0  

     for wordline in text1:
         xx = wordline.split('\n')
         if ([w for w in xx if re.search('(INCOMETAXDEPARWENT @|mcommx|INCOME|TAX|GOW|GOVT|GOVERNMENT|OVERNMENT|VERNMENT|DEPARTMENT|EPARTMENT|PARTMENT|ARTMENT|INDIA|NDIA)$', w)]):
             text1 = list(text1)
             lineno = text1.index(wordline)
             break

     text0 = text1[lineno+1:]


     def findword(textlist, wordstring):
         lineno = -1
         for wordline in textlist:
             xx = wordline.split( )
             if ([w for w in xx if re.search(wordstring, w)]):
                 lineno = textlist.index(wordline)
                 textlist = textlist[lineno+1:]
                 return textlist
         return textlist

    


     try:

    
         name = text0[0]
         name = name.rstrip()
         name = name.lstrip()
         name = name.replace("8", "B")
         name = name.replace("0", "D")
         name = name.replace("6", "G")
         name = name.replace("1", "I")
         name = re.sub('[^a-zA-Z] +', ' ', name)

    
         fname = text0[1]
         fname = fname.rstrip()
         fname = fname.lstrip()
         fname = fname.replace("8", "S")
         fname = fname.replace("0", "O")
         fname = fname.replace("6", "G")
         fname = fname.replace("1", "I")
         fname = fname.replace("\"", "A")
         fname = re.sub('[^a-zA-Z] +', ' ', fname)

    
         

         text0 = findword(text1, '(Pormanam|Number|umber|Account|ccount|count|Permanent|ermanent|manent|wumm)$')
         panline = text0[0]
         pan = panline.rstrip()
         pan = pan.lstrip()
         pan = pan.replace(" ", "")
         pan = pan.replace("\"", "")
         pan = pan.replace(")", "J")
         pan = pan.replace(";", "")
         pan = pan.replace("%", "L")

     except:
         pass
     lines = text

     for wordlist in lines.split('\n'):
        xx = wordlist.split()
        if [w for w in xx if re.search('(Year|Birth|irth|YoB|YOB:|DOB:|DOB)$', w)]:
            yearline = wordlist
            break
        else:
            text1.append(wordlist)
     try:
         text2 = text.split(yearline, 1)[1]
     except Exception:
        pass

     try:
        yearline = re.split('Year|Birth|irth|YoB|YOB:|DOB:|DOB', yearline)[1:]
        yearline = ''.join(str(e) for e in yearline).year
        if yearline:
            ayear = dparser.parse(yearline, fuzzy=True)
        dob = ayear
        dob = dob.rstrip()
        dob = dob.lstrip()
        dob = dob.replace('l', '/')
        dob = dob.replace('L', '/')
        dob = dob.replace('I', '/')
        dob = dob.replace('i', '/')
        dob = dob.replace('|', '/')
        dob = dob.replace('\"', '/1')
        dob = dob.replace(" ", "")
     except Exception:
        pass
    # Searching for Gender
     try:
        for wordlist in lines.split('\n'):
            xx = wordlist.split()
            if [w for w in xx if re.search(genderStr, w)]:
                enline = wordlist
                break

        if 'Female' in genline or 'FEMALE' in genline:
            gender = "Female"
        if 'Male' in genline or 'MALE' in genline:
            gender = "Male"

        text2 = text.split(genline, 1)[1]
     except Exception:
        pass

     # Searching for UID
     uid = set()
     try:
        newlist = []
        for xx in text2.split('\n'):
            newlist.append(xx)
        newlist = list(filter(lambda x: len(x) > 12, newlist))
        for no in newlist:
            print(no)
            if re.match("^[0-9 ]+$", no):
                uid.add(no)

     except Exception:
         pass
     data = {}
     data['Name'] = name
     
     if not list(uid) :
         data['Uid']= pan
     else:
         data['Uid'] = list(uid)[0]
     
     print(data)

     return data
     


if __name__ == "__main__":
    app.run()
