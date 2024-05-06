from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Реєстрація нового користувача.

    :param body: Дані нового користувача.
    :type body: UserModel
    :param background_tasks: Об'єкт для виконання фонових завдань.
    :type background_tasks: BackgroundTasks
    :param request: Запит, що містить інформацію про базовий URL.
    :type request: Request
    :param db: Сесія бази даних, яка використовується для збереження нового користувача.
    :type db: Session
    :return: Об'єкт, що містить нового користувача та детальну інформацію про успішне створення облікового запису.
    :rtype: Dict[str, Union[User, str]]
    :raises HTTPException 409: Якщо обліковий запис вже існує.
    """
     
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.hash_password(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Аутентифікація користувача.

    :param body: Форма запиту, що містить ім'я користувача та пароль.
    :type body: OAuth2PasswordRequestForm
    :param db: Сесія бази даних, яка використовується для перевірки користувача та оновлення токену.
    :type db: Session
    :return: Об'єкт, що містить токени доступу та оновлення.
    :rtype: Dict[str, str]
    :raises HTTPException 401: Якщо ім'я користувача або пароль неправильні або електронна адреса не підтверджена.
    """

    user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Оновлення refresh токену.

    :param credentials: Об'єкт, що містить HTTP-аутентифікаційні дані (refresh токен).
    :type credentials: HTTPAuthorizationCredentials
    :param db: Сесія бази даних, яка використовується для перевірки користувача та оновлення токену.
    :type db: Session
    :return: Об'єкт, що містить нові токени доступу та оновлення.
    :rtype: TokenModel
    :raises HTTPException 401: Якщо токен оновлення недійсний або не відповідає поточному користувачу.
    """

    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
   
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Підтвердження електронної адреси.
    
    :param token: Токен для підтвердження електронної адреси.
    :type token: str
    :param db: Сесія бази даних, яка використовується для перевірки користувача та позначення адреси як підтвердженої.
    :type db: Session
    :return: Об'єкт, що містить повідомлення про статус підтвердження електронної адреси.
    :rtype: Dict[str, str]
    :raises HTTPException 400: Якщо сталася помилка під час підтвердження електронної адреси.
    """

    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}