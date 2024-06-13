/** @odoo-module */

import { KanbanModel } from '@web/views/kanban/kanban_model';
import { SaleCatalogProductRecord } from './sale_catalog_product_record';

export class SaleCatalogProductKanbanModel extends KanbanModel { }

SaleCatalogProductKanbanModel.Record = SaleCatalogProductRecord;
