from trytond.model import ModelView, Workflow
from trytond.pool import PoolMeta, Pool


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
            to_save = []
            for production in productions:
                if production.state == 'draft':
                    production.state = 'waiting'
            Production.save(productions)
            Production.assign_try(productions)
            for production in productions:
                if production.state != 'assigned':
                    continue
                if production.outputs:
                    to_location = production.outputs[0].to_location
                    for move in production.origin.moves:
                        shipment = move.shipment
                        for m2 in shipment.inventory_moves:
                            if m2.origin == move:
                                m2.from_location = to_location
                                to_save.append(m2)
            cls.save(to_save)

        return super().assign_try(out_of_scope, with_childs, grouping)

    @classmethod
    @ModelView.button
    @Workflow.transition('done')
    def do(cls, moves):
        Production = Pool().get('production')

        for move in moves:
            linked = move.get_linked_production()
            if not linked:
                continue
            for production in linked:
                if production.state == 'assigned':
                    Production.run([production])
                if production.state == 'running':
                    Production.done([production])
                if production.state == 'done':
                    if production.outputs:
                        move.lot = production.outputs[0].lot
        super().do(moves)
