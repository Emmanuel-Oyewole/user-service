from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from uuid import UUID
from datetime import datetime
import secrets
from src.models.users import User
from src.config.security import hash_password, verify_password
from src.utils.exceptions import (
    AlreadyExistsException,
    NotFoundException,
    InvalidCredentialsException,
    DatabaseException,
)


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        role: str = "user",
    ) -> User:
        """Create a new user"""
        try:
            # Check if email already exists
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user:
                raise AlreadyExistsException(
                    message="Email already registered", resource="email"
                )

            # Check if phone already exists
            if phone:
                existing_phone = self.db.query(User).filter(User.phone == phone).first()
                if existing_phone:
                    raise AlreadyExistsException(
                        message="Phone number already registered", resource="phone"
                    )

            # Create user
            user = User(
                email=email,
                password_hash=hash_password(password),
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=role,
                is_active=True,
                is_verified=False,
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            return user

        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseException(f"Database error: {str(e)}")

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)

        if not user:
            raise InvalidCredentialsException()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsException()

        if not user.is_active:
            from src.utils.exceptions import InactiveUserException

            raise InactiveUserException()

        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()

        return user

    def update_password(self, user_id: UUID, new_password: str) -> User:
        """Update user password"""
        user = self.get_user_by_id(user_id)

        if not user:
            raise NotFoundException(message="User not found")

        user.password_hash = hash_password(new_password)
        self.db.commit()
        self.db.refresh(user)

        return user

    def verify_user_email(self, user_id: UUID) -> User:
        """Mark user email as verified"""
        user = self.get_user_by_id(user_id)

        if not user:
            raise NotFoundException(message="User not found")

        user.is_verified = True
        self.db.commit()
        self.db.refresh(user)

        return user

    def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate user account"""
        user = self.get_user_by_id(user_id)

        if not user:
            raise NotFoundException(message="User not found")

        user.is_active = False
        self.db.commit()
        self.db.refresh(user)

        return user

    def activate_user(self, user_id: UUID) -> User:
        """Activate user account"""
        user = self.get_user_by_id(user_id)

        if not user:
            raise NotFoundException(message="User not found")

        user.is_active = True
        self.db.commit()
        self.db.refresh(user)

        return user
