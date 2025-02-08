"""
This module creates a cli application for common tasks like
* manipulating the database
* rendering html pages
* reloading the app
* querying the forro-app
"""

import click

from forro_festivals.app import build_app
from forro_festivals.scripts.cli_utils import validate_event_ids
from forro_festivals.scripts.create_festivals_html import create_festivals_html
from forro_festivals.scripts.create_legal_notice_html import create_legal_notice_html
from forro_festivals.scripts.db_api import get_user
from forro_festivals.scripts.passwords import hash_password
from forro_festivals.scripts.render_html_pages import render_html_pages
from forro_festivals.scripts.reload_app import reload_app_by_touch
from forro_festivals.scripts.update_db_with_forro_app import update_db_with_forro_app
from forro_festivals.scripts.initialise import initialise
from forro_festivals.scripts.user import User
from forro_festivals.scripts import db_api

@click.group()
def ff():
    """Main entry point for Forro-Festivals."""
    pass

##############
# DEV SERVER #
##############
@ff.command()
def run():
    """Starts app locally."""
    build_app().run(debug=True)

#######
# APP #
#######
@click.group()
def app():
    """General purpose commands."""

@app.command()
def init():
    """Install some required input files for the app."""
    if click.confirm(text='This deletes existing database, if confirmed. Go on?', default=False):
        initialise()
    else:
        click.echo("cancelled.")

@app.command()
def reload():
    """Reloads the app on python-anywhere."""
    reload_app_by_touch()

@app.command()
def query_forro_app_update_db():
    """Queries festival data from forro-app.com and saves it into the database"""
    update_db_with_forro_app()


############
# DATABASE #
############
@click.group()
def db():
    """Database related commands."""
    pass

@db.command()
@click.option('--ids', required=True, type=str, callback=validate_event_ids, help='ID(s) of the record to delete. Example: "1,5,10-19,30"')
def delete(ids):
    """Delete record(s) from the database."""
    db_api.delete_events_by_ids(ids)

@db.command()
def backup():
    """Create a backup of the database."""
    db_api.backup_db()

@db.command()
@click.option('--delete', is_flag=True)
def init(delete):
    """Deletes database (if exists) and creates it fresh."""
    db_api.init_db(delete)

@db.command()
def show():
    """Prints all entries in the database."""
    for event in db_api.get_events_from_db():
        print(event)

#########
# USERS #
#########
@click.group()
def users():
    """Database related commands."""
    pass

@users.command()
@click.option('--id', required=True)
@click.option('--password', required=True)
@click.option('--permissions', required=True)
def create(id, password, permissions):
    """Creates a user."""
    user = User(
        id=id,
        permissions=permissions,
        hashed_pw=hash_password(password),
    )
    db_api.insert_user(user)

@users.command()
@click.option('--id', required=True)
@click.option('--permissions', required=True, default=None)
def update(id, permissions):
    """Updates permissions."""
    user = get_user(id)
    if not user:
        click.echo(f"User {id} does not exist")

    user = User(id=id, hashed_pw=user.hashed_pw, permissions=permissions)
    db_api.update_user(user)


@users.command()
def show():
    """Prints all users."""
    for user in db_api.get_users():
        print(f'{user.id} {user.permission_set}')

@users.command()
@click.option('--id', required=True)
def delete(id):
    """Deletes a user by id."""
    db_api.delete_user(id)


########
# HTML #
########
@click.group()
def html():
    """Render HTML pages."""

@html.command()
def legal_notice():
    """Renders the legal-notice.html ('Impressum') from its template"""
    create_legal_notice_html()

@html.command()
def festivals():
    """Renders the festivals.html from its template and the db"""
    create_festivals_html()

@html.command()
def all():
    """Recreates all static html pages"""
    render_html_pages()


ff.add_command(app)
ff.add_command(db)
ff.add_command(html)
ff.add_command(users)

if __name__ == '__main__':
    ff()
