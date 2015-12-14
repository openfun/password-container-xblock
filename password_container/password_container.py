# -*- coding: utf-8 -*-

import datetime
import dateutil.parser
import pkg_resources
from webob.response import Response

from django.contrib.auth.models import User
from django.template import Context, Template
from django.utils import timezone
from django.utils.translation import ugettext_lazy, ugettext as _
from courseware.models import XModuleStudentPrefsField
from opaque_keys.edx.block_types import BlockTypeKeyV1

from xblock.core import XBlock
from xblock.exceptions import JsonHandlerError
from xblock.fields import Scope, UserScope, BlockScope, Integer, Boolean, String, DateTime, Dict
from xblock.fragment import Fragment
from xblock.validation import Validation

# We forked xblockutils because the old version living in the edx-plaform venv do not have StudioContainerXBlockMixin
from xblockutils2.studio_editable import StudioContainerXBlockMixin

from .models import GroupConfiguration
from .forms import PasswordContainerXBlockForm

DATETIME_FORMAT = '%d/%m/%Y/ %H:%M'
MAX_TRIES = 5
TIME_LEFT_WARNING = 60 * 5

# '%Y-%m-%dT%H:%M:%S.%f'

class PasswordContainerXBlock(StudioContainerXBlockMixin, XBlock):
    """
    This Xblock will restrain access to its children to a time period and an identication process
    """

    has_children = True


    editable_fields = ['group_id', 'start_date', 'end_date', 'duration', 'password']
    display_name = String(
        help=ugettext_lazy("Component's name in the studio"),
        default="Time and password limited container",
        scope=Scope.settings
    )
    group_id = String(default="", scope=Scope.settings,
            display_name=ugettext_lazy('Identifiant de groupe'),
            help=ugettext_lazy(u"Tous les Xblock ayant cet identifiant en commun seront débloqués en même temps."))

    nb_tries = Dict(
            scope=Scope.preferences,
            help=ugettext_lazy(u"An Integer indicating how many times the user tried authenticating")
            )
    user_allowed = Dict(
            scope=Scope.preferences,
            help=ugettext_lazy(u"Set to True if user has once been allowed to see children blocks")
            ) 
    user_started = Dict(
            scope=Scope.preferences,
            help=ugettext_lazy(u"Time user started"))

    def __init__(self, *args, **kwargs):
        super(PasswordContainerXBlock, self).__init__(*args, **kwargs)
        self.get_configuration()

    def _is_studio(self):
        studio = False
        try:
            studio = self.runtime.is_author_mode
        except AttributeError:
            pass
        return studio

    def _user_is_staff(self):
        return getattr(self.runtime, 'user_is_staff', False)

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
                'user_is_staff': self._user_is_staff(),
                'group_id': self.group_id,
                'start_date': self.configuration.start_date,
                'end_date': self.configuration.end_date,
                'password': self.configuration.password,
                'duration': self.configuration.duration,
                'nb_tries': self.get_nb_tries(),
                'user_started': self.get_user_started(),
                'user_allowed': self.get_user_allowed(),
                },
                **kwargs)
        html = template.render(Context(context))
        return html

    def get_configuration(self, group_id=None):
        """Retrieve existing configuration if for a given `group_id` or create a new one."""
        group_id = group_id or self.group_id
        try:
            self.configuration = GroupConfiguration.objects.get(
                    course_id=self.runtime.course_id, group_id=group_id)
        except GroupConfiguration.DoesNotExist:
            self.configuration = GroupConfiguration(course_id=self.runtime.course_id,
                    group_id=group_id)

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

    def set_configuration(self):
        self.configuration.save()

    def set_nb_tries(self, value):
        self.nb_tries[self.group_id] = value

    def set_user_allowed(self, value):
        self.user_allowed[self.group_id] = value

    def set_user_started(self, value):
        self.user_started[self.group_id] = value.isoformat() if value else None

    @XBlock.handler
    def reset_user_state(self, request, context=None):
        """Reset user state."""
        if not self._user_is_staff():
            return
        try:
            user = User.objects.get(username=request.GET['username'])
        except User.DoesNotExist:
            return Response(_(u"L'utilisateur n'existe pas."))

        preferences = XModuleStudentPrefsField.objects.filter(module_type=BlockTypeKeyV1('xblock.v1', 'password_container'),
                                                              student=user)
        try:
            preference = preferences.get(field_name='nb_tries')
        except XModuleStudentPrefsField.DoesNotExist:
            pass
        else:
            preference.delete()
        try:
            preference = preferences.get(field_name='user_allowed')
        except XModuleStudentPrefsField.DoesNotExist:
            pass
        else:
            preference.delete()
        try:
            preference = preferences.get(field_name='user_started')
        except XModuleStudentPrefsField.DoesNotExist:
            pass
        else:
            preference.delete()
        return Response(_(u"Données réinitialisées."))

    @XBlock.json_handler
    def check_password(self, data, prefix=''):
        password = data.get('password')
        self.set_nb_tries(self.get_nb_tries() + 1)

        if password == self.configuration.password:  # A strong identification process is still to imagine
            self.set_user_allowed(True)
            self.set_user_started(timezone.now())
            result = {  # Javascript will reload the page
                'result': True,
                'message': _(u"The page will reload"),
                'reload': True
                }
        else:
            result = {
                'result': False,
                'nb_tries': self.get_nb_tries(),
                'message': _(u"Mot de passe invalide")
                }
            if (self.get_nb_tries() > MAX_TRIES):
                result['too_much_tries'] = True
                result['message'] = _(u"Too many tries")
        return result

    @XBlock.json_handler
    def get_time_left(self, data, prefix=''):
        """Return time left to access children.
        Time left until `end_date`
        OR if `duration` > 0: time left between time `user_started` and `duration`
        """
        user_started = self.get_user_started()
        warning = False
        if self.get_user_allowed():
            duration = datetime.timedelta(minutes=self.configuration.duration)
            time_left = (user_started + duration) - timezone.now()
        else:
            time_left = self.configuration.end_date - timezone.now()

        days = time_left.days
        seconds = time_left.seconds % 60
        minutes = time_left.seconds % 3600 // 60
        hours = time_left.seconds // 3600
        total = days * 3600 * 24 + time_left.seconds

        string = _(u"{days} jours ") if days else u""
        string += _(u"{hours:02} heures {minutes:02} minutes")

        if total < TIME_LEFT_WARNING:
            string += _(u" {seconds:02} secondes")
            warning = True

        return {
            'time_left': string.format(days=days, hours=hours, minutes=minutes, seconds=seconds),
            'total': total,
            'warning': warning,
            }

    def studio_view(self, context=None):
        """This is the view displaying xblock form in studio."""
        fragment = Fragment()
        initial = {
                'group_id': self.group_id,
                'start_date': self.configuration.start_date,
                'end_date': self.configuration.end_date,
                'password': self.configuration.password,
                'duration': self.configuration.duration,
                }
        form = PasswordContainerXBlockForm(initial=initial)
        context = {}
        context['form'] = form
        fragment.content = self._render_template('static/html/studio_edit.html', **context)
        fragment.add_javascript(self.resource_string("static/js/src/studio_edit.js"))
        fragment.initialize_js('PasswordContainerStudio')
        return fragment

    @XBlock.json_handler
    def submit_studio_edits(self, data, suffix=''):
        form = PasswordContainerXBlockForm(data=data['values'])
        if form.is_valid():
            self.group_id = form.cleaned_data['group_id']
            self.get_configuration(self.group_id)
            self.configuration.group_id = self.group_id
            self.configuration.start_date = form.cleaned_data['start_date']
            self.configuration.end_date = form.cleaned_data['end_date']
            self.configuration.duration = form.cleaned_data['duration']
            self.configuration.password = form.cleaned_data['password']
            self.configuration.save()
            return {'result': 'success'}

        error_message = u""
        for field, message in form.errors.items():
            error_message += u"<strong>%s</strong> : %s<br>" % (form.fields[field].label, ' '.join(message))

        raise JsonHandlerError(400, error_message)

    @XBlock.json_handler
    def get_existing_group(self, data, suffix=''):
        result = {}
        group_id = data['group_id']
        try:
            group = GroupConfiguration.objects.get(
                    course_id=self.runtime.course_id, group_id=group_id)
            result['start_date_0'] = group.start_date.strftime('%d/%m/%Y')
            result['start_date_1'] = group.start_date.strftime('%H:%M')
            result['end_date_0'] = group.end_date.strftime('%d/%m/%Y')
            result['end_date_1'] = group.end_date.strftime('%H:%M')
            result['duration'] = group.duration
            result['password'] = group.password
        except GroupConfiguration.DoesNotExist:
            pass
        return result

    def author_edit_view(self, context):
        """We override this view from StudioContainerXBlockMixin to allow
        the addition of children blocks."""
        fragment = Fragment()
        self.render_children(context, fragment, can_reorder=True, can_add=True)
        return fragment

    def staff_view(self):
        fragment = Fragment(self._render_template('static/html/staff-view.html'))
        child_frags = self.runtime.render_children(block=self, view_name='student_view')
        html = self._render_template('static/html/sequence.html', children=child_frags)
        fragment.add_content(html)
        fragment.add_frags_resources(child_frags)
        fragment.add_javascript(self.resource_string("static/js/src/lms_view.js"))
        fragment.initialize_js('PasswordContainerLmsView')
        return fragment

    def student_view(self, context=None):
        if self._is_studio():  # studio view
            fragment = Fragment(self._render_template('static/html/studio.html'))
            fragment.add_css(self.resource_string('static/css/password-container.css'))
            return fragment
        if self._user_is_staff():
            return self.staff_view()
        else:  # student view
            if self.configuration.start_date and self.configuration.end_date:
                user_started = self.get_user_started()
                now = timezone.now()
                if (now > self.configuration.start_date and now < self.configuration.end_date):
                    # with are in the availability interval
                    if self.get_user_allowed():
                        # user is granted (entered a good password)
                        if self.configuration.duration and (now > user_started + datetime.timedelta(minutes=self.configuration.duration)):
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

                elif now > self.configuration.end_date:
                    # content is no more available
                    fragment = Fragment(self._render_template('static/html/4-not-available-anymore.html'))
                else:
                    # content is not yet available
                    fragment = Fragment(self._render_template('static/html/1-not-yet-available.html'))

                fragment.add_css(self.resource_string('static/css/password-container.css'))
                fragment.add_javascript(self.resource_string("static/js/src/password_container.js"))

                return fragment

            # we should not be here !
            frag = Fragment(_(u"Cette activité n'est pas disponible"))
            return frag

