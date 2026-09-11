class DomainException(Exception):
    """Base class for MindOS domain logic errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class GoalNotFoundException(DomainException):
    pass


class GoalHasActiveTasksException(DomainException):
    """Raised when attempting to delete a Goal that still contains tasks."""
    pass


class TaskNotFoundException(DomainException):
    pass
