# -*- coding: utf-8 -*-

import datetime
import pkg_resources

from django.template import Context, Template

from xblock.core import XBlock
from xblock.fields import Scope, Integer, Boolean, String, DateTime
from xblock.fragment import Fragment

from xblockutils.studio_editable import StudioContainerXBlockMixin, StudioEditableXBlockMixin

DATE_FORMAT = '%Y-%m-%d %H:%M'

# '%Y-%m-%dT%H:%M:%S.%f'


class PasswordContainerXBlock(StudioContainerXBlockMixin, StudioEditableXBlockMixin, XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    has_children = True
    editable_fields = ['start_date', 'end_date', 'password']

    start_date = String(default="", scope=Scope.settings,
            display_name=u"Debut de la visibilité",
            help="Children visibility start date (%s)" % DATE_FORMAT)
    end_date = String(default="", scope=Scope.settings,
            display_name=u"Fin de la visibilité",
            help="Children visibility end date (%s)" % DATE_FORMAT)

    password = String(default="", scope=Scope.settings,
            display_name=u"Mot de passe",
            help="Password")

    #warning_message = String(default="You can't se this because...", scope=Scope.settings,
    #        display_name=u"",
    #        help="Message to display ")


    def _is_studio(self):
        studio = False
        try:
            studio = self.runtime.is_author_mode
        except AttributeError:
            pass
        return studio


    def get_icon_class(self):
        """Return the CSS class to be used in courseware sequence list."""
        return 'video'


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def _render_template(self, ressource, **kwargs):
        template = Template(self.resource_string(ressource))
        context = dict({'start_date': self.start_date, 'end_date': self.end_date, 'password': self.password},
                **kwargs)
        html = template.render(Context(context))
        return html

    def student_view(self, context=None):
        # studio view
        #import ipdb; ipdb.set_trace()
        if self._is_studio():
            fragment = Fragment(self._render_template('static/html/studio.html'))
            fragment.add_css(self.resource_string('static/css/password-container-studio.css'))
            child_frags = self.render_children(context, fragment, can_reorder=False, can_add=True)
            return fragment
        # student view
        else:
            if self.start_date and self.end_date:
                start_date = datetime.datetime.strptime(self.start_date, DATE_FORMAT)
                end_date = datetime.datetime.strptime(self.end_date, DATE_FORMAT)
                now = datetime.datetime.now()
                if now > start_date and now < end_date:
                    # display password inputbox
                    fragment = Fragment(self._render_template('static/html/2-enter-password.html'))
                    #child_frags = self.render_children(context, frag, can_reorder=False, can_add=True)
                    init_js = 'CheckPassword'

                elif now > end_date:
                    fragment = Fragment(self._render_template('static/html/4-not-available-anymore.html'))
                else:
                    fragment = Fragment(self._render_template('static/html/1-not-yet-available.html'))

                fragment.add_css(self.resource_string('static/css/password-container-lms.css'))
                fragment.add_javascript(self.resource_string("static/js/src/password_container.js"))
                if init_js:
                    fragment.initialize_js(init_js)

                return fragment

            # we should not be there !
            frag = Fragment("Erreur: les dates ne sont pas valides...")
            return frag



        #html = self.resource_string("static/html/password_container.html")
        #frag = Fragment(html.format(self=self))
        #frag.add_css(self.resource_string("static/css/password_container.css"))
        #frag.add_javascript(self.resource_string("static/js/src/password_container.js"))
        #frag.initialize_js('PasswordContainerXBlock')


    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("PasswordContainerXBlock",
             """<vertical_demo>
                <password_container/>
                </vertical_demo>
             """),
        ]
