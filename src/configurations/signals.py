from pprint import pprint

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver, Signal

from shared.enum import PasswordType

password_changed = Signal()


@receiver(user_logged_in)
def handle_login(sender, request, user, **kwargs):

    pprint("handle_login")
    pprint(user)

    # Get the user's current password hash
    current_password_hash = user.password

    # Check if the password hash has changed
    if user.check_password(current_password_hash):
        # Password has not changed

        pprint("Password has not changed")

        return

    # Password has changed, update the custom field
    user.password_type = PasswordType.CUSTOM
    user.save()

