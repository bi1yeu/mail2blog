import os
from markdownify import markdownify as md
from imap_tools import MailAttachment
from PIL import Image


def _convert_image_to_jpeg(input_path, output_path, max_width=600):
    with Image.open(input_path) as img:
        width, height = img.size
        if width > max_width:
            new_height = int(height * max_width / width)
            img = img.resize((max_width, new_height), Image.LANCZOS)
        img.convert("RGB").save(output_path, "JPEG")


def html_to_blog_md(html: str, attachments_dict: dict[str, MailAttachment]) -> str:
    # convert HTML content to markdown
    content = md(html)
    # save each of the attachments to the target assets directory
    assets_dir = os.environ.get("M2B_BLOG_ASSETS_DIR")
    for cid, att in attachments_dict.items():
        # add cid to filename to mitigate conflicts
        att_filename = f"{cid}.{att.filename}"
        is_image = att.content_type.split("/")[0] == "image"
        is_gif = att.content_type.lower() == "image/gif"

        # Only add .jpeg extension if it's an image but not a GIF
        if is_image and not is_gif:
            att_filename += ".jpeg"

        dest_path = os.path.join(assets_dir, att_filename)
        with open(dest_path, "wb") as dest_file:
            dest_file.write(att.payload)

        # Only convert to JPEG if it's an image but not a GIF
        if is_image and not is_gif:
            _convert_image_to_jpeg(dest_path, dest_path)

        # update the cid src to the path of the attachment file relative to the site base URL and the assets directory
        # TODO: make this generator agnostic; presently specific to jekyll
        att_rel_path = (
            f"{{{{ site.baseurl }}}}/{os.path.basename(assets_dir)}/{att_filename}"
        )
        content = content.replace(f"cid:{cid}", att_rel_path)
    return content
