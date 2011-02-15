"""
A base contact form for allowing users to send email messages through
a web interface, and a subclass demonstrating useful functionality.

"""


from django import forms
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader, RequestContext
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _


# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary.
attrs_dict = { 'class': 'required' }


class ContactForm(forms.Form):
    """
    Base contact form class from which all contact form classes should
    inherit.

    If you don't need any custom functionality, you can simply use
    this form to provide basic contact functionality; it will collect
    name, email address and message.

    The ``contact_form`` view included in this application knows how
    to work with this form and can handle many types of subclasses as
    well (see below for a discussion of the important points), so in
    many cases it will be all that you need. If you'd like to use this
    form or a subclass of it from one of your own views, just do the
    following:

    1. When you instantiate the form, pass the current ``HttpRequest``
       object to the constructor as the keyword argument ``request``;
       this is used internally by the base implementation, and also
       made available so that subclasses can add functionality which
       relies on inspecting the request.

    2. To send the message, call the form's ``save`` method, which
       accepts the keyword argument ``fail_silently`` and defaults it
       to ``False``. This argument is passed directly to
       ``send_mail``, and allows you to suppress or raise exceptions
       as needed for debugging. The ``save`` method has no return
       value.

    Other than that, treat it like any other form; validity checks and
    validated data are handled normally, through the ``is_valid``
    method and the ``cleaned_data`` dictionary.
    """

    name = forms.CharField(max_length=80, label=_('Your name'),
            widget=forms.TextInput(attrs=attrs_dict))

    email = forms.EmailField(label=_('Your email address'),
        widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=1000)))

    message = forms.CharField(label=_('Your message'),
        widget=forms.Textarea(attrs=attrs_dict))

    subject_template_name = "contact_form/subject.txt"
    body_template_name = 'contact_form/body.txt'

    def __init__(self, data=None, files=None, request=None, *args, **kwargs):
        if request is None:
            raise TypeError("Keyword argument 'request' must be supplied")
        super(ContactForm, self).__init__(
            data=data, files=files, *args, **kwargs)
        self.request = request

    # making these properties rather than attributes makes these setting
    # optional.  good in case you're overriding these anyway
    @property
    def to(self):
        # must be a list or tuple
        return (settings.CONTACT_FORM_TO,)
    @property
    def from_email(self):
        return settings.CONTACT_FORM_FROM

    def subject(self):
        """
        Render the subject of the message to a string.
        """
        subject = loader.render_to_string(
            self.subject_template_name, self.get_context())
        return u''.join(subject.splitlines())

    def body(self):
        """
        Render the body of the message to a string.
        """
        return loader.render_to_string(
            self.body_template_name, self.get_context())

    def headers(self):
        reply_to = u'"{name}" <{email}>'.format(
                name=self.cleaned_data['name'],
                email=self.cleaned_data['email']
            )
        return {'Reply-To': reply_to}


    def get_context(self):
        """
        Return the context used to render the templates for the email
        subject and body.
        """
        if not self.is_valid():
            raise ValueError("Can't generate Context: invalid contact form")
        return RequestContext(self.request,
                dict(self.cleaned_data, site=Site.objects.get_current()))

    def get_message_dict(self):
        """
        Generate the various parts of the message and return them in a
        dictionary, suitable for passing directly as keyword arguments
        to ``django.core.mail.EmailMessage()``.
        """
        if not self.is_valid():
            raise ValueError("Can't send message: invalid contact form")

        message_dict = {}
        for message_part in ('subject', 'body', 'from_email', 'to', 'headers'):
            attr = getattr(self, message_part)
            message_dict[message_part] = callable(attr) and attr() or attr
        return message_dict

    def save(self, fail_silently=False):
        """
        Build and send the email message.

        """
        email_mes = EmailMessage(**self.get_message_dict())
        email_mes.send(fail_silently=fail_silently)
