""" REST controller for therad network management ressource """
import logging
from flask.views import MethodView
from flask_smorest import Blueprint
from .rest_model import ThreadNetworkSetupSchema, ThreadMessageSchema

from server.managers.thread_manager import thread_manager_service
from server.common import ServerCameraException, ErrorCode

logger = logging.getLogger(__name__)

bp = Blueprint("thread", __name__, url_prefix="/thread")
""" The api blueprint. Should be registered in app main api object """

#TODO: review APIS (get_thread_network_setup)
@bp.route("/setup")
class ThreadNodesApi(MethodView):
    """API to retrieve node current thread configuration"""

    @bp.doc(responses={400: "BAD_REQUEST", 404: "NOT_FOUND"})
    @bp.response(status_code=200, schema=ThreadNetworkSetupSchema)
    def get(self):
        """Get node current thread configuration"""

        logger.info(f"GET thread/setup")

        return thread_manager_service.get_thread_network_setup()


@bp.route("/message")
class SendThreadMessage(MethodView):
    """API to send message to Thread border router"""

    @bp.doc(responses={400: "BAD_REQUEST"})
    @bp.arguments(ThreadMessageSchema, location="query")
    def post(self, args: ThreadMessageSchema):
        """
        Send thread message
        """
        logger.info(f"POST thread/message")

        thread_manager_service.send_thread_message_to_border_router(args["message"])
        return "Message sent"
