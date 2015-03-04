#* -coding: utf - 8 -* -
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv
from datetime import datetime, date
import datetime
import calendar
import decimal

class ProductCategory(osv.Model):
    _inherit = 'product.category'

    _columns = {
        'product_ids':fields.one2many('product.product','categ_id','Product List'),
		'update_date':fields.datetime('Last price update date'),
		'avg_mrp': fields.float(string='Average MRP',digits=(1,1)),
		'avg_price': fields.float(string='Average LifKart',digits=(1,1)),
		'low_price': fields.float(string='Lowest LifKart',digits=(1,1)),
		'high_price': fields.float(string='Highest LifKart',digits=(1,1)),
		'low_mrp': fields.float(string='Lowest MRP',digits=(1,1)),
		'high_mrp': fields.float(string='Highest MRP',digits=(1,1)),
		'city_ids':fields.many2many('website.city','category_city_ids','product_id','city_id','Deliverable Cities'),
		'calcu_ids':fields.one2many('category.calculation','categ_id','Price List'),
		'calcu_ids_final':fields.one2many('category.calculation.last','categ_id','Price List'),
		'count':fields.integer('Number of items in this category'),
		'category_uom': fields.many2one('product.uom','Category UoM'),
		
        
		
    }

    def update(self,cr,uid,ids,context=None):
		for rec in self.browse(cr,uid,ids):
			for prod in rec.product_ids:
				uom_id=rec.category_uom.id
				qty = prod.sale_qty
				if prod.sale_qty==0:
					qty=1
				mrp = prod.mrp
				if mrp == 0:
					mrp = prod.lst_price*1.05
				mrp_ref = mrp/qty
				price_ref = prod.lst_price/qty
				self.pool.get('product.product').write(cr, uid, [prod.id], {'mrp':mrp,
																			'sale_qty':qty,
																			'mrp_refined':mrp_ref,
																			'price_refined':price_ref,
																			'category_uom':uom_id,
																			
				
				})
							
							
		
				
		return True

	
    def calculate(self,cr,uid,ids,context=None):
		for rec in self.browse(cr,uid,ids):
			now=datetime.datetime.now()
			global_count=0
			global_mrp_total=0
			global_price_total=0
			global_mrp_low=10000000000000
			global_mrp_high=0
			global_mrp_avg=0
			global_price_low=10000000000000
			global_price_high=0
			global_price_avg=0
			for loc in rec.calcu_ids_final:
				local_count=0
				local_mrp_low=10000000000000
				local_mrp_high=0
				local_mrp_avg=0
				local_price_low=10000000000000
				local_price_high=0
				local_price_avg=0
				local_mrp_total=0
				prod_min=0
				prod_avg=0
				prod_max=0
				prod_med=0
				prod_var=10000000000000
				local_price_total=0
				mediun_mrp1=10000000000000
				mediun_mrp2=0
				mediun_price1=10000000000000
				mediun_price2=0
				mediun_op=0
				sd_price=0
				sd_mrp = 0
				
				for prod in rec.product_ids:
									
					for prodloc in prod.city_ids:
						if loc.city_ids.id == prodloc.id:
							local_count=local_count +1
							local_price_total=local_price_total +prod.price_refined
							local_mrp_total= local_mrp_total+prod.mrp_refined
							global_count= global_count+1
							global_price_total =global_price_total +prod.price_refined
							global_mrp_total =global_mrp_total +prod.mrp_refined
							#MRP highest and lowest
							if local_mrp_low > prod.mrp_refined:
								local_mrp_low = prod.mrp_refined
							if global_mrp_low > prod.mrp_refined:
								global_mrp_low = prod.mrp_refined
							if local_mrp_high < prod.mrp_refined:
								local_mrp_high = prod.mrp_refined
							if global_mrp_high < prod.mrp_refined:
								global_mrp_high = prod.mrp_refined
							#Price highest and lowest
							if local_price_low > prod.price_refined:
								local_price_low = prod.price_refined
							if global_price_low > prod.price_refined:
								global_price_low = prod.price_refined
							if local_price_high < prod.price_refined:
								local_price_high = prod.price_refined
							if global_price_high < prod.price_refined:
								global_price_high = prod.price_refined
							#Median MRP and price
							if prod.price_refined > mediun_price2 and prod.price_refined < mediun_price1 :
								mediun_price1 = prod.price_refined
								if mediun_price2 > mediun_price1:
									mediun_op = mediun_price2
									mediun_price2 = mediun_price1
									mediun_price1 = mediun_op
							
							if prod.mrp_refined > mediun_mrp2 and prod.price_refined < mediun_mrp1 :
								mediun_mrp2 = prod.mrp_refined
								if mediun_mrp2 > mediun_mrp1:
									mediun_op = mediun_mrp2
									mediun_mrp2 = mediun_mrp1
									mediun_mrp1 = mediun_op
							
									
							
				if local_count > 0 :
					local_price_avg = local_price_total/local_count	
					local_mrp_avg = local_mrp_total/local_count
					for product in rec.product_ids:
						for productloc in product.city_ids:
							if loc.city_ids.id == productloc.id:
								if product.price_refined == local_price_low:
									prod_min=product.id
								if product.price_refined == local_price_high:
									prod_max=product.id
								if product.price_refined == mediun_price2:
									prod_med=product.id
								prod_diff = local_price_avg - product.price_refined
								mrp_diff =  local_mrp_avg - product.mrp_refined
								sd_price = sd_price + (prod_diff*prod_diff)
								sd_mrp = sd_mrp + (mrp_diff*mrp_diff)
								if prod_diff < 0:
									prod_diff = 0-prod_diff
								if prod_var >= prod_diff:
									prod_var = prod_diff
									prod_avg = product.id
								
								#square root of variance to be added
								
								
								
									
				
					self.pool.get('category.calculation.last').write(cr, uid, [loc.id],{
                                                                                        'avg_mrp':local_mrp_avg,
                                                                                        'avg_price':local_price_avg,
                                                                                        'low_price':local_price_low,
                                                                                        'high_price':local_price_high,
                                                                                        'low_mrp':local_mrp_low,
                                                                                        'high_mrp':local_mrp_high,
                                                                                        'count':local_count,
                                                                                        'update_date':now,
                                                                                        'categ_id':rec.id,
																						'product_low':prod_min,
																						'product_avg':prod_avg,
																						'product_high':prod_max,
																						'product_med':prod_med,
																				
                                                                                        
                                                                                        })	
																						
																		

					statistics_id = self.pool.get('category.calculation').create(cr,uid,{
                                                                                        'avg_mrp':local_mrp_avg,
                                                                                        'avg_price':local_price_avg,
                                                                                        'low_price':local_price_low,
                                                                                        'high_price':local_price_high,
                                                                                        'low_mrp':local_mrp_low,
                                                                                        'high_mrp':local_mrp_high,
                                                                                        'city_ids':loc.city_ids.id,
                                                                                        'count':local_count,
                                                                                        'update_date':now,
                                                                                        'categ_id':rec.id,
																						'mediun_price':mediun_price2,
																						'mediun_mrp':mediun_mrp2,
                                                                                        'sd_mrp' : sd_mrp,
																						'sd_price' : sd_price,
																						'mediun_mrp': mediun_mrp2,
																						'mediun_price': mediun_price2,
																						
																						
                                                                                        })	
			global_price_avg = global_price_total/global_count	
			global_mrp_avg = global_mrp_total/global_count
			self.write(cr,uid,ids,{'update_date':now,
									'avg_mrp':global_mrp_avg,
                                    'avg_price':global_price_avg,
                                    'low_price':global_price_low,
									'high_price':global_price_high,
									'low_mrp':global_mrp_low,
									'high_mrp':global_mrp_high,
									'count':global_count,
                                                                                                                                                                                                
			})	
		return True

