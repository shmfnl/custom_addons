from odoo import models
from PyPDF2 import PdfMerger
import io
import base64

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _render_qweb_pdf(self, report_ref=None):
        report = self.env.ref(report_ref or 'sale.action_report_saleorder')
        base_pdf, _ = super()._render_qweb_pdf(report_ref)

        merger = PdfMerger()
        merger.append(io.BytesIO(base_pdf))

        seen_documents = set()
        for order in self:
            for line in order.order_line:
                for doc in line.product_id.product_tmpl_id.document_ids:
                    if doc.id in seen_documents:
                        continue
                    seen_documents.add(doc.id)
                    if doc.datas:
                        pdf_data = base64.b64decode(doc.datas)
                        merger.append(io.BytesIO(pdf_data))

        output = io.BytesIO()
        merger.write(output)
        merger.close()
        return output.getvalue(), 'pdf'
