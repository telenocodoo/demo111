# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

import re
from datetime import datetime

class ResPartner(models.Model):
    _inherit = 'res.partner'
    user_id=fields.Many2one("res.users","Salesperson",default=lambda self: self.env.uid)
    country_id = fields.Many2one(default=lambda s:s.env['res.country'].search([('name', '=', 'Saudi Arabia')], limit=1))
    state_id = fields.Many2one(string='Region',
                               default=lambda s:s.env['res.country.state'].search([('name', '=', 'riyadh')], limit=1))
    city = fields.Many2one("city.city","Region" ,
                           default=lambda s:s.env['city.city'].search([('name', '=', 'Riyadh')], limit=1))


class ResUsers(models.Model):
    _inherit = 'res.users'
    distributor_allowed=fields.Boolean("Manager")
    seq= fields.Many2one("ir.sequence","Squence")
    vendor_code_id = fields.Many2many("vendor.code",string="Vendor Code")
    city_id = fields.Many2many("city.city",string="Region")
    departments = fields.Many2one("hr.department", string="Department")

class InventoryReportWizard(models.TransientModel):
    _name = 'inventory.report.wizard'

    date_from = fields.Date('Date From',  default=fields.Date.today,required=True)
    date_to = fields.Date('Date To', default=fields.Date.today, required=True)
    sales_person = fields.Many2one('res.users','Salesperson')
    city = fields.Many2one('city.city','City')
    per_pm=fields.Many2one("hr.employee","Product Manager")
    pm = fields.Boolean("Per PM")
    sale = fields.Boolean("Per Saleperson")
    per_city = fields.Boolean("Per City")

    @api.onchange('sale')
    def _onchange_half_id(self):
        self.city= False
        self.pm = False
        self.per_city = False

    @api.onchange('pm')
    def _onchange_half_id(self):
        self.city = False
        self.sale = False
        self.per_city = False

    @api.onchange('per_city')
    def _onchange_half_id(self):
        self.pm = False
        self.sale = False

    @api.constrains('date_from', 'date_to')
    def check_date(self):
        if self.date_from and self.date_to:
            if self.date_to < self.date_from:
                raise UserError(_('Date To cannot be less than Date From.'))

            time_for_now = datetime.now().date()
            if self.date_to > time_for_now:
                raise UserError(_('Date To cannot be greater than today.'))

    # @api.multi
    def get_report(self):

        productObj = self.env['crm.lead'].search([])

        for RecProduct in productObj:

            data = {
                    'ids': self.ids,
                    'model': self._name,
                    'form': {
                        'date_from' :   self.date_from,
                        'date_to' : self.date_to,
                        'sales_person':self.sales_person,
                        'city': self.city,
                        'per_pm': self.per_pm,
                        'sale': self.sale,
                        'per_city': self.per_city,
                        'pm': self.pm,
                    },
                }
        return self.env.ref('distributor_portal.recap_report').report_action(self, data=data)

