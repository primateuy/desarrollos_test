from odoo import fields, models

class ReportStockByWarehouse(models.Model):
    _name = 'report.stock.by.warehouse'
    _description = 'Reporte de stock por almacén'
    _auto = False

    id = fields.Integer(string='ID', readonly=True)
    product_id = fields.Many2one('product.product', string="Producto")
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    location_id = fields.Many2one('stock.location', string="Ubicación")
    lot_id = fields.Many2one('stock.lot', string="Lote")
    qty_available = fields.Float(string="Stock Real")
    incoming_qty = fields.Float(string="Stock Entrante")
    outgoing_qty = fields.Float(string="Stock Saliente")
    virtual_available = fields.Float(string="Stock Pronosticado")
    yearly_outgoing_qty = fields.Float(string='Consumo Anual Salidas', readonly=True)
    days_of_stock = fields.Float(string='Stock en Días', readonly=True)
    
    
    def init(self):
        self._cr.execute("""
    CREATE OR REPLACE VIEW report_stock_by_warehouse AS (
SELECT
    row_number() OVER ()               AS id,
    sq.product_id,
    sq.location_id,
    sw.id                              AS warehouse_id,
    sq.lot_id                          AS lot_id,

    -- stock hoy
    SUM(sq.quantity)                   AS qty_available,

    -- reservado
    SUM(sq.reserved_quantity)          AS outgoing_qty,

    -- entrante
    COALESCE((
        SELECT SUM(sm.product_uom_qty)
        FROM stock_move_line sml
        JOIN stock_move sm ON sm.id = sml.move_id
        WHERE sm.product_id = sq.product_id
          AND sml.location_dest_id = sq.location_id
          AND sm.state IN ('confirmed', 'assigned', 'waiting')
          AND (
            (sml.lot_id IS NULL AND sq.lot_id IS NULL)
            OR (sml.lot_id = sq.lot_id)
          )
    ), 0)                             AS incoming_qty,

    -- disponible virtual
    SUM(sq.quantity)
    + COALESCE((
        SELECT SUM(sm.product_uom_qty)
        FROM stock_move_line sml
        JOIN stock_move sm ON sm.id = sml.move_id
        WHERE sm.product_id = sq.product_id
          AND sml.location_dest_id = sq.location_id
          AND sm.state IN ('confirmed', 'assigned', 'waiting')
          AND (
            (sml.lot_id IS NULL AND sq.lot_id IS NULL)
            OR (sml.lot_id = sq.lot_id)
          )
    ), 0)
    - SUM(sq.reserved_quantity)        AS virtual_available,

    -- consumo diario últimos 30 días (salidas)
    COALESCE((
        SELECT
            SUM(sm.product_uom_qty)::float / 30
        FROM stock_move_line sml
        JOIN stock_move sm ON sm.id = sml.move_id
        WHERE sm.product_id = sq.product_id
          AND sml.location_id = sq.location_id
          AND sm.state = 'done'
          AND sm.date >= current_date - interval '30 days'
          AND (
            (sml.lot_id IS NULL AND sq.lot_id IS NULL)
            OR (sml.lot_id = sq.lot_id)
          )
          AND sm.location_dest_id != sq.location_id  -- movimientos de salida
    ), 0)                             AS daily_consumption,

    -- días de stock disponibles (si consumo diario > 0)
    CASE
      WHEN COALESCE((
          SELECT
              SUM(sm.product_uom_qty)::float / 30
          FROM stock_move_line sml
          JOIN stock_move sm ON sm.id = sml.move_id
          WHERE sm.product_id = sq.product_id
            AND sml.location_id = sq.location_id
            AND sm.state = 'done'
            AND sm.date >= current_date - interval '30 days'
            AND (
              (sml.lot_id IS NULL AND sq.lot_id IS NULL)
              OR (sml.lot_id = sq.lot_id)
            )
            AND sm.location_dest_id != sq.location_id
      ), 0) > 0 THEN
        SUM(sq.quantity) / NULLIF((
            SELECT
                SUM(sm.product_uom_qty)::float / 30
            FROM stock_move_line sml
            JOIN stock_move sm ON sm.id = sml.move_id
            WHERE sm.product_id = sq.product_id
              AND sml.location_id = sq.location_id
              AND sm.state = 'done'
              AND sm.date >= current_date - interval '30 days'
              AND (
                (sml.lot_id IS NULL AND sq.lot_id IS NULL)
                OR (sml.lot_id = sq.lot_id)
              )
              AND sm.location_dest_id != sq.location_id
        ), 0) -- evita división por cero
      ELSE NULL
    END                              AS days_of_stock

FROM stock_quant sq
JOIN stock_location  sl ON sq.location_id = sl.id
JOIN stock_warehouse sw ON sl.warehouse_id = sw.id
GROUP BY
    sq.product_id,
    sq.location_id,
    sw.id,
    sq.lot_id
);
    """)