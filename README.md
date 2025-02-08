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
* creates a user that can access the admin dashboard and 
* creates a file with personal data for the legal-notice (I did not needlessly wanted to check that into github)

Start the server via
```bash
ENV='dev' python src/forro_festivals/app.py
```

View the app at `localhost:5000`
