# the outbound module dictates an API that interacts with a front end service 
# this api desginates endpoints for interacting with the database to pull report data through

# contains code that implements the user interface


import json

from flask import Flask

app = Flask(__name__)

@app.route('/users')
def get_users():
    users = [
        {
            'name':'exampleUser',
            'display_name': 'Jane Doe',
            'email': 'user@example.com'
        }
    ]
    return json.dumps(users)


if __name__ == '__main__':
    app.run()

