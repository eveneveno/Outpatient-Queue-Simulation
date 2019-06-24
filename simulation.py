from __future__ import division
import os
import pdb
import tqdm
import random
from random import (expovariate, uniform, triangular, gammavariate, lognormvariate, weibullvariate)
from csv import writer, reader
from decimal import getcontext
from itertools import cycle

import argparse
parser = argparse.ArgumentParser(description='Gaussian Process')
parser.add_argument('--case',type=str, default='class_change')
parser.add_argument('--path',type=str, default = './all_records.csv')

parser.add_argument('--write_csv',type=bool, default = True)

args = parser.parse_args()

import matplotlib
matplotlib.use("TkAgg")

from utils import random_choice, truncated_normal
from params_to_network import create_network
from station import ArrivalStation, Station, ExitStation

class Simulation(object):

    def __init__(self, network, station_class=None, arrival_station_class=None):

        self.network = network

        self.inter_arrival_times = self.find_times_dict('Arr')
        self.service_times = self.find_times_dict('Ser')

        self.priority_lev = self.network.priority_lev

        self.transitive_stations = [Station(i+1, self) for i in range(network.number_of_stations)] 
        self.all_stations        = ([ArrivalStation(self)] + self.transitive_stations + [ExitStation()]) 

    def simulate_until_max_time(self, max_simulation_time, progress_bar=False):

        next_active_station = self.find_next_active_station()

        current_time = next_active_station.next_event_date

        if progress_bar:
            self.progress_bar = tqdm.tqdm(total=max_simulation_time)

        while current_time < max_simulation_time:
            next_active_station = self.event_and_return_nextstation(next_active_station, current_time)

            if progress_bar:
                remaining_time = max_simulation_time - self.progress_bar.n
                time_increment = next_active_station.next_event_date - current_time
                self.progress_bar.update(min(time_increment, remaining_time))

            current_time = next_active_station.next_event_date

        self.wrap_up_servers(max_simulation_time)

        if progress_bar:
            remaining_time = max(max_simulation_time - self.progress_bar.n, 0)
            self.progress_bar.update(remaining_time)
            self.progress_bar.close()

    def find_next_active_station(self):
        """
        Returns the next active station:
        """
        next_event_date = min([station.next_event_date 
                            for station in self.all_stations])

        next_active_station_indices = [i 
            for i, station in enumerate(self.all_stations) 
            if station.next_event_date == next_event_date]

        if len(next_active_station_indices) > 1:
            return self.all_stations[random_choice(next_active_station_indices)]

        return self.all_stations[next_active_station_indices[0]]

    def event_and_return_nextstation(self, next_active_station, current_time):
        next_active_station.have_event()

        for station in self.transitive_stations:
            station.update_next_event_date(current_time)

        return self.find_next_active_station()

    def wrap_up_servers(self, current_time):
        for station in self.transitive_stations:
            station.wrap_up_servers(current_time)
            station.find_server_utilization()

    def find_times_dict(self, kind):

        return {station + 1: {clss: self.find_distributions(station, clss, kind) 
                for clss in range(self.network.number_of_classes)}
                for station in range(self.network.number_of_stations)}
                                
    def source(self, station, clss, kind):
        if kind == 'Arr':
            return self.network.patients[clss].arrival_dist[station]
        if kind == 'Ser':
            return self.network.patients[clss].service_dist[station]

    def find_distributions(self, station, clss, kind):

        if self.source(station, clss, kind) == 'NoArrivals':
            return lambda : float('Inf')
        if self.source(station, clss, kind)[0] == 'Uniform':
            return lambda : uniform(self.source(station, clss, kind)[1], 
                                    self.source(station, clss, kind)[2])
        if self.source(station, clss, kind)[0] == 'Deterministic':
            return lambda : self.source(station, clss, kind)[1]
        if self.source(station, clss, kind)[0] == 'Exponential':
            return lambda : expovariate(self.source(station, clss, kind)[1])
        if self.source(station, clss, kind)[0] == 'Normal':
            return lambda : truncated_normal(self.source(station, clss, kind)[1], 
                                             self.source(station, clss, kind)[2])
        if self.source(station, clss, kind)[0] == 'Custom':
            return lambda : random_choice(array = self.source(station, clss, kind)[1], 
                                          probs = self.source(station, clss, kind)[2])

        if self.source(station, clss, kind)[0] == 'UserDefined':
            return lambda : self.check_userdef_dist(self.source(station, clss, kind)[1])

        if self.source(station, clss, kind)[0] == 'TimeDependent':
            return lambda t : self.check_timedependent_dist(self.source(station, clss, kind)[1], kind, t)

        if self.source(station, clss, kind)[0] == 'Empirical':
            if isinstance(self.source(station, clss, kind)[1], str):
                return lambda : random_choice(self.import_empirical(self.source(station, clss, kind)[1]))
            return lambda : random_choice(self.source(station, clss, kind)[1])

    def check_userdef_dist(self, func):
        sample = func()
        if not isinstance(sample, float) or sample < 0:
            raise ValueError("UserDefined func must return positive float.")
        return sample

    def check_timedependent_dist(self, func, kind, current_time):
        sample = func(current_time)
        if kind in ['Arr', 'Ser'] and not isinstance(sample, float) or sample < 0:
            raise ValueError("TimeDependent func must return positive float.")
        return sample

    def import_empirical(self, dist_file):
        root = os.getcwd()
        file_name = root + '/' + dist_file
        empirical_file = open(file_name, 'r')
        rdr = reader(empirical_file)
        empirical_dist = [[float(x) for x in row] for row in rdr][0]
        empirical_file.close()
        return empirical_dist

    def get_all_patients(self):
        return [patient for station in self.all_stations[1:] 
            for patient in station.all_patients 
            if len(patient.data_records) > 0]

    def get_all_records(self):
        records = []
        for patient in self.get_all_patients():
            for record in patient.data_records:
                records.append(record)
        self.all_records = records
        return records

    def write_records_to_file(self, file_name, headers=True):
        """
        Writes the records for all patient to a csv file
        """
        root = os.getcwd()
        directory = os.path.join(root, file_name)
        data_file = open('%s' % directory, 'w')
        csv_wrtr = writer(data_file)
        if headers:
            csv_wrtr.writerow(['I.D. Number',
                               'Customer Class',
                               'Node',
                               'Arrival Date',
                               'Waiting Time',
                               'Service Start Date',
                               'Service Time',
                               'Service End Date',
                               'Exit Date',
                               'Destination',
                               'Queue Size at Arrival',
                               'Queue Size at Departure'])
        records = self.get_all_records()
        for row in records:
            csv_wrtr.writerow(row)
        data_file.close()

