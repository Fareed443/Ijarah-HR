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

class ijarah_hr_emp_equip(osv.osv):
	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):

			res = {}
			for order in self.browse(cr, uid, ids, context=context):
				res[order.id] = {               
				    'total_amount': 0.00,
				}
				val = val1 = val2 = val3 = val4= 0.00
				for line in order.lines:
				    val1 += line.amount 
			res[order.id]['total_amount'] = val1				
			return res		

	def create(self, cr, uid, vals,context=None):		
		name = vals['name']
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
                vals['salary'] = this.contract_id.basic_salary # name.dbfieldname			
                vals['emp_name'] = this.name_related # name.dbfieldname			
                vals['job_id'] = this.job_id.id # name.dbfieldname			
		return super(ijarah_hr_emp_equip,self).create(cr, uid, vals, context)
	
	def write(self, cr, uid, ids, vals, context=None):						
		name = vals.get('name')
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
		res={}	
		if vals.get('name'):
			vals['salary'] = this.contract_id.basic_salary # name.dbfieldname			
			vals['emp_name'] = this.name_related # name.dbfieldname			
			vals['job_id'] = this.job_id.id # name.dbfieldname			
			res.update({'salary': this.contract_id.basic_salary , 'emp_name':this.name_related,'job_id':this.job_id.id})		

		result = super(ijarah_hr_emp_equip, self).write(cr, uid, ids, vals, context=context)	
		return result

	def _get_number_of_days(self, for_month, month_end_date):
	
		DATETIME_FORMAT = "%Y-%m-%d"		
		from_dt = datetime.strptime(for_month, DATETIME_FORMAT)
		to_dt = datetime.strptime(month_end_date, DATETIME_FORMAT)
		timedelta = to_dt - from_dt
		diff_day = timedelta.days + float(timedelta.seconds) / 86400
		return diff_day		

	_name = "ijarah.hr.emp.equip"
	_columns = {
		'name'	: fields.many2one("hr.employee","Employee No",required=True,domain="[('activate','=',True)]",states={'Delivered':[('readonly',True)],'Received':[('readonly',True)]}),
		'emp_name':fields.char("Employee Name",readonly=True,states={'Delivered':[('readonly',True)],'Received':[('readonly',True)]}),
		'job_id':fields.many2one("hr.job","Job Title",readonly=True,states={'Delivered':[('readonly',True)],'Received':[('readonly',True)]}),
		'salary':fields.float("Salary",readonly=True,states={'Delivered':[('readonly',True)],'Received':[('readonly',True)]}),
		'state': fields.selection([('Draft', 'Draft'),('Delivered', 'Delivered'),('Received', 'Received')],'Status',  readonly=True,),
		'note':fields.text("Note",states={'Delivered':[('readonly',True)],'Received':[('readonly',True)]}),
		'total_amount': fields.function(_amount_all,method=True,string='Deduct Amount',multi='sums',store=True,type='float'),
		'lines':fields.one2many('ijarah.hr.emp.equip.child','equip_ids',ondelete="cascade"),
		'received_date':fields.date("Received Date",readonly=True),
		'paid':fields.boolean("Paid",readonly=True),	
	}
	_defaults = {			
		'state'  : lambda * a :'Draft',
		'paid': False,
	}

	def start_report(self, cr, uid, ids, data, context=None):
	    if 'form' not in data:
	        data['form'] = {}
	    data['form']['id'] = ids[0]            
	    data['model'] = 'ijarah.hr.emp.equip'
	    data['ids']=self.pool.get(data['model']).search(cr,uid,[])
	    return {
	            'type': 'ir.actions.report.xml',
	            'report_name': 'ijarah_equip_report',
	            'datas': data,
	            'nodestroy':True
	}    

	def receive_report(self, cr, uid, ids, data, context=None):
	    if 'form' not in data:
	        data['form'] = {}
	    data['form']['id'] = ids[0]            
	    data['model'] = 'ijarah.hr.emp.equip'
	    data['ids']=self.pool.get(data['model']).search(cr,uid,[])
	    return {
	            'type': 'ir.actions.report.xml',
	            'report_name': 'ijarah_equip_report_receive',
	            'datas': data,
	            'nodestroy':True
	}    
	
	def unlink(self, cr, uid, ids, context=None):
		ded = self.pool.get('ijarah.hr.emp.equip').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in ded:
		    if x['state'] in ('Draft'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete Equipment(s) which are already Delivered or Done state !'))
#		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
#		return True
		return super(ijarah_hr_emp_equip, self).unlink(cr, uid, ids, context=context)        
    		
	def deliver_state(self, cr, uid, ids, context=None):
		cr.execute("""UPDATE ijarah_hr_emp_equip_child set state_cond = 'Delivered' where equip_ids = %s """,[ids[0]])
		self.write(cr, uid, ids, {'state':'Delivered'}, context=context)
		return True
		         		    	
	def received_state(self, cr, uid, ids, context=None):
		rec_date = time.strftime('%Y/%m/%d') #Received Date / Todays Date
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Credit Account!')%(rec_date))
		for order in self.browse(cr, uid, ids, context=context):
			for line in order.lines:
				if not line.rec_date:
					raise osv.except_osv(_('Configuration Error!'),_('Please update Received date'))
				else:
					cr.execute("""UPDATE ijarah_hr_emp_equip_child set state_cond = 'Received' where equip_ids = %s """,[ids[0]])
		self.write(cr, uid, ids, {'state':'Received','received_date':rec_date}, context=context)
		return True

	def onchange_empno(self, cr, uid,ids,name,context=None):
		if name:		 
			this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
			contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
			value =	{'salary':this.contract_id.basic_salary,'emp_name':this.name_related,'job_id':this.job_id.id}
			return {'value': value}
		
ijarah_hr_emp_equip()

class ijarah_hr_emp_equip_child(osv.osv):
        
	_name = "ijarah.hr.emp.equip.child"
	_columns = {
		'equip_ids' : fields.many2one("ijarah.hr.emp.equip","EQUIP ID",hidden=True,ondelete='cascade'),
		'product_id':fields.many2one("ijarah.product","Product"),
		'product_cost':fields.float("Product Cost"),	
		'qty':fields.float("Quantity"),
		'description':fields.char("Description"),
		'serial_no':fields.char("Serial No"),
		'del_date' :fields.date("Assign Date"),
		'rec_date' : fields.date("Received Date"),
		'if_received':fields.boolean("Received"),
		'state': fields.selection([('Damaged', 'Damaged'),('Good Condition', 'Good Condition'),('Lost', 'Lost')],'Status',),
		'amount':fields.float("Deduction Amount"),
		'state_cond': fields.selection([('Draft', 'Draft'),('Delivered', 'Delivered'),('Received', 'Received')],'Status',invisible=True,),
	}    
	_defaults = {			
		'if_received'  : False,
		'state_cond':lambda * a :'Draft',
		'amount':lambda * a :0.00,		
	}

	def onchange_received_date(self, cr, uid,ids,rec_date,context=None):
		value = {}
		if rec_date:	
			value = {'if_received': True}
		else :
			return True
		return {'value': value}

ijarah_hr_emp_equip_child()        

