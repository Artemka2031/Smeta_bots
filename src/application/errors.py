class ApplicationError(Exception):
    pass


class ProjectNotFoundError(ApplicationError):
    pass


class ProjectDisabledError(ApplicationError):
    pass


class OperationNotFoundError(ApplicationError):
    pass


class OperationAccessError(ApplicationError):
    pass
