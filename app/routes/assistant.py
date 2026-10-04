"""Local prototype: bounded, expiring in-memory conversations, never in cookies."""
import secrets
import threading
import time
from flask import Blueprint, jsonify, render_template, request, session, url_for
from flask_login import current_user, login_required
from app.models.user import User
from app.services.assistant import respond, AssistantUnavailable
from app.utils.decorators import role_required

assistant_bp = Blueprint("assistant", __name__, url_prefix="/patient/assistant")
_conversations = {}
_lock = threading.Lock()
TTL = 1800
MAX_TURNS = 12


@assistant_bp.get("")
@login_required
@role_required("patient")
def page():
    response = render_template("patient/assistant.html")
    return response, 200, {"Cache-Control": "no-store"}


@assistant_bp.post("/message")
def message():
    if not current_user.is_authenticated:
        return jsonify(error="auth"), 401
    if current_user.role != "patient":
        return jsonify(error="forbidden"), 403
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="invalid"), 400
    text = data.get("message")
    language = data.get("language")
    if (not isinstance(text, str) or not 1 <= len(text.strip()) <= 2000
            or language not in ("fr", "ln") or data.get("consent") is not True):
        return jsonify(error="invalid"), 400
    token = session.get("assistant_token")
    if not token:
        token = secrets.token_urlsafe(24)
        session["assistant_token"] = token
    key = (current_user.id, token)
    now = time.monotonic()
    with _lock:
        for expired in [k for k, v in _conversations.items()
                        if now - v["updated"] > TTL and not v["busy"]]:
            del _conversations[expired]
        if key not in _conversations:
            if len(_conversations) >= 500:
                return jsonify(error="busy"), 503
            _conversations[key] = {"messages": [], "updated": now, "last": 0, "busy": False}
        state = _conversations[key]
        if state["busy"] or now - state["last"] < 3:
            return jsonify(error="busy"), 429
        if len(state["messages"]) >= MAX_TURNS * 2:
            return jsonify(error="limit"), 409
        state.update(busy=True, last=now, updated=now)
        history = state["messages"] + [{"role": "user", "content": text.strip()}]
    try:
        providers = User.query.filter(User.role.in_(["doctor", "pharmacy"])).order_by(User.id).limit(100).all()
        directory = [{"id": p.id, "name": p.name, "role": p.role,
                      "specialty": p.specialty, "workplace": p.workplace} for p in providers]
        answer = respond(history, language, directory)
        selected = set(answer["provider_ids"][:4]) if not answer["urgent"] else set()
        cards = [{"name": p.name, "role": p.role, "specialty": p.specialty,
                  "workplace": p.workplace,
                  "url": url_for("patient.book_appointment", doctor_id=p.id) if p.role == "doctor" else None,
                  "phone": p.phone if p.role == "pharmacy" else None}
                 for p in providers if p.id in selected]
        with _lock:
            state["messages"] = history + [{"role": "assistant", "content": answer["reply"]}]
        return jsonify(reply=answer["reply"], urgent=answer["urgent"], providers=cards)
    except AssistantUnavailable as error:
        # Only a fixed error category; no medical content or credentials.
        from flask import current_app
        current_app.logger.warning("Assistant unavailable: %s", str(error))
        return jsonify(error="unavailable"), 503
    finally:
        with _lock:
            state.update(busy=False, updated=time.monotonic())


@assistant_bp.post("/reset")
def reset():
    if not current_user.is_authenticated:
        return jsonify(error="auth"), 401
    if current_user.role != "patient":
        return jsonify(error="forbidden"), 403
    with _lock:
        key = (current_user.id, session.get("assistant_token"))
        if key in _conversations and _conversations[key]["busy"]:
            return jsonify(error="busy"), 409
        _conversations.pop(key, None)
    session.pop("assistant_token", None)
    return jsonify(ok=True)


@assistant_bp.after_request
def private_response(response):
    response.headers["Cache-Control"] = "no-store"
    return response
