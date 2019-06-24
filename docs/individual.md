## Patient and Server class

This module provides single `Server` class in each station and `Patient` class. 

### Server Class
Server Class has `ten` attributes: 

`Identification`
- **station** *object*
- **id_number** *int*

`Status`
- **patient** *object*
- **busy** *bool*

`Time Records`
- **start_date** *float*
- **busy_time** *float*
- **total_time** *float*
- **next_end_service_date** *float*

`Performance Measure`
- **utilisation** *float*

```python
class Server(object):

    def __init__(self, station, id_number, start_date=0.0):

        self.station = station
        self.id_number = id_number

        self.patient = False
        self.busy = False

        self.all_time = False
        self.start_date = start_date
        self.busy_time = False
        self.total_time = False
        self.next_end_service_date = float('Inf')

    @property
    def utilisation(self):
        return self.busy_time / self.total_time

```

### Patient Class
Server Class has `fifteen` attributes: 

`Identification`
- **id_number**
- **data_records** 

- **server**
- **prev_class**
- **priority_class**
- **prev_prioirity_class**

`Time Records`
- **arrival_date** *float*
- **service_start_date** *float*
- **service_time** *float*
- **service_end_date** *float*
- **exit_date** *float*
    - in the case when no blocking, **service_end_date = exit_date**

`Observed Measures`
- **queue_size_at_arrival** *int*
- **queue_size_at_departure** *int*

```python
    def __init__(self, id_number, patient_class=0, priority_class=0):

        # static
        self.id_number = id_number
        self.data_records = []

        # dynamic
        self.server = False
        self.destination = False

        self.patient_class = patient_class
        self.prev_class = patient_class
        self.priority_class = priority_class
        self.prev_priority_class = priority_class

        self.arrival_date = False
        self.service_start_date = False
        self.service_time = False
        self.service_end_date = False
        self.exit_date = False

        self.queue_size_at_arrival = False
        self.queue_size_at_departure = False
```
