# -*- coding: utf-8 -*-
# from odoo import http


# class Warcraft(http.Controller):
#     @http.route('/warcraft/warcraft', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/warcraft/warcraft/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('warcraft.listing', {
#             'root': '/warcraft/warcraft',
#             'objects': http.request.env['warcraft.warcraft'].search([]),
#         })

#     @http.route('/warcraft/warcraft/objects/<model("warcraft.warcraft"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('warcraft.object', {
#             'object': obj
#         })