ProductCategory()

class ProductProduct(osv.Model):
    _inherit = 'product.product'

    _columns = {
        'mrp': fields.float(string='MRP/Market Price',digits=(1,1)),
		'sale_qty': fields.float(string='Product Sale Quantity',digits=(1,1)),
		'mrp_refined': fields.float(string='Equivallent MRP/Market Price',digits=(1,1)),
		'price_refined': fields.float(string='Equivallent Price',digits=(1,1)),
		'category_uom': fields.many2one('product.uom','Category UoM'),
		'city_ids':fields.many2many('website.city','product_city_ids','product_id','city_id','Deliverable Cities'),
    }

ProductProduct()


class ProductTemplate(osv.Model):
    _inherit = 'product.template'

    _columns = {
        'mrp': fields.float(string='MRP/Market Price',digits=(1,1)),
		'sale_qty': fields.float(string='Product Sale Quantity',digits=(1,1)),
		'mrp_refined': fields.float(string='Equivallent MRP/Market Price',digits=(1,1)),
		'price_refined': fields.float(string='Equivallent Price',digits=(1,1)),
		'category_uom': fields.many2one('res.users','Approved By'),
		'city_ids':fields.many2many('website.city','product_city_ids','product_id','city_id','Deliverable Cities'),
    }

ProductTemplate()


