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

class ijarah_import_sales_commission(osv.osv):
    _name='ijarah.import.sales.commission'
    _columns = {       
	'name':fields.char("Name"),
        'desc':fields.char("Description"), 
        'date':fields.date("For Date"),
	'state': fields.selection([('Draft', 'Draft'),('Open', 'Open'),('Done', 'Done')],'Status',  readonly=True,), 
#        'sales_com_ids': fields.one2many('ijarah.hr.emp.sales.com', 'sales_com_run_id', 'Sales Commission ID'),
#	'lines':fields.one2many('ijarah.import.sales.commission.child','sc_ids',ondelete="cascade"),

}
    _defaults = {
        }    		
ijarah_import_sales_commission()

'''
class ijarah_import_sales_commission_child():
	_name = "ijarah.import.sales.commission.child"
	_columns = {
		'sc_ids' : fields.many2one("ijarah.import.sales.commission","Sales Commission ID",hidden=True,ondelete='cascade'),
		'emp_no':fields.many2one("hr.employee","Employee No"readonly=True),
		'emp_name': fields.char("Employee Name"),
		'amount':fields.float("Amount",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'month':fields.date('Date'),
		'paid':fields.boolean("Paid",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
	}
	def onchange_empno(self, cr, uid,ids,emp_no,context=None):
		if name:		 
			this = self.pool.get('hr.employee').browse(cr, uid,emp_no,context=context)
			value ={'emp_name':this.name_related}
			return {'value': value}
                
	_order = "month"

ijarah_import_sales_commission_child()
'''
