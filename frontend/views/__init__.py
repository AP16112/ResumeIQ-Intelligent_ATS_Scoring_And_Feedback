"""Views package for single-page app architecture"""


# Imports submodules (landing.py, scorer.py, history.py, resources.py) from the same package directory.
# This makes them available when you import views elsewhere in our project.
from . import landing, scorer, history, resources


# Defines the public API of the package.
# When someone does: from views import *
# only these modules (landing, scorer, history, resources) will be imported.
# Helps control namespace pollution and makes the package cleaner.
__all__ = ['landing', 'scorer', 'history', 'resources']