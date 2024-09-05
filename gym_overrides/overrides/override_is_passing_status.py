def is_passing_status(prev_fn, cls, status):
    """
    Given the status of a certificate, return a boolean indicating whether
    the student passed the course.
    """
    return status in ['downloadable', 'generating', 'audit_passing', 'honor_passing']
