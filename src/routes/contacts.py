from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.schemas import ContactBase,ContactResponse,ContactUpdate
from src.repository import contacts
from src.services.auth import auth_service
from src.database.models import User

router = APIRouter(prefix='/contacts', tags=["contacts"])

@router.get('/', response_model=List[ContactResponse],dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_contacts(db: Session = Depends(get_db),current_user: User = Depends(auth_service.get_current_user)):
    """
    Отримання списку контактів поточного користувача.

    :param db: Сесія бази даних, яка використовується для отримання контактів.
    :type db: Session
    :param current_user: Об'єкт поточного користувача, який використовується для фільтрації контактів.
    :type current_user: User
    :return: Список контактів поточного користувача.
    :rtype: List[Contact]
    """

    contacts_l = await contacts.get_contacts(db,current_user)
    return contacts_l

@router.get('/{contact_id}', response_model=ContactResponse,dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_contact(contact_id: int, db: Session = Depends(get_db),current_user: User = Depends(auth_service.get_current_user)):
    """
    Отримання конкретного контакту поточного користувача за ідентифікатором.

    :param contact_id: Ідентифікатор контакту, який потрібно отримати.
    :type contact_id: int
    :param db: Сесія бази даних, яка використовується для пошуку контакту.
    :type db: Session
    :param current_user: Об'єкт поточного користувача, який використовується для фільтрації контактів.
    :type current_user: User
    :return: Об'єкт контакту поточного користувача з вказаним ідентифікатором.
    :rtype: Contact
    :raises HTTPException 404: Якщо контакт не знайдено.
    """

    contact = await contacts.get_contact(contact_id,current_user,db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.post('/', response_model=ContactResponse,dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(body: ContactBase, db: Session = Depends(get_db),current_user: User = Depends(auth_service.get_current_user)):
    """
    Створення нового контакту для поточного користувача.

    :param body: Дані нового контакту.
    :type body: ContactBase
    :param db: Сесія бази даних, яка використовується для збереження нового контакту.
    :type db: Session
    :param current_user: Об'єкт поточного користувача, який використовується для прив'язки контакту до користувача.
    :type current_user: User
    :return: Об'єкт нового контакту.
    :rtype: Contact
    """

    return await contacts.create_contact(body, current_user, db)

@router.patch('/{contact_id}', response_model=ContactResponse,dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_cont(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Оновлення існуючого контакту.

    :param body: Нові дані для оновлення контакту.
    :type body: ContactUpdate
    :param contact_id: Ідентифікатор контакту, який потрібно оновити.
    :type contact_id: int
    :param db: Сесія бази даних, яка використовується для оновлення контакту.
    :type db: Session
    :param current_user: Об'єкт поточного користувача, який використовується для перевірки прав доступу до контакту.
    :type current_user: User
    :return: Оновлений об'єкт контакту.
    :rtype: Contact
    :raises HTTPException 404: Якщо контакт не знайдено.
    """
     
    contact = await contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.delete('/{contact_id}', response_model=ContactResponse,dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Видалення контакту.

    :param contact_id: Ідентифікатор контакту, який потрібно видалити.
    :type contact_id: int
    :param db: Сесія бази даних, яка використовується для видалення контакту.
    :type db: Session
    :param current_user: Об'єкт поточного користувача, який використовується для перевірки прав доступу до контакту.
    :type current_user: User
    :return: Повідомлення про успішне видалення контакту.
    :rtype: str
    :raises HTTPException 404: Якщо контакт не знайдено.
    """

    tag = await contacts.delete_contact(contact_id, current_user, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return tag

@router.get('/birthdays/',response_model=List[ContactResponse],dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_birth(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Отримання списку народжень контактів користувача.

    :param db: Сесія бази даних, яка використовується для пошуку контактів.
    :type db: Session
    :param current_user: Об'єкт поточного користувача, для якого отримуються контакти з днями народження.
    :type current_user: User
    :return: Список контактів з днями народження для поточного користувача.
    :rtype: List[Contact]
    """

    birthday = await contacts.get_birthdays(current_user,db)

    if birthday:
        return birthday
    else:
        return []
    
@router.get('/search/',response_model=List[ContactResponse],dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def search_contacts(query: str, current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    Пошук контактів.

    :param query: Запит для пошуку контактів.
    :type query: str
    :param db: Сесія бази даних, яка використовується для пошуку контактів.
    :type db: Session
    :param current_user: Об'єкт поточного користувача, для якого виконується пошук контактів.
    :type current_user: User
    :return: Список контактів, що відповідають запиту.
    :rtype: List[Contact]
    """

    search_results = await contacts.find_contact(query,current_user,db)
    if not search_results:
        return []
    return search_results