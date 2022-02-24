# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta

from odoo import models, api, fields,_
import werkzeug
import json
import requests
from datetime import timedelta, datetime,date
import logging
_logger = logging.getLogger(__name__)


class CalendlyRendezVous(models.Model):
    _name = 'calendly.rendezvous'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Rendez Vous Calendly"

    partner_id = fields.Many2one('res.partner',readonly=True)
    event_starttime = fields.Char('Date de début',readonly=True)
    event_endtime = fields.Char('Date de fin',readonly=True)
    name = fields.Char("Nom de l'évènement",readonly=True)


