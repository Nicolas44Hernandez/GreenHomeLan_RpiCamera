""" REST controller for wifi bands management ressource """
from ast import Str
import logging
from flask.views import MethodView
from flask_smorest import Blueprint
from server_box.managers.wifi_bands_manager import BANDS, wifi_bands_manager_service
from .rest_model import WifiStatusSchema

logger = logging.getLogger(__name__)

bp = Blueprint("wifi", __name__, url_prefix="/wifi")
""" The api blueprint. Should be registered in app main api object """


# TODO: Errors management in apis reponses

@bp.route("/")
class WifiStatusApi(MethodView):
    """API to retrieve wifi general status"""
    @bp.doc(
        security=[{"tokenAuth": []}],
        responses={400: "BAD_REQUEST", 404: "NOT_FOUND"},
    )
    @bp.response(status_code=200, schema=WifiStatusSchema)
    def get(self):
        """
        """
        #TOOD: update doc
        status = wifi_bands_manager_service.get_wifi_status()
        
        # TODO: build response
        return {"status": status}

    @bp.doc(security=[{"tokenAuth": []}], responses={ 400: "BAD_REQUEST"})
    @bp.arguments(WifiStatusSchema, location="query")
    @bp.response(status_code=200, schema=WifiStatusSchema)
    def post(self, args: WifiStatusSchema):
        # TODO: use class for translate schema to object
        """
        Set wifi status
        """
        new_status = wifi_bands_manager_service.set_wifi_status(args["status"])

        # TODO: build response
        return {"status": new_status}
    

@bp.route("/bands/<band>")
class WifiStatusApi(MethodView):
    """API to retrieve wifi band status"""
    @bp.doc(
        security=[{"tokenAuth": []}],
        responses={400: "BAD_REQUEST", 404: "NOT_FOUND"},
    )
    @bp.response(status_code=200, schema=WifiStatusSchema)
    def get(self, band: str):
        """
        """
        #TODO: update doc
        new_status = wifi_bands_manager_service.get_band_status(band)
        
        return {"status": new_status}

    @bp.doc(security=[{"tokenAuth": []}], responses={ 400: "BAD_REQUEST"})
    @bp.arguments(WifiStatusSchema, location="query")
    @bp.response(status_code=200, schema=WifiStatusSchema)
    def post(self, args: WifiStatusSchema, band: str):
        # TODO: use class for translate schema to object
        """
        Set wifi band status
        """        
        new_status = wifi_bands_manager_service.set_band_status(band, args["status"])

        # TODO: build response
        return {"status": new_status}