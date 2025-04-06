"""Module to interact with the mailbox."""

import os

from typing import Optional, Tuple

from imap_tools import MailBox, MailAttachment
from imap_tools.message import MailMessage


def read_mail() -> Tuple[Optional[MailMessage], Optional[dict[str, MailAttachment]]]:
    """Reads latest email from the mailbox configured by environment variables."""
    mailbox = MailBox(
        os.environ.get("M2B_IMAP_HOST", "localhost"),
        os.environ.get("M2B_IMAP_PORT", "993"),
    ).login(
        os.environ.get("M2B_MAILBOX_USER", ""), os.environ.get("M2B_MAILBOX_PASS", "")
    )

    mailbox.folder.set(os.environ.get("M2B_MAILBOX_FOLDER", "Blog"))

    # NOTE: this assumes the program is run at least as frequently as posts are
    # emailed. e.g. if you run m2b on a cron every 5 minutes, but send two post
    # emails in that time, only one of them would be published.
    mails = list(mailbox.fetch(limit=1, reverse=True))

    if len(mails) == 0:
        return None, None

    mail = mails[0]

    cid_to_att = {}

    for att in mail.attachments:
        cid_to_att[att.content_id] = att

    return mail, cid_to_att
