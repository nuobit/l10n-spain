# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


def migrate(cr, version):
    """Deliberately orphan the dropped EDI output template record.

    The 18 version stopped shipping ``facturae_output_template``, but
    ``edi.exchange.type`` rows still reference it
    (``output_template_id``), so the record can never be deleted. Without
    this, Odoo's data GC (``_process_end``) re-attempts the doomed delete
    on every module update and aborts the registry load with a
    ForeignKeyViolation.

    Removing the ``ir.model.data`` row detaches the record from the
    module: it stays in the database as plain instance data and no update
    ever tries to garbage-collect it again.
    """
    cr.execute(
        """
        DELETE FROM ir_model_data
         WHERE module = 'l10n_es_facturae_face'
           AND name = 'facturae_output_template'
        """
    )
