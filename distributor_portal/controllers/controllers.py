# -*- coding: utf-8 -*-
from odoo import http

# class DistributorPortal(http.Controller):
#     @http.route('/distributor_portal/distributor_portal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/distributor_portal/distributor_portal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('distributor_portal.listing', {
#             'root': '/distributor_portal/distributor_portal',
#             'objects': http.request.env['distributor_portal.distributor_portal'].search([]),
#         })

#     @http.route('/distributor_portal/distributor_portal/objects/<model("distributor_portal.distributor_portal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('distributor_portal.object', {
#             'object': obj
#         })