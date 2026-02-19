from domain.entities import TaskId
import uuid
from domain.ports import TaskIdGenerator


class TaskUuid4Generator(TaskIdGenerator):
    def __call__(self) -> TaskId:
        return TaskId(str(uuid.uuid4()))