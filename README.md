# forro-festivals.com

Providing an updated Forró Festival list at [www.forro-festivals.com](https://www.forro-festivals.com).

More Information in this README coming soon. Once I have pinned down the architecture I
will explain it here :-).


# Local development

Install the package in your virtualenv
```
pip install -e .
```

Before starting the app, we need to initialize some required files.

```bash
ff app init
```

This 
* initialized the database for the festivals
* created some user that can access the admin dashboard and 
* created a file with personal data for the legal-notice that I did not needlessly wanted on github

Start the server via
```bash
APP_SECRET_KEY='123' CONSOLE_LOG='True' python src/forro_festivals/app.py
```

View the app at `localhost:5000`
