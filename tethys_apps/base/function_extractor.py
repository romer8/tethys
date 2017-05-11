class TethysFunctionExtractor(object):
    """
    Base class for PersistentStore and HandoffHandler that returns a function handle from a string path to the function.

    Attributes:
        path (str): The path to a function in the form "app_name.module_name.function_name".
    """
    PATH_PREFIX = 'tethys_apps.tethysapp'

    def __init__(self, path, prefix=PATH_PREFIX, throw=False):
        self.path = path
        self.prefix = prefix
        self._throw = throw
        self._valid = None
        self._function = None

        if not isinstance(path, basestring):
            if path.callable():
                self.valid = True
                self.function = path

    @property
    def valid(self):
        """
        True if function is valid otherwise False.
        """
        if self._valid is None:
            self.function
        return self._valid

    @property
    def function(self):
        """
        The function pointed to by the path_str attribute.

        Returns:
            A handle to a Python function or None if function is not valid.
        """
        if not self._function and self._valid is None:
            try:
                # Split into parts and extract function name
                module_path, function_name = self.path.rsplit('.', 1)

                # Pre-process handler path
                full_module_path = '.'.join((self.prefix, module_path)) if self.prefix else module_path

                # Import module
                module = __import__(full_module_path, fromlist=[function_name])

            except (ValueError, ImportError) as e:
                self._valid = False
                if self._throw:
                    raise e
            else:
                # Get the function
                self._function = getattr(module, function_name)
                self._valid = True

        return self._function