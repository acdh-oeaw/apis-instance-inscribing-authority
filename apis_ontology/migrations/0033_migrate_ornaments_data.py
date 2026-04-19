from django.db import migrations


def migrate_ornaments_to_vocab(apps, schema_editor):
    Inscription = apps.get_model('apis_ontology', 'Inscription')
    Ornaments = apps.get_model('apis_ontology', 'Ornaments')

    for inscription in Inscription.objects.all():
        # ornaments was a TextField, now a M2M. The old field is still present at this migration step.
        ornaments_text = getattr(inscription, 'ornaments', None)
        if ornaments_text:
            for ornament in [o.strip() for o in ornaments_text.split(';') if o.strip()]:
                ornament_obj, _ = Ornaments.objects.get_or_create(label=ornament)


def reverse_func(apps, schema_editor):
    # No reverse migration
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('apis_ontology', '0032_ornaments'),
    ]

    operations = [
        migrations.RunPython(migrate_ornaments_to_vocab, reverse_func),
    ]