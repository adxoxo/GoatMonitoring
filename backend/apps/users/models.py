"""Users app models — admin accounts for the dashboard.

Workers are unauthenticated and have no account (see CLAUDE.md). This model
exists so admin/office-manager logins can be extended later (roles, contact
info) without another swappable-user-model migration. It subclasses
``AbstractUser`` and adds nothing yet — the win is owning the model now.
"""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Admin / office-manager account. Authenticates via JWT."""

    def __str__(self):
        return self.username
