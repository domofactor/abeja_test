# Abeja Test 201505 by Terrell Broomer
import requests
from bs4 import BeautifulSoup
import copy

baseurl = "http://www.posh24.com"

def getAllCelebs(baseurl):
  r = requests.get(baseurl + "/celebrities/a_to_z")
  html = r.text
  parsed_html= BeautifulSoup(html)
  return parsed_html
  
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

def getCeleb(celeb):
  celeb_path = celeb_dict[celeb]['path']
  r = requests.get(baseurl + celeb_path)
  html = r.text
  celeb_html = BeautifulSoup(html)
  return celeb_html

def parseCeleb(celeb,celeb_html):
  import re

  celeb_thumb = celeb_html.find('img')['src']
  celeb_dict[celeb]['thumb'] = celeb_thumb.strip('\n\t')

  celeb_desc = celeb_html.find('div', attrs={'class':'info x-readmore'}).text
  celeb_dict[celeb]['desc'] = celeb_desc.strip('\n\t')

  celeb_born = celeb_html.find('div', attrs={'class':'attributeTitle birth','class':'attributeContent'}).text
  celeb_dict[celeb]['born'] = celeb_born.strip(' \n\t')

  #Beautiful Soup doesn't seem to parse sub divs very well....FIX LATER
  #celeb_age = int(celeb_html.find('div', attrs={'class':'attributeTitle age','class':'attributeContent'}).text)
  #celeb_dict[celeb]['age'] = celeb_age

  return celeb_dict[celeb]

def formatCeleb(celeb_dict):
  import json
  return json.dumps(celeb_dict)

########
# Main #
########

parsed_html = getAllCelebs(baseurl)
celeb_dict = parseCelebsPath(parsed_html)


for celeb in celeb_dict:
  celeb_html = getCeleb(celeb)

  try:
    parseCeleb(celeb,celeb_html)
  except AttributeError:
    celeb_data = copy.deepcopy(celeb_dict)
    print "NOT A CELEBRITY, Removing from dictionary"
    celeb_data.pop(celeb, None)

  celeb_json = formatCeleb(celeb_data)
