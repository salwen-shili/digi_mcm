# -*- coding: utf-8 -*-
import functools
import xmlrpc.client
from odoo import http
from odoo.http import request
import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta, date
import re
import json
from odoo import _
import locale
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from unidecode import unidecode
import pyshorteners
import logging

_logger = logging.getLogger(__name__)


class WebhookController(http.Controller):
    """valider les dossier cpf pour digimoov  apres la creation par webhook"""

    @http.route(["/get_student_presence"], type="http", auth="public", methods=["POST"])
    def validate_cpf_digi(self, **kw):
        print("=====================================+>")

        print("/get_student_presence", json.loads(request.httprequest.data))
        return True
    

