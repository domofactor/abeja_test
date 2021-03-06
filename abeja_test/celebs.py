# Abeja Test 201505 by Terrell Broomer
import requests
from bs4 import BeautifulSoup
import re
import json
import copy
import sqlite3
import StringIO
import boto
import os

#Pull down html page with celebrities a-z
def getAllCelebs(baseurl):
  r = requests.get(baseurl + "/celebrities/a_to_z")
  html = r.text
  parsed_html= BeautifulSoup(html)
  return parsed_html

#Parse the main html page with all celebrities and return a dict of celebrities  
def parseCelebsPath(parsed_html):
  celeb_dict = {}
  celebs = parsed_html.body.find_all('div', attrs={'class':'col-xs-6 col-md-4'})

  for celeb in celebs:
    celeb_link = celeb.find_all('a')
    for link in celeb_link:
      name = link.text
      path = link.get('href')
      celeb_dict[name] = {}
      celeb_dict[name]['path'] = path
  return celeb_dict

#Pull down the celebrity's html page
def getCeleb(celeb):
  celeb_path = celeb_dict[celeb]['path']
  r = requests.get(baseurl + celeb_path)
  html = r.text
  celeb_html = BeautifulSoup(html)
  return celeb_html

#parse the celebrity's html page
def parseCeleb(celeb,celeb_html):
  celeb_thumb = celeb_html.find('img')['src']
  celeb_data[celeb]['thumb'] = celeb_thumb.strip('\n\t')

  celeb_desc = celeb_html.find('div', attrs={'class':'info x-readmore'}).text
  celeb_data[celeb]['desc'] = celeb_desc.strip('\n\t').replace('"', "'") #the replace here in important as it prevents us from getting info quotation problems

  celeb_born = celeb_html.find('div', attrs={'class':'attributeTitle birth','class':'attributeContent'}).text
  celeb_data[celeb]['born'] = celeb_born.strip(' \n\t')

  #Beautiful Soup doesn't seem to parse sub divs very well....FIX LATER
  #celeb_age = int(celeb_html.find('div', attrs={'class':'attributeTitle age','class':'attributeContent'}).text)
  #celeb_dict[celeb]['age'] = celeb_age

  return celeb_data[celeb]

def CelebThumbToS3(celeb):
  bucket_name = 'abeja_test_celebrities'
  
  #Save URL of Thumbnail to a StringIO instead of saving to disk
  thumb_url = celeb_data[celeb]['thumb']
  key_name = celeb_data[celeb]['path'].replace("/","") + '.jpg'
  r = requests.get(thumb_url)
  thumb_img = StringIO.StringIO(r.content)

  #Connect to S3
  conn = boto.connect_s3() 

  #Grab the Bucket we want to use
  try:
    bucket = conn.get_bucket(bucket_name)
  except boto.exception.S3ResponseError:
    conn.create_bucket(bucket_name)

  #Upload thumbnail to S3 and return public url
  key = boto.s3.key.Key(bucket)
  key.name = key_name
  key.set_contents_from_string(thumb_img.getvalue(), headers={"Content-Type": "image/jpeg"})
  key.make_public()
  url = key.generate_url(expires_in=0, query_auth=False)
  return url

#Format the Celebrity dict into json so we can push it into SQLITE nicely
def formatCeleb(celeb_data,celeb):
  data = celeb_data[celeb]
  jdata = json.dumps(data)
  return jdata

#Create the celebs DB and table
def createCelebsDB(sqlite_file,sqlite_table_name):
  conn = sqlite3.connect(sqlite_file)
  c = conn.cursor()
  query = 'CREATE TABLE %s (name text primary key,born text,desc text,thumb text,path text,s3_path text);' % (sqlite_table_name)
  c.execute(query)
  conn.commit()
  conn.close()

#Populate celebs table with celebrities data
def insertCelebs(celeb_json,celeb,sqlite_file,sqlite_table_name):
  conn = sqlite3.connect(sqlite_file)
  c = conn.cursor()
  jdata = json.loads(celeb_json)
  columns = ', '.join(jdata.keys())
  data = ''+'\",\"'.join(jdata.values())
  query = 'INSERT INTO %s (name, %s) VALUES (\"%s\",\"%s\");' % (sqlite_table_name,columns,celeb,data)
  c.execute(query)
  conn.commit()
  conn.close()

def cleanupCelebs(celeb,sqlite_file,sqlite_table_name):
  sqlite_column_name = 'name'
  conn = sqlite3.connect(sqlite_file)
  c = conn.cursor()
  query = 'DELETE FROM %s WHERE %s = \"%s\";' % (sqlite_table_name,sqlite_column_name,celeb)
  c.execute(query)
  conn.commit()
  conn.close()

#Build an index based on the populated celebs table
def indexCelebs(sqlite_file,sqlite_table_name):
  sqlite_index_name = 'celebs_index'
  sqlite_column_name = 'name'
  conn = sqlite3.connect(sqlite_file)
  c = conn.cursor()
  query = 'CREATE UNIQUE INDEX %s ON %s(%s);' % (sqlite_index_name,sqlite_table_name,sqlite_column_name)
  c.execute(query)
  conn.commit()
  conn.close()

########
# Main #
########
#Lets populate some common vars
baseurl = "http://www.posh24.com"
cwd = os.getcwd()
sqlite_file = cwd + '/celebs.sqlite'
sqlite_table_name = 'celebs'

#Parse page with list of celebs and generate a dict of names and paths
parsed_html = getAllCelebs(baseurl)
celeb_dict = parseCelebsPath(parsed_html)

#make a copy of the celeb dict so we can modify it while iterating through the original
celeb_data = copy.deepcopy(celeb_dict)

#Iterate over each celebrity
count=0

for celeb in celeb_dict:
  #Grab an overall total so we can display progress
  celeb_total = len(celeb_data)

  try:
    #Counter and display progress to the user
    count +=1
    percent_complete = 100.0 * count / celeb_total
    print "%s [%d/%d] %.2f%%" % (celeb,count,celeb_total,percent_complete)

    #Begin parsing for celeb data
    celeb_html = getCeleb(celeb)
    celeb_parsed = parseCeleb(celeb,celeb_html)

    #Upload thumbnail image to s3
    s3_path = CelebThumbToS3(celeb)
    celeb_data[celeb]['s3_path'] = s3_path

    #Format the celeb data into json so we can work with it nicely
    celeb_json = formatCeleb(celeb_data,celeb)

    #Insert celeb data into SQLite DB
    createCelebsDB(sqlite_file,sqlite_table_name)
    insertCelebs(celeb_json,celeb,sqlite_file,sqlite_table_name)

  #There's several pages that are in fact not celebrities, so lets remove those from the celebs dictionary
  except AttributeError:
    celeb_data.pop(celeb, None) #Not a Celebrity, removing from dictionary
    count -=1
  #Do some cleanup on the celebrities row if SQlite barfs due to a row already existing(no duplicates allowed due to the name column being a primary key)
  except sqlite3.OperationalError:
    cleanupCelebs(celeb,sqlite_file,sqlite_table_name)
    insertCelebs(celeb_json,celeb,sqlite_file,sqlite_table_name)

#Once all celebs have been parsed and uploaded, create a unique index on the DB for better search performance
indexCelebs(sqlite_file,sqlite_table_name)
