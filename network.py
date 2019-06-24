class StationClass(object):

    def __init__(self, number_of_servers, queue_capacity, class_change_matrix=None):
        self.number_of_servers = number_of_servers
        self.queue_capacity = queue_capacity
        self.class_change_matrix = class_change_matrix

class PatientClass(object):

    def __init__(self, arrival_dist, service_dist, 
                       transition_mat, priority_cls):
        self.arrival_dist = arrival_dist
        self.service_dist = service_dist
        self.transition_mat = transition_mat
        self.priority_cls = priority_cls

class Network(object):
    
    def __init__(self, stations, patients):
        
        self.stations = stations
        self.patients = patients
        self.number_of_stations = len(stations)
        self.number_of_classes = len(patients)
        
        self.priority_lev = len(set([
            clss.priority_cls for clss in patients])) 
        
        self.priority_cls_mapping = {i: clss.priority_cls 
            for i, clss in enumerate(patients)}