class ProductCities(osv.osv):
    _name="website.city"
    _description="Website Cities"


    _columns={
    
        'name':fields.char('City Name',size=20),
        'pin':fields.integer('Base Pin Code'),
        'state':fields.many2one('res.country.state','State'),
        
        
    }

ProductCities()

class CategoryCalculation(osv.osv):
    _name="category.calculation"
    _description="Website Cities"


    _columns={
		
		'name': fields.char('Analytic Name',size=20),
        'avg_mrp': fields.float(string='Avg MRP',digits=(1,1)),
		'avg_price': fields.float(string='Our Avg',digits=(1,1)),
		'low_price': fields.float(string='Our Low',digits=(1,1)),
		'high_price': fields.float(string='Our High',digits=(1,1)),
		'low_mrp': fields.float(string='Low MRP',digits=(1,1)),
		'high_mrp': fields.float(string='High MRP',digits=(1,1)),
		'city_ids':fields.many2one('website.city','City'),
		'categ_id': fields.many2one('product.category','Related Category'),
		'count':fields.integer('Count'),
		'update_date':fields.datetime('Date'),
		'mediun_mrp': fields.float(string='Median MRP',digits=(1,1)),
		'sd_mrp': fields.float(string='SD MRP',digits=(1,1)),
		'sd_price': fields.float(string='Our SD',digits=(1,1)),
		'mediun_price': fields.float(string='Our Median',digits=(1,1)),
		'high_margin': fields.float(string='Margin Max',digits=(1,1)),
		'Low_margin': fields.float(string='Margin Min',digits=(1,1)),
		'tot_sale': fields.float(string='Sale Total',digits=(1,1)),
		'high_sale': fields.float(string='Sale High',digits=(1,1)),
		'high_sale_prod': fields.many2one('product.product','High Prod'),
		'inflation': fields.float(string='Inflation',digits=(1,1)),
        

        
    }



CategoryCalculation()

class CategoryCalculationLast(osv.osv):
    _name="category.calculation.last"
    _description="Website Cities"


    _columns={
    
        'avg_mrp': fields.float(string='Average MRP',digits=(1,1)),
		'avg_price': fields.float(string='Average LifKart',digits=(1,1)),
		'low_price': fields.float(string='Low LifKart',digits=(1,1)),
		'high_price': fields.float(string='High LifKart',digits=(1,1)),
		'low_mrp': fields.float(string='Lowest MRP',digits=(1,1)),
		'high_mrp': fields.float(string='Highest MRP',digits=(1,1)),
		'city_ids':fields.many2one('website.city','Deliverable City'),
		'categ_id': fields.many2one('product.category','Related Category'),
		'count':fields.integer('Count'),
		'update_date':fields.datetime('Date'),
		'product_low':fields.many2one('product.product','Lowest Product'),
        'product_avg':fields.many2one('product.product','Average Product'),
		'product_high':fields.many2one('product.product','High Product'),
		'product_med':fields.many2one('product.product','Median Product'),
		
        

        
    }



CategoryCalculationLast()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
