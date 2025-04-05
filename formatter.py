"""Formats mail message HTML as markdown; copies and populates images"""

import os
from markdownify import markdownify as md
from PIL import Image


def _convert_image_to_jpeg(input_path, output_path, max_width=600):
    with Image.open(input_path) as img:
        width, height = img.size
        if width > max_width:
            new_height = int(height * max_width / width)
            img = img.resize((max_width, new_height), Image.LANCZOS)
        img.convert("RGB").save(output_path, "JPEG")


def html_to_blog_md(html: str, attachments_dict: dict) -> str:
    content = md(html)

    # copy each of the attachments to the target assets directory

    assets_dir = os.environ.get("M2B_BLOG_ASSETS_DIR")
    for cid, att_path in attachments_dict.items():
        src_path = os.path.join("./attachments", att_path)
        # NOTE: only handles image attachments
        att_path += ".jpeg"
        dest_path = os.path.join(assets_dir, att_path)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Copy the file
        with open(src_path, "rb") as src_file:
            with open(dest_path, "wb") as dest_file:
                dest_file.write(src_file.read())

        _convert_image_to_jpeg(dest_path, dest_path)

        # update the cid src to the path of the attachment file relative to the site base URL and the assets directory
        # TODO: make this generator agnostic; presently specific to jekyll
        att_rel_path = (
            f"{{{{ site.baseurl }}}}/{os.path.basename(assets_dir)}/{att_path}"
        )
        content = content.replace(f"cid:{cid}", att_rel_path)

    return content
