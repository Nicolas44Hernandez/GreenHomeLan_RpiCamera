""" App initialization module."""

import logging
from logging.config import dictConfig
from os import path
import yaml
from flask import Flask
from .managers.thread_manager import thread_manager_service
from .managers.doorbell_manager import doorbell_manager_service
from .managers.presence_detection_manager import presence_detection_manager_service
from .managers.wifi_connection_manager import wifi_connection_manager_service
from .managers.video_manager import video_manager_service
from .notification.cloud_notifier import cloud_notifier_service
from .rest_api.thread_setup import bp as thread_controler_bp
from .rest_api.video_manager import bp as video_manager_controler_bp
from .rest_api.wifi_connection import bp as wifi_connection_manager_controler_bp
from .extension import api
from .common import ServerCameraException, handle_server_camera_exception

logger = logging.getLogger(__name__)


def create_app(
    config_dir: str = path.join(path.dirname(path.abspath(__file__)), "config"),
):
    """Create the Flask app"""

    # Create app Flask
    app = Flask("Server Camera")

    # Get configuration files
    app_config = path.join(config_dir, "server-camera-config.yml")

    logging_config = path.join(config_dir, "logging-config.yml")

    # Load logging configuration and configure flask application logger
    with open(logging_config) as stream:
        dictConfig(yaml.full_load(stream))

    logger.info("App config file: %s", app_config)

    # Load configuration
    app.config.from_file(app_config, load=yaml.full_load)

    # Register extensions
    register_extensions(app)
    # Register blueprints for REST API
    register_blueprints(app)
    logger.info("App ready!!")

    return app


def register_extensions(app: Flask):
    """Initialize all extensions"""

    # Initialize REST APIs.
    #
    # The spec_kwargs dict is used to generate the OpenAPI document that describes our APIs.
    # The securitySchemes field defines the security scheme used to protect our APIs.
    #   - BasicAuth  allows to authenticate a user with a login and a password.
    #   - BearerAuth allows to authenticate a user using a token (the /login API allows to a user
    #     to retrieve a valid token).

    api.init_app(
        app,
        spec_kwargs={
            "info": {"description": "`Server Camera` OpenAPI 3.0 specification."},
            "components": {
                "securitySchemes": {
                    "basicAuth": {"type": "http", "scheme": "basic"},
                    "tokenAuth": {"type": "http", "scheme": "bearer"},
                },
            },
        },
    )

    # Thread manager extension
    thread_manager_service.init_app(app=app)
    # Doorbell manager extension
    doorbell_manager_service.init_app(app=app)
    # Presence detection manager extension
    presence_detection_manager_service.init_app(app=app)
    # Wifi connection manager extention
    wifi_connection_manager_service.init_app(app=app)
    # Video manager extension
    video_manager_service.init_app(app=app)
    # Cloud notifier extension
    cloud_notifier_service.init_app(app=app)


def register_blueprints(app: Flask):
    """Store App APIs blueprints."""
    # Register error handler
    app.register_error_handler(ServerCameraException, handle_server_camera_exception)
    # Register REST blueprints
    api.register_blueprint(thread_controler_bp)
    api.register_blueprint(video_manager_controler_bp)
    api.register_blueprint(wifi_connection_manager_controler_bp)