class ReportAttendanceRecap(models.AbstractModel):

    _name = 'report.distributor_portal.inventory_recap_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sales_person = data['form']['sales_person']
        city = data['form']['city']
        per_pm = data['form']['per_pm']
        sale = data['form']['sale']
        per_city = data['form']['per_city']
        pm = data['form']['pm']
        date_start_obj1 = datetime.strptime(date_from, DATE_FORMAT)
        date_end_obj1 = datetime.strptime(date_to, DATE_FORMAT)
        date_start_obj = date_start_obj1.date()
        date_end_obj = date_end_obj1.date()
        date_start_obj2 = date_start_obj.strftime("%d-%b-%Y")
        date_end_obj2 = date_end_obj.strftime("%d-%b-%Y")

        print(sales_person)
        print(per_pm)
        print(city)



        if per_pm:
            if pm:

                u = (re.findall(r'\d+', per_pm))
                t = []
                for i in u:
                    t.append(int(i))
                docs = []
                locs = []
                lostObj = self.env['crm.lead'].search([('create_date', '>=', date_start_obj), ('create_date', '<=', date_end_obj),('manager', 'in', t),('active', '=', False)])
                OporObj = self.env['crm.lead'].search([('create_date', '>=', date_start_obj), ('create_date', '<=', date_end_obj), ('manager', 'in', t)])

                count = 0
                opportunity = 0
                won = 0
                lost = 0
                for RecOpor in OporObj:
                    if RecOpor.stage_id.name== "Won":
                        won=won+1

                for RecOpor in lostObj:
                  lost=lost+1

                if won > 0 or lost >0:
                        locs.append({'won': (((won) / (lost + won)) * 100), 'lost': (((lost) / (lost + won)) * 100)})

                else:
                    locs.append(
                            {'won': 0, 'lost': 0})


                for RecOpor in OporObj:

                    print(RecOpor.manager)
                    docs.append(
                        {'user_id': RecOpor.user_id.name, 'oppurtunity_name': RecOpor.name, 'city': RecOpor.city_id.name, 'manager': RecOpor.manager.name, 'department': RecOpor.department.name})
                return {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'date_from': date_start_obj2,
                    'date_to': date_end_obj2,
                    'docs': docs,
                    'locs': locs,
                }

        if sales_person:
            if sale:

                u = (re.findall(r'\d+', sales_person))
                print(u)

                t = []
                for i in u:
                    t.append(int(i))
                docs = []
                locs = []
                lostObj = self.env['crm.lead'].search(
                    [('create_date', '>=', date_start_obj), ('create_date', '<=', date_end_obj), ('user_id', 'in', t),
                     ('active', '=', False)])
                OporObj = self.env['crm.lead'].search(
                    [('create_date', '>=', date_start_obj), ('create_date', '<=', date_end_obj), ('user_id', 'in', t)])

                count = 0
                opportunity = 0
                won = 0
                lost = 0
                for RecOpor in OporObj:
                    if RecOpor.stage_id.name == "Won":
                        won = won + 1

                print(won)

                if won > 0 or lost > 0:
                    locs.append({'won': (((won) / (lost + won)) * 100), 'lost': (((lost) / (lost + won)) * 100)})

                else:
                    locs.append(
                        {'won': 0, 'lost': 0})

                for RecOpor in OporObj:
                    docs.append(
                        {'user_id': RecOpor.user_id.name, 'oppurtunity_name': RecOpor.name,
                         'city': RecOpor.city_id.name, 'manager': RecOpor.manager.name,
                         'department': RecOpor.department.name})
                return {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'date_from': date_start_obj2,
                    'date_to': date_end_obj2,
                    'docs': docs,
                    'locs': locs,
                }

        if city:
            if per_city:

                u = (re.findall(r'\d+', city))
                t = []
                for i in u:
                    t.append(int(i))

                lostObj = self.env['crm.lead'].search(
                    [('create_date', '>=', date_start_obj), ('create_date', '<=', date_end_obj), ('city', '=', city),('active', '=', False)])

                docs = []
                locs = []

                OporObj = self.env['crm.lead'].search([('create_date', '>=', date_start_obj), ('create_date', '<=', date_end_obj),('city_id', 'in', t)])
                count = 0
                opportunity = 0
                print(opportunity)

                won = 0
                lost = 0
                for RecOpor in OporObj:
                    if RecOpor.stage_id.name == "Won":
                        won = won + 1

                print(won)


                for RecOpor in lostObj:

                        lost = lost + 1
                if won > 0 or lost > 0:
                    locs.append({'won': (((won) / (lost + won)) * 100), 'lost': (((lost) / (lost + won)) * 100)})

                else:
                    locs.append(
                        {'won': 0, 'lost': 0})

                print("lost",opportunity)

                for RecOpor in OporObj:
                    docs.append ({'user_id': RecOpor.user_id.name, 'oppurtunity_name': RecOpor.name, 'city': RecOpor.city_id.name, 'manager': RecOpor.manager.name, 'department': RecOpor.department.name})
                return {
                    'doc_ids': data['ids'],
                    'doc_model': data['model'],
                    'date_from': date_start_obj2,
                    'date_to': date_end_obj2,
                    'docs': docs,
                    'locs': locs,
                }
        else:
            raise UserError(
                _('You have to select option.'))


