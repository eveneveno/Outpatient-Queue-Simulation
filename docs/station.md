## Station class

This module provides transitive `Station` accompanied by two additional `ArrivalStation` and `ExitStation`.

### ArrivalStation Class
ArrivalStation Class has `eight` attributes: 
`basic`
- **simulation** *object*
    - interacted big environment 
- **number_of_patients** *int*
- **number_of_accepted_patients** *int*

`main rocords`
- **event_dates_dict** *dict*
- **rejection_dict** *dict*

- **next_station** *int*
- **next_class** *int*
- **next_event_date** *float*

`Initialized func calls`
- **initialize_event_dates_dict()**
- **find_next_event_date()**

```python
class ArrivalStation(object):

    def __init__(self, simulation):

        self.simulation = simulation
        self.number_of_patients = 0
        self.number_of_accepted_patients = 0

        self.event_dates_dict = {station + 1: {clss: False 
            for clss in range(self.simulation.network.number_of_classes)} 
            for station in range(self.simulation.network.number_of_stations)}
        self.rejection_dict = {station + 1: {clss:[] 
            for clss in range(self.simulation.network.number_of_classes)} 
            for station in range(self.simulation.network.number_of_stations)}

        self.initialize_event_dates_dict()  # take action
        self.find_next_event_date()         # take action
```
`Functions`
##### <font color='blue'>Initialization: Initialize the next event dates dictionary with random times for each station and class</font>
- *def* **`initialize_event_dates_dict (self):`**
    - 🍃require *def* **`inter_arrival (self, station, clss, current_time):`**
        - 👉resort to *def* **`simulation.inter_arrival_times[station][clss] ():`**
```python
    def initialize_event_dates_dict(self):

        for station in self.event_dates_dict:
            for clss in self.event_dates_dict[station]:

                self.event_dates_dict[station][clss] = self.inter_arrival(station, clss, 0.0)
```
```python
    def inter_arrival(self, station , clss, current_time):
        """
        Samples the inter-arrival time for next class and node.
        """
        if self.simulation.network.patients[clss].arrival_dist[station-1][0] == "TimeDependent":
            return self.simulation.inter_arrival_times[station][clss](current_time)
        return self.simulation.inter_arrival_times[station][clss]()
```

##### <font color='blue'> Event Based Core: </font>
- 👑*def* **`have_event (self):`** 
    - 🍃require *def* **`release_patient (self, next_station, next_patient):`**
        - 🍃require *def* **`record_rejection (self, next_station):`**
        - 🍃require *def* **`send_patient (self, next_station, next_patient):`**`
    - 🍃 require *def* **`find_next_event_date (self):`**
```python
    def have_event(self): 
        """
        Send new arrival to this station.
        """
        self.number_of_patients += 1
        # create new arrival (patient)
        priority_class = self.simulation.network.priority_cls_mapping[self.next_class]
        next_patient = Patient(self.number_of_patients, self.next_class, priority_class)
        
        # send patient next station
        next_station = self.simulation.transitive_stations[self.next_station - 1]
        self.release_patient(next_station, next_patient)

        # add new event_dates for new arrival
        self.event_dates_dict[self.next_station][self.next_class] = self.increment_time(
            self.event_dates_dict[self.next_station][self.next_class], 
            self.inter_arrival(self.next_station, self.next_class, self.next_event_date))

        self.find_next_event_date()
```
```python
    def release_patient(self, next_station, next_patient):
        """
        Either sends next_patient to the next station, or rejects
        """
        if next_station.number_of_patients >= next_station.station_capacity:
            self.record_rejection(next_station)
        else:
            self.send_patient(next_station, next_patient) 
```
```python
    def record_rejection(self, next_station):
        """
        Adds a patient to the rejection dictionary
        """
        self.rejection_dict[next_station.id_number][
            self.next_class].append(self.next_event_date)

    def send_patient(self, next_station, next_patient):
        """
        Sends the next_individual to the next_station
        """
        self.number_of_accepted_patients += 1
        next_station.accept(next_patient, self.next_event_date)
```
```python
    def find_next_event_date(self):
        """
        Finds the time of the next arrival.
        """
        times = [[self.event_dates_dict[station + 1][clss] 
            for clss in range(len(self.event_dates_dict[1]))] 
            for station in range(len(self.event_dates_dict))]

        min_times = [min(obs) for obs in times]
        station = min_times.index(min(min_times))
        clss = times[station].index(min(times[station]))

        self.next_station = station + 1
        self.next_class = clss
        self.next_event_date  = self.event_dates_dict[self.next_station][self.next_class]
