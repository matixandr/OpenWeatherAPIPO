from flask import Flask, jsonify, request, Blueprint
from werkzeug.exceptions import HTTPException
from api.endpoints import bp as api_v1_bp
from flask_caching import Cache
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

cache_config = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
}
cache = Cache(app, config=cache_config)

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(api_v1_bp, url_prefix="/v1")
app.register_blueprint(api_bp, url_prefix="/api")

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)

    if isinstance(e, HTTPException):
        response = {
            "error": e.name,
            "message": e.description,
            "status_code": e.code
        }
        return jsonify(response), e.code

    response = {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "status_code": 500
    }
    return jsonify(response), 500

@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.path} - {request.remote_addr}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response: {response.status_code}")
    return response

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Run the OpenWeatherAPI application or tests.')
    parser.add_argument('--test', type=str, help='Run tests. Use "e" for endpoints, "r" for repository, "s" for services, or "all" for all tests.')
    args = parser.parse_args()

    if args.test:
        import pytest

        if args.test == 'e':
            logger.info("Running endpoint tests...")
            sys.exit(pytest.main(['tests/test_endpoints.py']))
        elif args.test == 'r':
            logger.info("Running repository tests...")
            sys.exit(pytest.main(['tests/test_repository.py']))
        elif args.test == 's':
            logger.info("Running service tests...")
            sys.exit(pytest.main(['tests/test_services.py']))
        elif args.test == 'all':
            logger.info("Running all tests...")
            sys.exit(pytest.main(['tests/']))
        else:
            logger.error(f"Unknown test type: {args.test}")
            sys.exit(1)
    else:
        logger.info("Starting application...")
        app.run(host="0.0.0.0", port=8000, debug=True)