class qualifiedprospects(models.TransientModel):
    _name = 'qualified.report.wizard'


    date_from = fields.Date('Date From',  default=fields.Date.today,required=True)
    date_to = fields.Date('Date To', default=fields.Date.today, required=True)
    qualified_prospect = fields.Boolean("Qualified Prospects")


    @api.constrains('date_from', 'date_to')
    def check_date(self):
        if self.date_from and self.date_to:
            if self.date_to < self.date_from:
                raise UserError(_('Date To cannot be less than Date From.'))

            time_for_now = datetime.now().date()
            if self.date_to > time_for_now:
                raise UserError(_('Date To cannot be greater than today.'))

    # @api.multi
    def get_report(self):
        """Call when button 'Get Report' clicked.
        """
        productObj = self.env['crm.lead'].search([])

        for RecProduct in productObj:
            data = {
                    'ids': self.ids,
                    'model': self._name,
                    'form': {
                        'date_from' :   self.date_from,
                        'date_to' : self.date_to,
                        'qualified_prospect': self.qualified_prospect,
                    },
                }
        return self.env.ref('distributor_portal.qualified_recap_report').report_action(self, data=data)

class QualifiedProspects(models.AbstractModel):

    _name = 'report.distributor_portal.qualified_recap_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        qualified_prospect = data['form']['qualified_prospect']
        date_start_obj1 = datetime.strptime(date_from, DATE_FORMAT)
        date_end_obj1 = datetime.strptime(date_to, DATE_FORMAT)
        date_start_obj = date_start_obj1.date()
        date_end_obj = date_end_obj1.date()
        date_start_obj2 = date_start_obj.strftime("%d-%b-%Y")
        date_end_obj2 = date_end_obj.strftime("%d-%b-%Y")

        docs = []

        prospect = self.env['crm.lead'].search(
            [('create_date', '>=', date_start_obj), ('create_date', '<=', date_end_obj), ('stage_id.name', '=', "Qualified")])

        for i in prospect:


            docs.append({'qualified': i.name,'user_id': i.user_id.name,'city': i.city_id.name,'manager': i.manager.name,'department': i.department.name})
            # locs.append({'qualified': count})
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': date_start_obj2,
            'date_to': date_end_obj2,
            'docs': docs,
        }


class Lead(models.Model):
    _inherit = "crm.lead"

    state=fields.Selection([('draft', 'Draft'),('confirm', 'Confirm')], default='draft')
    manager = fields.Many2one("hr.employee",string="Product Manager")
    vendor_code_id = fields.Many2one("vendor.code",string="Vendor Code")
    department = fields.Many2one("hr.department", string="Department")
    city_id = fields.Many2one("city.city","Region")
    # is_user_employee = fields.Boolean(compute="get_is_employee")
    # is_vendor_code = fields.Boolean(compute="get_is_employee")
    # is_region = fields.Boolean(compute="get_is_employee")

    # @api.multi
    # def get_is_employee(self):
    #     user = self.env.user
    #     for record in self:
    #         if record.user_id == user and record.vendor_code_id == user.vendor_code_id :
    #             record.is_vendor_code = True
    #             if record.city_id == user.city_id:
    #                 record.is_user_employee = True

    # @api.multi
    def action_confirm(self):
        return self.write({'state': 'confirm'})


class VendorCode(models.Model):
    _name = "vendor.code"

    name = fields.Char(string="Code")
    description = fields.Char(string="Description")
    vendor_state = fields.Selection(string="Position", selection=[('employee', 'employee'), ('manager', 'manager'), ])

class City(models.Model):
    _name = "city.city"

    name = fields.Char(string="Region")

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    city = fields.Many2one("city.city","Region",required=True)

# class ResPartner(models.Model):
#     _inherit = "res.partner"

    # city=fields.Selection([('riyadh', 'Riyadh'), ('jeddah', 'Jeddah'), ('makkah', 'Makkah'), ('Medina', 'Medina'),
    #                   ('Sulţānah', 'Sulţānah'), ('Dammam', 'Dammam'), ('Taif', 'Taif'), ('Tabuk', 'Tabuk'),
    #                   ('Al Kharj ', 'Al Kharj'), ('Buraidah', 'Buraidah'), ('Khamis Mushait', 'Khamis Mushait'),
    #                   ('Al Hufūf', 'Al Hufūf')], default='riyadh')



