import math
from datetime import datetime, timedelta

class PeriodCalculator:
    def __init__(self, user_preferences):
        self.user_preferences = user_preferences
        self.discount_rates = [] # array of discounted rates formatted as [standard , high, low] just as rates
        self.season_rates = [] # array of rates formatted as [standard , high, low] just as rates
    def calculate_days(self, start_date, end_date):
        """Calculate the number of days in each season."""
        common_year = 2000
        high_start = datetime.strptime(f"{self.user_preferences['HIGH_START']}.{common_year}", "%d.%m.%Y")
        high_end = datetime.strptime(f"{self.user_preferences['HIGH_END']}.{common_year}", "%d.%m.%Y")
        low_start = datetime.strptime(f"{self.user_preferences['LOW_START']}.{common_year}", "%d.%m.%Y")
        low_end = datetime.strptime(f"{self.user_preferences['LOW_END']}.{common_year}", "%d.%m.%Y")

        HighDays = StandardDays = LowDays = 0
        current_date = start_date

        while current_date < end_date:
            compare_date = current_date.replace(year=common_year)

            if low_start <= compare_date or compare_date < low_end:
                LowDays += 1
            elif high_start <= compare_date < high_end:
                HighDays += 1
            else:
                StandardDays += 1

            current_date += timedelta(days=1)

        return HighDays, StandardDays, LowDays
    def calculate_rent(self,HighDays, StandardDays, LowDays, rates):
        """Calculate total rent based on the season days."""
        autovanPriceStandard, autovanPriceHigh, autovanPriceLow = rates
        total_days = HighDays + StandardDays + LowDays

        HighDiscount = 0.9 if total_days >= self.user_preferences["MIN_DAYS_HIGH"] else 1.0
        StandardDiscount = 0.9 if total_days >= self.user_preferences["MIN_DAYS_STANDARD"] else 1.0
        LowDiscount = 0.9 if total_days >= self.user_preferences["MIN_DAYS_LOW"] else 1.0
        self.discount_rates = [StandardDiscount, HighDiscount, LowDiscount]
        self.season_rates = [autovanPriceStandard, autovanPriceHigh, autovanPriceLow]
        total_rent = (
            math.ceil(autovanPriceHigh  * HighDiscount) * HighDays +
            math.ceil(autovanPriceStandard * StandardDiscount) * StandardDays +
            math.ceil(autovanPriceLow * LowDiscount) * LowDays +
            self.user_preferences["MAINTENANCE_COST"]
        )
        self.season_rates[0] = autovanPriceStandard if autovanPriceStandard * StandardDays != 0 else 0
        self.season_rates[1] = autovanPriceHigh if autovanPriceHigh * HighDays != 0 else 0
        self.season_rates[2] = autovanPriceLow if autovanPriceLow * LowDays != 0 else 0
        
        self.discount_rates[0] = autovanPriceStandard * StandardDiscount if StandardDiscount != 1 else 0
        self.discount_rates[1] = autovanPriceHigh * HighDiscount if HighDiscount != 1 else 0
        self.discount_rates[2] = autovanPriceLow * LowDiscount if LowDiscount != 1 else 0
        
        total_rent = int(round(total_rent))  
        if HighDays >= StandardDays and HighDays >= LowDays:
            rent_per_day = autovanPriceHigh
        elif StandardDays >= HighDays and StandardDays >= LowDays:
            rent_per_day = autovanPriceStandard
        else:
            rent_per_day = autovanPriceLow 

        return total_rent, self.season_rates, self.discount_rates
