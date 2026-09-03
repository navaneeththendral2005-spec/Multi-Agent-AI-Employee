import os

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


# =========================================================
# GMAIL PERMISSIONS
# =========================================================

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

CREDENTIALS_FILE = os.path.join(
    BASE_DIR,
    "credentials",
    "credentials.json"
)

TOKEN_DIR = os.path.join(
    BASE_DIR,
    "tokens"
)

TOKEN_FILE = os.path.join(
    TOKEN_DIR,
    "gmail_token.json"
)


# =========================================================
# TOKEN HELPERS
# =========================================================

def _delete_invalid_token():
    """
    Delete the locally stored Gmail OAuth token.

    This is required when Google reports that the
    refresh token has expired or been revoked.
    """

    if os.path.exists(TOKEN_FILE):
        try:
            os.remove(TOKEN_FILE)

            print(
                "[GMAIL AUTH] Invalid OAuth token removed."
            )

        except OSError as error:
            print(
                "[GMAIL AUTH] Could not remove invalid "
                f"token: {error}"
            )


def _save_credentials(credentials):
    """
    Save Gmail OAuth credentials locally.
    """

    os.makedirs(
        TOKEN_DIR,
        exist_ok=True
    )

    with open(
        TOKEN_FILE,
        "w",
        encoding="utf-8"
    ) as token:

        token.write(
            credentials.to_json()
        )

    print(
        "[GMAIL AUTH] OAuth token saved."
    )


# =========================================================
# FRESH OAUTH AUTHENTICATION
# =========================================================

def _authenticate_with_google():
    """
    Start a fresh Google OAuth authorization flow.

    A browser window will open when authorization is required.
    """

    if not os.path.exists(
        CREDENTIALS_FILE
    ):
        raise FileNotFoundError(
            "Gmail credentials.json was not found at: "
            f"{CREDENTIALS_FILE}"
        )

    print(
        "[GMAIL AUTH] Starting fresh Google OAuth "
        "authorization..."
    )

    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE,
        SCOPES
    )

    credentials = flow.run_local_server(
        port=0
    )

    _save_credentials(
        credentials
    )

    print(
        "[GMAIL AUTH] Google OAuth authorization "
        "completed successfully."
    )

    return credentials


# =========================================================
# GMAIL AUTHENTICATION
# =========================================================

def get_gmail_credentials():
    """
    Return valid Gmail OAuth credentials.

    Authentication flow:

    1. Load existing token.
    2. If valid, use it.
    3. If expired, refresh it.
    4. If the refresh token is expired/revoked,
       delete the stale token.
    5. Start a fresh Google OAuth authorization.
    6. Save the new token.
    """

    credentials = None

    # =====================================================
    # LOAD EXISTING TOKEN
    # =====================================================

    if os.path.exists(
        TOKEN_FILE
    ):

        print(
            "[GMAIL AUTH] Loading saved OAuth token..."
        )

        try:
            credentials = (
                Credentials.from_authorized_user_file(
                    TOKEN_FILE,
                    SCOPES
                )
            )

        except Exception as error:

            print(
                "[GMAIL AUTH] Saved token could not "
                f"be loaded: {error}"
            )

            _delete_invalid_token()

            credentials = None

    # =====================================================
    # VALID TOKEN
    # =====================================================

    if credentials and credentials.valid:

        print(
            "[GMAIL AUTH] Existing OAuth token is valid."
        )

        return credentials

    # =====================================================
    # EXPIRED TOKEN — TRY REFRESH
    # =====================================================

    if credentials and credentials.expired:

        print(
            "[GMAIL AUTH] OAuth token is expired."
        )

        if credentials.refresh_token:

            print(
                "[GMAIL AUTH] Attempting to refresh "
                "OAuth token..."
            )

            try:

                credentials.refresh(
                    Request()
                )

                # Save the refreshed credentials.
                _save_credentials(
                    credentials
                )

                print(
                    "[GMAIL AUTH] OAuth token refreshed "
                    "successfully."
                )

                return credentials

            except RefreshError as error:

                print(
                    "[GMAIL AUTH] OAuth refresh failed."
                )

                print(
                    f"[GMAIL AUTH] Google response: {error}"
                )

                # The refresh token is no longer usable.
                _delete_invalid_token()

                credentials = None

            except Exception as error:

                print(
                    "[GMAIL AUTH] Unexpected OAuth refresh "
                    f"error: {error}"
                )

                _delete_invalid_token()

                credentials = None

        else:

            print(
                "[GMAIL AUTH] No refresh token is available."
            )

            credentials = None

    # =====================================================
    # NO VALID CREDENTIALS
    # =====================================================

    if not credentials or not credentials.valid:

        print(
            "[GMAIL AUTH] Fresh Google authorization "
            "is required."
        )

        credentials = _authenticate_with_google()

    # =====================================================
    # FINAL VALIDATION
    # =====================================================

    if not credentials or not credentials.valid:

        raise RuntimeError(
            "Gmail authentication failed. "
            "Google did not return valid credentials."
        )

    return credentials