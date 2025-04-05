"""Module to generate Jekyll posts with YAML front matter."""

import os
import re
import datetime


def slugify(title: str) -> str:
    """Generate a URL-friendly slug from the title."""
    slug = re.sub(r"[\W_]+", "-", title.lower()).strip("-")
    return slug


class JekyllPost:
    """JekyllPost with YAML front matter for Jekyll blog posts."""

    def __init__(
        self,
        title=None,
        author=None,
        date=None,
        layout="post",
        categories=None,
        tags=None,
        content="",
    ):
        self.title = title or "Untitled"
        self.author = author or "Unknown"
        self.date = date or datetime.datetime.now()
        self.layout = layout
        self.categories = categories if categories is not None else []
        self.tags = tags if tags is not None else []
        self.content = content

    def generate_filename(self):
        """Generate a filename in the format YYYY-MM-DD-title.md."""
        date_str = self.date.strftime("%Y-%m-%d")
        title_slug = slugify(self.title)
        return f"{date_str}-{title_slug}.md"

    def _generate_front_matter(self):
        """Build the YAML front matter."""
        fm = [
            "---",
            f"layout: {self.layout}",
            f'title: "{self.title}"',
            f'author: "{self.author}"',
            f"date: {self.date.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        if self.categories:
            fm.append(f"categories: [{', '.join(self.categories)}]")
        if self.tags:
            fm.append(f"tags: [{', '.join(self.tags)}]")
        fm.append("---\n")
        return "\n".join(fm)

    def generate_post(self):
        """Combine the front matter and content."""
        return self._generate_front_matter() + self.content

    def save(self, directory="."):
        """Save the post to the given directory."""
        filename = self.generate_filename()
        # Expand the "~" to an absolute path.
        directory = os.path.expanduser(directory)
        filepath = os.path.join(directory, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.generate_post())
        print(f"Post saved to {filepath}")
        return filepath
