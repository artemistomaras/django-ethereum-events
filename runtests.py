import os, sys

from django.conf import settings
import django

def runtests():
    settings_file = 'django_ethereum_events.settings.test'
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_file)

    django.setup()

    from django.test.runner import DiscoverRunner
    runner_class = DiscoverRunner
    test_args = ['django_ethereum_events']

    failures = runner_class(
        verbosity=1, interactive=True, failfast=False).run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()