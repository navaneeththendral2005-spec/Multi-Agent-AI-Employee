from communication_tools.gmail_tool import GmailTool

class CommunicationRouter:
    """
    Routes communication requests to the appropriate
    email platform.

    Supported platforms:
    - Gmail

    Real email sending is supported through the
    respective communication tools.
    """

    def __init__(self):
        # -------------------------------------------------
        # EMAIL TOOLS
        # -------------------------------------------------

        self.gmail = GmailTool()
    # -----------------------------------------------------
    # SEND EMAIL
    # -----------------------------------------------------

    def send_email(
        self,
        platform: str,
        to: str,
        subject: str,
        message: str,
        cc: str | None = None,
        bcc: str | None = None,
        attachments: list[str] | None = None
    ) -> dict:
        """
        Route an email request to Gmail.
        """

        # -------------------------------------------------
        # VALIDATE PLATFORM
        # -------------------------------------------------

        if not platform:
            raise ValueError(
                "Email platform is required. "
                "Use Gmail."
            )

        platform = (
            platform
            .strip()
            .lower()
        )

        # -------------------------------------------------
        # GMAIL
        # -------------------------------------------------

        if platform == "gmail":

            return self.gmail.send_email(
                to=to,
                subject=subject,
                message=message,
                cc=cc,
                bcc=bcc,
                attachments=attachments
            )

        # -------------------------------------------------
        # UNSUPPORTED PLATFORM
        # -------------------------------------------------

        raise ValueError(
            "Unsupported communication platform: "
            f"{platform}. "
            "Use Gmail."
        )