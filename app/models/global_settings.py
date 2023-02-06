import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from ._mixins import IDMixin

__all__ = [
    "GlobalSettings",
]


class GlobalSettingsUser(Base, IDMixin):
    __tablename__ = "m2m_global_settings_user"

    global_settings_id = sa.Column(UUID(as_uuid=True), ForeignKey("global_settings.id"))
    user_id = sa.Column(UUID(as_uuid=True), ForeignKey("user.id"))


class GlobalSettings(Base, IDMixin):
    __tablename__ = 'global_settings'

    random_email_id_min_length = Column(

    )


