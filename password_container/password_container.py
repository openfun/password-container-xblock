# -*- coding: utf-8 -*-

import datetime
import dateutil.parser
import pkg_resources

from django.template import Context, Template
from django.utils import timezone

from xblock.core import XBlock
from xblock.fields import Scope, Integer, Boolean, String, DateTime, Dict
from xblock.fragment import Fragment

from xblockutils2.studio_editable import StudioContainerXBlockMixin, StudioEditableXBlockMixin

DATETIME_FORMAT = '%d/%m/%Y/ %H:%M'
MAX_TRIES = 5
TIME_LEFT_WARNING = 60 * 5

# '%Y-%m-%dT%H:%M:%S.%f'


class PasswordContainerXBlock(StudioContainerXBlockMixin, StudioEditableXBlockMixin, XBlock):
    """
    This Xblock will restrain access to its children to a time period and an identication process
    """

    has_children = True
    AJAX = False  # if True, children will be loaded by ajax when password is ok instead of reloading the whole page

    editable_fields = ['group_id', 'start_date', 'end_date', 'duration', 'password']

    display_name = String(
        help="Component's name in the studio",
        default="Time and password limited container",
        scope=Scope.settings
    )

    group_id = String(default="", scope=Scope.settings,
            display_name=u"Identifiant de groupe",
            help=u"Tous les Xblock ayant cet identifiant en commun seront débloqués en même temps.")
    start_date = DateTime(default="", scope=Scope.settings,
            display_name=u"Debut de la visibilité",
            help=u"Children visibility start date and time (UTC)")
    end_date = DateTime(default="", scope=Scope.settings,
            display_name=u"Fin de la visibilité",
            help=u"Children visibility end date and time (UTC)")

    password = String(default="", scope=Scope.settings,
            display_name=u"Mot de passe",
            help=u"Global password, all student will use this password to unlock content")
    duration = Integer(
            default=None, scope=Scope.settings,
            display_name=u"Durée de disponibilité",
            help=u"Durée de la disponibilité du contenu en minutes (facultatif)")

    nb_tries = Dict(
            scope=Scope.preferences,
            help=u"An Integer indicating how many times the user tried authenticating"
            )
    user_allowed = Dict(
            scope=Scope.preferences,
            help=u"Set to True if user has once been allowed to see children blocks"
            )
    user_started = Dict(
            scope=Scope.preferences,
            help=u"Time user started")

    def _is_studio(self):
        studio = False
        try:
            studio = self.runtime.is_author_mode
        except AttributeError:
            pass
        return studio


    def get_icon_class(self):
        """Return the CSS class to be used in courseware sequence list."""
        return 'seq_problem'


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def _render_template(self, ressource, **kwargs):
        template = Template(self.resource_string(ressource))
        context = dict({
                'group_id': self.group_id,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'password': self.password,
                'nb_tries': self.get_nb_tries(),
                'duration': self.duration,
                'user_started': self.get_user_started(),
                },
                **kwargs)
        html = template.render(Context(context))
        return html

    def get_nb_tries(self):
        if self.group_id in self.nb_tries:
            return self.nb_tries[self.group_id]
        else:
            return 0

    def get_user_allowed(self):
        if self.group_id in self.user_allowed:
            return self.user_allowed[self.group_id]
        else:
            return False

    def get_user_started(self):
        if self.group_id in self.user_started and self.user_started[self.group_id]:
            return dateutil.parser.parse(self.user_started[self.group_id])
        else:
            return None

    def set_nb_tries(self, value):
        self.nb_tries[self.group_id] = value

    def set_user_allowed(self, value):
        self.user_allowed[self.group_id] = value

    def set_user_started(self, value):
        self.user_started[self.group_id] = value.isoformat() if value else None  # allow to set to None

    @XBlock.json_handler
    def reset_user_state(self, data, prefix=''):
        """Reset user state for testing purpose."""
        # TODO: restrain to staff
        self.user_allowed = {}
        self.nb_tries = {}
        self.user_started = {}
        self.set_user_allowed(False)
        self.set_nb_tries(0)
        self.set_user_started(None)
        return {'result': 'ok'}


    @XBlock.json_handler
    def check_password(self, data, prefix=''):
        email = data.get('email')
        password = data.get('password')

        self.set_nb_tries(self.get_nb_tries() + 1)
        #if self.runtime.get_real_user is not None:
        #    email=self.runtime.get_real_user(self.runtime.anonymous_student_id).email

        if password == self.password:  # A strong identification process is still to imagine
            self.set_user_allowed(True)
            self.set_user_started(timezone.now())
            result = {  # Javascript will reload the page
                'result': True,
                'message': u"The page will reload",
                'reload': True
                }
        else:
            result = {
                'result': False,
                'nb_tries': self.get_nb_tries(),
                'message': u"Mot de passe invalide"
                }
            if (self.get_nb_tries() > MAX_TRIES):
                result['too_much_tries'] = True
                result['message'] = u"Too many tries"
        return result


    @XBlock.json_handler
    def get_time_left(self, data, prefix=''):
        """Return time left to access children.
        Time left until `end_date`
        OR if `duration` > 0: time left between time `user_started` and `duration`
        """
        user_started = self.get_user_started()
        warning = False
        if self.duration and self.get_user_allowed():
            duration = datetime.timedelta(minutes=self.duration)
            time_left = (user_started + duration) - timezone.now()
        else:
            time_left = self.end_date - timezone.now()

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
                user_started = self.get_user_started()
                now = timezone.now()
                if (now > self.start_date and now < self.end_date):
                    # with are in the availability interval
                    if self.get_user_allowed():
                        # user is granted (entered a good password)
                        if self.duration and (now > user_started + datetime.timedelta(minutes=self.duration)):
                            # time allowed to access content is elapsed
                            fragment = Fragment(self._render_template('static/html/5-time-elapsed.html'))
                            fragment.initialize_js('PasswordContainerXBlock', 'bindResetButton')  # call Run to allow reset in debug mode
                        else:
                            # content is available
                            fragment = Fragment(self._render_template('static/html/3-available.html'))
                            child_frags = self.runtime.render_children(block=self, view_name='student_view', context=context)
                            html = self._render_template('static/html/sequence.html', children=child_frags)
                            fragment.add_content(html)
                            fragment.add_frags_resources(child_frags)
                            fragment.initialize_js('PasswordContainerXBlock', 'startExam')
                    else:
                        # user is not granted
                        if self.get_nb_tries() < MAX_TRIES:
                            # password is now required
                            fragment = Fragment(self._render_template('static/html/2-enter-password.html'))
                            child_frags = self.runtime.render_children(block=self, view_name='student_view', context=context)
                            fragment.add_frags_resources(child_frags)
                            fragment.initialize_js('PasswordContainerXBlock', 'checkPassword')
                        else:
                            # too much password failures
                            fragment = Fragment(self._render_template('static/html/4-not-available-anymore.html'))

                elif now > self.end_date:
                    # content is no more available
                    fragment = Fragment(self._render_template('static/html/4-not-available-anymore.html'))
                else:
                    # content is not yet available
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
