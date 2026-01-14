"""
MongoDB Automatic Backup System
Cria backups diários do banco de dados
"""

import asyncio
import logging
import os
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

class MongoDBBackup:
    """Sistema de backup automático para MongoDB"""
    
    def __init__(self, backup_dir: str = "/app/backups"):
        default_dir = Path(__file__).resolve().parent.parent / "backups"
        env_dir = os.environ.get("BACKUP_DIR")
        self.backup_dir = Path(env_dir) if env_dir else Path(backup_dir)
        if env_dir is None and backup_dir == "/app/backups":
            self.backup_dir = default_dir
        self.enabled = True
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self.enabled = False
            logger.warning(f"Backup directory not writable: {self.backup_dir} ({e})")
            return
        
        # Get MongoDB connection from env
        self.mongo_url = os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = self._extract_db_name(self.mongo_url)
        
        # Retention policy
        self.retention_days = 7  # Keep backups for 7 days
        
        logger.info(f"MongoDB Backup initialized: {self.backup_dir}")
    
    def _extract_db_name(self, mongo_url: str) -> str:
        """Extract database name from MongoDB URL"""
        # Example: mongodb://localhost:27017/osprey_db
        try:
            if '/' in mongo_url:
                db_name = mongo_url.split('/')[-1]
                # Remove query parameters if any
                if '?' in db_name:
                    db_name = db_name.split('?')[0]
                return db_name if db_name else 'osprey_db'
        except Exception:
            pass
        return 'osprey_db'
    
    async def create_backup(self) -> dict:
        """
        Cria um backup do MongoDB
        
        Returns:
            Dict com status e informações do backup
        """
        try:
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{self.db_name}_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            logger.info(f"Starting backup: {backup_name}")
            
            # Create backup using mongodump
            cmd = [
                'mongodump',
                f'--uri={self.mongo_url}',
                f'--out={backup_path}',
                '--gzip'  # Compress for space saving
            ]
            
            # Run mongodump
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Get backup size
                size = self._get_dir_size(backup_path)
                
                logger.info(
                    f"Backup completed successfully",
                    extra={
                        "backup_name": backup_name,
                        "size_mb": round(size / 1024 / 1024, 2)
                    }
                )
                
                # Cleanup old backups
                await self.cleanup_old_backups()
                
                return {
                    "success": True,
                    "backup_name": backup_name,
                    "backup_path": str(backup_path),
                    "size_bytes": size,
                    "size_mb": round(size / 1024 / 1024, 2),
                    "timestamp": timestamp
                }
            else:
                error_msg = stderr.decode('utf-8')
                logger.error(f"Backup failed: {error_msg}")
                
                return {
                    "success": False,
                    "error": error_msg
                }
        
        except FileNotFoundError:
            logger.error("mongodump not found. Install MongoDB tools: apt-get install mongodb-database-tools")
            return {
                "success": False,
                "error": "mongodump not installed"
            }
        
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_dir_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        total = 0
        for entry in path.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
        return total
    
    async def cleanup_old_backups(self):
        """Remove backups older than retention_days"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
            
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir() and backup_dir.name.startswith('backup_'):
                    # Extract timestamp from backup name
                    try:
                        timestamp_str = backup_dir.name.split('_')[-2] + backup_dir.name.split('_')[-1]
                        backup_date = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
                        
                        if backup_date < cutoff_date:
                            logger.info(f"Removing old backup: {backup_dir.name}")
                            shutil.rmtree(backup_dir)
                    
                    except Exception:
                        logger.warning(f"Could not parse backup date: {backup_dir.name}")
        
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {str(e)}")
    
    async def restore_backup(self, backup_name: str) -> dict:
        """
        Restaura um backup
        
        Args:
            backup_name: Nome do backup para restaurar
        
        Returns:
            Dict com status da restauração
        """
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                return {
                    "success": False,
                    "error": f"Backup not found: {backup_name}"
                }
            
            logger.info(f"Restoring backup: {backup_name}")
            
            # Restore using mongorestore
            cmd = [
                'mongorestore',
                f'--uri={self.mongo_url}',
                '--drop',  # Drop collections before restoring
                '--gzip',
                str(backup_path / self.db_name)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Backup restored successfully: {backup_name}")
                return {
                    "success": True,
                    "backup_name": backup_name
                }
            else:
                error_msg = stderr.decode('utf-8')
                logger.error(f"Restore failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
        
        except Exception as e:
            logger.error(f"Error restoring backup: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self) -> list:
        """Lista todos os backups disponíveis"""
        try:
            backups = []
            
            for backup_dir in sorted(self.backup_dir.iterdir(), reverse=True):
                if backup_dir.is_dir() and backup_dir.name.startswith('backup_'):
                    size = self._get_dir_size(backup_dir)
                    
                    # Extract timestamp
                    try:
                        timestamp_str = backup_dir.name.split('_')[-2] + backup_dir.name.split('_')[-1]
                        backup_date = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
                        
                        backups.append({
                            "name": backup_dir.name,
                            "date": backup_date.isoformat(),
                            "size_bytes": size,
                            "size_mb": round(size / 1024 / 1024, 2),
                            "path": str(backup_dir)
                        })
                    except Exception:
                        pass
            
            return backups
        
        except Exception as e:
            logger.error(f"Error listing backups: {str(e)}")
            return []
    
    async def schedule_daily_backup(self):
        """
        Background task para backup diário
        Roda às 3AM UTC todos os dias
        """
        while True:
            try:
                # Calculate time until next 3AM
                now = datetime.now(timezone.utc)
                next_backup = now.replace(hour=3, minute=0, second=0, microsecond=0)
                
                if next_backup <= now:
                    next_backup += timedelta(days=1)
                
                sleep_seconds = (next_backup - now).total_seconds()
                
                logger.info(f"Next backup scheduled for: {next_backup.isoformat()}")
                
                # Sleep until 3AM
                await asyncio.sleep(sleep_seconds)
                
                # Create backup
                result = await self.create_backup()
                
                if result["success"]:
                    logger.info(f"Daily backup completed: {result['backup_name']}")
                else:
                    logger.error(f"Daily backup failed: {result.get('error')}")
            
            except Exception as e:
                logger.error(f"Error in backup scheduler: {str(e)}")
                # Sleep 1 hour before retrying
                await asyncio.sleep(3600)


# Global instance
mongodb_backup = MongoDBBackup()
