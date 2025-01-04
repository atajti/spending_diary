import base64
from googleapiclient.discovery import build, Resource
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText


def get_user_email(service: Resource):
    """Retrieve the authenticated user's email address.
    :param service: result of build("gmail", "v1", credentials)
    :return: an e-mail address
    """
    profile = service.users().getProfile(userId='me').execute()
    return profile['emailAddress']


def encode_message(sender: str,
                   to: str,
                   subject: str,
                   message_text: str) -> str:
    """Create a message for an email.
    :param sender: e-mail address
    :param to: e-mail address
    :param subject: subject of the e-mail
    :param message: body of the e-mail
    :return: all e-mail data base64-encoded
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}


def insert_message(service: Resource,
                   message: str,
                   user_id: str = "me"):
    """Insert a message into the user's mailbox.
    :param service: result of build("gmail", "v1", credentials)
    :param message: base64-encoded content of the e-mail, see create_message()
    :param user_id: it should be the string "me"
    :return: all infomation about the message 
    """
    try:
        message = service.users().messages() \
                         .insert(userId=user_id,
                                 body=message) \
                         .execute()
        return message
    except Exception as error:
        raise error


def move_to_inbox(service: Resource,
                  message_id: str,
                  user_id: str = "me"):
    """Add a label to a message.
    :param service: result of build("gmail", "v1", credentials)
    :param message_id: id of a message
    :param user_id: it should be the string "me"
    :return: None
    """
    try:
        msg_labels = {'addLabelIds': ["INBOX", "UNREAD"]}
        message = service.users().messages().modify(userId=user_id,
                                                    id=message_id,
                                                    body=msg_labels) \
                                 .execute()
    except Exception as error:
        raise error


def send_mail_alert(email_content: dict[str,str],
                    credentials: Credentials) -> dict[str, str]:
    """Insert the alert email into the user's inbox
    :param email_content: dict containing subject and body, see analyze.generate_email()
    :param credentials: result of extract.authenticate()
    :return: the message and its metadata
    """
    try:
        service = build("gmail", "v1", credentials=credentials)
        user_email = get_user_email(service)
        raw_message = encode_message(user_email,
                                     f"{user_email[:-10]}+spending_alert@gmail.com",
                                     email_content["subject"],
                                     email_content["body"])
        inserted_message = insert_message(service, raw_message)
        move_to_inbox(service, inserted_message["id"])
    except Exception as error:
        raise error
