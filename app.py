import requests, os
import pandas as pd
import numpy as np
from flask import Flask, render_template, send_from_directory
import logging
import sqlite3
from sqlite3 import Connection
from sqlite3 import Error
import queries as q




app=Flask(__name__)
SESS = requests.session()
app.secret_key='shutupthisisasecretkeydonttellanyonewhatitis'
DBFILE = os.path.join('cache','dogs.sqlite')



ll = logging

"""
SQLite
"""

class sqlDogs():
    def __init__(self, db_file=DBFILE):
        self.db_file=db_file
        self.conn = self.create_connection()



    def create_connection(self):
        """ create a database connection to a SQLite database """
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.db_file)
            print(sqlite3.version)
            return self.conn
        except Error as e:
            print(e)


    def create_table(self, create_table_sql: str) -> None:
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            resp = c.executescript(create_table_sql)
            return resp
        except Error as e:
            print(e)
            raise




    def write_dog(self, dog):
        """
        Create a new project into the projects table
        :param conn:
        :param project:
        :return: project id
        """
        
        cur = self.conn.cursor()
        #r = cur.execute()
        try:
            r = cur.execute(q.INSERT_DOG(dog))
            return cur.lastrowid
        except Exception as e:
            ll.critical(f"Couldnt write the record - {e}          {dog}")


    def loadBreeds(self):
        breeds = pd.read_csv('dogs.csv', sep="\t")
        breeds = breeds.replace(np.nan, '', regex=True)
        return breeds

    def writeDogs(self, breeds):
        for _,breed in breeds.iterrows():
            #write_dog(breeds)
            self.write_dog(",".join([f"""'{i.replace("'","")}'""" if type(i)==str else f"{i}" for i in breed.values]))
        self.conn.commit()

    def reloadDogs(self, breeds):
        d = sqlDogs()
        try: 
            resp = d.create_table(q.CREATE_DOGS)
            ll.info(f"Dog table is present - {resp}")
            
            
            try:
                resp = self.writeDogs(breeds)
                print(resp)
            except Exception as e:
                ll.critical(f"Failed to write data - {e}")
        except Exception as e:
            print(f"No table created - {e}")


def saveImage(content, file):
    with open(file, 'wb') as ouf:
        ouf.write(content)
    ouf.close()

def pullImages(breeds):
    imgs=[]
    for idx, breed in breeds.iterrows():
        try:
            resp = SESS.get(f"https://api.thedogapi.com/v1/images/search?breed_id={breed.id}").json()
            imgs.append(resp[0]['url'])
            #saveImage(SESS.get(resp[0]['url']).content, os.path.join('images',f'{idx+1}.jpg'))
            
        except Exception as e:
            print(e, resp)
            imgs.append("")

    breeds['img']=imgs
    breeds.to_csv('dogs.csv', index=False, sep="\t")

def pullDogs():
    dogs = requests.get('https://api.thedogapi.com/v1/breeds').json()
    breedDf = pd.DataFrame(dogs)
    breedDf['images']=''
    breedDf['weight']=[f"{i['imperial']} lbs" for i in breedDf['weight']]
    breedDf['height']=[f"{i['imperial']} in" for i in breedDf['height']]
    breedDf.to_csv('dogs.csv', index=False, sep="\t")
    breeds = breedDf
    return breeds

def breedPage(page=0, columns=4):
    rows = 6
    columns = columns
    total = rows*columns
    d = sqlDogs()
    conn = d.conn
    cur = conn.cursor()
    resp = cur.execute(q.DOGS)
    try:
        page = int(page)
        if page>0:
            page-=1
    except Exception as e:
        print(f"Bad page value {e}")
        page=0
    #['id','name','bred_for','breed_group','temperament','img' ]
    bdf=[d for d in resp]
    return  [bdf[0+(page*total):((page+1)*total)][i*columns:(i*columns)+columns] for i in range(0,rows)], len(bdf)

@app.route('/images/<id>')
def sendImage(id):
    return send_from_directory('images', f"{id}.jpg")

@app.route('/breeds/<page>')
def breedsPage(page):
    bl, total = breedPage(page)
    pages = [p+1 for p in range(0,int(total/24))]
    return render_template('index.html', breeds=bl, pages=pages, page=page)

@app.route('/', defaults={'page':0})
@app.route('/<page>')
def home(page):
    bl, total = breedPage(page)
    pages = [p+1 for p in range(0,int(total/24))]
    return render_template('index.html', breeds=bl, pages=pages, page=0)



if __name__ == '__main__':
    d = sqlDogs()
    breeds = d.loadBreeds()
    #breeds = pullDogs()
    #breeds = pullImages(breeds)
    #d.reloadDogs(breeds)
    app.run(debug=True)





    



    