"""
********************************************************************************
* Name: utilities.py
* Author: Nathan Swain
* Created On: 2020
* Copyright: (c) Aquaveo, LLC 2020
* License: BSD 2-Clause
********************************************************************************
"""
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.models import User


def log_user_in(request, user=None, username=None):
    """
    Handle user login and session creation of existing user.

    Args:
        request (HttpRequest): The request object.
        user (auth.models.User): The user to login. Required if username not provided.
        username (str): The username of the user to login. Required if user not provided.

    Returns:
        HttpResponse: redirect to post login page.
    """
    if not user and not username:
        raise ValueError(
            'You must provide either the "user" or the "username" arguments.'
        )

    # Get user from username if not provided
    if not user and username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.warning(
                request,
                "Whoops! We were not able to log you in. Please check your username and "
                "password and try again.",
            )
            return redirect("accounts:login")

    # The user is valid, active, and authenticated, so login in the user
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")

    # Redirect after logged in using next parameter or default to user profile
    if "next" in request.GET:
        return redirect(request.GET["next"])
    else:
        return redirect("app_library")


from importlib import import_module


class MissingOptionalDependency(ImportError):
    pass


class FailedImport:
    def __init__(self, module, import_error):
        self.module_name = module
        self.error = import_error

    def __getattr__(self, item):
        raise MissingOptionalDependency(
                f'Optional dependency "{self.module_name}" was not able to be imported because of the following error:\n'
                f'{self.error}.'
            )


def optional_import(module, from_module=None, error_message=None):
    try:
        if from_module:
            return getattr(import_module(from_module), module)
        return import_module(module)
    except ImportError as e:
        return FailedImport(module, e)


class OptionalModule:
    def __init__(self, module_name):
        self.module_name = module_name
        self.module = None
        self.error = None
        try:
            self.module = import_module(self.module_name)
        except ImportError as e:
            self.error = e

    def __call__(self, error_message=None):
        if self.module:
            return self.module
        else:
            error_message = error_message or (
                f'Optional dependency "{self.module_name}" was not able to be imported because of the '
                f'following error:\n{self.error}.'
            )
            raise MissingOptionalDependency(error_message)


def lazy_import(module_name):
    return OptionalModule(module_name)
