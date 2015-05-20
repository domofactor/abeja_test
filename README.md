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
This is a python script that pulls down a list of celebrities along with their various info such as Name,Birthplace, Description and an image. The image is uploaded to the [abeja_test_celebrities](https://s3.amazonaws.com/abeja_test_celebrities) S3 bucket and all celebrity data is stored into an SQLite database.

##How do I run it?
simply run ```python abeja_test/celebs.py```

##TODO
* Convert from one single python script to smaller pieces as part of a python module
* Add a logger class/function to give the user better information about what's going on
* Write tests using pytest or nose
* Fix parsing age from celebrity html page. There seems to be some wierdness with parsing sub divs in beautifulsoup.
* Improve performance(it takes roughly about 120min to fully populate the DB)
* Write a RESTful service to pull data from SQlite based on a given name.
