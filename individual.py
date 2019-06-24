from __future__ import division

class Server(object):

    def __init__(self, station, id_number, start_date=0.0):

        self.station = station
        self.id_number = id_number

        self.patient = False
        self.busy = False

        self.start_date = start_date
        self.busy_time = False
        self.total_time = False
        self.next_end_service_date = float('Inf')

    @property
    def utilisation(self):
        return self.busy_time / self.total_time

class Patient(object):

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
