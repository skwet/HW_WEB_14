from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.schemas import UserDB
from dotenv import load_dotenv
import os

load_dotenv()

cloud_name = os.environ.get('CLOUDINARY_NAME')
cloud_key = os.environ.get('CLOUDINARY_API_KEY')
cloud_secret = os.environ.get('CLOUDINARY_API_SECRET')

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDB)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Отримання інформації про поточного користувача.

    :param current_user: Об'єкт поточного користувача.
    :type current_user: User
    :return: Об'єкт поточного користувача.
    :rtype: User
    """
     
    return current_user


@router.patch('/avatar', response_model=UserDB)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),db: Session = Depends(get_db)):
    """
    Оновлення аватара користувача.
    
    :param file: Зображення файлу для оновлення аватара.
    :type file: UploadFile
    :param current_user: Об'єкт поточного користувача, для якого оновлюється аватар.
    :type current_user: User
    :param db: Сесія бази даних, яка використовується для оновлення аватара користувача.
    :type db: Session
    :return: Оновлений об'єкт користувача.
    :rtype: User
    """

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=cloud_key,
        api_secret=cloud_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
