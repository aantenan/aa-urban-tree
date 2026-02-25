"""WhatsApp Business API integration: receive webhooks and send messages."""
import os
from typing import Any

from config import WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID
from utils.logging import get_logger

logger = get_logger(__name__)

GRAPH_URL = "https://graph.facebook.com/v18.0"


class WhatsAppService:
    """Send messages via WhatsApp Business API; parse incoming webhook payloads."""

    def __init__(self) -> None:
        self._token = WHATSAPP_ACCESS_TOKEN
        self._phone_number_id = WHATSAPP_PHONE_NUMBER_ID

    def is_configured(self) -> bool:
        return bool(self._token and self._phone_number_id)

    def send_text_message(self, to_wa_id: str, text: str) -> dict[str, Any]:
        """
        Send a text message to a WhatsApp user. to_wa_id is the recipient phone number ID
        (e.g. 15551234567 without +). Returns response from Graph API or error dict.
        """
        if not self.is_configured():
            return {"error": "WhatsApp not configured", "success": False}
        import urllib.request
        import json
        url = f"{GRAPH_URL}/{self._phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to_wa_id.lstrip("+").replace(" ", ""),
            "type": "text",
            "text": {"body": text[:4096]},
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return {"success": True, "response": json.loads(resp.read().decode())}
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else "{}"
            try:
                err = json.loads(body)
            except Exception:
                err = {"error": {"message": body}}
            logger.warning("WhatsApp send failed: %s %s", e.code, err)
            return {"success": False, "error": err, "status_code": e.code}
        except Exception as e:
            logger.exception("WhatsApp send error: %s", e)
            return {"success": False, "error": str(e)}

    @staticmethod
    def parse_incoming_messages(body: dict) -> list[dict[str, Any]]:
        """
        Extract incoming message events from WhatsApp webhook payload.
        Returns list of { from_wa_id, message_id, type, text, timestamp }.
        """
        out = []
        try:
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") != "messages":
                        continue
                    value = change.get("value", {})
                    for msg in value.get("messages", []):
                        from_id = msg.get("from")
                        msg_id = msg.get("id")
                        msg_type = msg.get("type", "unknown")
                        text = None
                        if msg_type == "text":
                            text = (msg.get("text") or {}).get("body")
                        out.append({
                            "from_wa_id": from_id,
                            "message_id": msg_id,
                            "type": msg_type,
                            "text": text,
                            "timestamp": msg.get("timestamp"),
                        })
        except Exception as e:
            logger.warning("WhatsApp parse_incoming_messages: %s", e)
        return out
