"""
diy_framework by sirMackk
@link https://github.com/sirMackk/diy_framework
"""
class DiyFrameworkException(Exception):
    pass


class NotFoundException(DiyFrameworkException):
    code = 404


class BadRequestException(DiyFrameworkException):
    code = 400


class DuplicateRoute(DiyFrameworkException):
    pass


class TimeoutException(DiyFrameworkException):
    code = 500
