from api.dependencies import get_air_quality_service, get_validation_service
from flask import Blueprint, request, jsonify, abort, views, current_app, Response
from api.models import EnvironmentalReadingSchema
from marshmallow import ValidationError
from datetime import datetime

bp = Blueprint('environmental', __name__)

environmental_schema = EnvironmentalReadingSchema()

class ReadingView(views.MethodView):
    def post(self) -> tuple[Response, int]:
        air_quality_service = get_air_quality_service()
        validation_service = get_validation_service()

        json_data = request.get_json()
        if not json_data:
            abort(400, description="No input data provided")

        try:
            reading = environmental_schema.load(json_data)
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400

        if not validation_service.validate_reading(reading):
            abort(400, description="Invalid reading data")

        air_quality_service.save_reading(reading)

        return jsonify(environmental_schema.dump(reading)), 201


class ClosestReadingView(views.MethodView):
    def get(self) -> Response:
        air_quality_service = get_air_quality_service()

        timestamp_str = request.args.get('timestamp')
        if not timestamp_str:
            abort(400, description="Timestamp parameter is required")

        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except ValueError:
            abort(400, description="Invalid timestamp format")

        cache_key = f"closest_reading_{timestamp.isoformat()}"
        cached_result = current_app.extensions['cache'].get(cache_key)

        if cached_result:
            return jsonify(cached_result)

        reading = air_quality_service.get_reading_closest_to_timestamp(timestamp)

        if not reading:
            abort(404, description="No readings available")

        result = environmental_schema.dump(reading)

        current_app.extensions['cache'].set(cache_key, result)

        return jsonify(result)


class FetchDataView(views.MethodView):
    def get(self) -> Response:
        air_quality_service = get_air_quality_service()

        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            abort(400, description="Both start_date and end_date parameters are required")

        try:
            start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
            end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
        except ValueError:
            abort(400, description="Invalid date format")

        readings = air_quality_service.fetch_and_store_air_quality_data(
            start_date,
            end_date
        )

        return jsonify({"readings": [environmental_schema.dump(reading) for reading in readings]})


class ReadingsListView(views.MethodView):
    def get(self) -> Response:
        air_quality_service = get_air_quality_service()

        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))

            if page < 1:
                abort(400, description="Page number must be positive")
            if per_page < 1 or per_page > 100:
                abort(400, description="Items per page must be between 1 and 100")

        except ValueError:
            abort(400, description="Invalid pagination parameters")

        cache_key = f"readings_list_page_{page}_per_page_{per_page}"
        cached_response = current_app.extensions['cache'].get(cache_key)

        if cached_response:
            return jsonify(cached_response)

        readings, total = air_quality_service.get_paginated_readings(page, per_page)

        total_pages = (total + per_page - 1) // per_page if total > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1

        response = {
            "readings": [environmental_schema.dump(reading) for reading in readings],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }

        current_app.extensions['cache'].set(cache_key, response)

        return jsonify(response)

bp.add_url_rule('/readings', view_func=ReadingView.as_view('reading'))
bp.add_url_rule('/readings/closest', view_func=ClosestReadingView.as_view('closest_reading'))
bp.add_url_rule('/readings/list', view_func=ReadingsListView.as_view('readings_list'))
bp.add_url_rule('/fetch-data', view_func=FetchDataView.as_view('fetch_data'))