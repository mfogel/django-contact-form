from django.conf.urls.defaults import *

from .views import ContactFormView, ContactFormSentView

urlpatterns = patterns('',
    url(r'^$',
        view=ContactFormView.as_view(),
        name='contact-form'
    ),
    url(r'^sent/$',
        view=ContactFormSentView.as_view(),
        name='contact-form-sent'
    ),
)
