"""Tests for backend service framework: responses, confirmation numbers, validation errors."""
from utils.confirmation_number import generate_confirmation_number
from utils.responses import api_response, error_response, success_response
from utils.errors import format_validation_errors


class TestResponses:
    def test_success_response_default(self):
        r = success_response()
        assert r["success"] is True
        assert "data" not in r or r.get("data") is None

    def test_success_response_with_data(self):
        r = success_response(data={"id": 1})
        assert r["success"] is True
        assert r["data"] == {"id": 1}

    def test_success_response_with_message(self):
        r = success_response(message="Created")
        assert r["success"] is True
        assert r["message"] == "Created"

    def test_error_response(self):
        r = error_response("Something failed")
        assert r["success"] is False
        assert r["message"] == "Something failed"

    def test_api_response_explicit(self):
        r = api_response(success=False, message="Bad", data={"code": 400})
        assert r["success"] is False
        assert r["message"] == "Bad"
        assert r["data"] == {"code": 400}


class TestConfirmationNumber:
    def test_format_utp_yyyy_nnnn(self):
        n = generate_confirmation_number(year=2025)
        assert n.startswith("UTP-2025-")
        assert len(n) == len("UTP-2025-0001")

    def test_sequence_increments(self):
        a = generate_confirmation_number(year=2024)
        b = generate_confirmation_number(year=2024)
        na = int(a.split("-")[-1])
        nb = int(b.split("-")[-1])
        assert nb == na + 1

    def test_custom_prefix(self):
        n = generate_confirmation_number(prefix="X", year=2023)
        assert n.startswith("X-2023-")

    def test_custom_sequence(self):
        seq = [10, 11]
        gen = iter(seq)
        n1 = generate_confirmation_number(year=2025, next_sequence=lambda: next(gen))
        n2 = generate_confirmation_number(year=2025, next_sequence=lambda: next(gen))
        assert n1 == "UTP-2025-0010"
        assert n2 == "UTP-2025-0011"


class TestFormatValidationErrors:
    def test_dict_errors(self):
        errors = [{"loc": ("body", "email"), "msg": "field required", "type": "value_error.missing"}]
        out = format_validation_errors(errors)
        assert len(out) == 1
        assert out[0]["loc"] == ["body", "email"]
        assert out[0]["msg"] == "field required"
        assert out[0]["type"] == "value_error.missing"
