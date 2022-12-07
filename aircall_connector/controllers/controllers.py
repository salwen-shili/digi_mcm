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
        if call["event"] in ["call.answered", "call.commented", "call.created", "call.tagged", "call.ended"]:
            call_data = call["data"]
            societe = call_data["number"]["name"]
            started_at = call_data['started_at']
            _logger.info(' call_data : %s' % str(call_data))
            start_call_date = datetime.fromtimestamp(call_data['started_at'])
            subtype_id = request.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
            # Get calls of DIGIMOOV using call number name from api response
            call_detail = request.env['call.detail'].sudo().search([('call_id', "=", call_data['id'])])
            _logger.info('search call_detail : %s' % str(call_detail))
            if call_detail:
                call_detail.sudo().write({
                    'call_recording': call_data['asset'],
                    'call_duration': call_data['duration']
                })
                comments = ''
                call_data_comments = call_data["comments"]
                _logger.info(" call_detail call_data call_data_comments : %s" % (str(call_data["comments"])))
                if call_data_comments:
                    for note in call_data_comments:
                        _logger.info("call_data note of comments : %s" % (str(note)))
                        comments += str(note['content']) + '\n'
                    _logger.info(" call_detail call_data comments : %s" % (str(comments)))
                    call_detail.write({'notes': comments})
                    call_detail.action_update_notes()

                if call_detail.call_recording == False:
                    call_detail.call_recording = "https://assets.aircall.io/calls/%s/recording" % call_data['id']
                if not call_detail.call_contact:
                    call_detail.action_find_user_using_phone()

                if call_detail.call_contact.company_id.id == 2:
                    call_detail.call_contact.total_time_visio_hour += call_detail.duration
                if call_data['tags']:
                    tags = []
                    for tag in call_data['tags']:
                        _logger.info("odooooooooo tag : %s" % (tag))
                        odoo_tag = request.env['res.partner.category'].sudo().search(
                            ['|', ('call_tag_id', "=", tag['id']), ('call_tag_id', "=", tag['name'])])
                        if not odoo_tag:
                            odoo_tag = request.env['res.partner.category'].sudo().create({
                                'call_tag_id': tag['id'],
                                'name': tag['name'],
                            })
                            _logger.info("odooooooooo tag : %s" % (odoo_tag))
                        _logger.info("odooooooooo tag : %s" % (odoo_tag))
                        if odoo_tag:
                            tags.append(odoo_tag.id)
                    _logger.info("call data tags : %s" % (tags))
                    if tags:
                        call_detail.sudo().write({'air_call_tag': [(6, 0, tags)]})

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
                    new_call_detail.sudo().write({
                        'owner': call_data["user"]["name"],
                    })
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

                if call_data['tags']:
                    tags = []
                    for tag in call_data['tags']:
                        _logger.info("odooooooooo tag : %s" % (tag))
                        odoo_tag = request.env['res.partner.category'].sudo().search(
                            ['|', ('call_tag_id', "=", tag['id']), ('call_tag_id', "=", tag['name'])])
                        if not odoo_tag:
                            odoo_tag = request.env['res.partner.category'].sudo().create({
                                'call_tag_id': tag['id'],
                                'name': tag['name'],
                            })
                            _logger.info("odooooooooo tag : %s" % (odoo_tag))
                        _logger.info("odooooooooo tag : %s" % (odoo_tag))
                        if odoo_tag:
                            tags.append(odoo_tag.id)
                    _logger.info("call data tags : %s" % (tags))
                    if tags:
                        new_call_detail.sudo().write({'air_call_tag': [(6, 0, tags)]})

                if new_call_detail and new_call_detail.phone_number:
                    new_call_detail.action_find_user_using_phone()
                if new_call_detail and new_call_detail.call_contact and new_call_detail.notes:
                    new_call_detail.action_update_notes()
                request.env.cr.commit()
