def create_test_result_response(success, message=None, verbose=None, fixed=False):
    """
    Create a test result response object.
    """
    response = {"success": success, "message": message, "fixed": fixed}

    if verbose:
        response["verbose"] = verbose

    return response
