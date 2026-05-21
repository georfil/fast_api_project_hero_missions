from fastapi import Depends, HTTPException, status
from typing import Annotated
from .db import SessionDep
from .security import oauth_scheme, SECRET_KEY, ALGORITHM
from .models import User
from jose import jwt, JWTError
from sqlmodel import select

def get_current_user(
        token: Annotated[str, Depends(oauth_scheme)],
        session: SessionDep
) -> User:
    """Decode the Bearer JWT and return the matching User.

    Args:
        token: The Bearer JWT extracted from the Authorization header.
        session: The database session used to look up the user.

    Returns:
        The authenticated User instance.

    Raises:
        HTTPException: 401 if the token is invalid, expired, or the user no longer exists.
    """
    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate user credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )

    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception #User doesnt exist in db
    
    return user

#Alias for User Dependency
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_admin(user: CurrentUser) -> User:
    """Verify the current user has admin privileges.

    Args:
        user: The authenticated User instance from get_current_user.

    Returns:
        The authenticated User instance if they are an admin.

    Raises:
        HTTPException: 403 if the user does not have admin permission.
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User doesn't have admin permission to access this resource",
            headers={"WWW-Authenticate":"Bearer"}
        )
    return user

#Alias for Adnin Dependency
AdminUser = Annotated[User, Depends(get_current_admin)]
