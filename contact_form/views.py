from django.core.urlresolvers import reverse
from django.views.generic import FormView, TemplateView

from .forms import ContactForm

class ContactFormView(FormView):
    form_class = ContactForm
    template_name = 'contact_form/iframes/contact_form.html'

    def form_valid(self, form):
        form.save()
        return super(ContactFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse('contact-form-sent')

    def get_form_kwargs(self):
        kwargs = super(ContactFormView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
        })
        return kwargs

class ContactFormSentView(TemplateView):
    template_name = 'contact_form/iframes/contact_form_sent.html'
