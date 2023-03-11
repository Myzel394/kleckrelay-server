from datetime import datetime
import logging

from sqlalchemy.orm import Session

from app import logger
from app.controllers.api_key import delete_expired_api_keys
from app.controllers.cron_report import (
    create_cron_report, delete_expired_cron_reports,
)
from app.controllers.user import delete_non_verified_users
from app.cron_report_builder import CronReportBuilder
from app.database.dependencies import with_db
from maid_utils.image_proxy import delete_expired_images


def clean_up(
    db: Session,
    report_builder: CronReportBuilder,
) -> None:
    logger.info("Maid: Starting cleanup.")
    logger.info("Maid: Cleaning up expired images.")

    expired_images_count = delete_expired_images(db)

    logger.info(f"Maid: Deleted {expired_images_count} expired images.")

    report_builder.expired_images = expired_images_count

    logger.info("Maid: Cleaning up non-verified old users.")

    non_verified_amount = delete_non_verified_users(db)
    logger.info(f"Maid: Deleted {non_verified_amount} non verified users.")
    report_builder.non_verified_users = non_verified_amount

    reports_amount = delete_expired_cron_reports(db)
    logger.info(f"Maid: Deleted {reports_amount} reports.")
    report_builder.expired_reports = reports_amount

    api_keys_amount = delete_expired_api_keys(db)
    logger.info(f"Maid: Deleted {api_keys_amount} API keys.")
    report_builder.expired_api_keys = api_keys_amount

    logger.info("Maid: Finished cleanup.")


def main() -> None:
    logger.info("Maid: Starting Maid.")

    logger.info("Maid: Getting database.")
    with with_db() as db:
        logger.info("Maid: Got database.")
        report_builder = CronReportBuilder(
            started_at=datetime.utcnow(),
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
            report_builder.finished_at = datetime.utcnow()

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
