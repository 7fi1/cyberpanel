# Generated migration for email filtering features

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CatchAllEmail',
            fields=[
                ('domain', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    primary_key=True,
                    serialize=False,
                    to='mailServer.Domains'
                )),
                ('destination', models.CharField(max_length=255)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'e_catchall',
            },
        ),
        migrations.CreateModel(
            name='EmailServerSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plus_addressing_enabled', models.BooleanField(default=False)),
                ('plus_addressing_delimiter', models.CharField(default='+', max_length=1)),
            ],
            options={
                'db_table': 'e_server_settings',
            },
        ),
        migrations.CreateModel(
            name='PlusAddressingOverride',
            fields=[
                ('domain', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    primary_key=True,
                    serialize=False,
                    to='mailServer.Domains'
                )),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'e_plus_override',
            },
        ),
        migrations.CreateModel(
            name='PatternForwarding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pattern', models.CharField(max_length=255)),
                ('destination', models.CharField(max_length=255)),
                ('pattern_type', models.CharField(
                    choices=[('wildcard', 'Wildcard'), ('regex', 'Regular Expression')],
                    default='wildcard',
                    max_length=20
                )),
                ('priority', models.IntegerField(default=100)),
                ('enabled', models.BooleanField(default=True)),
                ('domain', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='mailServer.Domains'
                )),
            ],
            options={
                'db_table': 'e_pattern_forwarding',
                'ordering': ['priority'],
            },
        ),
    ]
