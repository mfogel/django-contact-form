from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase


class ContactFormTests(TestCase):
    urls = 'contact_form.urls'

    def setUp(self):
        self.post_url = reverse('contact-form')
        self.sent_url = reverse('contact-form-sent')

    def test_validation(self):
        response = self.client.post(self.post_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                'contact_form/iframes/contact_form.html')
        self.assertFormError(response,
                'form', 'name', 'This field is required.')
        self.assertFormError(response,
                'form', 'email', 'This field is required.')
        self.assertFormError(response,
                'form', 'message', 'This field is required.')

        response = self.client.post(self.post_url, {'email': 'aslkdjf'})
        self.assertFormError(response,
                'form', 'email', 'Enter a valid e-mail address.')

    def test_email_sends(self):
        # send a valid message
        post_data = {
            'name': 'Joe Smoe',
            'email': 'joe@gmail.com',
            'message': 'test, test'
        }
        min_len = len(' '.join(post_data.values()))
        response = self.client.post(self.post_url, post_data)
        self.assertRedirects(response, self.sent_url)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, settings.CONTACT_FORM_TO)
        self.assertGreaterEqual(len(mail.outbox[0].body), min_len)
        self.assertEqual(len(mail.outbox), 1)

    def test_sent_view(self):
        response = self.client.get(self.sent_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                'contact_form/iframes/contact_form_sent.html')
