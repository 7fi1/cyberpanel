# Generated migration for email filtering features
# Uses raw SQL since existing email models weren't created via Django migrations

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS `e_catchall` (
                    `domain_id` varchar(50) NOT NULL PRIMARY KEY,
                    `destination` varchar(255) NOT NULL,
                    `enabled` tinyint(1) NOT NULL DEFAULT 1,
                    CONSTRAINT `fk_catchall_domain` FOREIGN KEY (`domain_id`) REFERENCES `e_domains` (`domain`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            reverse_sql="DROP TABLE IF EXISTS `e_catchall`;"
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS `e_server_settings` (
                    `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    `plus_addressing_enabled` tinyint(1) NOT NULL DEFAULT 0,
                    `plus_addressing_delimiter` varchar(1) NOT NULL DEFAULT '+'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            reverse_sql="DROP TABLE IF EXISTS `e_server_settings`;"
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS `e_plus_override` (
                    `domain_id` varchar(50) NOT NULL PRIMARY KEY,
                    `enabled` tinyint(1) NOT NULL DEFAULT 1,
                    CONSTRAINT `fk_plus_override_domain` FOREIGN KEY (`domain_id`) REFERENCES `e_domains` (`domain`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            reverse_sql="DROP TABLE IF EXISTS `e_plus_override`;"
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS `e_pattern_forwarding` (
                    `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    `domain_id` varchar(50) NOT NULL,
                    `pattern` varchar(255) NOT NULL,
                    `destination` varchar(255) NOT NULL,
                    `pattern_type` varchar(20) NOT NULL DEFAULT 'wildcard',
                    `priority` int(11) NOT NULL DEFAULT 100,
                    `enabled` tinyint(1) NOT NULL DEFAULT 1,
                    CONSTRAINT `fk_pattern_domain` FOREIGN KEY (`domain_id`) REFERENCES `e_domains` (`domain`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            reverse_sql="DROP TABLE IF EXISTS `e_pattern_forwarding`;"
        ),
    ]
