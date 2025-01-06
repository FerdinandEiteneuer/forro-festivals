"""
This module creates a cli application for common tasks like
* manipulating the database
* rendering html pages
* reloading the app
* querying the forro-app
"""

import click

from forro_festivals.scripts.cli_utils import validate_event_ids
from forro_festivals.scripts.create_festivals_html import create_festivals_html
from forro_festivals.scripts.create_impressum_html import create_impressum_html
from forro_festivals.scripts.render_html_pages import render_html_pages
from forro_festivals.scripts.db import backup_db, delete_events_by_ids, init_db
from forro_festivals.scripts.reload_app import reload_app_by_touch
from forro_festivals.scripts.update_db_with_forro_app import update_db_with_forro_app


@click.group()
def ff():
    """Main entry point for Forro-Festivals."""
    pass

@ff.command()
def reload_app():
    """Reloads the app."""
    reload_app_by_touch()

@ff.command()
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
    delete_events_by_ids(ids)

@db.command()
def backup():
    """Create a backup of the database."""
    backup_db

@db.command()
def init():
    """Deletes database (if exists) and creates it fresh"""
    init_db()

########
# HTML #
########
@click.group()
def html():
    """Render HTML pages."""

@html.command()
def impressum():
    """Renders the impressum.html from its template"""
    create_impressum_html()

@html.command()
def festivals():
    """Renders the festivals.html from its template and the db"""
    create_festivals_html()

@html.command()
def all():
    """Recreates all static html pages"""
    render_html_pages()


ff.add_command(db)
ff.add_command(html)

if __name__ == '__main__':
    ff()
