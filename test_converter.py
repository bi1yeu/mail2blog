import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
from imap_tools import MailAttachment
from converter import html_to_blog_md


class TestHtmlToBlogMd(unittest.TestCase):
    @patch("converter.md")
    @patch("converter.os.environ.get")
    @patch("converter.open", new_callable=mock_open)
    @patch("converter._convert_image_to_jpeg")
    def test_html_to_blog_md_basic(
        self, mock_convert, mock_file, mock_env_get, mock_md
    ):
        # Setup
        mock_env_get.return_value = "assets"
        mock_md.return_value = "# Converted Content\n\nWith image: ![image](cid:123)"

        html = "<h1>Test HTML</h1>"
        attachment = MagicMock(spec=MailAttachment)
        attachment.content_type = "image/jpeg"
        attachment.filename = "test.jpg"
        attachment.payload = b"image_data"

        attachments_dict = {"123": attachment}

        # Call the function
        result = html_to_blog_md(html, attachments_dict)

        # Assertions
        mock_md.assert_called_once_with(html)
        mock_env_get.assert_called_once_with("M2B_BLOG_ASSETS_DIR")
        mock_file.assert_called_once_with(
            os.path.join("assets", "123.test.jpg.jpeg"), "wb"
        )
        mock_file().write.assert_called_once_with(b"image_data")
        mock_convert.assert_called_once_with(
            os.path.join("assets", "123.test.jpg.jpeg"),
            os.path.join("assets", "123.test.jpg.jpeg"),
        )
        self.assertEqual(
            result,
            "# Converted Content\n\nWith image: ![image]({{ site.baseurl }}/assets/123.test.jpg.jpeg)",
        )

    @patch("converter.md")
    @patch("converter.os.environ.get")
    @patch("converter.open", new_callable=mock_open)
    @patch("converter._convert_image_to_jpeg")
    def test_html_to_blog_md_multiple_attachments(
        self, mock_convert, mock_file, mock_env_get, mock_md
    ):
        # Setup
        mock_env_get.return_value = "assets"
        mock_md.return_value = "# Content\n\nImage1: ![](cid:123)\nImage2: ![](cid:456)"

        html = "<h1>Test HTML</h1>"

        attachment1 = MagicMock(spec=MailAttachment)
        attachment1.content_type = "image/png"
        attachment1.filename = "image1.png"
        attachment1.payload = b"image1_data"

        attachment2 = MagicMock(spec=MailAttachment)
        attachment2.content_type = "image/jpeg"
        attachment2.filename = "image2.jpg"
        attachment2.payload = b"image2_data"

        attachments_dict = {"123": attachment1, "456": attachment2}

        # Call the function
        result = html_to_blog_md(html, attachments_dict)

        # Assertions
        self.assertEqual(mock_file.call_count, 2)
        self.assertEqual(mock_convert.call_count, 2)
        self.assertEqual(
            result,
            "# Content\n\nImage1: ![]({{ site.baseurl }}/assets/123.image1.png.jpeg)\nImage2: ![]({{ site.baseurl }}/assets/456.image2.jpg.jpeg)",
        )

    @patch("converter.md")
    @patch("converter.os.environ.get")
    @patch("converter.open", new_callable=mock_open)
    @patch("converter._convert_image_to_jpeg")
    def test_html_to_blog_md_non_image_attachment(
        self, mock_convert, mock_file, mock_env_get, mock_md
    ):
        # Setup
        mock_env_get.return_value = "assets"
        mock_md.return_value = "# Content\n\nWith attachment: [file](cid:123)"

        html = "<h1>Test HTML</h1>"

        attachment = MagicMock(spec=MailAttachment)
        attachment.content_type = "application/pdf"
        attachment.filename = "document.pdf"
        attachment.payload = b"pdf_data"

        attachments_dict = {"123": attachment}

        # Call the function
        result = html_to_blog_md(html, attachments_dict)

        # Assertions
        mock_file.assert_called_once_with(
            os.path.join("assets", "123.document.pdf"), "wb"
        )
        # PDF should NOT be converted
        mock_convert.assert_not_called()
        self.assertEqual(
            result,
            "# Content\n\nWith attachment: [file]({{ site.baseurl }}/assets/123.document.pdf)",
        )

    @patch("converter.md")
    @patch("converter.os.environ.get")
    @patch("converter.open", new_callable=mock_open)
    @patch("converter._convert_image_to_jpeg")
    def test_html_to_blog_md_gif_attachment(
        self, mock_convert, mock_file, mock_env_get, mock_md
    ):
        # Setup
        mock_env_get.return_value = "assets"
        mock_md.return_value = "# Content\n\nWith GIF: ![animation](cid:123)"

        html = "<h1>Test HTML</h1>"

        attachment = MagicMock(spec=MailAttachment)
        attachment.content_type = "image/gif"
        attachment.filename = "animation.gif"
        attachment.payload = b"gif_data"

        attachments_dict = {"123": attachment}

        # Call the function
        result = html_to_blog_md(html, attachments_dict)

        # Assertions
        mock_file.assert_called_once_with(
            os.path.join("assets", "123.animation.gif"), "wb"
        )
        # GIF should NOT be converted
        mock_convert.assert_not_called()
        self.assertEqual(
            result,
            "# Content\n\nWith GIF: ![animation]({{ site.baseurl }}/assets/123.animation.gif)",
        )

    @patch("converter.md")
    @patch("converter.os.environ.get")
    @patch("converter.open", new_callable=mock_open)
    @patch("converter._convert_image_to_jpeg")
    def test_html_to_blog_md_no_attachments(
        self, mock_convert, mock_file, mock_env_get, mock_md
    ):
        # Setup
        mock_env_get.return_value = "assets"
        mock_md.return_value = "# Just Content\n\nNo images here."

        html = "<h1>Test HTML</h1>"
        attachments_dict = {}

        # Call the function
        result = html_to_blog_md(html, attachments_dict)

        # Assertions
        mock_md.assert_called_once_with(html)
        mock_file.assert_not_called()
        mock_convert.assert_not_called()
        self.assertEqual(result, "# Just Content\n\nNo images here.")

    @patch("converter.md")
    @patch("converter.os.environ.get")
    def test_html_to_blog_md_custom_assets_dir(self, mock_env_get, mock_md):
        # Setup
        mock_env_get.return_value = "custom_assets_dir"
        mock_md.return_value = "Content"

        html = "<p>Test</p>"
        attachments_dict = {}

        # Call the function with mocked file operations
        with patch("converter.open", new_callable=mock_open) as mock_file:
            with patch("converter._convert_image_to_jpeg") as mock_convert:
                html_to_blog_md(html, attachments_dict)

        # Assertions
        mock_env_get.assert_called_once_with("M2B_BLOG_ASSETS_DIR")