```

### Station Class (idx)
Station Class has `eight` attributes: 
`basic`
- **simulation** *object*
    - interacted big environment 
- **station_id** *int*
- **number_of_servers** *int*
- **station_capacity** *int*

- **transition_row**
- **class_change**
- **next_event_date** *float*

`patient info`
- **patients** *list*
- **number_of_patients** *int*
- **all_patients**

`server info`
- **servers**
- **server_id_max**
- **all_servers_total**
- **all_servers_busy**

```python
class Station(object):

    def __init__(self, idx, simulation):
        self.simulation = simulation
        self.station_id = idx 
        station = self.simulation.network.stations[idx - 1]

        self.number_of_servers = station.number_of_servers
        self.station_capacity = station.queue_capacity + self.number_of_servers

        self.transition_row = [self.simulation.network.patients[clss].transition_mat[idx - 1]
            for clss in range(self.simulation.network.number_of_classes)]

        self.class_change = station.class_change_matrix

        self.next_event_date = float("Inf")

        # servers
        if not isinf(self.number_of_servers):
            self.servers = [Server(self, i+1, 0.0) for i in range(self.number_of_servers)]
        self.server_id_max = self.number_of_servers
        self.all_servers_total = []
        self.all_servers_busy = []
        # patients
        self.patients = [[] for _ in range(simulation.priority_lev)]
        self.number_of_patients = 0
```

##### <font color='blue'> Event Based Core: </font>
- 👑*def* **`have_event (self):`** 
    - 🍃require *def* **`find_next_patient (self):`**
    - 🍃require *def* **`change_patient_class (self, patient):`**
    - 🍃require *def* **`release(self, next_patient_idx, next_station, current_time):`**
        - 🍃 require *def* **`detatch_server(self, server, patient):`**
        - 🍃 require *def* **`write_patient_record(self, patient):`**
        - 🍃 require *def* **`begin_service_if_possible_release(self, current_time):`**
            - 🍃 require *def* **`free_server(self):`**
            - 🍃 require *def* **`find_free_server(self):`**
            - 🍃 reuqire *def* **`attach_server(self, server, patient):`**
        - 🍃 require *def* **`accept(self, next_patient, current_time):`**
            - 🍃 require *def* **`begin_service_if_possible_accept(self, next_patient, current_time):`**
                - 🍃 require *def* **`get_service_time(self, clss, current_time):`**
                - 🍃 reuqire *def* **`attach_server(self, server, patient):`**
    - 🍃 *def* **`next_station(self, patient_class):`**
```python
    def have_event(self):
        next_patient, next_patient_index = self.find_next_patient()

        self.change_patient_class(next_patient)

        next_station = self.next_station(next_patient.patient_class)
        
        next_patient.destination = next_station.station_id

        if not isinf(self.number_of_servers):
            next_patient.server.next_end_service_date = float('Inf')

        self.release(next_patient_index, next_station, self.next_event_date)
```
```python
    def find_next_patient(self):
        """
        Finds the next individual that should now finish service
        """
        next_patient_indices = [i for i, ind in enumerate(self.all_patients) 
            if ind.service_end_date == self.next_event_date]
        if len(next_patient_indices) > 1:
            next_patient_index = random_choice(next_patient_indices)
        else:
            next_patient_index = next_patient_indices[0]

        return self.all_patients[next_patient_index], next_patient_index
```
```python
    def change_patient_class(self, patient):
        """
        Takes patient and changes patient class according to the probability distribution.
        """
        if self.class_change:
            patient.prev_class = patient.patient_class
            patient.patient_class = random_choice(
                range(self.simulation.network.number_of_classes), self.class_change[patient.prev_class])
            patient.prev_priority_class = patient.priority_class
            patient.priority_class = self.simulation.network.priority_cls_mapping[patient.patient_class]
```
```python
    def release(self, next_patient_idx, next_station, current_time):
        """
        Update station when a patient is released.
        """
        next_patient =  self.all_patients[next_patient_idx]
        self.patients[next_patient.prev_priority_class].remove(next_patient)
        self.number_of_patients -= 1
        next_patient.queue_size_at_departure = self.number_of_patients
        next_patient.exit_date = current_time

        if not isinf(self.number_of_servers):
            self.detatch_server(next_patient.server, next_patient)
        
        # write record
        self.write_patient_record(next_patient)

        self.begin_service_if_possible_release(current_time)

        next_station.accept(next_patient, current_time)
