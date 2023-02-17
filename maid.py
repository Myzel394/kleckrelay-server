from datetime import datetime
import logging

from sqlalchemy.orm import Session

from app import logger
from app.controllers.cron_report import create_cron_report
from app.controllers.image_proxy import get_expired_images
from app.controllers.user import delete_user, get_non_verified_users_to_delete
from app.cron_report_builder import CronReportBuilder
from app.database.dependencies import with_db
from app.models.image_proxy import STORAGE_PATH


def clean_up(
    db: Session,
    report_builder: CronReportBuilder,
) -> None:
    logger.info("Maid: Starting cleanup.")
    logger.info("Maid: Cleaning up expired images.")

    expired_images = get_expired_images(db)

    logger.info(f"Maid: Found {len(expired_images)} images to delete.")
    for image in expired_images:
        path = STORAGE_PATH / image.filename

        if path.exists():
            path.unlink()
            logger.info(f"Maid: Deleted {path}.")

    report_builder.expired_images = len(expired_images)

    logger.info("Maid: Cleaning up non-verified old users.")

    users = get_non_verified_users_to_delete(db)

    logger.info(f"Maid: Found {len(users)} users to delete.")
    for user in users:
        delete_user(db, user)
        logger.info(f"Maid: Deleted user {user.id}.")

    report_builder.non_verified_users = len(users)

    logger.info("Maid: Finished cleanup.")


def main() -> None:
    logger.info("Maid: Starting Maid.")

    logger.info("Maid: Getting database.")
    with with_db() as db:
        report_builder = CronReportBuilder(
            started_at=datetime.now(),
        )

        try:
            clean_up(
                db=db,
                report_builder=report_builder,
            )
        except Exception as error:
            logging.error(f"Maid: Error: {error}")
            report_builder.status = "error"
        else:
            report_builder.status = "success"
        finally:
            report_builder.finished_at = datetime.now()

        logger.info("Maid: Creating report.")
        try:
            create_cron_report(
                db,
                report_data=report_builder,
            )
        except Exception as error:
            logging.error(f"Maid: Error: {error}")
            logger.info("Maid: Failed to save report.")
        else:
            logger.info("Maid: Saved report successfully!")

    logger.info("Maid: Finished Maid.")


if __name__ == "__main__":
    main()
