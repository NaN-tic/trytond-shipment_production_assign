# This file is part shipment_production_assign module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase
from trytond.modules.company.tests import (
    CompanyTestMixin, create_company, set_company)
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.transaction import Transaction
from trytond.pool import Pool
from decimal import Decimal
import datetime


class ShipmentProductionAssignTestCase(ModuleTestCase):
    'Test Shipment Production Assign module'
    module = 'shipment_production_assign'

    @with_transaction()
    def test_shipment_production(self):
        'Sale assign production'
        pool = Pool()
        Template = pool.get('product.template')
        Uom = pool.get('product.uom')
        Location = pool.get('stock.location')
        Move = pool.get('stock.move')
        Party = pool.get('party.party')
        PaymentTerm = pool.get('account.invoice.payment_term')
        Shipment = pool.get('stock.shipment.out')
        Sale = pool.get('sale.sale')
        Production = pool.get('production')

        company = create_company()
        with set_company(company):
            unit, = Uom.search([('name', '=', 'Unit')])
            template, = Template.create([{
                        'name': 'Test Move.income/expense_analytic_lines',
                        'type': 'goods',
                        'list_price': Decimal(4),
                        'cost_price_method': 'fixed',
                        'default_uom': unit.id,
                        'products': [
                            ('create', [{}]),
                            ],
                        }])
            product, = template.products
            supplier, = Location.search([('code', '=', 'SUP')])
            customer, = Location.search([('code', '=', 'CUS')])
            storage, = Location.search([('code', '=', 'STO')])
            storage2, = Location.create([{
                        'name': 'Storage 2',
                        'code': 'STO2',
                        'type': 'storage',
                        'parent': storage.id,
                        }])

            today = datetime.date.today()

            # Create origin fields for moves
            party, = Party.create([{
                        'name': 'Customer/Supplier',
                        }])
            term, = PaymentTerm.create([{
                        'name': 'Payment Term',
                        'lines': [
                            ('create', [{
                                        'sequence': 0,
                                        'type': 'remainder',
                                        }])]
                        }])

        party, = Party.create([{
                        'name': 'Customer/Supplier',
                        }])
        party.addresses = [{}]
        term, = PaymentTerm.create([{
                        'name': 'Payment Term',
                        'lines': [
                            ('create', [{
                                        'sequence': 0,
                                        'type': 'remainder',
                                        }])]
                        }])
        sale, = Sale.create([{
                        'party': party.id,
                        'payment_term': term.id,
                        'company': company.id,
                        'currency': company.currency.id,
                        'lines': [('create', [{
                                        'quantity': 1.0,
                                        'unit_price': Decimal(1),
                                        'description': 'desc',
                                        }])],

                        }])
        sale_line, = sale.lines
        moves = Move.create([{
                    'product': product.id,
                    'uom': unit.id,
                    'quantity': 5,
                    'from_location': supplier.id,
                    'to_location': customer.id,
                    'planned_date': today,
                    'effective_date': today,
                    'company': company.id,
                    'unit_price': Decimal('1'),
                    'currency': company.currency.id,
                    'origin': str(sale_line),
                    }, {
                    'product': product.id,
                    'uom': unit.id,
                    'quantity': 10,
                    'from_location': supplier.id,
                    'to_location': storage.id,
                    'planned_date': today,
                    'effective_date': today,
                    'company': company.id,
                    'unit_price': Decimal('1'),
                    'currency': company.currency.id,
                    'origin': str(sale_line),
                    }, {
                    'product': product.id,
                    'uom': unit.id,
                    'quantity': 5,
                    'from_location': storage.id,
                    'to_location': storage2.id,
                    'planned_date': today,
                    'effective_date': today,
                    'company': company.id,
                    'unit_price': Decimal('1'),
                    'currency': company.currency.id,
                    }, {
                    'product': product.id,
                    'uom': unit.id,
                    'quantity': 5,
                    'from_location': storage2.id,
                    'to_location': customer.id,
                    'planned_date': today,
                    'effective_date': today,
                    'company': company.id,
                    'unit_price': Decimal('1'),
                    'currency': company.currency.id,
                    'origin': str(sale_line),
                    }])
        with set_company(company):
            shipment = Shipment()
            shipment.customer = party
            shipment.delivery_address, = party.addresses
            shipment.warehouse = Shipment.default_warehouse()
            shipment.on_change_warehouse()
            shipment.save()
            shipment.moves = moves
            Move.assign_try(moves, with_childs=True, grouping=('product',))
            shipment.save()
            shipment.wait([shipment])
            Shipment.pick([shipment])
            Shipment.pack([shipment])
            Shipment.done([shipment])
            sale.save()
            shipment.save()
            self.assertEqual(shipment.state, 'done')
            self.assertEqual(sale.state, 'done')

del ModuleTestCase
