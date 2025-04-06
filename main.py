#!/usr/bin/env python3

import os
import json
import logging
from jekyll import JekyllPost
import mail
import converter

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("mail2blog")


class PostManager:
    M2B_POST_HISTORY_FILEPATH = "./.post_history.json"

    def __init__(self):
        # read post history from json file
        if os.path.exists(self.M2B_POST_HISTORY_FILEPATH):
            with open(self.M2B_POST_HISTORY_FILEPATH, "r", encoding="utf-8") as f:
                self.post_history = json.load(f)
        else:
            self.post_history = {}

    def previously_posted(self, message_id: str) -> bool:
        """
        Check if a message_id has already been processed and recorded in the post history.
        """
        return message_id in self.post_history

    def record_posting(self, message_id: str, filepath: str):
        """
        Record the message_id and the filepath of the saved post in the post history.
        """
        self.post_history[message_id] = filepath
        # save the updated post history to the file
        with open(self.M2B_POST_HISTORY_FILEPATH, "w", encoding="utf-8") as f:
            json.dump(self.post_history, f, indent=4)


if __name__ == "__main__":
    logger.info("Starting mail2blog process")
    post_manager = PostManager()
    for mail_message, attachments_dict in mail.read_mail():
        try:
            # Extract details from the email
            title = mail_message.subject or "Untitled"
            message_id = mail_message.headers["message-id"][0]

            if post_manager.previously_posted(message_id):
                logger.info(
                    f"Not processing email, already posted: {title} ({message_id})"
                )
                continue

            logger.info(f"Processing email: {title} ({message_id})")
            content = converter.html_to_blog_md(mail_message.html, attachments_dict)
            author = mail_message.from_values.name
            date = mail_message.date

            # Create a Jekyll post
            post = JekyllPost(title=title, author=author, date=date, content=content)

            # Save the post to the blog directory and record that it's been posted
            post_dir = os.environ.get("M2B_BLOG_POST_DIR")
            logger.info(f"Saving post '{title}' to {post_dir}")
            post_filepath = post.save(directory=post_dir)
            post_manager.record_posting(message_id, post_filepath)
            logger.info(f"Successfully processed email: {title}")
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}", exc_info=True)
