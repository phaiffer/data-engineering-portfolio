from __future__ import annotations

import logging

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from config import load_config
from db import DatabaseQueryError
from routes import api_bp


def create_app() -> Flask:
    """Create and configure the local job-market dashboard API."""
    app = Flask(__name__)
    app.config["API_CONFIG"] = load_config()
    app.register_blueprint(api_bp)

    logging.basicConfig(level=logging.INFO)

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        api_config = app.config["API_CONFIG"]
        if origin in api_config.cors_allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    @app.errorhandler(DatabaseQueryError)
    def handle_database_error(error):
        app.logger.exception("Database query failed: %s", error)
        return (
            jsonify(
                {
                    "error": {
                        "message": "The API could not read from the PostgreSQL mart layer."
                    }
                }
            ),
            503,
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"error": {"message": error.description}}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unexpected API error: %s", error)
        return jsonify({"error": {"message": "Unexpected API error."}}), 500

    return app


if __name__ == "__main__":
    flask_app = create_app()
    api_config = flask_app.config["API_CONFIG"]
    flask_app.run(
        host=api_config.host,
        port=api_config.port,
        debug=api_config.debug,
    )
