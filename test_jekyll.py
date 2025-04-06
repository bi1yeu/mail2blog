import unittest
import os
import datetime
import tempfile
from unittest.mock import patch
from jekyll import JekyllPost


class TestJekyllPost(unittest.TestCase):
    def setUp(self):
        self.title = "Test Post"
        self.author = "Test Author"
        self.date = datetime.datetime(2023, 1, 1, 12, 0, 0)
        self.layout = "post"
        self.categories = ["cat1", "cat2"]
        self.tags = ["tag1", "tag2"]
        self.content = "This is test content."
        self.post = JekyllPost(
            title=self.title,
            author=self.author,
            date=self.date,
            layout=self.layout,
            categories=self.categories,
            tags=self.tags,
            content=self.content,
        )

    def test_init_with_defaults(self):
        """Test initializing with default values."""
        post = JekyllPost()
        self.assertEqual(post.title, "Untitled")
        self.assertEqual(post.author, "Unknown")
        self.assertIsInstance(post.date, datetime.datetime)
        self.assertEqual(post.layout, "post")
        self.assertEqual(post.categories, [])
        self.assertEqual(post.tags, [])
        self.assertEqual(post.content, "")

    def test_init_with_values(self):
        """Test initializing with specific values."""
        self.assertEqual(self.post.title, self.title)
        self.assertEqual(self.post.author, self.author)
        self.assertEqual(self.post.date, self.date)
        self.assertEqual(self.post.layout, self.layout)
        self.assertEqual(self.post.categories, self.categories)
        self.assertEqual(self.post.tags, self.tags)
        self.assertEqual(self.post.content, self.content)

    def test_generate_filename(self):
        """Test filename generation."""
        expected = "2023-01-01-test-post.md"
        self.assertEqual(self.post._generate_filename(), expected)

    def test_generate_front_matter(self):
        """Test YAML front matter generation."""
        expected = (
            "---\n"
            "layout: post\n"
            'title: "Test Post"\n'
            'author: "Test Author"\n'
            "date: 2023-01-01 12:00:00\n"
            "categories: [cat1, cat2]\n"
            "tags: [tag1, tag2]\n"
            "---\n"
        )
        self.assertEqual(self.post._generate_front_matter(), expected)

    def test_generate_front_matter_without_categories_and_tags(self):
        """Test front matter generation without categories and tags."""
        post = JekyllPost(title=self.title, author=self.author, date=self.date)
        expected = (
            "---\n"
            "layout: post\n"
            'title: "Test Post"\n'
            'author: "Test Author"\n'
            "date: 2023-01-01 12:00:00\n"
            "---\n"
        )
        self.assertEqual(post._generate_front_matter(), expected)

    def test_generate_post(self):
        """Test complete post generation."""
        front_matter = self.post._generate_front_matter()
        expected = front_matter + self.content
        self.assertEqual(self.post.generate_post(), expected)

    def test_save(self):
        """Test saving post to a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = self.post.save(temp_dir)
            expected_path = os.path.join(temp_dir, "2023-01-01-test-post.md")
            self.assertEqual(filepath, expected_path)
            self.assertTrue(os.path.exists(filepath))

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertEqual(content, self.post.generate_post())

    @patch("os.path.expanduser")
    def test_save_with_user_path(self, mock_expanduser):
        """Test saving post with a path containing a user directory."""
        mock_expanduser.return_value = "/home/user/blog"

        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            filepath = self.post.save("~/blog")

            mock_expanduser.assert_called_once_with("~/blog")
            expected_path = os.path.join("/home/user/blog", "2023-01-01-test-post.md")
            self.assertEqual(filepath, expected_path)
            mock_file.assert_called_once_with(expected_path, "w", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
