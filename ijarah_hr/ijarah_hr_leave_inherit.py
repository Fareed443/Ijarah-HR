from openerp.osv import osv, fields
from datetime import datetime,time
from datetime import datetime
from dateutil import relativedelta
from lxml import etree    
import datetime
import time
import math
from openerp.tools.translate import _
from datetime import date, timedelta
from datetime import date
from openerp import netsvc
from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp.tools.safe_eval import safe_eval as eval

class hr_holidays(osv.osv):
	"""Employee Holidays """		

	def create(self, cr, uid, vals,context=None):		
		employee_id = vals['employee_id']
		cr.execute("SELECT max(id) from hr_holidays where employee_id = %s and type = 'remove'",[employee_id])
		max_id = cr.fetchone()[0]		
		cr.execute("""SELECT leave_request_no from hr_holidays where id = %s """,[max_id])
		leave_request_no = cr.fetchone()
#		raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal  %s has not properly configured the Credit Account!')%(leave_request_no))
		#if leave_request_no:
		if leave_request_no == None:
			result = '1'				
		elif leave_request_no != None:
			num = int(leave_request_no[0])
			num = num + 1
			result = num
                vals['leave_request_no'] = result# name.dbfieldname			
		return super(hr_holidays,self).create(cr, uid, vals, context)

	def _employee_leave_no(self,cr,uid,employee_id,context=None):
	####CHANGING REQUIRED HERE IN THIS FUNCTIONN
		emp_id = employee_id
		cr.execute("SELECT max(id) from hr_holidays where employee_id = %s and type = 'remove' and state='validate' ",[emp_id])
		max_id = cr.fetchone()[0]		
		cr.execute("""SELECT leave_request_no from hr_holidays where id = %s """,[max_id])
		leave_request_no = cr.fetchone()
		if leave_request_no == None:
			result = '1'				
		elif leave_request_no != None:
			#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal  %s has not properly configured the Credit Account!')%(leave_request_no))
			num = int(leave_request_no[0])
			num = num + 1
			result = num
		return result
		
	_name = "hr.holidays"
	_description = "Leave"
	_inherit = ['hr.holidays', 'ir.needaction_mixin']
	_columns = {
	'manager_id': fields.many2one('hr.employee', "Manager",domain="[('activate','=',True)]",), #,domain=[('name','=',['Ijarah','OutSource'])],),
	'leave_request_no':fields.char("Leave Request No",size=3,readonly=True),
	'remaining_leave':fields.float("Remaining Leaves"),
	'remaining_leave_int':fields.integer("Remaining Leaves"),
	'paid':fields.boolean("Paid",readonly=True),
	}
	_default = {
#		'leave_request_no':_employee_leave_no,
		'paid':False,
	}		
	def onchange_employee(self, cr, uid, ids, employee_id):
		result = {'value': {'department_id': False,'manager_id': False}}
		my_leave = self._employee_leave_no(cr,uid,employee_id,context=None)
		if employee_id:
			employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
			result['value'] = {'department_id': employee.department_id.id,'manager_id':employee.parent_id.id,
				'remaining_leave':employee.remaining_leaves,'leave_request_no':my_leave,'remaining_leave_int':int(employee.remaining_leaves),} 
		return result

	def onchange_number_of_days(self, cr, uid, ids, no_of_days_temp_int):
		if no_of_days_temp_int:
			value ={'number_of_days_temp': no_of_days_temp_int}
			return {'value': value}
		return True

hr_holidays()

