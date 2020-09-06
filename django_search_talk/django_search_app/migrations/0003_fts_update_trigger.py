from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('django_search_app', '0002_auto_20200716_0758'),
    ]

    migration = '''
        CREATE TRIGGER review_index_update BEFORE INSERT OR UPDATE
        ON django_search_app_ftsreview FOR EACH ROW EXECUTE FUNCTION
        tsvector_update_trigger(review_index, 'pg_catalog.english', review_summary, review_text);

        UPDATE django_search_app_ftsreview set ID = ID;
    '''

    reverse_migration = '''
        DROP TRIGGER review_index_update ON django_search_app_ftsreview;
    '''

    operations = [
        migrations.RunSQL(migration, reverse_migration)
    ]


