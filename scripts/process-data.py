#!/usr/bin/env python
from bikeshares import programs
from bikeshares.program import TripSubset
import argparse
import sys

ROUNDING = 4

def get_program(name):
    return {
        "nyc": programs.nyc.CitiBike,
        "chicago": programs.chicago.Divvy,
        "boston": programs.boston.Hubway
    }[name]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--program", type=get_program)
    parser.add_argument("--trips")
    parser.add_argument("--stations")
    args = parser.parse_args()
    return args

def get_female_pct(subset):
    mean = (subset["rider_gender"] == "F").mean()
    return round(mean, ROUNDING)

def calculate_gender(program):
    gendered_subset = TripSubset(program.trips[program.trips["rider_gender"].notnull()])
    station_data = gendered_subset.by_station().set_index("station_id")
    station_data["fpct_started"] = gendered_subset.groupby("start_station").apply(get_female_pct)
    station_data["fpct_ended"] = gendered_subset.groupby("end_station").apply(get_female_pct)
    total_fpct = ((station_data["fpct_started"] * station_data["trips_started"]) +\
        (station_data["fpct_ended"] * station_data["trips_ended"])) / (station_data["trips_total"])
    station_data["fpct_total"] = total_fpct.apply(lambda x: round(x, ROUNDING))
    stations = program.stations.set_index("id")[["name", "lat", "lng"]]\
        .join(station_data)
    return stations.sort("trips_total", ascending=False)
    
def main():
    args = parse_args()
    program = args.program()
    program.load_trips(args.trips).load_stations(args.stations)
    calculations = calculate_gender(program)
    calculations.to_json(sys.stdout, orient="records")
    
if __name__ == "__main__":
    main()