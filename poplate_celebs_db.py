# Abeja Test 201505 by Terrell Broomer
import requests
from bs4 import BeautifulSoup
import re
import json
import copy
import sqlite3

def percentage(part, whole):
  return 100 * float(part)/float(whole)

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

#Format the Celebrity dict into json so we can push it into SQLITE nicely
def formatCelebs(celeb_data):
  return json.dumps(celeb_data)

#Create the celebs DB and table
def createCelebsDB(sqlite_file,sqlite_table_name):
  print "=> Creating required SQLite DB and table!"
  sleep(1)
  conn = sqlite3.connect(sqlite_file)
  c = conn.cursor()

  query = 'CREATE TABLE %s (name text primary key,born text,desc text,thumb text,path text);' % (sqlite_table_name)
  print query
  c.execute(query)
  conn.commit()
  conn.close()

#Populate celebs table with celebrities data
def insertCelebs(celeb_json,sqlite_file,sqlite_table_name):
  print "=> inserting Celebs into table"
  sleep(1)
  # Connecting to the database file
  conn = sqlite3.connect(sqlite_file)
  c = conn.cursor()

  jdata = json.loads(celeb_json)

  for celeb,data in jdata.iteritems():
    columns = ', '.join(data.keys())
    placeholders = ''+'\",\"'.join(data.values())
    query = 'INSERT INTO %s (name, %s) VALUES (\"%s\",\"%s\");' % (sqlite_table_name,columns,celeb,placeholders)
    print query
    c.execute(query, data)
    conn.commit()

  conn.close()

#Build an index based on the populated celebs table
def indexCelebs(sqlite_file,sqlite_table_name):
  print "Create Unique Index on celebs table"
  sleep(1)
  sqlite_index_name = 'celebs_index'
  sqlite_column_name = 'name'

  # Connecting to the database file
  conn = sqlite3.connect(sqlite_file)
  c = conn.cursor()

  query = 'CREATE UNIQUE INDEX %s ON %s(%s);' % (sqlite_index_name,sqlite_table_name,sqlite_column_name)
  print query
  c.execute(query)
  conn.commit()
  conn.close()

########
# Main #
########
baseurl = "http://www.posh24.com"
parsed_html = getAllCelebs(baseurl)
celeb_dict = parseCelebsPath(parsed_html)
celeb_data = copy.deepcopy(celeb_dict)
count=0

for celeb in celeb_dict:
  celeb_total = len(celeb_data)
  try:
    count +=1
    percent_complete = 100.0 * count / celeb_total
    print "%s [%d/%d] %.2f%%" % (celeb,count,celeb_total,percent_complete)
    celeb_html = getCeleb(celeb)
    celeb_parsed = parseCeleb(celeb,celeb_html)
  except AttributeError:
    celeb_data.pop(celeb, None) #Not a Celebrity, removing from dictionary
    count -=1

celeb_json = formatCelebs(celeb_data)

# Store celebrity data in SQlite
try:
  sqlite_file = 'celebs2.sqlite'
  sqlite_table_name = 'celebs'
  createCelebsDB(sqlite_file,sqlite_table_name)
except sqlite3.OperationalError:
  insertCelebs(celeb_json,sqlite_file,sqlite_table_name)
  indexCelebs(sqlite_file,sqlite_table_name)
