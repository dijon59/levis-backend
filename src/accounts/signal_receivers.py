import json, requests

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.conf import settings
from src.accounts.models import FCMDeviceToken
from src.electric_app.models import Task


@receiver(m2m_changed, sender=Task.assignees.through)
def notify_task_assignment(sender, instance, action, pk_set, **kwargs):
    """
    Send push notifications when users are assigned to a task
    """
    # We only want to send notifications when users are added to the task
    # Only proceed if the action is post_add (after users are added)
    if action != "post_add":
        return

    if pk_set:
        for user_id in pk_set:
            devices = FCMDeviceToken.objects.filter(
                user_id=user_id
            )
            for i in devices:
                message = {
                    "message": {
                        "token": i.device_token,
                        "notification": {
                            "title": "Hello!",
                            "body": "A new Task has been assigned to you"
                        }
                    }
                }

                # Send the request
                requests.post(settings.FCM_URL, headers=settings.FCM_HEADERS, data=json.dumps(message))
