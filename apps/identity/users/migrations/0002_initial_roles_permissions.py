from django.db import migrations

def create_roles_and_permissions(apps, schema_editor):
    # Modelos via apps.get_model para segurança da migração
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # 1. Lista de Roles baseada no Enum em user.py
    roles = [
        "Player", "Tutor", "Senior Tutor", 
        "GameMaster", "Community Manager", "Administrator"
    ]

    # Criar todos os grupos
    groups = {}
    for name in roles:
        group, _ = Group.objects.get_or_create(name=name)
        groups[name] = group

    # 2. Atribuição de Permissões
    try:
        # Localiza o ContentType do MonsterConfig para a permissão existir
        monster_config_ct = ContentType.objects.get(app_label='killstats', model='monsterconfig')
        
        # Obtém a permissão que você identificou na BossCuratorView
        change_perm = Permission.objects.get(
            codename='change_monsterconfig', 
            content_type=monster_config_ct
        )

        # Linkar ao perfil Administrator
        groups["Administrator"].permissions.add(change_perm)

    except (ContentType.DoesNotExist, Permission.DoesNotExist):
        # Se os apps ainda não foram migrados ou o modelo mudou, não trava o deploy
        pass

def remove_roles(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    roles = ["Player", "Tutor", "Senior Tutor", "GameMaster", "Community Manager", "Administrator"]
    Group.objects.filter(name__in=roles).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_roles_and_permissions, remove_roles),
    ]
