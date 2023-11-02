
# from apps.rrhh.funcionarios.controllers.asistenciasf.asistenciasip import ZkController

# Hacer lo siguiente
# crontab -e
# */1 * * * * /home/thotenn/www/mg/kernel/shell/cron.sh
# dejar un espacio al final del archivo crontab -e
# systemctl restart cron

PJOBS: dict = {
    # 'asistenciabyip': {'class': ZkController, 'title': 'Controlador de Imp. Auto. de Relojes Bio.'},
    'backup_bd_dropbox': {'class_dir': "apps_administrador_controllers_backups_bd_BdBackupDropbox_BdBackupDropbox", 'title': 'Controlador Backup de bd en Dropbox'}
}
