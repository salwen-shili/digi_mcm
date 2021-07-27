# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    training_line_done_ids = fields.One2many('hr.training.done.line', 'employee_id', string="Formations faites")
    training_line_todo_ids = fields.One2many('hr.training.todo.line', 'employee_id', string="Formations à faire")


class TrainingLineDone(models.Model):
        _name = 'hr.training.done.line'
        _description = "Training line Done of an employee"
        _order = "date"

        employee_id = fields.Many2one('hr.employee', required=True, ondelete='cascade')
        name = fields.Char(required=True)
        date = fields.Date(required=True)
        organisme = fields.Text(string="Organisme de formation", required=True)
        document = fields.Binary('Document', help="Charger votre document", required=True)


class TrainingLineToDo(models.Model):
    _name = 'hr.training.todo.line'
    _description = "Training line ToDo of an employee"
    _order = "date"

    employee_id = fields.Many2one('hr.employee', required=True, ondelete='cascade')
    name = fields.Char(required=True)
    date = fields.Date(required=True)
    organisme = fields.Text(string="Organisme de formation",required=True)
    document = fields.Binary('Document', help="Charger votre document",required=True)


