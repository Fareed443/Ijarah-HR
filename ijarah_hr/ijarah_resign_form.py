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


class ijarah_hr_emp_resign(osv.osv):

	def create(self, cr, uid, vals,context=None):		
		name = vals['name']
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
                vals['grade'] = this.contract_id.grade # name.dbfieldname			
                vals['emp_name'] = this.name_related # name.dbfieldname			
                vals['job_id'] = this.job_id.id # name.dbfieldname			
                vals['dept_id'] = this.department_id.id # name.dbfieldname
#		vals['assign_name']= str(prod.designation.name)		
		return super(ijarah_hr_emp_resign,self).create(cr, uid, vals, context)
	
	def write(self, cr, uid, ids, vals, context=None):						
		name = vals.get('name')
		this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
		contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
		res={}	
		if vals.get('name'):
			vals['grade'] = this.contract_id.grade # name.dbfieldname			
			vals['emp_name'] = this.name_related # name.dbfieldname			
			vals['job_id'] = this.job_id.id # name.dbfieldname
			vals['dept_id']=this.department_id.id			
			res.update({'grade': this.contract_id.grade,'emp_name':this.name_related,'job_id':this.job_id.id ,'dept_id':this.department_id.id})
		result = super(ijarah_hr_emp_resign, self).write(cr, uid, ids, vals, context=context)	
		return result

	_name = "ijarah.hr.emp.resign"
	_description = "Employee Resignation Form"
	_columns = {
		'name'	: fields.many2one("hr.employee","Employee No",required=True,domain="[('activate','=',True)]",states={'Approved':[('readonly',True)]}),
		'emp_name':fields.char("Employee Name",readonly=True,states={'Approved':[('readonly',True)]}),
		'job_id':fields.many2one("hr.job","Job Title",readonly=True,states={'Approved':[('readonly',True)]}),
		'state': fields.selection([('Draft', 'Draft'),('Approved', 'Approved'),('Cancel','Cancel'),('Resigned','Resigned')],'Status', readonly=True,),
		'dept_id':fields.many2one("hr.department","Dept/Branch",readonly=True),
		'grade':fields.char("Grade",readonly=True),
		'contact_no':fields.char("Contact Number"),
		'date_of_subm':fields.date("Date of Submission"),
		'last_work_day':fields.date("Last Working Day"),
		'notice_period': fields.selection([
			('I will work', 'I will work'),
			('I will not work', 'I will not work'),
			('Cancel the Notice Period', 'Cancel the Notice Period')],'Notice Period(1 Month)',required=True),
		'resign_reason':fields.text("Reason for Resignation",required=True),
		'approved_by':fields.many2one("res.users","Approved By",readonly=True),
	}
	_defaults = {			
		'state'  : lambda * a :'Draft',
	}
	
	def unlink(self, cr, uid, ids, context=None):
		res = self.pool.get('ijarah.hr.emp.resign').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in res:
		    if x['state'] in ('Draft'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete Form which are already Approved & Cancel !'))
#		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
#		return True
		return super(ijarah_hr_emp_resign, self).unlink(cr, uid, ids, context=context)
        	
	def approved_state(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'Approved','approved_by':uid}, context=context)
		return True
		
	def cancel_state(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'Cancel'}, context=context)
		return True

	def resigned_state(self, cr, uid, ids,context=None):
		this = self.browse(cr,uid, ids[0], context=None)
#		nam = this.name.id
		cr.execute("""SELECT state from ijarah_hr_emp_equip where name = %s """,[this.name.id])
		x = cr.fetchone()	
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
		if x:
			if x[0] == "Received" or x[0] == "Draft":			
				self.write(cr, uid, ids, {'state':'Resigned'}, context=context)
				cr.execute("""UPDATE hr_employee set activate = 'False',state = 'Resigned' where id = %s""",[this.name.id])
			if x[0] == 'Delivered':			
				raise osv.except_osv(_('Configuration Error!'),_('Assets are Pending for this Employee'))
		else:
			self.write(cr, uid, ids, {'state':'Resigned'}, context=context)
			cr.execute("""UPDATE hr_employee set activate = 'False',state = 'Resigned' where id = %s""",[this.name.id])
			return True			


	def onchange_contact_no(self, cr, uid, ids,contact_no,context=None):
		if contact_no:
			if contact_no.isdigit()==False:
				return { 'warning':{'title':'warning','message':'Contact Number should be digit'},'value' :{'contact_no':''}}	
		return {'value': {}}	
		         		    	
	def onchange_empno(self, cr, uid,ids,name,context=None):
		if name:		 
			this = self.pool.get('hr.employee').browse(cr, uid,name,context=context)
			contract_id = self.pool.get('hr.contract').browse(cr,uid,name,context=context)
			value ={'grade':this.contract_id.grade,'emp_name':this.name_related,'job_id':this.job_id.id,'dept_id':this.department_id.id}
			return {'value': value}

ijarah_hr_emp_resign()

