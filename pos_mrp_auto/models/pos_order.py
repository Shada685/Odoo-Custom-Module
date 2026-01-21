from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # ---------------------------------------------------------
    # POS ORDER CREATION (VALIDATION STAGE)
    # ---------------------------------------------------------
    @api.model
    def _process_order(self, order, draft=False, *args, **kwargs):
        """


        - Validate manufactured products BEFORE order creation
        - Prevent POS payment if BoM is missing
        """

        for line in order.get('lines', []):
            # POS line format: [0, 0, {data}]
            data = line[2]
            product_id = data.get('product_id')
            product = self.env['product.product'].browse(product_id)

            if product.manufacture_from_pos:
                bom_dict = self.env['mrp.bom']._bom_find(
                    product,
                    company_id=order.get('company_id')
                )
                bom = bom_dict.get(product)

                if not bom:
                    raise UserError(_(
                        "Cannot sell '%s' in POS.\n\n"
                        "This product is configured to be manufactured "
                        "but has no Bill of Materials."
                    ) % product.display_name)


        return super()._process_order(order, draft, *args, **kwargs)

    # ---------------------------------------------------------
    # POS PAYMENT CONFIRMATION (MO CREATION)
    # ---------------------------------------------------------
    def action_pos_order_paid(self):
        """
        Triggered after POS payment is completed.
        Creates Manufacturing Orders for eligible products.
        """
        res = super().action_pos_order_paid()

        for order in self:
            for line in order.lines:
                product = line.product_id

                if product.manufacture_from_pos:
                    bom_dict = self.env['mrp.bom']._bom_find(
                        product,
                        company_id=order.company_id.id
                    )
                    bom = bom_dict.get(product)

                    if not bom:
                        raise UserError(_(
                            "Manufacturing failed.\n\n"
                            "Product '%s' has no Bill of Materials."
                        ) % product.display_name)

                    self._create_mo_from_pos_line(order, line, bom)

        return res

    # ---------------------------------------------------------
    # MANUFACTURING ORDER CREATION
    # ---------------------------------------------------------
    def _create_mo_from_pos_line(self, order, line, bom):
        """
        Create and confirm Manufacturing Order from POS line
        """

        picking_type = (
            bom.picking_type_id
            or order.config_id.picking_type_id
        )

        mo = self.env['mrp.production'].create({
            'product_id': line.product_id.id,
            'product_qty': line.qty,
            'product_uom_id': line.product_uom_id.id,
            'bom_id': bom.id,
            'origin': order.name,
            'company_id': order.company_id.id,
            'location_src_id': picking_type.default_location_src_id.id,
            'location_dest_id': picking_type.default_location_dest_id.id,
            'date_start': fields.Datetime.now(),
        })

        # Confirm MO → reserve components
        mo.action_confirm()
