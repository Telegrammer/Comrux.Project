import logging
import asyncio
from application.compositions import ProcessTasksComposition
from application.ports.gateways.query_params import TaskListParams
from application.ports import Clock


logger = logging.getLogger(__name__)


class TaskPollingWorker:

    def __init__(
        self,
        clock: Clock,
        worker: ProcessTasksComposition,
        poll_interval: float,
        batch_size: int,
    ):
        self._clock = clock
        self._worker = worker
        self._poll_interval = poll_interval
        self._batch_size = batch_size
        self._running = True

    async def run(self):

        while self._running:
            now = self._clock.now()
            try:
                await self._worker(TaskListParams(self._batch_size, now))
            except Exception:
                logger.exception("Worker iteration failed.")

            await asyncio.sleep(self._poll_interval)

    def stop(self):
        self._running = False
