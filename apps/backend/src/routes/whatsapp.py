"""WhatsApp Business API webhook: verification and incoming messages."""
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse, PlainTextResponse

from config import WHATSAPP_VERIFY_TOKEN
from services.whatsapp_service import WhatsAppService
from utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks/whatsapp", tags=["whatsapp"])


def _whatsapp_service() -> WhatsAppService:
    return WhatsAppService()


@router.get("")
async def whatsapp_webhook_verify(
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_verify_token: str = Query(alias="hub.verify_token", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
):
    """
    Webhook verification: Meta sends GET with hub.mode=subscribe, hub.verify_token, hub.challenge.
    Return hub.challenge if verify_token matches.
    """
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge)
    return JSONResponse(content={"error": "forbidden"}, status_code=403)


@router.post("")
async def whatsapp_webhook_receive(request: Request):
    """
    Receive incoming WhatsApp messages. Parse and optionally reply via WhatsAppService.
    Returns 200 quickly so Meta does not retry; processing can be async.
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(content={"ok": True})
    svc = _whatsapp_service()
    messages = WhatsAppService.parse_incoming_messages(body)
    for m in messages:
        logger.info("WhatsApp incoming from %s: %s", m.get("from_wa_id"), m.get("text") or m.get("type"))
        if m.get("type") == "text" and m.get("text") and svc.is_configured():
            reply = _handle_incoming_message(m.get("text"), m.get("from_wa_id"))
            if reply:
                svc.send_text_message(m["from_wa_id"], reply)
    return JSONResponse(content={"ok": True})


def _handle_incoming_message(text: str, from_wa_id: str) -> str | None:
    """
    Simple reply logic: echo or canned responses. Replace with assistant/LLM later.
    """
    t = (text or "").strip().lower()
    if t in ("hi", "hello", "hey"):
        return "Hello! You can ask about urban tree grants, complaints, or public data. How can we help?"
    if "complaint" in t:
        return "To file a complaint, visit our website or say 'file complaint' and we'll guide you."
    if "grant" in t or "application" in t:
        return "Urban tree grant applications are available at our website. Would you like the link?"
    if "status" in t:
        return "Check your complaint or application status by logging in at our website."
    return "Thanks for your message. For detailed help, visit our website or type 'complaint', 'grant', or 'status'."
