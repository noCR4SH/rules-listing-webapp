# rules-listing-webapp

Simple webapp for generating rule reports.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Installing

Get all the necessary packages via pip:

```
pip install -r requirements.txt
```

Create .env file in the root project directory. Use this template:

```
AUTH0_CLIENT_ID=<client id>
AUTH0_DOMAIN=<tenant address>
AUTH0_CLIENT_SECRET=<client secret>
AUTH0_CALLBACK_URL=<application's callback url>
AUTH0_AUDIENCE=<leave it empty for now, might be necesarry in the future>
AUTH0_M2M_AUDIENCE=https://<tenant>.auth0.com/api/v2/
```

That's it!

## Running the app

Simply start server.py:

```
python server.py
```

Then open browser, go to: http://localhost:3000/ and log in with account that has access to the app.

## Built With

* Flask
* Bulma
* Auth0

