"""Module to interact with the mailbox."""

import os

from typing import Optional

from imap_tools import MailBox
from imap_tools.message import MailMessage


def read_mail() -> Optional[MailMessage]:
    """Reads latest email from the mailbox configured by environment variables."""
    mailbox = MailBox(
        os.environ.get("M2B_IMAP_HOST", "localhost"),
        os.environ.get("M2B_IMAP_PORT", "993"),
    ).login(
        os.environ.get("M2B_MAILBOX_USER", ""), os.environ.get("M2B_MAILBOX_PASS", "")
    )

    mailbox.folder.set(os.environ.get("M2B_MAILBOX_FOLDER", "Blog"))

    mails = list(mailbox.fetch(limit=1, reverse=True))

    if len(mails) == 0:
        return None

    mail = mails[0]

    attachment_map = _download_attachments(mail)

    return mail, attachment_map


def _download_attachments(mail: MailMessage) -> dict:
    attd = {}

    attachments_dir = "./attachments"
    os.makedirs(attachments_dir, exist_ok=True)
    for att in mail.attachments:
        filename = f"{att.content_id}.{att.filename}"
        with open(f"{attachments_dir}/{filename}", "wb") as f:
            f.write(att.payload)

        attd[att.content_id] = filename

    return attd
