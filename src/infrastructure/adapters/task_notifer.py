from faststream.kafka import KafkaBroker
from domain.entities import Task, TaskId
from application.ports import TaskSendResult


class KafkaTaskNotifier:

    def __init__(self, producer: KafkaBroker):
        self._producer: KafkaBroker = producer

    async def notify_batch(self, tasks: list[Task]) -> dict[TaskId, TaskSendResult]:

        results: dict[TaskId, TaskSendResult] = {}
        for task in tasks:
            ack: bool = await self._producer.publish(
                message=task.payload,
                topic=task.task_type,
                key=str(task.id_).encode("utf-8"),
            )
            results.update({task.id_: TaskSendResult(ack)})
        return results
