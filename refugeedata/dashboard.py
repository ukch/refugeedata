"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'refugee.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
#from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        self.children.append(modules.Group(
            column=1,
            collapsible=True,
            children=[
                modules.ModelList(
                    _("Users"),
                    models=[
                        "django.contrib.auth.models.User",
                    ]
                ),
                modules.ModelList(
                    _("Registration"),
                    models=[
                        "refugeedata.models.RegistrationCardBatch",
                        "refugeedata.models.RegistrationNumber",
                        "refugeedata.models.Language",
                        "refugeedata.models.Person",
                    ]
                ),
                modules.ModelList(
                    _("Distribution"),
                    models=[
                        "refugeedata.models.Distribution",
                        "refugeedata.models.Template",
                    ]
                ),
                modules.LinkList(
                    _("Extra"),
                    children=[{
                        "title": _("Show all faces"),
                        "url": reverse("show_faces"),
                    }]
                ),
            ]
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Support'),
            column=2,
            children=[
                {
                    'title': _('Refugeedata Website'),
                    'url': 'http://joelcross.co.uk/refugeedata/',
                    'external': True,
                },
                {
                    'title': _('Bug/Issue Tracker'),
                    'url': 'https://github.com/ukch/refugeedata/issues',
                    'external': True,
                },
            ]
        ))

        # TODO replace this with an actual news feed
        # append a feed module
        """self.children.append(modules.Feed(
            _('Latest News'),
            column=2,
            feed_url="https://github.com/ukch/refugeedata/commits/stable.atom",
            limit=5
        ))"""

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=False,
            column=2,
        ))
