import asyncio
import logging
import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from backend.admin.products import initialize_products_in_db
from backend.admin.security import init_db as init_admin_security_db
from backend.agents.maria import api as maria_api
import osprey_chat_api
import documents_api
from backend.utils.proactive_alerts import ProactiveAlertSystem
from backend.core.auth import set_db as set_auth_db

logger = logging.getLogger(__name__)


class DBProxy:
    def __init__(self):
        self._db = None

    def set(self, db):
        self._db = db

    def __getattr__(self, name):
        if self._db is None:
            raise AttributeError("Database not initialized")
        return getattr(self._db, name)

    def __getitem__(self, name):
        if self._db is None:
            raise KeyError("Database not initialized")
        return self._db[name]


client: Optional[AsyncIOMotorClient] = None
db = DBProxy()
alert_system = None
visa_scheduler = None


async def startup_db_client():
    """Startup event to connect to MongoDB with optimized indexes."""
    global client, db, alert_system, visa_scheduler

    try:
        mongo_url = os.environ.get("MONGODB_URI") or os.environ.get(
            "MONGO_URL", "mongodb://localhost:27017/"
        )
        client = AsyncIOMotorClient(mongo_url)
        db_obj = client[
            os.environ.get("MONGODB_DB") or os.environ.get("DB_NAME", "osprey_immigration_db")
        ]
        db.set(db_obj)

        await client.admin.command("ping")
        logger.info("Successfully connected to MongoDB!")

        alert_system = ProactiveAlertSystem(db)
        logger.info("Proactive Alert System initialized!")

        maria_api.init_db(db)
        logger.info("✅ Maria - Assistente Virtual initialized!")

        osprey_chat_api.init_db(db)
        logger.info("✅ Osprey Legal Chat initialized!")

        documents_api.init_db(db)
        logger.info("✅ Documents API initialized!")

        from backend.reminders_worker import start_reminders_worker
        start_reminders_worker(db)
        logger.info("✅ Reminders Worker initialized!")

        init_admin_security_db(db)
        logger.info("✅ Admin Security (RBAC) initialized!")

        await initialize_products_in_db(db)
        logger.info("✅ Products initialized in MongoDB!")

        await _create_indexes(db)

        await _start_visa_scheduler(db)
        await _start_backup_scheduler()
        await _start_rate_limiter_cleanup()

        # Start reminders worker
        try:
            from reminders_worker import start_reminders_worker
            start_reminders_worker(db)
            logger.info("✅ Reminders Worker started!")
        except Exception as rw_err:
            logger.warning(f"⚠️ Reminders Worker not started: {rw_err}")

        set_auth_db(db)
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        raise


async def shutdown_db_client():
    """Shutdown event to close connections."""
    global client, visa_scheduler
    try:
        if visa_scheduler:
            visa_scheduler.stop()
            logger.info("✅ Visa update scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")

    if client:
        client.close()
        logger.info("✅ MongoDB connection closed")


