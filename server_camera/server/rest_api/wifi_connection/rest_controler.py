""" REST controller for wifi connection status ressource """
import logging
from flask.views import MethodView
from flask_smorest import Blueprint
from server.managers.wifi_connection_manager import wifi_connection_manager_service
from .rest_model import WifiConnectionSchema


logger = logging.getLogger(__name__)

bp = Blueprint("wifi", __name__, url_prefix="/wifi")
""" The api blueprint. Should be registered in app main api object """


@bp.route("/connected")
class ThreadNodesApi(MethodView):
    """API to retrieve wifi connection status"""

    @bp.doc(responses={400: "BAD_REQUEST", 404: "NOT_FOUND"})
    @bp.response(status_code=200, schema=WifiConnectionSchema)
    def get(self):
        """Get node wifi connection status"""

        logger.info(f"GET wifi/connected")

        return {"connected": wifi_connection_manager_service.connected}
