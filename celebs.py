# Abeja Test 201505 by Terrell Broomer
import requests
from bs4 import BeautifulSoup

baseurl = "http://www.posh24.com"

def getData(baseurl):
  r = requests.get(baseurl + "/celebrities/a_to_z")
  html = r.text
  parsed_html= BeautifulSoup(html)
  return parsed_html
  
def getCelebPath(parsed_html):
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

def getCelebData(celeb):
  celeb_path = celeb_dict[celeb]['path']
  r = requests.get(baseurl + celeb_path)
  html = r.text
  celeb_html = BeautifulSoup(html)
  return celeb_html

def parseCelebHTML(celeb,celeb_html):
  celeb_thumb = celeb_html.find('img')['src']
  celeb_dict[celeb]['thumb'] = celeb_thumb

  celeb_desc = celeb_html.find('div', attrs={'class':'info x-readmore'}).text
  celeb_dict[celeb]['desc'] = celeb_desc

  celeb_born = celeb_html.find('div', attrs={'class':'attributeTitle birth','class':'attributeContent'}).text
  celeb_dict[celeb]['born'] = celeb_born

  celeb_age_str = celeb_html.find_all('div', attrs={'class':'attributeTitle age','class':'attributeContent'})[-2].getText()
  celeb_age = int(celeb_age_str)
  celeb_dict[celeb]['age'] = celeb_age

  return celeb_dict[celeb]

def formatCelebData(celeb_dict):
  import json
  return json.dumps(celeb_dict)

########
# Main #
########

parsed_html = getData(baseurl)
celeb_dict = getCelebPath(parsed_html)


for celeb in celeb_dict:
  celeb_html = getCelebData(celeb)
  celeb_data = parseCelebHTML(celeb,celeb_html)
  celeb_json = formatCelebData(celeb_dict)
