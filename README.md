# How to launch the program
Follow the following steps: 

* Make sure that you are using python3, and have a virtual environment running python3. 

* in order to create a virtual environment, type in the following command: `virtualenv (yourvirtualenvname)`

* use the following command to access your virtual environment: `source (yourvirtualenvname)/bin/activate`

* install the requirements.txt by running this command: `pip install -r requirements.txt`, this will install all module
you need in order to run your application.

* Make sure that you have a postgres server installed in your machine and create a database called `electric_db`
click on the link to download postgres: [download_postgres](https://postgresapp.com/downloads.html)

* in the following link, you will see how to install postgres: 
[postgres_installation](http://www.postgresqltutorial.com/install-postgresql/)

* in order to create the database, go to your postgres command prompt and type in the following command:
`CREATE DATABASE electric_db`, or just type `createdb electric_db` in your project command prompt this will create the database in your postgres server.

* In the terminal, in the ecommerce folder type the following command:
`python manage.py migrate`, and type `python manage.py runserver` to launch your application, then start development
server at `http://127.0.0.1:8000/` in your browser.

* in order to have access to the administration of the application, you should create a super user, to do that
type in the following command: `python manage.py createsuperuser`, then you will be prompted to enter a username and 
password.

* project need redis to be able to work properly, make sure redis is installed and run the following command: `redis-server`