from django.core.management.base import BaseCommand
import subprocess, sys, signal


class Command(BaseCommand):
    help = "🔥 Run Locust load testing for the Django project."

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            default='http://localhost:8000',
            help='🌐 Host URL to run Locust against (default: http://localhost:8000)'
        )
        
        parser.add_argument(
            '--locustfile',
            type=str,
            default='locustfile.py',
            help='📂 Path to the locustfile (default: locustfile.py)'
        )
        # parser.add_argument(
        #     '--headless',
        #     action='store_true',
        #     help='🤖 Run Locust in headless mode (no web UI)'
        # )
        # parser.add_argument(
        #     '--users',
        #     type=int,
        #     default=10,
        #     help='👥 Number of users to simulate (default: 10)'
        # )
        # parser.add_argument(
        #     '--spawn-rate',
        #     type=int,
        #     default=2,
        #     help='⚡ Spawn rate of users per second (default: 2)'
        # )
        # parser.add_argument(
        #     '--run-time',
        #     type=str,
        #     default='1m',
        #     help='⏰ Total run time for headless mode (e.g., 1m, 10s, 1h)'
        # )

    def handle(self, *args, **options):
        # host = options['host']
        locustfile = options['locustfile']
        # headless = options['headless']
        # users = options['users']
        # spawn_rate = options['spawn_rate']
        # run_time = options['run_time']

        # 🔥 Base Locust command
        command = [
            'locust',
            '-f', locustfile,
            # '--host', host
        ]

        # 🤖 If headless mode is enabled, add these arguments
        # if headless:
        #     command += [
        #         '--headless',
        #         '-u', str(users),
        #         '-r', str(spawn_rate),
        #         '--run-time', run_time
        #     ]

        print("🚀 Starting Locust with command:\n{}".format(command))

        def signal_handler(sig, frame):
            print("\n👋 Gracefully stopping Locust...")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 🎯 Run the locust command
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print("❌ Locust failed with error:\n{}".format(e))
