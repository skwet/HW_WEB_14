from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database.models import Contact,User
from src.schemas import ContactBase
from datetime import datetime,timedelta


async def get_contacts(db: Session,user: User) -> List[Contact]:
    """
    Отримує контакти для зазначеного користувача.

    :param db: Об'єкт сеансу бази даних.
    :type db: Session
    :param user: Користувач, для якого потрібно отримати контакти.
    :type user: User
    :return: Список контактів, пов'язаних із заданим користувачем.
    :rtype: List[Contact]
    """

    return db.query(Contact).filter(Contact.user_id == user.id).all()

async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Отримує контакт з бази даних за заданим ідентифікатором контакту та користувачем.

    :param contact_id: Ідентифікатор контакту, який потрібно отримати.
    :type contact_id: int
    :param user: Користувач, для якого потрібно отримати контакт.
    :type user: User
    :param db: Об'єкт сеансу бази даних.
    :type db: Session
    :return: Знайдений контакт.
    :rtype: Contact
    """

    return db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()


async def create_contact(body: ContactBase, user: User, db: Session) -> Contact:
    """
    Створює новий контакт y базі даних.

    :param body: Об'єкт, що містить дані для створення контакту.
    :type body: ContactBase
    :param user: Об'єкт, користувач, для якого створюється контакт.
    :type user: User
    :param db: Об'єкт сеансу бази даних.
    :type db: Session
    :return: Створений контакт.
    :rtype: Contact
    """

    contact = Contact(first_name=body.first_name,
                  last_name = body.last_name,
                  email = body.email,
                  phone_num = body.phone_num,
                  birthday = body.birthday, #.strftime("%Y-%m-%d")
                  user_id = user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def update_contact(contact_id: int, body: ContactBase, user: User, db: Session) -> Contact | None:
    """
    Оновлює контакт з вказаним ідентифікатором для користувача.

    :param contact_id: Ідентифікатор контакту, який потрібно оновити.
    :type contact_id: int
    :param body: Об'єкт, який містить дані для оновлення контакту.
    :type body: ContactBase
    :param user: Об'єкт, користувач, якому належить контакт.
    :type user: User
    :param db: Об'єкт сеансу бази даних.
    :type db: Session
    :return: Оновлений об'єкт контакту або None, якщо контакт не знайдено.
    :rtype: Union[Contact, None]
    """

    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.email = body.email
        contact.phone_num = body.phone_num

        db.commit()
        
        return contact

    
async def delete_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Видаляє контакт користувача з бази даних.

    :param contact_id: Ідентифікатор контакту, який потрібно видалити.
    :type contact_id: int
    :param user: Користувач, якому належить контакт.
    :type user: User
    :param db: Об'єкт сеансу бази даних.
    :type db: Session
    :return: Видалений контакт, якщо він існує, або None, якщо контакт не знайдено.
    :rtype: Optional[Contact]
    """

    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_birthdays(user: User, db: Session) -> Contact | None:
    """
    Отримує дні народження контактів користувача, які відбудуться протягом наступного тижня.

    :param user: Користувач, для якого потрібно отримати дні народження контактів.
    :type user: User
    :param db: Об'єкт сеансу бази даних.
    :type db: Session
    :return: Список контактів, у яких день народження відбудеться протягом наступного тижня. Якщо немає жодного контакту, 
             день народження якого відповідає критеріям, повертається None.
    :rtype: Union[Contact, None]
    """

    today = datetime.now().date()

    end = today + timedelta(days=7)

    birthday_contacts = []

    for contact in db.query(Contact).filter_by(user_id = user.id).all():
        contact_birthday = contact.birthday.replace(year=today.year)
        if today <= contact_birthday <= end:
            birthday_contacts.append(contact)

    return birthday_contacts

async def find_contact(query: str, user: User, db: Session) -> Contact:
    """
    Пошук контакту.

    :param query: Запит для пошуку контакту.
    :type query: str
    :param user: Користувач, для якого відбувається пошук контакту.
    :type user: User
    :param db: Об'єкт сеансу бази даних.
    :type db: Session
    :return: Знайдені контакти, що відповідають запиту.
    :rtype: List[Contact]
    """
     
    results = db.query(Contact).filter(
        (Contact.user_id == user.id) &
        (Contact.first_name.ilike(f"%{query}%") |
         Contact.last_name.ilike(f"%{query}%") |
         Contact.email.ilike(f"%{query}%"))
    ).all()
    return results