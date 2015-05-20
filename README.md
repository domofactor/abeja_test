#Abeja Test

##System Requirements
* Python 2.7
* Boto Config(/etc/boto.cfg)
* Python Package Manager(pip)

##Python Package Requirements
These can be installed via ```sudo pip install <pkg>```

* beautifulsoup4
* boto
* sqlite3

##What does it do?
This is a python script that pulls down a list of celebrities along with their various info such as Name,Birthplace, Description and a Thumbnail image. The celebrity thumbnail is uploaded to the ```abeja_test_celebrities``` S3 bucket and all celebrity data is stored into an SQLite database.

thumbnail images are also uploaded to the ```abeja_test_celebrities``` S3 bucket.

##How do I run it?
simply run ```python celebs.py```

##TODO
* Fix parsing age from celebrity html page. There seems to be some wierdness with parsing sub divs in beautifulsoup.
* Improve performance(it takes roughly 30min to run)
* Write a RESTful service to pull data from SQlite based on a given name.
