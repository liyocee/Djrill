from django.core import mail

from djrill.tests.mock_backend import DjrillBackendMockAPITestCase


class DjrillMandrillSendTemplateTests(DjrillBackendMockAPITestCase):
    """Test Djrill backend support for Mandrill send-template features"""

    def test_send_template(self):
        msg = mail.EmailMessage('Subject', 'Text Body',
            'from@example.com', ['to@example.com'])
        msg.template_name = "PERSONALIZED_SPECIALS"
        msg.template_content = {
            'HEADLINE': "<h1>Specials Just For *|FNAME|*</h1>",
            'OFFER_BLOCK': "<p><em>Half off</em> all fruit</p>"
        }
        msg.send()
        self.assert_mandrill_called("/messages/send-template.json")
        data = self.get_api_call_data()
        self.assertEqual(data['template_name'], "PERSONALIZED_SPECIALS")
        # Djrill expands simple python dicts into the more-verbose name/value
        # structures the Mandrill API uses
        self.assertEqual(data['template_content'],
            [ {'name': "HEADLINE",
               'value': "<h1>Specials Just For *|FNAME|*</h1>"},
              {'name': "OFFER_BLOCK",
               'value': "<p><em>Half off</em> all fruit</p>"} ]
        )

    def test_no_template_content(self):
        # Just a template, without any template_content to be merged
        msg = mail.EmailMessage('Subject', 'Text Body',
            'from@example.com', ['to@example.com'])
        msg.template_name = "WELCOME_MESSAGE"
        msg.send()
        self.assert_mandrill_called("/messages/send-template.json")
        data = self.get_api_call_data()
        self.assertEqual(data['template_name'], "WELCOME_MESSAGE")
        self.assertFalse('template_content' in data)

    def test_non_template_send(self):
        # Make sure the non-template case still uses /messages/send.json
        msg = mail.EmailMessage('Subject', 'Text Body',
            'from@example.com', ['to@example.com'])
        msg.send()
        self.assert_mandrill_called("/messages/send.json")
        data = self.get_api_call_data()
        self.assertFalse('template_name' in data)
        self.assertFalse('template_content' in data)
        self.assertFalse('async' in data)