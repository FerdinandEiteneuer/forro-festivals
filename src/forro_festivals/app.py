from flask import Flask

from forro_festivals.config import APP_SECRET_KEY
from forro_festivals.routes import blueprints, auth


def build_app():
    app = Flask(__name__)
    app.secret_key = APP_SECRET_KEY

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    auth.login_manager.init_app(app)
    return app

app = build_app()


if __name__ == '__main__':
    app.run(debug=True)
