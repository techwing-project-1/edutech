import asyncio
from typing import Callable, Any
from app.core.logger import logger

class NotificationQueue:
    """In-memory async queue for processing notifications."""
    def __init__(self):
        self._queue = asyncio.Queue()
        self._worker_task = None
        
    async def enqueue(self, task: Callable, *args, **kwargs):
        await self._queue.put((task, args, kwargs))
        
    async def _worker(self):
        while True:
            try:
                task, args, kwargs = await self._queue.get()
                try:
                    await task(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error processing notification task: {e}")
                finally:
                    self._queue.task_done()
            except asyncio.CancelledError:
                break
                
    def start(self):
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())
            
    async def stop(self):
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

# Global instance for the engine
notification_queue = NotificationQueue()
