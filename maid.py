from app import logger
from app.controllers.image_proxy import get_expired_images
from app.controllers.user import delete_user, get_non_verified_users_to_delete
from app.database.dependencies import with_db
from app.models.image_proxy import STORAGE_PATH


def main():
    logger.info("Maid: Starting cleanup.")

    with with_db() as db:
        logger.info("Maid: Cleaning up expired images.")

        expired_images = get_expired_images(db)

        logger.info(f"Maid: Found {len(expired_images)} images to delete.")
        for image in expired_images:
            path = STORAGE_PATH / image.filename

            if path.exists():
                path.unlink()
                logger.info(f"Maid: Deleted {path}.")


        logger.info("Maid: Cleaning up non-verified old users.")

        users = get_non_verified_users_to_delete(db)

        logger.info(f"Maid: Found {len(users)} users to delete.")
        for user in users:
            delete_user(db, user)
            logger.info(f"Maid: Deleted user {user.id}.")

    logger.info("Maid: Finished cleanup.")


if __name__ == "__main__":
    main()
