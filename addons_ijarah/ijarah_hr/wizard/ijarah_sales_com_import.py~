# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import fields,osv
import datetime

class ijarah_sales_com_import(osv.osv_memory):
    _name='ijarah.sales.com.import'
    _columns = {       
        'from_date':fields.date("From Date"), 
        'to_date':fields.date("To Date"), 
        }
    _defaults = {
        }    		

    def import_report(self, cr, uid, ids, data, context=None):
        for wiz_obj in self.read(cr,uid,ids):
            if 'form' not in data:
                data['form'] = {}
            data['form']['from_date'] = wiz_obj['from_date']
            data['form']['to_date'] = wiz_obj['to_date']
            data['model'] = 'ijarah.sales.com.import'
            data['ids']=self.pool.get(data['model']).search(cr,uid,[])
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'ijarah_sales_com_report',
                    'datas': data,
            }          
ijarah_sales_com_import()
