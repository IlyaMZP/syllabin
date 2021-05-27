# syllabin
Student managment system <br />
This was a part of my course project at university. Written in a couple of weeks with a lot of breaks. Don't expect to see quality code.

# Setup
Clone the project <br />
`git clone https://github.com/IlyaMZP/syllabin.git --recurse-submodules`

Install required libraries either in virtual environment or as user <br />
`pip install -r requirements.txt --user`

Change parameters in `syllabin/settings.py` <br />
Initialize the database by running <br />
`flask init`

Now you can run the server <br />
`flask run`

Login won't work unless you either disable `SESSION_COOKIE_SECURE` or proxy the server with HTTPS.