async def _create_indexes(db):
    try:

        async def safe_create_index(collection, keys, **kwargs):
            try:
                await collection.create_index(keys, **kwargs)
            except Exception as e:
                error_msg = str(e)
                if (
                    "already exists" not in error_msg.lower()
                    and "IndexOptionsConflict" not in error_msg
                    and "IndexKeySpecsConflict" not in error_msg
                ):
                    logger.warning(f"Error creating index {keys} on {collection.name}: {error_msg}")

        await safe_create_index(db.auto_cases, "case_id", unique=True)
        await safe_create_index(db.auto_cases, "user_id")
        await safe_create_index(db.auto_cases, "session_token")
        await safe_create_index(db.auto_cases, "status")
        await safe_create_index(db.auto_cases, "created_at")
        await safe_create_index(db.auto_cases, [("user_id", 1), ("status", 1)])

        await safe_create_index(db.users, "email", unique=True)
        await safe_create_index(db.users, "id", unique=True)

        await safe_create_index(db.documents, "user_id")
        await safe_create_index(db.documents, "document_type")
        await safe_create_index(db.documents, "case_id")
        await safe_create_index(db.documents, [("user_id", 1), ("document_type", 1)])

        await safe_create_index(db.chat_history, "user_id")
        await safe_create_index(db.chat_history, "session_id")
        await safe_create_index(db.chat_history, "created_at")

        await safe_create_index(db.owl_sessions, "session_id", unique=True)
        await safe_create_index(db.owl_sessions, "case_id")
        await safe_create_index(db.owl_sessions, "status")
        await safe_create_index(db.owl_sessions, "created_at")

        await safe_create_index(db.owl_responses, "session_id")
        await safe_create_index(db.owl_responses, "field_id")
        await safe_create_index(db.owl_responses, "timestamp")

        await safe_create_index(db.owl_generated_forms, "session_id")
        await safe_create_index(db.owl_generated_forms, "case_id")
        await safe_create_index(db.owl_generated_forms, "visa_type")
        await safe_create_index(db.owl_generated_forms, "created_at")

        await safe_create_index(db.owl_users, "email", unique=True)
        await safe_create_index(db.owl_users, "user_id", unique=True)
        await safe_create_index(db.owl_users, "created_at")

        await safe_create_index(
            db.payment_transactions, "stripe_session_id", unique=True, sparse=True
        )
        await safe_create_index(db.payment_transactions, "owl_session_id")
        await safe_create_index(db.payment_transactions, "user_email")
        await safe_create_index(db.payment_transactions, "payment_status")
        await safe_create_index(db.payment_transactions, "created_at")

        await safe_create_index(db.owl_downloads, "download_id", unique=True)
        await safe_create_index(db.owl_downloads, "stripe_session_id")
        await safe_create_index(db.owl_downloads, "owl_session_id")

        await safe_create_index(db.maria_conversations, "conversation_id")
        await safe_create_index(db.maria_conversations, "user_id")
        await safe_create_index(db.maria_conversations, "timestamp")
        await safe_create_index(db.maria_conversations, [("conversation_id", 1), ("timestamp", 1)])
        await safe_create_index(db.owl_downloads, "expires_at")

        # B2B Multi-tenant indexes
        await safe_create_index(db.offices, "office_id", unique=True)
        await safe_create_index(db.offices, "is_active")
        await safe_create_index(db.b2b_users, "email", unique=True)
        await safe_create_index(db.b2b_users, "office_id")
        await safe_create_index(db.b2b_users, "user_id", unique=True)
        await safe_create_index(db.b2b_cases, "case_id", unique=True)
        await safe_create_index(db.b2b_cases, "office_id")
        await safe_create_index(db.b2b_cases, "status")
        await safe_create_index(db.b2b_cases, [("office_id", 1), ("status", 1)])
        await safe_create_index(db.osprey_chat_conversations, "office_id")

        # Letters
        await safe_create_index(db.letters, "letter_id", unique=True)
        await safe_create_index(db.letters, "case_id")
        await safe_create_index(db.letters, "office_id")

        # Rate limits per office per day
        await safe_create_index(db.rate_limits, [("office_id", 1), ("date", 1)], unique=True)

        logger.info("Database indexes created successfully for optimized performance!")
    except Exception as index_error:
        logger.warning(f"Some indexes may already exist: {str(index_error)}")


async def _start_visa_scheduler(db):
    try:
        from backend.utils.scheduler import get_visa_update_scheduler

        llm_key = os.environ.get("EMERGENT_LLM_KEY")
        if llm_key:
            global visa_scheduler
            visa_scheduler = get_visa_update_scheduler(db, llm_key)
            visa_scheduler.start()
            logger.info("✅ Visa Update Scheduler started successfully!")
        else:
            logger.warning("⚠️ EMERGENT_LLM_KEY not found - Visa update scheduler not started")
    except Exception as scheduler_error:
        logger.error(f"❌ Failed to start visa update scheduler: {str(scheduler_error)}")


async def _start_backup_scheduler():
    try:
        mongo_url = os.environ.get("MONGODB_URI") or os.environ.get("MONGO_URL", "")
        if "localhost" in mongo_url or "127.0.0.1" in mongo_url:
            from backend.scripts.mongodb_backup import mongodb_backup

            if mongodb_backup.enabled:
                asyncio.create_task(mongodb_backup.schedule_daily_backup())
                logger.info("✅ MongoDB Backup Scheduler started (daily at 3AM UTC)")
            else:
                logger.warning("⚠️ MongoDB Backup Scheduler not started: backup dir not writable")
        else:
            logger.info("ℹ️ MongoDB Backup Scheduler skipped (using managed MongoDB Atlas)")
    except Exception as backup_error:
        logger.warning(f"⚠️ MongoDB Backup Scheduler not started: {str(backup_error)}")


async def _start_rate_limiter_cleanup():
    try:
        from backend.utils.rate_limiter import rate_limiter

        asyncio.create_task(rate_limiter.cleanup_old_entries())
        logger.info("✅ Rate Limiter cleanup task started")
    except Exception as rate_limiter_error:
        logger.warning(f"⚠️ Rate Limiter cleanup not started: {str(rate_limiter_error)}")
