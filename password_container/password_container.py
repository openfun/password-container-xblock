# -*- coding: utf-8 -*-

import datetime
import pkg_resources

from django.template import Context, Template
from django.utils import timezone

from xblock.core import XBlock
from xblock.fields import Scope, Integer, Boolean, String, DateTime
from xblock.fragment import Fragment

from xblockutils.studio_editable import StudioContainerXBlockMixin, StudioEditableXBlockMixin

DATE_FORMAT = '%d/%m/%Y/ %H:%M'
MAX_TRIES = 5
TIME_LEFT_WARNING = 60 * 5

# '%Y-%m-%dT%H:%M:%S.%f'

# override default DateTime to handle french date format
class XDateTime(DateTime):
    DATETIME_FORMAT = DATE_FORMAT


class PasswordContainerXBlock(StudioContainerXBlockMixin, StudioEditableXBlockMixin, XBlock):
    """
    This Xblock will restrain access to its children to a time period and an identication process
    """

    has_children = True
    AJAX = False  # if True, children will be loaded by ajax when password is ok instead of reloading the whole page

    editable_fields = ['start_date', 'end_date', 'password']

    start_date = XDateTime(default="", scope=Scope.settings,
            display_name=u"Debut de la visibilité",
            help="Children visibility start date (%s)" % DATE_FORMAT)
    end_date = XDateTime(default="", scope=Scope.settings,
            display_name=u"Fin de la visibilité",
            help="Children visibility end date (%s)" % DATE_FORMAT)

    password = String(default="", scope=Scope.settings,
            display_name=u"Mot de passe",
            help="Password")

    nb_tries = Integer(
        default=0, scope=Scope.user_info,
        help="An Integer indicating how many times the user tried authenticating"
    )
    user_allowed = Boolean(
        default=False, scope=Scope.user_info,
        help="Set to True if user has once been allowed to see children blocks"
    )


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
        context = dict({'start_date': self.start_date,
                'end_date': self.end_date,
                'password': self.password,
                'nb_tries': self.nb_tries,
                },
                **kwargs)
        html = template.render(Context(context))
        return html


    @XBlock.json_handler
    def reset_user_state(self, data, prefix=''):
        """Reset user state for testing purpose."""
        # TODO: restrain to staff
        self.user_allowed = False
        self.nb_tries = 0
        return {'result': 'ok'}


    @XBlock.json_handler
    def check_password(self, data, prefix=''):
        email = data.get('email')
        password = data.get('password')

        self.nb_tries += 1

        #if self.runtime.get_real_user is not None:
        #    email=self.runtime.get_real_user(self.runtime.anonymous_student_id).email

        if password == self.password:  # A strong identification process is still to imagine
            self.user_allowed = True
            if self.AJAX:  # This do not work, as it do not correctly initialyze quizz Javascript
                fragment = Fragment(self._render_template('static/html/3-available.html'))
                child_frags = self.runtime.render_children(block=self, view_name='student_view', context=None)
                html = self._render_template('static/html/sequence.html', children=child_frags)
                fragment.add_content(html)
                result = {
                    'result': True,
                    'message': u"Go !",
                    'i4x_uri': self.location.to_deprecated_string(),
                    'html': fragment.body_html(),
                    }
            else:
                result = {  # Javascript will reload the page
                    'result': True,
                    'message': u"The page will reload",
                    'reload': True
                    }

        else:
            result = {
                'result': False,
                'message': u"Mot de passe invalide"
                }
            if (self.nb_tries > MAX_TRIES):
                result['message'] = u"Too many tries"

        return result


    @XBlock.json_handler
    def get_time_left(self, data, prefix=''):
        """Return time left to access children."""

        time_left = self.end_date - timezone.now()
        warning = False
        days = time_left.days
        seconds = time_left.seconds % 60
        minutes = time_left.seconds % 3600 // 60
        hours = time_left.seconds // 3600
        total = days * 3600 * 24 + time_left.seconds

        string = u"{days} jours " if days else u""
        string += u"{hours:02} heures {minutes:02} minutes"

        if total < TIME_LEFT_WARNING:
            string += u" {seconds:02} secondes"
            warning = True

        return {
            'time_left': string.format(days=days, hours=hours, minutes=minutes, seconds=seconds),
            'total': total,
            'warning': warning,
            }


    def student_view(self, context=None):

        if self._is_studio():  # studio view
            fragment = Fragment(self._render_template('static/html/studio.html'))
            fragment.add_css(self.resource_string('static/css/password-container-studio.css'))
            child_frags = self.render_children(context, fragment, can_reorder=False, can_add=True)
            return fragment

        else:  # student view
            if self.start_date and self.end_date:

                now = timezone.now()
                if now > self.start_date and now < self.end_date:
                    if self.user_allowed:
                        fragment = Fragment(self._render_template('static/html/3-available.html'))
                        child_frags = self.runtime.render_children(block=self, view_name='student_view', context=context)
                        html = self._render_template('static/html/sequence.html', children=child_frags)
                        fragment.add_content(html)
                        fragment.add_frags_resources(child_frags)
                        fragment.initialize_js('PasswordContainerXBlock', 'Run')

                    else:
                        fragment = Fragment(self._render_template('static/html/2-enter-password.html'))
                        child_frags = self.runtime.render_children(block=self, view_name='student_view', context=context)
                        fragment.add_frags_resources(child_frags)
                        fragment.initialize_js('PasswordContainerXBlock', 'CheckPassword')

                elif now > self.end_date:
                    fragment = Fragment(self._render_template('static/html/4-not-available-anymore.html'))
                else:
                    fragment = Fragment(self._render_template('static/html/1-not-yet-available.html'))

                fragment.add_css(self.resource_string('static/css/password-container-lms.css'))
                fragment.add_javascript(self.resource_string("static/js/src/password_container.js"))

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
