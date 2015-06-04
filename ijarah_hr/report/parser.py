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

from openerp.osv import osv, fields
import pooler
import datetime
from openerp.addons import jasper_reports
from openerp.tools.translate import _


def ijarah_equip( cr, uid, ids, data, context ):
      id1 = data['form']['id']
      return {
        'parameters': {	
          	'x': id1
        },
   }

jasper_reports.report_jasper('report.ijarah_equip_report', 'ijarah.hr.emp.equip', parser=ijarah_equip)
############################################# Receive Asset REports ###############################################################
def ijarah_equip_receive( cr, uid, ids, data, context ):
      id1 = data['form']['id']
      return {
        'parameters': {	
          	'x': id1
        },
   }

jasper_reports.report_jasper('report.ijarah_equip_report_receive', 'ijarah.hr.emp.equip', parser=ijarah_equip_receive)
######################################################### Sales Commission Import ###################################################
def ijarah_sales_com_parser(cr, uid, ids, data, context ):
    
	from_date = data['form'].get('from_date')
	to_date = data['form'].get('to_date')
	return {
		'parameters': {    
			'from_date': from_date,
			'to_date': to_date,
			},
		}
jasper_reports.report_jasper('report.ijarah_sales_com_report', 'ijarah.hr.emp.sales.com', parser=ijarah_sales_com_parser)