``` 
```python
    def detatch_server(self, server, patient):
        """
        Detatches a server from an individual, and vice versa
        """
        server.patient = False
        server.busy = False

        patient.server = False

        if not server.busy_time:
            server.busy_time = (patient.exit_date - patient.service_start_date)
        else:
            server.busy_time += (patient.exit_date - patient.service_start_date)
        server.total_time = self.increment_time(patient.exit_date, - server.start_date)

   def write_patient_record(self, patient):
        DataRecord = namedtuple('Record', ['id_number', 'patient_class', 'station',
                                'arrival_date', 'waiting_time', 'service_start_date', 'service_time', 'service_end_date', 'exit_date', 'destination',
                                'queue_size_at_arrival', 'queue_size_at_departure'])

        record = DataRecord(
            patient.id_number,
            patient.prev_class,
            self.station_id,
            patient.arrival_date,
            patient.service_start_date - patient.arrival_date,
            patient.service_start_date,
            patient.service_end_date - patient.service_start_date,
            patient.service_end_date,
            patient.exit_date,
            patient.destination,
            patient.queue_size_at_arrival,
            patient.queue_size_at_departure)
        patient.data_records.append(record)

        patient.arrival_date = False
        patient.service_time = False
        patient.service_start_date = False
        patient.service_end_date = False
        patient.exit_date = False
        patient.queue_size_at_arrival = False
        patient.queue_size_at_departure = False
        patient.destination = False

    def begin_service_if_possible_release(self, current_time):
        """
        Begins the service of the next patient, giving that patient a service time, end date and station.
        """
        if self.free_server() and (not isinf(self.number_of_servers)):
            server = self.find_free_server()

            inds_without_server = [i for i in self.all_patients if not i.server]

            if len(inds_without_server) > 0:
                # Policy: choose the first one
                ind = inds_without_server[0] 
                ind.service_start_date = self.get_now(current_time)
                ind.service_end_date = self.increment_time(ind.service_start_date, ind.service_time)
                self.attach_server(server, ind)
```
```python
    def free_server(self):
        """
        Returns True if a server is available, False otherwise
        """
        if isinf(self.number_of_servers):
            return True
        return len([server for server in self.servers if not server.busy]) > 0

    def find_free_server(self):
        """
        Finds a free server.
        """
        for server in self.servers:
            # Policy: choose the first one
            if not server.busy: 
                return server

    def attach_server(self, server, patient):
        """
        Attaches a server to an individual, and vice versa.
        """
        server.patient = patient
        server.busy = True
        patient.server = server
        server.next_end_service_date = patient.service_end_date
```
```python
    def accept(self, next_patient, current_time):
        """
        Accepts a new customer to the queue.
        """
        next_patient.exit_date = False

        self.begin_service_if_possible_accept(next_patient, current_time)

        next_patient.queue_size_at_arrival = self.number_of_patients
        self.patients[next_patient.priority_class].append(next_patient)
        self.number_of_patients += 1
```
```python
    def begin_service_if_possible_accept(self, next_patient, current_time):
        """
        Begins the service of the next individual, giving
        that customer a service time, end date and node.
        """
        next_patient.arrival_date = current_time
        next_patient.service_time = self.get_service_time(next_patient.patient_class, current_time)

        if self.free_server():
            next_patient.service_start_date = self.get_now(current_time)
            next_patient.service_end_date = self.increment(current_time + next_patient.service_time)
            if not isinf(self.number_of_servers):
                self.attach_server(self.find_free_server(), next_patient)
```
```python
    def get_service_time(self, clss, current_time):
        if self.simulation.network.patients[clss].service_dist[self.station_id-1][0] == 'TimeDependent':
            return self.simulation.service_times[self.station_id][clss](current_time)
        return self.simulation.service_times[self.station_id][clss]()
```
```python
    def next_station(self, patient_class):
        """
        Finds the next station according the transition distributions.
        """
        return random_choice(array = self.simulation.all_stations[1:], 
            probs = self.transition_row[patient_class] + [1.0 - sum(self.transition_row[patient_class])])
  
```
##### Used for Future Simulation
- 🍩 *def* **`update_next_event_date(self, current_time):`**
- 🍩 *def* **`wrap_up_servers(self, current_time):`**
- 🍩 *def* **`def find_server_utilization(self):`**

### ExitStation Class

```python
class ExitStation(object):

    def __init__(self):
        self.all_patients = []
        self.number_of_patients = 0
        self.station_id = -1
        self.next_event_date = float("Inf")
        self.station_capacity = float("Inf")

    def accept(self, next_patient, current_time):
        self.all_patients.append(next_patient)
        self.number_of_patients += 1
```