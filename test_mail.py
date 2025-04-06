import unittest
from unittest.mock import patch, MagicMock
from imap_tools.message import MailMessage
from imap_tools import MailAttachment
from mail import read_mail


class TestReadMail(unittest.TestCase):
    @patch("mail.MailBox")
    def test_read_mail_configuration(self, mock_mailbox):
        # Setup mock
        mock_instance = MagicMock()
        mock_mailbox.return_value.login.return_value = mock_instance
        mock_instance.fetch.return_value = []

        # Call function
        result = read_mail()

        # Assert MailBox was called with correct default parameters
        mock_mailbox.assert_called_with("localhost", "993")

        # Assert login was called with correct default parameters
        mock_mailbox.return_value.login.assert_called_with("mail_user", "mail_pw")

        # Assert folder was set correctly
        mock_instance.folder.set.assert_called_with("Blog")

        # Assert fetch was called with correct parameters
        mock_instance.fetch.assert_called_with(limit=10, reverse=True)

        # Assert empty result
        self.assertEqual(result, [])

    @patch("mail.MailBox")
    def test_read_mail_with_messages(self, mock_mailbox):
        # Setup mock
        mock_instance = MagicMock()
        mock_mailbox.return_value.login.return_value = mock_instance

        # Create test mail messages with attachments
        mail1 = MagicMock(spec=MailMessage)
        attachment1 = MagicMock(spec=MailAttachment)
        attachment1.content_id = "cid1"
        mail1.attachments = [attachment1]

        mail2 = MagicMock(spec=MailMessage)
        attachment2 = MagicMock(spec=MailAttachment)
        attachment2.content_id = "cid2"
        mail2.attachments = [attachment2]

        mock_instance.fetch.return_value = [mail1, mail2]

        # Call function
        result = read_mail()

        # Assert result contains correct data
        self.assertEqual(len(result), 2)

        # First mail
        self.assertEqual(result[0][0], mail1)
        self.assertEqual(len(result[0][1]), 1)
        self.assertEqual(result[0][1]["cid1"], attachment1)

        # Second mail
        self.assertEqual(result[1][0], mail2)
        self.assertEqual(len(result[1][1]), 1)
        self.assertEqual(result[1][1]["cid2"], attachment2)

    @patch("mail.MailBox")
    @patch("mail.os.environ.get")
    def test_read_mail_with_custom_env_vars(self, mock_env_get, mock_mailbox):
        # Setup environment variable mocks
        def env_side_effect(var, default):
            env_vars = {
                "M2B_IMAP_HOST": "custom-host.com",
                "M2B_IMAP_PORT": "1234",
                "M2B_MAILBOX_USER": "testuser",
                "M2B_MAILBOX_PASS": "testpass",
                "M2B_MAILBOX_FOLDER": "CustomFolder",
            }
            return env_vars.get(var, default)

        mock_env_get.side_effect = env_side_effect

        # Setup mailbox mock
        mock_instance = MagicMock()
        mock_mailbox.return_value.login.return_value = mock_instance
        mock_instance.fetch.return_value = []

        # Call function
        read_mail()

        # Assert MailBox was called with custom parameters
        mock_mailbox.assert_called_with("custom-host.com", "1234")

        # Assert login was called with custom parameters
        mock_mailbox.return_value.login.assert_called_with("testuser", "testpass")

        # Assert folder was set correctly
        mock_instance.folder.set.assert_called_with("CustomFolder")


if __name__ == "__main__":
    unittest.main()
