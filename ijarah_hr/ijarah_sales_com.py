from openerp.osv import osv, fields
from datetime import datetime,time
from openerp.addons import jasper_reports
from lxml import etree    
import datetime
import time
import math
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
from datetime import timedelta
from dateutil import relativedelta
from datetime import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

class ijarah_hr_emp_sales_com(osv.osv_memory):
	
	def create(self, cr, uid, vals,context=None):		
		name = vals['name']
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
                vals['emp_name'] = this.name_related # name.dbfieldname			
		return super(ijarah_hr_emp_sales_com,self).create(cr, uid, vals, context)
	
	def write(self, cr, uid, ids, vals, context=None):						
		name = vals.get('name')
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		res={}	
		if vals.get('name'):
			vals['emp_name'] = this.name_related # name.dbfieldname			
			res.update({'emp_name':this.name_related,})		
		result = super(ijarah_hr_emp_sales_com, self).write(cr, uid, ids, vals, context=context)	
		return result

	_name = "ijarah.hr.emp.sales.com"
	_columns = {
		'name'	: fields.many2one("hr.employee","Employee No",required=True,domain="[('activate','=',True)]",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'emp_name':fields.char("Employee Name",readonly=True,states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'amount':fields.float("Amount",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'paid':fields.boolean("Paid",states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
		'state': fields.selection([('Draft', 'Draft'),('Open', 'Open'),('Done', 'Done')],'Status',  readonly=True,),
		'month':fields.date('Date',states={'Open':[('readonly',True)],'Done':[('readonly',True)]}),
	        'sales_com_run_id': fields.many2one('ijarah.sales.com.batch', 'Sales Commission ID', readonly=True, states={'draft': [('readonly', False)]}),
	}
	_defaults = {			
		'state'  : lambda * a :'Draft',
		'paid': False,	
	}
	
	def unlink(self, cr, uid, ids, context=None):
		this = self.pool.get('ijarah.hr.emp.sales.com').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in this:
		    if x['state'] in ('Draft'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete Entries which are already Done state !'))
#		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		return super(ijarah_hr_emp_sales_com, self).unlink(cr, uid, ids, context=context)
#		return True
        
    		
	def validate_state(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'Open'}, context=context)
		return True
		         		    	
	def onchange_empno(self, cr, uid,ids,name,context=None):
		if name:		 
			this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
			value ={'emp_name':this.name_related}
			return {'value': value}

ijarah_hr_emp_sales_com
