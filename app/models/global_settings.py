import sqlalchemy as sa

from app.database.base import Base
from ._mixins import IDMixin

__all__ = [
    "GlobalSettings",
]


# All fields in this model must be named in the snake case version of the corresponding
# `default_life_constants` field
# Example: `ALLOW_STATISTICS` in `default_life_constants` must be named `allow_statistics` in
# this model
# All fields must be nullable as a `NULL` value means that the field should use the given
# environment variable or the default value from `default_life_constants`

# `ADMINS` will NOT be included in this model as being an admin should be read only
class GlobalSettings(Base, IDMixin):
    __tablename__ = 'global_settings'

    random_email_id_min_length = sa.Column(
        sa.SmallInteger(),
        default=None,
        nullable=True,
    )
    random_email_id_chars = sa.Column(
        sa.String(
            length=1023,
        ),
        default=None,
        nullable=True,
    )
    random_email_length_increase_on_percentage = sa.Column(
        sa.Float(),
        default=None,
        nullable=True,
    )
    custom_email_suffix_length = sa.Column(
        sa.SmallInteger(),
        default=None,
        nullable=True,
    )
    custom_email_suffix_chars = sa.Column(
        sa.String(
            length=1023,
        ),
        default=None,
        nullable=True,
    )
    image_proxy_storage_life_time_in_hours = sa.Column(
        # A `SmallInteger` would limit the user to a maximum of about 3 years,
        # but we want to allow the user to set a higher timeout.
        sa.Integer(),
        default=None,
        nullable=True,
    )
    enable_image_proxy = sa.Column(
        sa.Boolean(),
        default=None,
        nullable=True,
    )
    user_email_enable_disposable_emails = sa.Column(
        sa.Boolean(),
        default=None,
        nullable=True,
    )
    user_email_enable_other_relays = sa.Column(
        sa.Boolean(),
        default=None,
        nullable=True,
    )
    allow_statistics = sa.Column(
        sa.Boolean(),
        default=None,
        nullable=True,
    )

