
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("invoices", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE invoices_invoice
                ADD COLUMN IF NOT EXISTS uploaded_by_id integer NULL;

                CREATE INDEX IF NOT EXISTS
                invoices_invoice_uploaded_by_id_idx
                ON invoices_invoice (uploaded_by_id);

                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint
                        WHERE conname = 'invoices_invoice_uploaded_by_id_fk'
                    ) THEN
                        ALTER TABLE invoices_invoice
                        ADD CONSTRAINT invoices_invoice_uploaded_by_id_fk
                        FOREIGN KEY (uploaded_by_id)
                        REFERENCES auth_user(id)
                        ON DELETE SET NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                ALTER TABLE invoices_invoice
                DROP CONSTRAINT IF EXISTS
                invoices_invoice_uploaded_by_id_fk;

                DROP INDEX IF EXISTS
                invoices_invoice_uploaded_by_id_idx;

                ALTER TABLE invoices_invoice
                DROP COLUMN IF EXISTS uploaded_by_id;
            """,
        ),
    ]
