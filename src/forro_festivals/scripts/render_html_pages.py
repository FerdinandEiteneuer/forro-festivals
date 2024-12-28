"""
This module is responsible for creating the 'impressum' and the 'festivals' pages.

# Note: Instead of using this, I can call both scripts in the reload-all.sh script.
        Keeping this functionality here, the update mechanisms don't need to be touched
        when changing the content.
"""

from forro_festivals.scripts.create_festivals_html import create_festivals_html
from forro_festivals.scripts.create_impressum_html import create_impressum_html

def render_html_pages():
    # impressum.html
    create_impressum_html()

    # festivals.html
    create_festivals_html()


if __name__ == '__main__':
    render_html_pages()
