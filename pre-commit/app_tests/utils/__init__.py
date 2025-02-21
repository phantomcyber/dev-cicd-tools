def create_test_result_response(success, message=None, verbose=None):
    """
    Create a test result response object.
    """
    response = {
        "success": success,
        "message": message,
    }

    if verbose:
        response["verbose"] = verbose

    return response