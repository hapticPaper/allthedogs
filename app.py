import requests, os
import pandas as pd
from flask import Flask, render_template, send_from_directory


app=Flask(__name__)
SESS = requests.session()
app.secret_key='shutupthisisasecretkeydonttellanyonewhatitis'

BREEDS=[]
def loadBreeds():
    global BREEDS
    BREEDS = pd.read_csv('dogs.csv')

def saveImage(content, file):
    with open(file, 'wb') as ouf:
        ouf.write(content)
    ouf.close()

def pullImages():
    global BREEDS
    BREEDS['img']=''
    imgs=[]
    for idx, breed in BREEDS.iterrows():
        try:
            resp = SESS.get(f"https://api.thedogapi.com/v1/images/search?breed_id={idx+1}").json()
            imgs.append(resp[0]['url'])
            #saveImage(SESS.get(resp[0]['url']).content, os.path.join('images',f'{idx+1}.jpg'))

        except Exception as e:
            print(e, resp)
            imgs.append("")

    BREEDS['img']=imgs
    BREEDS.to_csv('dogs.csv')

def pullDogs():
    global BREEDS
    dogs = requests.get('https://api.thedogapi.com/v1/breeds').json()
    breedDf = pd.DataFrame(dogs)
    breedDf.to_csv('dogs.csv')
    BREEDS = breedDf

def breedPage(page=0):
    return BREEDS.iloc[0+(page*25):((page+1)*25)]

@app.route('/images/<id>')
def sendImage(id):
    return send_from_directory('images', f"{id}.jpg")

@app.route('/breeds/<page>')
def breeds(page):
    breeds = breedPage(page)
    return render_template('index.html', breeds=breeds)

@app.route('/')
def home():
    breeds = breedPage(0)
    breeds=breeds[['id','name','bred_for','breed_group','temperament','img' ]]
    return render_template('index.html', breeds=list(breeds.values))


if __name__=='__main__':
    #pullDogs()
    loadBreeds()
    #pullImages()
    app.run(debug=True)