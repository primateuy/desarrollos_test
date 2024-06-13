/** @odoo-module */

import { registry } from "@web/core/registry";
import { kanbanView } from '@web/views/kanban/kanban_view';
import { SaleCatalogProductKanbanModel } from "./sale_catalog_product_kanban_model";
import { SaleCatalogProductKanbanRenderer } from "./sale_catalog_product_kanban_renderer";

export const salecatalogProductKanbanView = {
    ...kanbanView,
    Model: SaleCatalogProductKanbanModel,
    Renderer: SaleCatalogProductKanbanRenderer,
};

registry.category('views').add('sale_catalog_product_kanban', salecatalogProductKanbanView);