if __name__ == "__main__":

    if args.case == "basic_3":
        N = create_network(
            Arrival_distributions=[['Exponential', 0.2]],
            Service_distributions=[['Exponential', 0.1]],
            Number_of_servers=[3])

        random.seed(1)
        Q = Simulation(N)
        Q.simulate_until_max_time(1440)
        recs = Q.get_all_records()
        servicetimes = [r.service_time for r in recs]
        waits = [r.waiting_time for r in recs]

        import matplotlib.pyplot as plt
        plt.hist(waits)
        plt.show()
    
    if args.case == "basic_4":
        N = create_network(
            Arrival_distributions=[['Exponential', 0.2]],
            Service_distributions=[['Exponential', 0.1]],
            Number_of_servers=[4])

        average_waits = []
        for trial in range(10):
            random.seed(trial)
            Q = Simulation(N)
            Q.simulate_until_max_time(1640)
            recs = Q.get_all_records()
            waits = [r.waiting_time for r in recs if r.arrival_date > 100 and r.arrival_date < 1540]
            mean_wait = sum(waits) / len(waits)
            average_waits.append(mean_wait)

        print(sum(average_waits) / len(average_waits))

    if args.case == "homo_class_with_transition":
        N = create_network(
            Arrival_distributions=[['Exponential', 0.3],
                                   ['Exponential', 0.2],
                                   'NoArrivals'],
            Service_distributions=[['Exponential', 1.0],
                                   ['Exponential', 0.4],
                                   ['Exponential', 0.5]],
            Transition_matrices=[[0.0, 0.3, 0.7],
                                 [0.0, 0.0, 1.0],
                                 [0.0, 0.0, 0.0]],
            Number_of_servers=[1, 2, 2]
        )

        completed_pats = []
        for trial in range(10):
            random.seed(trial)
            Q = Simulation(N)
            Q.simulate_until_max_time(200)
            recs = Q.get_all_records()
            num_completed = len([r for r in recs if r.station==3 and r.arrival_date < 180])
            completed_pats.append(num_completed)

        print(sum(completed_pats) / len(completed_pats))

    if args.case == "hetero_class_with_transition":
        N = create_network(
            Arrival_distributions={'Class 0': [['Exponential', 1.0],
                                               'NoArrivals',
                                               'NoArrivals'],
                                   'Class 1': [['Exponential', 2.0],
                                               'NoArrivals',
                                               'NoArrivals']},
            Service_distributions={'Class 0': [['Exponential', 4.0],
                                               ['Exponential', 1.0],
                                               ['Deterministic', 0.0]],
                                   'Class 1': [['Exponential', 6.0],
                                               ['Deterministic', 0.0],
                                               ['Exponential', 1.0]]},
            Transition_matrices={'Class 0': [[0.0, 1.0, 0.0],
                                             [0.0, 0.0, 0.0],
                                             [0.0, 0.0, 0.0]],
                                 'Class 1': [[0.0, 0.0, 1.0],
                                             [0.0, 0.0, 0.0],
                                             [0.0, 0.0, 0.0]]},
            Number_of_servers=[1, 2, 3],
        )

        Q = Simulation(N)
        Q.simulate_until_max_time(9)
        recs = Q.get_all_records()
        visited_by_babies = {1, 2}
        print(set([r.station for r in recs 
            if r.patient_class==0]) == visited_by_babies)
    
        average_waits_1 = []
        average_waits_2 = []
        average_waits_3 = []
        for trial in range(16):
            random.seed(trial)
            Q = Simulation(N)
            Q.simulate_until_max_time(30)
            recs = Q.get_all_records()
            waits1 = [r.waiting_time for r in recs if r.station==1 and r.arrival_date > 3 and r.arrival_date < 27]
            waits2 = [r.waiting_time for r in recs if r.station==2 and r.arrival_date > 3 and r.arrival_date < 27]
            waits3 = [r.waiting_time for r in recs if r.station==3 and r.arrival_date > 3 and r.arrival_date < 27]
            average_waits_1.append(sum(waits1) / len(waits1))
            average_waits_2.append(sum(waits2) / len(waits2))
            average_waits_3.append(sum(waits3) / len(waits3))
        
        print(sum(average_waits_1) / len(average_waits_1))
        print(sum(average_waits_2) / len(average_waits_2))
        print(sum(average_waits_3) / len(average_waits_3))

    if args.case == "priority":
        N = create_network(
            Arrival_distributions={'Class 0': [['Exponential', 5]],
                                   'Class 1': [['Exponential', 5]]},
            Service_distributions={'Class 0': [['Exponential', 10]],
                                   'Class 1': [['Exponential', 10]]},
            Priority_classes={'Class 0': 0, 'Class 1': 1},
            Number_of_servers=[1]
        )
        random.seed(1)
        Q = Simulation(N)
        Q.simulate_until_max_time(100.0)
        recs = Q.get_all_records()
        waits_0 = [r.waiting_time 
            for r in recs if r.patient_class==0]
        print(sum(waits_0)/len(waits_0))
        waits_1 = [r.waiting_time 
            for r in recs if r.patient_class==1]
        print(sum(waits_1)/len(waits_1))

    if args.case == "class_change":
        N = create_network(
            Arrival_distributions={'Class 0': [['Exponential', 5]],
                                   'Class 1': ['NoArrivals'],
                                   'Class 2': ['NoArrivals']},
            Service_distributions={'Class 0': [['Exponential', 10]],
                                   'Class 1': [['Exponential', 10]],
                                   'Class 2': [['Exponential', 10]]},
            Transition_matrices={'Class 0': [[1.0]],
                                 'Class 1': [[1.0]],
                                 'Class 2': [[1.0]]},
            Class_change_matrices={'Station 1': [[0.0, 0.5, 0.5],
                                              [0.5, 0.0, 0.5],
                                              [0.5, 0.5, 0.0]]},
            Number_of_servers=[1]
        )      
        from collections import Counter
        random.seed(1)
        Q = Simulation(N)
        Q.simulate_until_max_time(50.0)
        recs = Q.get_all_records()
        print(Counter([r.patient_class for r in recs]))
    
    if args.write_csv:
        Q.write_records_to_file(args.path) 

    # pdb.set_trace()