from uuid import UUID
import logging

from flask import Blueprint, jsonify, request

from app.config.config_app import settings as app_settings
from app.schemas import NotificationCreate
from app.services.service_notification import (
    NotificationNotFoundError,
    NotificationService,
)
from app.validators.notification_validator import NotificationValidationError
from app.uow import NotificationUnitOfWork
from app.repositories.notification_repository import NotificationRepository
from app.message_broker.notification_broker import CeleryMessageBroker
from app.database.relational_database import _async_session

log = logging.getLogger(__name__)

notification_blueprint = Blueprint(
    "notifications",
    __name__,
    url_prefix="/api/v1/notifications",
)


notification_service = NotificationService(
    uow_factory=lambda: NotificationUnitOfWork(
        session_factory=_async_session,
        repository_factory=NotificationRepository
    ),
    message_broker=CeleryMessageBroker()
)



@notification_blueprint.get("/")
async def list_notifications():
    status = request.args.get("status")
    if not status:
        return jsonify({"error": "status query parameter is required"}), 400
    
    ALLOWED_STATUSES = {"queued", "sent", "failed"}
    if status not in ALLOWED_STATUSES:
        return jsonify({"error": f"status must be one of {sorted(ALLOWED_STATUSES)}"}), 400
    
    try:
        limit = int(request.args.get("limit", app_settings.PAGINATION_DEFAULT_LIMIT))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"error": "limit and offset must be integers"}), 400
    if limit < 1 or offset < 0:
        return jsonify({"error": "limit must be >= 1 and offset >= 0"}), 400
    limit = min(limit, app_settings.PAGINATION_MAX_LIMIT)

    results = await notification_service.list_notifications(
        status=status, limit=limit, offset=offset,
    )
    
    return jsonify(results), 200


@notification_blueprint.get("/<uuid:notification_id>")
async def get_notification(notification_id: UUID):
    try:
        result = await notification_service.get_notification(notification_id)
    except NotificationNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify(result), 200


@notification_blueprint.post("/")
async def create_notification():
    log.info("request received: create_notification")

    payload = request.get_json(silent=True)
    if payload is None:
        log.warning("invalid JSON payload")
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    try:
        notification = NotificationCreate.model_validate(payload)
    except Exception as e:
        log.warning(f"validation error: {str(e)}")
        return jsonify({"error": "Invalid notification data", "details": str(e)}), 400
    
    try:
        created_notification = await notification_service.create_notification(notification)
        log.info(f"notification created id={created_notification['id']}")
        return jsonify(created_notification), 201
    except NotificationValidationError as e:
        log.warning(f"validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400