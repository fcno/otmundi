from django.db import migrations
from django.contrib.auth.management import create_permissions
from django.apps import apps as global_apps

def create_roles_and_permissions(apps, schema_editor):
    # Força a criação das permissões usando o registro global de apps
    for app_config in global_apps.get_app_configs():
        create_permissions(app_config, verbosity=0)

    # Agora usamos o registro 'apps' da migração para acessar os modelos
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # 1. Criar os 6 perfis baseados no seu modelo User
    roles = [
        "Player", "Tutor", "Senior Tutor", 
        "GameMaster", "Community Manager", "Administrator"
    ]
    
    for name in roles:
        Group.objects.get_or_create(name=name)

    # 2. Atribuir TODAS as permissões ao Administrator
    admin_group = Group.objects.get(name="Administrator")
    all_permissions = Permission.objects.all()
    
    if all_permissions.exists():
        admin_group.permissions.set(all_permissions)

def remove_roles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    roles = ["Player", "Tutor", "Senior Tutor", "GameMaster", "Community Manager", "Administrator"]
    Group.objects.filter(name__in=roles).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
        ('killstats', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_roles_and_permissions, remove_roles),
    ]
