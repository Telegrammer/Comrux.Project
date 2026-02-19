from pydantic import UUID4
from application.compositions import CreateContentTicketComposition
from application.usecases import CreateContentTicketRequest, CreateContentTicketResponse
from presentation.presenters.auth_info import ContentTicketPresenter
from presentation.models import ContentTicketCreated


class CreateContentTicketHandler:

    def __init__(
        self, usecase: CreateContentTicketComposition, presenter: ContentTicketPresenter
    ):
        self._usecase: CreateContentTicketComposition = usecase
        self._presenter: ContentTicketPresenter = presenter

    async def __call__(
        self, project_id: UUID4, document_id: UUID4
    ) -> ContentTicketCreated:

        response: CreateContentTicketResponse = await self._usecase(
            CreateContentTicketRequest.from_primitives(
                str(project_id), str(document_id)
            )
        )
        return ContentTicketCreated(token=self._presenter.present(response))
