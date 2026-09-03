import base64
import mimetypes
import os
from email.message import EmailMessage

from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from communication_auth.gmail_auth import get_gmail_credentials


class GmailTool:
    """
    Gmail communication tool.

    Sends real emails through the Gmail API.

    OAuth authentication is handled by gmail_auth.py.
    User approval is handled before this tool is called.
    """

    def __init__(self):
        """
        Initialize the Gmail tool.

        Real Gmail sending is enabled.
        """

        self.dry_run = False

    # =====================================================
    # SEND EMAIL
    # =====================================================

    def send_email(
        self,
        to: str,
        subject: str,
        message: str,
        cc: str | None = None,
        bcc: str | None = None,
        attachments: list[str] | None = None,
    ) -> dict:
        """
        Send an actual email through the Gmail API.
        """

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        to = str(to).strip() if to else ""
        subject = str(subject).strip() if subject else ""
        message = str(message).strip() if message else ""

        if not to:
            raise ValueError(
                "Recipient email address is required."
            )

        if not subject:
            raise ValueError(
                "Email subject is required."
            )

        if not message:
            raise ValueError(
                "Email message is required."
            )

        attachments = attachments or []

        # -------------------------------------------------
        # SAFETY CHECK
        # -------------------------------------------------

        if self.dry_run:
            raise RuntimeError(
                "GmailTool is unexpectedly running "
                "in dry-run mode."
            )

        # -------------------------------------------------
        # AUTHENTICATION
        # -------------------------------------------------

        print(
            "[GMAIL] Authenticating with Gmail..."
        )

        try:
            credentials = get_gmail_credentials()

        except RefreshError as error:
            print(
                "[GMAIL] OAuth token refresh failed."
            )

            raise RuntimeError(
                "Gmail authorization has expired or "
                "been revoked. Please re-authorize "
                "your Gmail account."
            ) from error

        except Exception as error:
            print(
                f"[GMAIL] Authentication error: {error}"
            )

            raise RuntimeError(
                "Gmail authentication failed. "
                "Please re-authorize your Gmail account."
            ) from error

        if credentials is None:
            raise RuntimeError(
                "Gmail authentication failed. "
                "No credentials were returned."
            )

        # -------------------------------------------------
        # BUILD GMAIL SERVICE
        # -------------------------------------------------

        print(
            "[GMAIL] Building Gmail API service..."
        )

        try:
            service = build(
                "gmail",
                "v1",
                credentials=credentials,
            )

        except Exception as error:
            print(
                f"[GMAIL] Failed to build Gmail service: "
                f"{error}"
            )

            raise RuntimeError(
                "Unable to connect to the Gmail API. "
                "Please check your Gmail authorization."
            ) from error

        # -------------------------------------------------
        # CREATE EMAIL
        # -------------------------------------------------

        email = EmailMessage()

        email["To"] = to
        email["Subject"] = subject

        if cc:
            email["Cc"] = str(cc).strip()

        if bcc:
            email["Bcc"] = str(bcc).strip()

        email.set_content(message)

        # -------------------------------------------------
        # ATTACHMENTS
        # -------------------------------------------------

        for attachment in attachments:

            attachment = str(attachment).strip()

            if not attachment:
                continue

            if not os.path.isfile(attachment):
                raise FileNotFoundError(
                    f"Attachment not found: {attachment}"
                )

            with open(
                attachment,
                "rb",
            ) as file:
                file_data = file.read()

            filename = os.path.basename(
                attachment
            )

            mime_type, _ = mimetypes.guess_type(
                filename
            )

            if mime_type:
                maintype, subtype = mime_type.split(
                    "/",
                    1,
                )
            else:
                maintype = "application"
                subtype = "octet-stream"

            email.add_attachment(
                file_data,
                maintype=maintype,
                subtype=subtype,
                filename=filename,
            )

        # -------------------------------------------------
        # ENCODE MESSAGE
        # -------------------------------------------------

        encoded_message = (
            base64.urlsafe_b64encode(
                email.as_bytes()
            )
            .decode("utf-8")
        )

        body = {
            "raw": encoded_message
        }

        # -------------------------------------------------
        # SEND THROUGH GMAIL API
        # -------------------------------------------------

        print(
            "[GMAIL] Sending email through Gmail API..."
        )

        try:
            result = (
                service.users()
                .messages()
                .send(
                    userId="me",
                    body=body,
                )
                .execute()
            )

        except HttpError as error:
            print(
                f"[GMAIL] Gmail API error: {error}"
            )

            error_text = str(error).lower()

            if (
                "invalid_grant" in error_text
                or "token has been expired" in error_text
                or "token has been revoked" in error_text
                or "unauthorized" in error_text
            ):
                raise RuntimeError(
                    "Gmail authorization has expired "
                    "or been revoked. Please "
                    "re-authorize your Gmail account."
                ) from error

            raise RuntimeError(
                f"Gmail could not send the email: {error}"
            ) from error

        except RefreshError as error:
            print(
                "[GMAIL] Gmail OAuth refresh failed "
                "during send."
            )

            raise RuntimeError(
                "Gmail authorization has expired "
                "or been revoked. Please "
                "re-authorize your Gmail account."
            ) from error

        except Exception as error:
            print(
                f"[GMAIL] Email sending failed: {error}"
            )

            raise RuntimeError(
                f"Gmail could not send the email: {error}"
            ) from error

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        message_id = result.get("id")

        print(
            "[GMAIL] Email sent successfully."
        )

        return {
            "status": "sent",
            "platform": "gmail",
            "action": "send_email",
            "to": to,
            "cc": cc,
            "bcc": bcc,
            "subject": subject,
            "message_id": message_id,
            "sent": True,
            "message_text": (
                "Email was successfully sent "
                "through Gmail."
            ),
        }