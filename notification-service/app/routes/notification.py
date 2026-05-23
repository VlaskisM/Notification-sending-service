from flask import Blueprint, jsonify, request
import asyncio

from app.schemas import NotificationCreate, NotificationResponse
from app.services.service_notification import NotificationService, NotificationValidationError
from app.uow import NotificationUnitOfWork
from app.repositories.notification_repository import NotificationRepository
from app.message_broker.notification_broker import CeleryMessageBroker
from app.database.relational_database import _async_session

notification_blueprint = Blueprint(
    "notifications",
    __name__,
    url_prefix="/notifications",
)


create_notification_service = NotificationService(
    uow_factory=lambda: NotificationUnitOfWork(
        session_factory=_async_session,
        repository_factory=NotificationRepository,
    ),
    message_broker=CeleryMessageBroker(),
)

@notification_blueprint.get("/")
async def list_notifications():
    return jsonify([])


@notification_blueprint.get("/<int:notification_id>")
async def get_notification(notification_id: int):
    return jsonify({"id": notification_id})


@notification_blueprint.post("/")
async def create_notification():
    
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    notification = NotificationCreate(**payload)

    
    try:
        created_notification = await create_notification_service.create_notification(notification)
        return jsonify({"created": created_notification}), 201
    except NotificationValidationError as e:
        return jsonify({"error": str(e)}), 400