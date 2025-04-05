#!/usr/bin/env python3

import os
from jekyll import JekyllPost
import mail

if __name__ == "__main__":
    mail_message = mail.read_mail()

    if not mail_message:
        print("No new emails found.")
        exit(0)

    # Extract details from the email
    title = mail_message.subject or "Untitled"
    content = mail_message.text
    author = mail_message.from_values.name
    date = mail_message.date

    # Create a Jekyll post
    post = JekyllPost(title=title, author=author, date=date, content=content)

    # Save the post to the current directory
    post.save(directory=os.environ.get("M2B_BLOG_POST_DIR"))
