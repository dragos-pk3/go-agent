import math
from datetime import datetime, timedelta

class PeriodCalculator:
    def __init__(self, user_config):
        self.user_config = user_config

    def calculate_days(self, start_date, end_date, current_year):
        """Calculate the number of days in each season."""
        # TODO: make sure to extend the check for the next year
        high_start = datetime.strptime(f"{self.user_config["HIGH_START"]}.{current_year}", "%d.%m.%Y")
        high_end = datetime.strptime(f"{self.user_config["HIGH_END"]}.{current_year}", "%d.%m.%Y")
        low_start = datetime.strptime(f"{self.user_config["LOW_START"]}.{current_year}", "%d.%m.%Y")
        low_end = datetime.strptime(f"{self.user_config["LOW_END"]}.{current_year + 1}", "%d.%m.%Y")
        # TODO: use coding standards for this file
        HighDays = StandardDays = LowDays = 0

        current_date = start_date
        while current_date < end_date:
            if low_start <= current_date < low_end:
                LowDays += 1
            elif high_start <= current_date < high_end:
                HighDays += 1
            else:
                StandardDays += 1
            current_date += timedelta(days=1)

        return HighDays, StandardDays, LowDays

    def calculate_rent(self,HighDays, StandardDays, LowDays, rates):
        """Calculate total rent based on the season days."""
        autovanPriceStandard, autovanPriceHigh, autovanPriceLow = rates
        total_days = HighDays + StandardDays + LowDays

        HighDiscount = 0.9 if total_days >= self.user_config["MIN_DAYS_HIGH"] else 1.0
        StandardDiscount = 0.9 if total_days >= self.user_config["MIN_DAYS_STANDARD"] else 1.0
        LowDiscount = 0.9 if total_days >= self.user_config["MIN_DAYS_LOW"] else 1.0
        total_rent = (
            math.ceil(autovanPriceHigh  * HighDiscount) * HighDays +
            math.ceil(autovanPriceStandard * StandardDiscount) * StandardDays +
            math.ceil(autovanPriceLow * LowDiscount) * LowDays +
            self.user_config["MAINTENANCE_COST"]
        )
        
        total_rent = int(round(total_rent))  # Rounding and converting to integer
        # TODO: rent_per_day should keep track of all season days and not just the most days
        if HighDays >= StandardDays and HighDays >= LowDays:
            rent_per_day = autovanPriceHigh
        elif StandardDays >= HighDays and StandardDays >= LowDays:
            rent_per_day = autovanPriceStandard
        else:
            rent_per_day = autovanPriceLow 

        return total_rent, rent_per_day
