from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging

class ReminderService:
    def __init__(self, bot, repo):
        self.bot = bot
        self.repo = repo
        self.scheduler = BackgroundScheduler(timezone="UTC")
        self.started = False
        self.logger = logging.getLogger(__name__)

    def start(self):
        if not self.started:
            self.scheduler.start()
            self.started = True
            self._restore_reminders()  # Recuperar al iniciar

    def _restore_reminders(self):
        """Recupera todos los recordatorios de la base de datos al iniciar"""
        try:
            reminders = self.repo.get_all_reminders()
            for reminder in reminders:
                self.schedule_plant(
                    reminder['user_id'],
                    reminder['plant_name'],
                    reminder['days_interval']
                )
            self.logger.info(f"Restaurados {len(reminders)} recordatorios")
        except Exception as e:
            self.logger.error(f"Error restaurando recordatorios: {e}")


    def schedule_plant(self, user_id, plant_name, days_interval):
        # Guardar en BD primero
        self.repo.set_reminder(user_id, plant_name, days_interval)
        
        job_id = f"plant_{user_id}_{plant_name}".replace(" ", "_")
        
        # Remover job existente
        try:
            self.scheduler.remove_job(job_id)
        except:
            pass
        
        # Programar nuevo job
        self.scheduler.add_job(
            self._job_send_plant,
            trigger=IntervalTrigger(days=days_interval),
            args=[user_id, plant_name],  #Mejor que lambda
            id=job_id,
            replace_existing=True
        )

    def _job_send_plant(self, user_id, plant_name):
        try:
            self.bot.send_message(user_id, f"💧 ¡Hora de regar tu {plant_name}!")
        except Exception as e:
            self.logger.error(f"Error enviando mensaje a {user_id}: {e}")

    def remove_plant_reminder(self, user_id, plant_name):
        """Eliminar recordatorio completamente"""
        job_id = f"plant_{user_id}_{plant_name}".replace(" ", "_")
        try:
            self.scheduler.remove_job(job_id)
            self.repo.remove_reminder(user_id, plant_name)
            return True
        except Exception as e:
            self.logger.error(f"Error eliminando reminder: {e}")
            return False
        



# -------------------test --------------------


    def schedule_test_reminder(self, user_id, minutes):
        job_id = f"test_{user_id}"

        # Programar nuevo job
        self.scheduler.add_job(
            self._job_send_test, # Llamamos a una función separada
            trigger=IntervalTrigger(minutes=minutes),
            args=[user_id],      # Pasamos el user_id
            id=job_id,
            replace_existing=True
        )
        self.logger.info(f"Test reminder programado para user {user_id} cada {minutes} minutos.")

    def _job_send_test(self, user_id):
        """Job para enviar el recordatorio de prueba."""
        try:
            self.bot.send_message(user_id, "💧 ¡Hora de regar tu planta! (test funciona).")
        except Exception as e:
            self.logger.error(f"Error enviando mensaje de prueba a {user_id}: {e}")

    def remove_test_reminder(self, user_id):
        job_id = f"test_{user_id}"
        try:
            self.scheduler.remove_job(job_id)
            return True
        except:
            return False
