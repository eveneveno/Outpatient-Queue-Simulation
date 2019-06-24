## Network class

This module provides the integrated `Network` class consisting of one `Station` and one `Patient`. 

### Station Class
Station Class has `three` basic attributes: 
- **number_of_servers** *int*
    - e.g., 1 X-ray station have 3 machines.
- **queue_capacity** *int*
    - e.g., the queue capacity at the outpatient clinic should be no more than 200 (pratically we could set this number large enough to avoid blocking issue which is rare in the Chinese hospital setting.)
- **class_change_matrix** *matrix*
    - e.g., patients during services might change their patient classes, from a "New Patient" to "Revisit Patient" after some examinations.

```python
class StationClass(object):

    def __init__(self, number_of_servers, queue_capacity, class_change_matrix=None):

        self.number_of_servers = number_of_servers
        self.queue_capacity = queue_capacity
        self.class_change_matrix = class_change_matrix
```

### Patient Class
Patient Class has `four` basic attributes: 
- **arrival_dist** *func*
    - The distribution that models patient `arrival patterns`. Current allowed distributions include:
        - NoArrivals
        - `Uniform`: ['Uniform', 0.1, 0.7]
        - `Deterministic`: ['Deterministic', 0.4]
        - `Exponential`: ['Exponential', 6.0] with mean 1/6.0 = 0.1666...
        - `Normal`: truncated normal
        - `Custom`: ['Custom', [0.2, 0.4], [0.5, 0.5]]
        - UserDefined
        - TimeDepedent
        - `Empirical`: ['Empirical', [0.1, 0.1, 0.1, 0.2] randomly chosen from
- **service_dist** *func*
    - The distribution that models patient's corresponding `service patterns`.
- **transition_mat** *matrix*
    - Markov Transition matrix
- **priority_cls** *dict*
    - Assign different priority levels to different classes of patient
    
```python
class PatientClass(object):

    def __init__(self, arrival_dist, service_dist, 
                       transition_mat, priority_cls):
        self.arrival_dist = arrival_dist
        self.service_dist = service_dist
        self.transition_mat = transition_mat
        self.priority_cls = priority_cls
```
### Integrated Network
Network Class has `five` components: 
- **stations** *list*
    - collection of all stations info
- **patients** *list*
    - collection of all patient demography
- **number_of_stations** *int*
    - elements number in [stations]
- **number_of_classess** *int*
    - elements number in [patients]
- **priority_lev** *int*
    - unique levels of patients set
- **priority_cls_mapping** *dict*
    - dictionary display priority class information

```python
class Network(object):
    
    def __init__(self, stations, patients):
        
        self.stations = stations
        self.patients = patients
        self.number_of_stations = len(stations)
        self.number_of_classes = len(patients)
        self.priority_lev = len(set([clss.priority_cls for clss in patients])) 
        self.priority_cls_mapping = {i: clss.priority_cls for i, clss in enumerate(patients)}

```