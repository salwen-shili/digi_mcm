# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, _logger
import dateutil
import werkzeug
import locale
import json
import logging
import requests
import odoo
from odoo.tools import datetime

_logger = logging.getLogger(__name__)


class AircallConnector(http.Controller):

    @http.route(['/webhook-digi-mcm-aircall'], type='json', auth="public", csrf=False)
    def webhook_import_calls(self, **kw):
        request.uid = odoo.SUPERUSER_ID
        call = json.loads(request.httprequest.data)
        # add events
        if call["event"] in ["call.answered", "call.commented", "call.created", "call.tagged", "call.ended"]:
            call_data = call["data"]
            societe = call_data["number"]["name"]
            started_at = call_data['started_at']
            _logger.info(' call_data : %s' % str(call_data))
            start_call_date = datetime.fromtimestamp(call_data['started_at'])
            subtype_id = request.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
            call_detail = request.env['call.detail'].sudo().search([('call_id', "=", call_data['id'])], limit=1)
            _logger.info('search call_detail : %s' % str(call_detail))
            # if call  exist
            if call_detail:
                # add recording and duration
                call_detail.sudo().write({
                    'call_recording': call_data['asset'],
                    'call_duration': call_data['duration']
                })
                comments = ''
                call_data_comments = call_data["comments"]
                _logger.info(" call_detail call_data call_data_comments : %s" % (str(call_data["comments"])))
                # if comments
                # add comments
                if call_data_comments:
                    for note in call_data_comments:
                        _logger.info("call_data note of comments : %s" % (str(note)))
                        comments += str(note['content']) + '\n'
                    _logger.info(" call_detail call_data comments : %s" % (str(comments)))
                    call_detail.write({'notes': comments})
                    if call["event"] == "call.commented":
                        call_detail.action_update_notes()
                # add recording url using id call
                if call_detail.call_recording == False:
                    call_detail.call_recording = "https://assets.aircall.io/calls/%s/recording" % call_data['id']
                # add client_id using phone number
                if not call_detail.call_contact:
                    call_detail.action_find_user_using_phone()
                call_duration_min = call_detail.call_duration / 60
                heure = int((call_detail.call_duration / 3600))
                minute = int((call_detail.call_duration - (3600 * heure)) / 60)
                secondes = int(call_detail.call_duration - (3600 * heure) - (60 * minute))
                _logger.info(heure)
                _logger.info(minute)
                _logger.info(secondes)
                _logger.info(str(" %s h :   %s  m:  %s s" % (heure, minute, secondes)))
                call_detail.call_duration = float(call_duration_min)
                call_detail.call_duration_char = (str(" %s h :   %s  m:  %s s" % (heure, minute, secondes)))
                start_call_date = datetime.fromtimestamp(call_data['started_at'])
                if call["event"] == "call.ended":
                    if call_detail.call_contact.company_id.id == 2:
                        call_detail.call_contact.mooc_temps_passe_seconde += call_duration_min
                    elif call_detail.call_contact.company_id.id == 1:
                        call_detail.call_contact.mooc_temps_passe_seconde += call_duration_min

                _logger.info("call data tags response : %s" % (str(call_data['tags'])))
                # add tags
                if call_data['tags']:
                    tags = []
                    for tag in call_data['tags']:
                        _logger.info("call data tags response : %s" % (tag))
                        odoo_tag = request.env['res.partner.category'].sudo().search(
                            ['|', ('call_tag_id', "=", tag['id']), ('call_tag_id', "=", tag['name'])])
                        if not odoo_tag:
                            odoo_tag = request.env['res.partner.category'].sudo().create({
                                'call_tag_id': tag['id'],
                                'name': tag['name'],
                            })
                            _logger.info("call data tagss: %s" % (odoo_tag))
                        _logger.info("call data tag : %s" % (odoo_tag))
                        if odoo_tag:
                            tags.append(odoo_tag.id)
                    _logger.info("call data tags : %s" % (tags))
                    if tags:
                        call_detail.sudo().write({'air_call_tag': [(6, 0, tags)]})
            # if not exist
            # create nnew call_data and add data to partner
            if not call_detail:
                new_call_detail = request.env['call.detail'].sudo().create({'call_id': call_data['id'],
                                                                            'call_status': call_data['status'],
                                                                            'call_direction': call_data['direction'],
                                                                            'call_duration': call_data['duration'],
                                                                            'call_date': start_call_date,
                                                                            'phone_number': call_data['raw_digits'],
                                                                            'call_recording': call_data['asset'],
                                                                            'digits': call_data['number']['digits'],
                                                                            'company_name': call_data['number']['name'],
                                                                            })
                if new_call_detail and new_call_detail.phone_number:
                    new_call_detail.action_find_user_using_phone()
                    if "name" in call_data["user"]:
                        new_call_detail.sudo().write({
                            'owner': call_data["user"]["name"] if call_data["user"] else False,
                        })
                    """change state for crm lead for every call detail creation"""
                    if new_call_detail.call_contact.statut == "indecis":
                        new_call_detail.call_contact.changestage("Indécis appelé", new_call_detail.call_contact)
                        lead = request.env['crm.lead'].sudo().search(
                            [('partner_id', "=", new_call_detail.call_contact.id)])
                        _logger.info('createeeeee webhook note  before if********************************')
                        if lead:
                            _logger.info('lead %s' % str(lead))
                            if "user" in call_data:
                                lead.conseiller = call_data["user"]["name"]
                                _logger.info('createeeeee webhook note ********************************')
                comments = ''
                call_data_comments = call_data["comments"]
                _logger.info("call_data call_data_comments : %s" % (str(call_data["comments"])))

                if call_data_comments:
                    for note in call_data_comments:
                        _logger.info("call_data note of comments : %s" % (str(note)))
                        comments += str(note['content']) + '\n'

                    _logger.info("call_data comments : %s" % (str(comments)))
                    _logger.info("call_data new_call_detail : %s" % (str(new_call_detail)))
                    new_call_detail.sudo().write({'notes': comments})
                _logger.info("call data tags response : %s" % (str(call_data['tags'])))
                if call_data['tags']:
                    tags = []
                    for tag in call_data['tags']:
                        _logger.info("call data tags response tag : %s" % (tag))
                        odoo_tag = request.env['res.partner.category'].sudo().search(
                            ['|', ('call_tag_id', "=", tag['id']), ('call_tag_id', "=", tag['name'])])
                        if not odoo_tag:
                            odoo_tag = request.env['res.partner.category'].sudo().create({
                                'call_tag_id': tag['id'],
                                'name': tag['name'],
                            })
                            _logger.info("call data tags response odoo tag : %s" % (odoo_tag))
                        _logger.info("call data tags response odoo tag : %s" % (odoo_tag))
                        if odoo_tag:
                            tags.append(odoo_tag.id)
                    _logger.info("call data tags : %s" % (tags))
                    if tags:
                        new_call_detail.sudo().write({'air_call_tag': [(6, 0, tags)]})

                if new_call_detail and new_call_detail.phone_number:
                    new_call_detail.action_find_user_using_phone()

            request.env.cr.commit()
