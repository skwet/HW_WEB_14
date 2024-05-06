from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service

import os
from dotenv import load_dotenv

load_dotenv()

username = os.environ.get('MAIL_USERNAME')
password = os.environ.get('MAIL_PASSWORD')
mail_from = os.environ.get('MAIL_FROM')
port = os.environ.get('MAIL_PORT')
server = os.environ.get('MAIL_SERVER')

conf = ConnectionConfig(
    MAIL_USERNAME=username,
    MAIL_PASSWORD=password,
    MAIL_FROM=mail_from,
    MAIL_PORT=port,
    MAIL_SERVER=server,
    MAIL_FROM_NAME="Example email",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent/'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Надіслати електронний лист для підтвердження електронної адреси.
    
    :param email: Електронна адреса, на яку буде надіслано лист.
    :type email: EmailStr
    :param username: Ім'я користувача, яке буде включено до листа.
    :type username: str
    :param host: Хост або URL-адреса, яка буде використана для підтвердження адреси.
    :type host: str
    :raises ConnectionErrors: Якщо виникає помилка під час надсилання листа.
    """

    try:
        token_verification = auth_service.create_email_token({'sub': email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name='email_template.html')
    except ConnectionErrors as err:
        print(err)

