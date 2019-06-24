## Simulation Environment
`patient info`
- **inter_arrival_times**
- **service_times**
- **priority_lev**
- **transitive_stations**
- **all_stations**

```python
class Simulation(object):

    def __init__(self, network, station_class=None, arrival_station_class=None):

        self.network = network
        # patients info
        self.inter_arrival_times = self.find_times_dict('Arr')
        self.service_times = self.find_times_dict('Ser')
        self.priority_lev = self.network.priority_lev
        # stations info
        self.transitive_stations = [Station(i+1, self) for i in range(network.number_of_stations)] 
        self.all_stations = ([ArrivalStation(self)] + self.transitive_stations + [ExitStation()]) 
```
- 👑 *def* **`__init__(self, network, station_class=None, arrival_station_class=None):`**
    - 🍃 require *def* **`find_distributions(self, station, clss, kind):`**
        - 🍃 require *def* **`find_distributions(self, station, clss, kind):`**
            - 🍃 require *def* **`check_userdef_dist(self, func):`**
            - 🍃 require *def* **`check_timedependent_dist(self, func, kind, current_time):`**
            - 🍃 require *def* **`import_empirical(self, dist_file):`**
```python
    def find_times_dict(self, kind):
        """
        Create the dictionary of service and arrival
        time functions for each node for each class
        """
        return {station + 1: {clss: self.find_distributions(station, clss, kind) 
                for clss in range(self.network.number_of_classes)}
                for station in range(self.network.number_of_stations)}

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
```
```python
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
```
- 👑 *def* **`simulate_until_max_time(self, max_simulation_time, progress_bar=False):`**
    - 🍃 require *def* **`find_next_active_station(self):`**
    - 🍃 require *def* **`event_and_return_nextstation(self, next_active_station, current_time):`**
    - 🍃 require *def* **`wrap_up_servers(self, current_time):`**
        - 🍃 resort to *def* **`station.wrap_up_servers(current_time)`**
        - 🍃 resort to *def* **`find_server_utilization()`**
 
```python
    def simulate_until_max_time(self, max_simulation_time, progress_bar=False):
        """
        Runs the simulation until max_simulation_time is reached.
        """
        next_active_station = self.find_next_active_station()

        current_time = next_active_station.next_event_date ## [1]

        if progress_bar:
            self.progress_bar = tqdm.tqdm(total=max_simulation_time)

        while current_time < max_simulation_time:
            next_active_station = self.event_and_return_nextstation(next_active_station, current_time) ## [2]

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
```
```python
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
```
```python
    def event_and_return_nextstation(self, next_active_station, current_time):
        """
        Carries out the event of current next_active_node, and return the next
        next_active_node
        """
        next_active_station.have_event()

        for station in self.transitive_stations:
            station.update_next_event_date(current_time)

        return self.find_next_active_station()
```
```python
    def wrap_up_servers(self, current_time):
        """
        Updates the servers' total_time and busy_time as the end of the simulation run. Finds the overall server utilization for each sattion.
        """
        for station in self.transitive_stations:
            station.wrap_up_servers(current_time)
            station.find_server_utilization()
```

#### Access Records

```python
    def get_all_records(self):
        records = []
        for patient in self.get_all_patients():
            for record in patient.data_records:
                records.append(record)
        self.all_records = records
        return records

    def get_all_patients(self):
        return [patient for station in self.all_stations[1:] 
            for patient in station.all_patients 
            if len(patient.data_records) > 0]
```