""" REST controller for video capture management ressource """
import logging
from flask.views import MethodView
from flask_smorest import Blueprint
from server.managers.video_manager import video_manager_service

logger = logging.getLogger(__name__)

bp = Blueprint("video_stream", __name__, url_prefix="/video_stream")
""" The api blueprint. Should be registered in app main api object """

FRAME_FILE_NAME = "last_captured_frame"


@bp.route("/")
class ThreadNodesApi(MethodView):
    """API to retrieve video stream"""

    @bp.doc(responses={400: "BAD_REQUEST", 404: "NOT_FOUND"})
    @bp.response(status_code=200)
    def get(self):
        """Get video stream"""

        logger.info(f"GET video_stream/")

        return video_manager_service.get_video_stream()
