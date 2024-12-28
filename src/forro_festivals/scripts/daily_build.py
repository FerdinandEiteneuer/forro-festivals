"""
This moddule is responsible for
1. querying external sourcesof forro events (forro-app.com)
2. writing them into the database
3. rendering all statically served pages
"""

from forro_festivals.scripts.render_html_pages import render_html_pages
from forro_festivals.scripts.update_db_with_forro_app import update_db_with_forro_app

def daily_build():
    update_db_with_forro_app()
    render_html_pages()

if __name__ == '__main__':
    daily_build()
