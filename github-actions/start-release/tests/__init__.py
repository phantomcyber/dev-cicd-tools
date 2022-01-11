import shutil


def copy_app_dir(request):
    def remove_app_dir_copy():
        shutil.rmtree(app_dir_copy, ignore_errors=True)

    app_dir = request.param
    app_dir_copy = app_dir + '_copy'

    shutil.copytree(app_dir, app_dir_copy)
    request.addfinalizer(remove_app_dir_copy)

    return app_dir_copy
