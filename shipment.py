from trytond.model import ModelView, Workflow
from trytond.pool import PoolMeta, Pool
from trytond.modules.company.model import set_employee


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

    def get_linked_production(self):
        SaleLine = Pool().get('sale.line')
        if isinstance(self.origin, Move) and isinstance(self.origin.origin, SaleLine):
            return self.origin.origin.productions

    @classmethod
    def assign_try(cls, moves, with_childs=True, grouping=('product',)):
        pool = Pool()
        Production = pool.get('production')

        productions = []
        out_of_scope = []
        for move in moves:
            linked = move.get_linked_production()
            if linked:
                productions += linked
            else:
                out_of_scope.append(move)
        if productions:
            for production in productions:
                production.state = 'waiting'
            Production.assign_try(productions)
            for production in productions:
                if production.state == 'waiting':
                    cls.assign(production.origin.moves)
        return super().assign_try(out_of_scope, with_childs, grouping)

    @classmethod
    def pack(cls, moves):
        Production = Pool().get('production')
        for move in moves:
            linked = move.get_linked_production()
            if linked:
                to_run = []
                for production in linked:
                    if production.state == 'assigned':
                        to_run.append(production)
                if to_run:
                    Production.run(to_run)
                    Production.done(to_run)

#si la produccio ha anat be, reservar moviment

class ShipmentOut(metaclass=PoolMeta):
    __name__ = 'stock.shipment.out'

    @classmethod
    @ModelView.button
    @Workflow.transition('picked')
    @set_employee('picked_by')
    def pick(cls, shipments):
        Move = Pool().get('stock.move')

        productions = []
        for shipment in shipments:
            for move in shipment.moves:
                linked = move.get_linked_production()
                if linked:
                    productions += [move]
        Move.assign_try(productions, with_childs=True, grouping=('product',))
        return super(ShipmentOut, cls).pick(shipments)

    @classmethod
    @ModelView.button
    @Workflow.transition('packed')
    @set_employee('packed_by')
    def pack(cls, shipments):
        Move = Pool().get('stock.move')

        productions = []
        for shipment in shipments:
            for move in shipment.moves:
                linked = move.get_linked_production()
                if linked:
                    productions += [move]
        Move.pack(productions)
        return super(ShipmentOut, cls).pack(shipments)

