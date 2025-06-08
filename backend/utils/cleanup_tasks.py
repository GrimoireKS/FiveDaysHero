"""
定时清理任务
提供过期文件清理、日志清理等定时任务功能
"""

import os
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any

from services.session_service import get_session_service
from utils.logger import get_logger

logger = get_logger(__name__)


class CleanupTaskManager:
    """清理任务管理器"""
    
    def __init__(self):
        """初始化清理任务管理器"""
        self.session_service = get_session_service()
        self.is_running = False
        self.scheduler_thread = None
        
        # 配置清理任务
        self._setup_cleanup_tasks()
        
        logger.info("清理任务管理器初始化完成")
    
    def _setup_cleanup_tasks(self):
        """设置清理任务"""
        # 每天凌晨2点清理过期游戏文件
        schedule.every().day.at("02:00").do(self._cleanup_expired_games)
        
        # 每周日凌晨3点清理过期日志文件
        schedule.every().sunday.at("03:00").do(self._cleanup_old_logs)
        
        # 每天凌晨4点清理过期备份文件
        schedule.every().day.at("04:00").do(self._cleanup_old_backups)
        
        # 每小时检查一次存储空间使用情况
        schedule.every().hour.do(self._check_storage_usage)
        
        logger.info("清理任务配置完成")
    
    def start(self):
        """启动清理任务调度器"""
        if self.is_running:
            logger.warning("清理任务调度器已在运行")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("清理任务调度器启动成功")
    
    def stop(self):
        """停止清理任务调度器"""
        if not self.is_running:
            logger.warning("清理任务调度器未在运行")
            return
        
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("清理任务调度器停止成功")
    
    def _run_scheduler(self):
        """运行调度器主循环"""
        logger.info("清理任务调度器主循环开始")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                logger.error(f"清理任务调度器异常: {e}")
                time.sleep(60)
        
        logger.info("清理任务调度器主循环结束")
    
    def _cleanup_expired_games(self):
        """清理过期的游戏文件"""
        try:
            logger.info("开始清理过期游戏文件")
            
            deleted_count = self.session_service.cleanup_expired_sessions()
            
            logger.info(f"过期游戏文件清理完成，删除了 {deleted_count} 个文件")
            
            # 记录清理统计
            self._log_cleanup_stats("expired_games", deleted_count)
            
        except Exception as e:
            logger.error(f"清理过期游戏文件异常: {e}")
    
    def _cleanup_old_logs(self):
        """清理过期的日志文件"""
        try:
            logger.info("开始清理过期日志文件")
            
            logs_dir = "backend/logs"
            if not os.path.exists(logs_dir):
                logger.warning(f"日志目录不存在: {logs_dir}")
                return
            
            # 删除7天前的日志文件
            cutoff_date = datetime.now() - timedelta(days=7)
            deleted_count = 0
            
            for filename in os.listdir(logs_dir):
                if not filename.startswith("service.log."):
                    continue
                
                file_path = os.path.join(logs_dir, filename)
                
                try:
                    # 从文件名提取日期
                    date_str = filename.replace("service.log.", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    if file_date < cutoff_date:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.debug(f"删除过期日志文件: {filename}")
                        
                except (ValueError, OSError) as e:
                    logger.warning(f"处理日志文件失败 {filename}: {e}")
            
            logger.info(f"过期日志文件清理完成，删除了 {deleted_count} 个文件")
            
            # 记录清理统计
            self._log_cleanup_stats("old_logs", deleted_count)
            
        except Exception as e:
            logger.error(f"清理过期日志文件异常: {e}")
    
    def _cleanup_old_backups(self):
        """清理过期的备份文件"""
        try:
            logger.info("开始清理过期备份文件")
            
            backups_dir = "backend/data/backups"
            if not os.path.exists(backups_dir):
                logger.warning(f"备份目录不存在: {backups_dir}")
                return
            
            # 删除30天前的备份文件
            cutoff_date = datetime.now() - timedelta(days=30)
            deleted_count = 0
            
            for date_dir in os.listdir(backups_dir):
                date_dir_path = os.path.join(backups_dir, date_dir)
                
                if not os.path.isdir(date_dir_path):
                    continue
                
                try:
                    # 从目录名提取日期
                    dir_date = datetime.strptime(date_dir, "%Y-%m-%d")
                    
                    if dir_date < cutoff_date:
                        # 删除整个日期目录
                        import shutil
                        shutil.rmtree(date_dir_path)
                        deleted_count += 1
                        logger.debug(f"删除过期备份目录: {date_dir}")
                        
                except (ValueError, OSError) as e:
                    logger.warning(f"处理备份目录失败 {date_dir}: {e}")
            
            logger.info(f"过期备份文件清理完成，删除了 {deleted_count} 个目录")
            
            # 记录清理统计
            self._log_cleanup_stats("old_backups", deleted_count)
            
        except Exception as e:
            logger.error(f"清理过期备份文件异常: {e}")
    
    def _check_storage_usage(self):
        """检查存储空间使用情况"""
        try:
            stats = self.session_service.get_session_statistics()
            storage_usage_mb = stats.get("storage_usage_mb", 0)
            
            # 如果存储使用超过100MB，记录警告
            if storage_usage_mb > 100:
                logger.warning(f"存储使用量较高: {storage_usage_mb:.2f} MB")
            
            # 如果存储使用超过500MB，触发额外清理
            if storage_usage_mb > 500:
                logger.warning(f"存储使用量过高: {storage_usage_mb:.2f} MB，触发额外清理")
                self._emergency_cleanup()
            
            logger.debug(f"存储使用检查完成: {storage_usage_mb:.2f} MB")
            
        except Exception as e:
            logger.error(f"检查存储使用情况异常: {e}")
    
    def _emergency_cleanup(self):
        """紧急清理，释放存储空间"""
        try:
            logger.warning("开始紧急清理")
            
            # 清理所有过期文件
            self._cleanup_expired_games()
            self._cleanup_old_logs()
            self._cleanup_old_backups()
            
            # 清理更老的备份文件（15天前）
            backups_dir = "backend/data/backups"
            if os.path.exists(backups_dir):
                cutoff_date = datetime.now() - timedelta(days=15)
                deleted_count = 0
                
                for date_dir in os.listdir(backups_dir):
                    date_dir_path = os.path.join(backups_dir, date_dir)
                    
                    if not os.path.isdir(date_dir_path):
                        continue
                    
                    try:
                        dir_date = datetime.strptime(date_dir, "%Y-%m-%d")
                        
                        if dir_date < cutoff_date:
                            import shutil
                            shutil.rmtree(date_dir_path)
                            deleted_count += 1
                            logger.debug(f"紧急清理备份目录: {date_dir}")
                            
                    except (ValueError, OSError) as e:
                        logger.warning(f"紧急清理备份目录失败 {date_dir}: {e}")
                
                logger.info(f"紧急清理完成，额外删除了 {deleted_count} 个备份目录")
            
        except Exception as e:
            logger.error(f"紧急清理异常: {e}")
    
    def _log_cleanup_stats(self, task_type: str, deleted_count: int):
        """记录清理统计信息"""
        try:
            stats_file = "backend/data/logs/cleanup_stats.log"
            
            # 确保目录存在
            os.makedirs(os.path.dirname(stats_file), exist_ok=True)
            
            timestamp = datetime.now().isoformat()
            log_entry = f"{timestamp} - {task_type}: {deleted_count} items deleted\n"
            
            with open(stats_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
        except Exception as e:
            logger.error(f"记录清理统计失败: {e}")
    
    def run_manual_cleanup(self, task_type: str = "all") -> Dict[str, Any]:
        """
        手动运行清理任务
        
        Args:
            task_type (str): 清理任务类型 ("all", "games", "logs", "backups")
            
        Returns:
            Dict[str, Any]: 清理结果统计
        """
        try:
            logger.info(f"开始手动清理任务: {task_type}")
            
            results = {}
            
            if task_type in ["all", "games"]:
                deleted_games = self.session_service.cleanup_expired_sessions()
                results["expired_games"] = deleted_games
                logger.info(f"手动清理过期游戏: {deleted_games} 个")
            
            if task_type in ["all", "logs"]:
                self._cleanup_old_logs()
                results["old_logs"] = "completed"
                logger.info("手动清理过期日志完成")
            
            if task_type in ["all", "backups"]:
                self._cleanup_old_backups()
                results["old_backups"] = "completed"
                logger.info("手动清理过期备份完成")
            
            logger.info(f"手动清理任务完成: {task_type}")
            return results
            
        except Exception as e:
            logger.error(f"手动清理任务异常 {task_type}: {e}")
            return {"error": str(e)}
    
    def get_next_cleanup_times(self) -> Dict[str, str]:
        """
        获取下次清理任务的时间
        
        Returns:
            Dict[str, str]: 各清理任务的下次执行时间
        """
        try:
            next_times = {}
            
            for job in schedule.jobs:
                job_func_name = job.job_func.__name__
                next_run = job.next_run
                
                if next_run:
                    next_times[job_func_name] = next_run.strftime("%Y-%m-%d %H:%M:%S")
            
            return next_times
            
        except Exception as e:
            logger.error(f"获取下次清理时间异常: {e}")
            return {}


# 全局清理任务管理器实例
_cleanup_manager = None


def get_cleanup_manager() -> CleanupTaskManager:
    """
    获取全局清理任务管理器实例
    
    Returns:
        CleanupTaskManager: 清理任务管理器实例
    """
    global _cleanup_manager
    if _cleanup_manager is None:
        _cleanup_manager = CleanupTaskManager()
    return _cleanup_manager


def start_cleanup_tasks():
    """启动清理任务"""
    manager = get_cleanup_manager()
    manager.start()


def stop_cleanup_tasks():
    """停止清理任务"""
    manager = get_cleanup_manager()
    manager.stop()
