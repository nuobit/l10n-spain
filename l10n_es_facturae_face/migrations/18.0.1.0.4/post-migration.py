# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Remove the legacy EDI output template this version stopped shipping.

    Up to 17.0 the module's data declared ``facturae_output_template``
    (``edi.exchange.template.output``) and output generation went through
    it. The 18.0 migration moved generation into
    ``l10n_es.facturae.face.output.handler`` (which renders the report
    directly) and dropped the template from the data files, but shipped no
    migration to clean up the record left behind in existing databases.

    Meanwhile ``edi_exchange_template_oca``'s 18.0.1.2.0 pre-migration
    converts the legacy ``template.type_id`` link into
    ``edi.exchange.type.output_template_id`` (ondelete=restrict), so the
    stale record ends up referenced by the exchange type. Odoo's module
    data GC (``ir.model.data._process_end``) then re-attempts the doomed
    DELETE on every update of this module and aborts the registry load
    with a ForeignKeyViolation.

    Fix at the origin: clear the now-unused pointer and delete the record
    the module abandoned. The exchange type keeps generating through the
    handler (``generate_model_id``), so behavior is unchanged. Idempotent:
    databases where the template is already gone are left untouched.
    """
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    template = env.ref(
        "l10n_es_facturae_face.facturae_output_template", raise_if_not_found=False
    )
    if not template:
        return
    types = env["edi.exchange.type"].search([("output_template_id", "=", template.id)])
    types.write({"output_template_id": False})
    template.unlink()
