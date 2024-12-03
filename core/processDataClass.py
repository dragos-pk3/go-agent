from datetime import datetime, timedelta
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from db import dbOperations
from periodCalculatorClass import PeriodCalculator
import jsonSRW

class ProcessData:
    def __init__(self):
        self.user_preferences = jsonSRW.read_json("__userfiles__\\user_preferences.json")
        self.output = {}
    
    def process(self, autovanIndex, startDate:str, endDate:str):
        self.autovanIndex = autovanIndex
        self.startDateString = startDate.strip()
        self.endDateString = endDate.strip()
        currentDate = datetime.strptime(f"{datetime.now().day}.{datetime.now().month}", "%d.%m")
        currentYear = datetime.now().year
        nextYear = currentYear + 1

        self.startDate = datetime.strptime(f"{self.startDateString}", "%d.%m")
        self.endDate = datetime.strptime(f"{self.endDateString}", "%d.%m")
        if self.startDate < currentDate:
            self.startDateWithYear = datetime.strptime(f"{self.startDateString}.{nextYear}", "%d.%m.%Y")
        else:
            self.startDateWithYear = datetime.strptime(f"{self.startDateString}.{currentYear}", "%d.%m.%Y")
        if self.endDate < self.startDate:
            self.endDateWithYear = datetime.strptime(f"{self.endDateString}.{self.startDateWithYear.year + 1}", "%d.%m.%Y")
        else:
            self.endDateWithYear = datetime.strptime(f"{self.endDateString}.{self.startDateWithYear.year}", "%d.%m.%Y")
        vehicleData = dbOperations.get_vehicle_details(self.autovanIndex)
        if vehicleData is None:
            return None
        periodCalculator = PeriodCalculator(self.user_preferences)
        HighDays, StandardDays, LowDays = periodCalculator.calculate_days(self.startDate, self.endDate)
        total_rent, rent_per_day, discount_rates = periodCalculator.calculate_rent(HighDays, StandardDays, LowDays,[vehicleData['standard_rate'], vehicleData['high_rate'], vehicleData['low_rate']])
        self.output = {
            'Autovan': vehicleData['autovan_type'],
            'Start Date': self.startDateWithYear.strftime("%d.%m.%Y"),
            'End Date': self.endDateWithYear.strftime("%d.%m.%Y"),
            'Total Days': (self.endDateWithYear - self.startDateWithYear).days,
            'Location': vehicleData['location_city'],
            'Rent Per Day': rent_per_day,
            'Total Rent': total_rent,
            'Link to Photo': vehicleData['gallery_link'],
            'High Days': HighDays,
            'Standard Days': StandardDays,
            'Low Days': LowDays,
            'Discount Rates': discount_rates
        }
