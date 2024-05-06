from sqlalchemy.orm import Session
from libgravatar import Gravatar

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Отримання користувача за email.

    :param email: Email користувача для пошуку.
    :type email: str
    :param db: Об'єкт сесії бази даних.
    :type db: Session
    :return: Користувач, якщо він існує у базі даних за вказаним email, або None, якщо користувач не знайдений.
    :rtype: Optional[User]
    """

    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Створення нового користувача.

    :param body: Модель користувача, що містить дані для створення нового користувача.
    :type body: UserModel
    :param db: Об'єкт сесії бази даних.
    :type db: Session
    :return: Новостворений користувач.
    :rtype: User
    """

    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Оновлення токену користувача.

    :param user: Користувач, для якого оновлюється токен.
    :type user: User
    :param token: Новий токен доступу користувача. Якщо значення None, токен буде видалено.
    :type token: Optional[str]
    :param db: Об'єкт сесії бази даних.
    :type db: Session
    :return: None
    :rtype: None
    """

    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Підтвердження email користувача.

    :param email: Email користувача, якому потрібно підтвердити.
    :type email: str
    :param db: Об'єкт сесії бази даних.
    :type db: Session
    :return: None
    :rtype: None
    """

    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

async def update_avatar(email, url: str, db: Session) -> User:
    """
    Оновлення аватара користувача.

    :param email: Email користувача, для якого оновлюється аватар.
    :type email: str
    :param url: Новий URL аватара користувача.
    :type url: str
    :param db: Об'єкт сесії бази даних.
    :type db: Session
    :return: Користувач з оновленим аватаром.
    :rtype: User
    """

    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user