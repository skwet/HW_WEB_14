from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
import fastapi.security
from passlib.context import CryptContext
from datetime import date,datetime,timedelta
import datetime
from sqlalchemy.orm import Session
import os 
from dotenv import load_dotenv

from src.database.db import get_db
from src.repository import users as repository_users

load_dotenv()

class Auth:
    """
    Клас Auth відповідає за автентифікацію користувачів.

    Attributes:
        HASH_CONTEXT (CryptContext): Об'єкт CryptContext для хешування паролів.
        ALGORITHM (str): Алгоритм шифрування, отриманий з змінної середовища.
        SECRET (str): Секретний ключ, отриманий з змінної середовища.
        oauth2_scheme (OAuth2PasswordBearer): Схема OAuth2 для аутентифікації через токен.
    """
    HASH_CONTEXT = CryptContext(schemes=['bcrypt'])
    ALGORITHM = os.environ.get('ALGORITHM')
    SECRET = os.environ.get('SECRET')
    oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        """
        Перевірка правильності пароля.

        :param plain_password: Незахешований пароль для перевірки.
        :type plain_password: str
        :param hashed_password: Хешований пароль, з яким порівнюється незахешований пароль.
        :type hashed_password: str
        :return: Повертає True, якщо паролі відповідають один одному, інакше False.
        :rtype: bool
        """

        return self.HASH_CONTEXT.verify(plain_password, hashed_password)
    
    def hash_password(self,plain_password: str):
        """
        Хешування пароля.

        :param plain_password: Незахешований пароль для хешування.
        :type plain_password: str
        :return: Хешований пароль.
        :rtype: str
        """
        return self.HASH_CONTEXT.hash(plain_password)
    
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Створення access токену.

        :param data: Інформація, яка включається до токену.
        :type data: dict
        :param expires_delta: Опційний параметр, що визначає термін дії токену.
                            Якщо не вказано, токен буде дійсний протягом 15 хвилин.
        :type expires_delta: Optional[float]
        :return: Згенерований токен доступу.
        :rtype: str
        """
         
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.datetime.now(datetime.timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.datetime.now(datetime.timezone.utc) + timedelta(minutes=15)

        to_encode.update({"iat": datetime.datetime.now(datetime.timezone.utc), 
                          "exp": expire, 
                          "scope": "access_token"})
        
        encoded_access_token = jwt.encode(to_encode, self.SECRET, algorithm=self.ALGORITHM)
        return encoded_access_token
    
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Створення refresh токену.

        :param data: Інформація, яка включається до токену.
        :type data: dict
        :param expires_delta: Опційний параметр, що визначає термін дії токену.
                            Якщо не вказано, токен буде дійсний протягом 7 днів.
        :type expires_delta: Optional[float]
        :return: Згенерований refresh токуну.
        :rtype: str
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.datetime.now(datetime.timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.datetime.now(datetime.timezone.utc) + timedelta(days=7)

        to_encode.update({"iat": datetime.datetime.now(datetime.timezone.utc),
                           "exp": expire, 
                           "scope": "refresh_token"})
        
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET, algorithm=self.ALGORITHM)
        return encoded_refresh_token
    
    async def decode_refresh_token(self, refresh_token: str):
        """
        Декодування токену оновлення.

        :param refresh_token: Refresh токен для декодування.
        :type refresh_token: str
        :return: Електронна адреса користувача, яка згенерувала токен.
        :rtype: str
        :raises HTTPException 401: Якщо токен або його область недійсні.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Отримання поточного користувача.

        :param token: Access токен для перевірки автентифікації користувача.
        :type token: str
        :param db: Сесія бази даних, яка використовується для пошуку користувача.
        :type db: Session
        :return: Користувач, який здійснив запит з поточним access токеном.
        :rtype: User
        :raises HTTPException 401: Якщо токен або його область недійсні або користувач не знайдений.
        """

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    def create_email_token(self, data: dict):
        """
        Створення токену електронної пошти.

        :param data: Інформація, яка включається до токену.
        :type data: dict
        :return: Згенерований токен електронної пошти.
        :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.datetime.now(datetime.timezone.utc) + timedelta(days=7)
        to_encode.update({'iat': datetime.datetime.now(datetime.timezone.utc), 
                          'exp': expire})
        token = jwt.encode(to_encode, self.SECRET, algorithm=self.ALGORITHM)
        return token
    
    async def get_email_from_token(self, token: str):
        """
        Отримання електронної адреси з токену.

        Цей метод призначений для отримання електронної адреси з токену електронної пошти.

        :param token: Токен електронної пошти для декодування.
        :type token: str
        :return: Електронна адреса, яка відповідає токену.
        :rtype: str
        :raises HTTPException 422: Якщо токен недійсний або не може бути оброблений.
        """
        try:
            payload = jwt.decode(token, self.SECRET, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")

auth_service = Auth()