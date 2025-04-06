"""Module to interact with the mailbox."""

import os

from typing import Optional

from imap_tools import MailBox, MailAttachment
from imap_tools.message import MailMessage


def read_mail() -> (
    list[tuple[Optional[MailMessage], Optional[dict[str, MailAttachment]]]]
):
    """Reads latest emails from the mailbox configured by environment variables."""
    mailbox = MailBox(
        os.environ.get("M2B_IMAP_HOST", "localhost"),
        os.environ.get("M2B_IMAP_PORT", "993"),
    ).login(
        os.environ.get("M2B_MAILBOX_USER", ""), os.environ.get("M2B_MAILBOX_PASS", "")
    )

    mailbox.folder.set(os.environ.get("M2B_MAILBOX_FOLDER", "Blog"))

    # NOTE: tune program invocation frequency against post limit
    FETCH_POST_LIMIT = 10
    mails = list(mailbox.fetch(limit=FETCH_POST_LIMIT, reverse=True))

    ret_mails = []
    for mail in mails:
        cid_to_att = {}

        for att in mail.attachments:
            cid_to_att[att.content_id] = att

        ret_mails.append((mail, cid_to_att))

    return ret_mails
