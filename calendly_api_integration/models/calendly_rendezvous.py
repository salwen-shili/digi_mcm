# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta

from odoo import models, api, fields, _, SUPERUSER_ID
import werkzeug
import json
import requests
from datetime import timedelta, datetime, date
import logging

_logger = logging.getLogger(__name__)


class CalendlyRendezVous(models.Model):
    _name = 'calendly.rendezvous'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Rendez Vous Calendly"

    partner_id = fields.Many2one('res.partner')
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    event_starttime = fields.Date('Date de début')
    event_starttime_char = fields.Char('Date de début')

    event_endtime = fields.Date('Date de fin')
    name = fields.Char("Nom de l'évènement")
    zoomlink = fields.Char("Lien de l'évènement")
