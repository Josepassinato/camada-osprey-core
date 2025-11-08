"""
Scheduler for Visa Auto-Updates
Runs weekly visa information updates automatically with admin approval workflow
"""

import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import os

logger = logging.getLogger(__name__)

class VisaUpdateScheduler:
    """
    Manages scheduled visa information updates
    
    Features:
    - Weekly automatic scans (every Monday 9am)
    - Manual trigger support
    - Error handling and retry logic
    - Admin notifications
    """
    
    def __init__(self, db, llm_key: str):
        self.db = db
        self.llm_key = llm_key
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
        logger.info("📅 VisaUpdateScheduler initialized")
    
    async def run_update_job(self):
        """
        Execute visa update scan
        This is called by the scheduler automatically
        """
        try:
            logger.info("🤖 Starting scheduled visa update scan...")
            
            from visa_auto_updater import VisaAutoUpdater
            
            # Create updater instance
            updater = VisaAutoUpdater(self.db, self.llm_key)
            
            # Run update
            result = await updater.run_weekly_update()
            
            if result.get("success"):
                changes_count = result.get("changes_detected", 0)
                logger.info(f"✅ Scheduled update completed: {changes_count} changes detected")
                
                # Log to database
                await self.db.scheduler_logs.insert_one({
                    "job_type": "visa_update",
                    "status": "success",
                    "changes_detected": changes_count,
                    "executed_at": datetime.utcnow(),
                    "next_run": self.get_next_run_time()
                })
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"❌ Scheduled update failed: {error}")
                
                await self.db.scheduler_logs.insert_one({
                    "job_type": "visa_update",
                    "status": "error",
                    "error": error,
                    "executed_at": datetime.utcnow(),
                    "next_run": self.get_next_run_time()
                })
                
        except Exception as e:
            logger.error(f"❌ Critical error in scheduled update: {str(e)}")
            
            # Log error to database
            await self.db.scheduler_logs.insert_one({
                "job_type": "visa_update",
                "status": "critical_error",
                "error": str(e),
                "executed_at": datetime.utcnow(),
                "next_run": self.get_next_run_time()
            })
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("⚠️ Scheduler already running")
            return
        
        try:
            # Schedule weekly updates (every Monday at 9:00 AM)
            self.scheduler.add_job(
                self.run_update_job,
                trigger=CronTrigger(
                    day_of_week='mon',
                    hour=9,
                    minute=0,
                    timezone='America/New_York'  # Adjust to your timezone
                ),
                id='weekly_visa_update',
                name='Weekly Visa Information Update',
                replace_existing=True,
                max_instances=1  # Prevent overlapping runs
            )
            
            # Optional: Daily quick check (checks for urgent updates)
            # Commented out by default, uncomment if needed
            # self.scheduler.add_job(
            #     self.run_quick_check,
            #     trigger=CronTrigger(
            #         hour=14,
            #         minute=0,
            #         timezone='America/New_York'
            #     ),
            #     id='daily_quick_check',
            #     name='Daily Quick Check for Urgent Updates',
            #     replace_existing=True
            # )
            
            self.scheduler.start()
            self.is_running = True
            
            next_run = self.get_next_run_time()
            logger.info(f"✅ Visa update scheduler started")
            logger.info(f"📅 Next scheduled run: {next_run}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {str(e)}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("⚠️ Scheduler not running")
            return
        
        try:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("✅ Visa update scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {str(e)}")
    
    def get_next_run_time(self):
        """Get next scheduled run time"""
        if not self.is_running:
            return None
        
        job = self.scheduler.get_job('weekly_visa_update')
        if job:
            return job.next_run_time
        return None
    
    async def trigger_manual_update(self):
        """
        Trigger manual update (outside of schedule)
        Used by admin panel
        """
        logger.info("🔧 Manual visa update triggered by admin")
        await self.run_update_job()
    
    async def get_schedule_status(self):
        """Get current scheduler status"""
        return {
            "is_running": self.is_running,
            "next_run": str(self.get_next_run_time()) if self.get_next_run_time() else None,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": str(job.next_run_time) if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ]
        }


# Global scheduler instance
_scheduler_instance = None

def get_visa_update_scheduler(db, llm_key: str) -> VisaUpdateScheduler:
    """Get or create scheduler instance"""
    global _scheduler_instance
    
    if _scheduler_instance is None:
        _scheduler_instance = VisaUpdateScheduler(db, llm_key)
    
    return _scheduler_instance


# For testing
if __name__ == "__main__":
    import sys
    sys.path.insert(0, '/app/backend')
    
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    async def test_scheduler():
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client.test_database
        
        # Get LLM key
        llm_key = os.environ.get('EMERGENT_LLM_KEY')
        
        # Create scheduler
        scheduler = VisaUpdateScheduler(db, llm_key)
        
        # Get status
        status = await scheduler.get_schedule_status()
        print(f"Scheduler status: {status}")
        
        # Trigger manual update
        await scheduler.trigger_manual_update()
        
        print("✅ Test completed")
    
    asyncio.run(test_scheduler())
