from fastapi import APIRouter

from app.schemas import APIResponse, ChatRequest, ChatData, APIError
from app.services.chat_service import get_chat_service

router = APIRouter(tags=["Ask Saarthi Chat"])


@router.post("/chat", response_model=APIResponse[ChatData])
def chat(req: ChatRequest):
    # Validate request body
    if not req.message or not req.message.strip():
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="EMPTY_QUERY",
                message="Please ask a question."
            )
        )

    try:
        service = get_chat_service()
        data = service.process_chat(req)
        return APIResponse(status="ok", data=data, error=None)
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="CHAT_SERVICE_ERROR",
                message=f"An issue occurred while consulting the agricultural knowledge base: {str(e)}"
            )
        )