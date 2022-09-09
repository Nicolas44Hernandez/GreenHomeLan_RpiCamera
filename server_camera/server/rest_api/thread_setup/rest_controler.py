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


@bp.route("/setup")
class ThreadNodesApi(MethodView):
    """API to retrieve node current thread configuration"""

    @bp.doc(responses={400: "BAD_REQUEST", 404: "NOT_FOUND"})
    @bp.response(status_code=200, schema=ThreadNetworkSetupSchema)
    def get(self):
        """Get node current thread configuration"""

        logger.info(f"GET thread/setup")

        return thread_manager_service.get_thread_network_setup()


@bp.route("/setup")
class SetupThreadNetworkNode(MethodView):
    """API to receive the Thread network configuration"""

    @bp.doc(responses={400: "BAD_REQUEST"})
    @bp.arguments(ThreadNetworkSetupSchema, location="json")
    def post(self, args: ThreadNetworkSetupSchema):
        """
        Set Thread network configuration in the node
        """
        logger.info(f"POST thread/setup")

        thread_manager_service.join_thread_network(
            ipv6_otbr=args["ipv6_otbr"],
            ipv6_mesh=args["ipv6_mesh"],
            dataset_key=args["dataset_key"],
        )
        return "Thread setup OK"


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
