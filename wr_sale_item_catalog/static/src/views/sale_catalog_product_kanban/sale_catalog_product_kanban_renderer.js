/** @odoo-module */

import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { SaleCatalogProductKanbanRecord } from "./sale_catalog_product_kanban_record";

export class SaleCatalogProductKanbanRenderer extends KanbanRenderer { }

SaleCatalogProductKanbanRenderer.components = {
    ...KanbanRenderer.components,
    KanbanRecord: SaleCatalogProductKanbanRecord,
};
