import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
from main import PostManager, main


class TestPostManager(unittest.TestCase):
    @patch(
        "builtins.open", new_callable=mock_open, read_data='{"test_id": "test_path.md"}'
    )
    @patch("os.path.exists", return_value=True)
    def test_init_with_existing_history(self, mock_exists, mock_file):
        post_manager = PostManager()
        self.assertEqual(post_manager.post_history, {"test_id": "test_path.md"})
        mock_exists.assert_called_once_with(post_manager.M2B_POST_HISTORY_FILEPATH)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=False)
    def test_init_without_history(self, mock_exists, mock_file):
        post_manager = PostManager()
        self.assertEqual(post_manager.post_history, {})
        mock_exists.assert_called_once_with(post_manager.M2B_POST_HISTORY_FILEPATH)

    def test_previously_posted(self):
        post_manager = PostManager()
        post_manager.post_history = {"existing_id": "path.md"}

        self.assertTrue(post_manager.previously_posted("existing_id"))
        self.assertFalse(post_manager.previously_posted("new_id"))

    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    @patch("json.dump")
    def test_record_posting(self, mock_json_dump, mock_file):
        """Test that record_posting correctly updates post_history and saves it to file."""
        post_manager = PostManager()
        post_manager.post_history = {}

        post_manager.record_posting("new_id", "new_path.md")

        self.assertEqual(post_manager.post_history, {"new_id": "new_path.md"})
        # Check that one of the calls to open was with the correct write parameters
        mock_file.assert_any_call(
            post_manager.M2B_POST_HISTORY_FILEPATH, "w", encoding="utf-8"
        )
        mock_json_dump.assert_called_once()


class TestMain(unittest.TestCase):
    @patch("main.mail.read_mail")
    @patch("main.PostManager")
    @patch("main.converter.html_to_blog_md")
    @patch("main.JekyllPost")
    def test_main_processes_new_emails(
        self, mock_jekyll_post, mock_converter, mock_post_manager, mock_read_mail
    ):
        # Setup mocks
        mock_post_manager_instance = MagicMock()
        mock_post_manager_instance.previously_posted.return_value = False
        mock_post_manager.return_value = mock_post_manager_instance

        mock_mail_message = MagicMock()
        mock_mail_message.subject = "Test Subject"
        mock_mail_message.headers = {"message-id": ["test_id"]}
        mock_mail_message.html = "<p>Test content</p>"
        mock_mail_message.from_values.name = "Test Author"
        mock_mail_message.date = "2023-01-01"

        mock_attachments = {"cid1": "attachment1"}
        mock_read_mail.return_value = [(mock_mail_message, mock_attachments)]

        mock_converter.return_value = "Converted markdown content"

        mock_jekyll_post_instance = MagicMock()
        mock_jekyll_post_instance.save.return_value = "/path/to/post.md"
        mock_jekyll_post.return_value = mock_jekyll_post_instance

        # Call the main function
        with patch.dict("os.environ", {"M2B_BLOG_POST_DIR": "/blog/posts"}):
            main()

        # Assertions
        mock_post_manager_instance.previously_posted.assert_called_once_with("test_id")
        mock_converter.assert_called_once_with("<p>Test content</p>", mock_attachments)
        mock_jekyll_post.assert_called_once_with(
            title="Test Subject",
            author="Test Author",
            date="2023-01-01",
            content="Converted markdown content",
        )
        mock_jekyll_post_instance.save.assert_called_once_with(directory="/blog/posts")
        mock_post_manager_instance.record_posting.assert_called_once_with(
            "test_id", "/path/to/post.md"
        )

    @patch("main.mail.read_mail")
    @patch("main.PostManager")
    @patch("main.converter.html_to_blog_md")
    @patch("main.JekyllPost")
    def test_main_skips_previously_posted(
        self, mock_jekyll_post, mock_converter, mock_post_manager, mock_read_mail
    ):
        # Setup mocks
        mock_post_manager_instance = MagicMock()
        mock_post_manager_instance.previously_posted.return_value = True
        mock_post_manager.return_value = mock_post_manager_instance

        mock_mail_message = MagicMock()
        mock_mail_message.subject = "Test Subject"
        mock_mail_message.headers = {"message-id": ["test_id"]}

        mock_read_mail.return_value = [(mock_mail_message, {})]

        # Call the main function
        main()

        # Assertions
        mock_post_manager_instance.previously_posted.assert_called_once_with("test_id")
        mock_converter.assert_not_called()
        mock_jekyll_post.assert_not_called()
        mock_post_manager_instance.record_posting.assert_not_called()


if __name__ == "__main__":
    unittest.main()
