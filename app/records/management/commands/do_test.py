import random
import time
from statistics import mean

from app.deliveryoptions.api import delivery_options_request_handler
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Performance test for delivery options API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=1000,
            help="Number of API calls to perform",
        )

    def handle(self, *args, **options):
        num_calls = options["count"]
        times = []

        self.stdout.write(self.style.WARNING(f"Running {num_calls} calls...\n"))

        for i in range(num_calls):
            iaid = self.generate_iaid()

            start = time.perf_counter()

            result = None
            try:
                result = delivery_options_request_handler(iaid)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"[{i+1}] Error for IAID {iaid}: {e}")
                )

            duration = time.perf_counter() - start
            times.append(duration)

            # Extract "options" if available
            options_value = None
            if isinstance(result, list) and len(result) > 0:
                options_value = result[0].get("options")

            self.stdout.write(
                f"[{i+1}] IAID {iaid} | options={options_value} | Time={duration:.4f}s"
            )

        self.print_summary(times)

    def generate_iaid(self):
        """IAIDs like A12345, A24567, A31234"""
        first_digit = random.choice([1, 2, 3])
        remaining = random.randint(0, 999999)
        return f"C{first_digit}{remaining:06d}"

    def print_summary(self, times):
        self.stdout.write("\n=== SUMMARY ===")
        self.stdout.write(f"Total calls:       {len(times)}")
        self.stdout.write(f"Cumulative time:   {sum(times):.4f}s")
        self.stdout.write(f"Average time:      {mean(times):.4f}s")
        self.stdout.write(f"Fastest call:      {min(times):.4f}s")
        self.stdout.write(f"Slowest call:      {max(times):.4f}s")

        # Timing buckets
        under_1 = sum(1 for t in times if t < 1)
        between_1_2 = sum(1 for t in times if 1 <= t < 2)
        between_2_3 = sum(1 for t in times if 2 <= t < 3)
        over_3 = sum(1 for t in times if t >= 3)

        self.stdout.write("\n--- Timing Buckets ---")
        self.stdout.write(f"< 1s:        {under_1}")
        self.stdout.write(f"1–2s:        {between_1_2}")
        self.stdout.write(f"2–3s:        {between_2_3}")
        self.stdout.write(f"> 3s:        {over_3}")

        self.stdout.write(self.style.SUCCESS("\nDone."))
