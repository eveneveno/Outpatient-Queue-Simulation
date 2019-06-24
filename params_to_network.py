import os
import yaml
import copy
import pdb

from network import StationClass, PatientClass, Network

def create_network(Arrival_distributions=None,  # required
                   Service_distributions=None,  # required   
                   Number_of_servers=None,      # required

                   Transition_matrices=None,    # required for multi-stations
                   Queue_capacities=None,   
                   Priority_classes=None,
                   Class_change_matrices=None):

    params = {'Arrival_distributions': Arrival_distributions,
              'Service_distributions': Service_distributions,
              'Number_of_servers':     Number_of_servers}

    if Transition_matrices != None:     
        params['Transition_matrices'] = Transition_matrices
    if Queue_capacities != None:     
        params['Queue_capacities'] = Queue_capacities
    if Priority_classes != None:     
        params['Priority_classes'] = Priority_classes    
    if Class_change_matrices != None:   
        params['Class_change_matrices'] = Class_change_matrices    

    pars = copy.deepcopy(params)

    if isinstance(pars['Arrival_distributions'], list): 
        pars['Arrival_distributions'] = {'Class 0': pars['Arrival_distributions']}
    if isinstance(pars['Service_distributions'], list): 
        pars['Service_distributions'] = {'Class 0': pars['Service_distributions']}
    if 'Transition_matrices' in pars:
        if isinstance(pars['Transition_matrices'], list): 
            pars['Transition_matrices'] = {'Class 0': pars['Transition_matrices']}


    number_of_classes = len(pars['Arrival_distributions'])
    number_of_stations = len(pars['Number_of_servers'])

    default_dict = {'Number_of_stations': number_of_stations,
                    'Number_of_classes': number_of_classes,
                    'Queue_capacities': ['Inf' 
                        for _ in range(number_of_stations)],
                    'Transition_matrices': {'Class ' + str(i): [[0.0]] 
                        for i in range(number_of_classes)},
                    'Priority_classes': {'Class ' + str(i): 0 
                        for i in range(number_of_classes)} }


    for content in default_dict:
        pars[content] = pars.get(content, default_dict[content])

    arrival_dists = [pars['Arrival_distributions']['Class ' + str(clss)] 
                    for clss in range(len(pars['Arrival_distributions']))]
    service_dists = [pars['Service_distributions']['Class ' + str(clss)] 
                    for clss in range(len(pars['Service_distributions']))]
    transition_mats = [pars['Transition_matrices']['Class ' + str(clss)] 
                    for clss in range(len(pars['Transition_matrices']))]
    queue_capacities = [float(i) if i == "Inf" else i 
                    for i in pars['Queue_capacities']]
    priority_clss = [pars['Priority_classes']['Class ' + str(clss)] 
                    for clss in range(len(pars['Priority_classes']))]

    class_change_matrices = pars.get('Class_change_matrices',
        {'Station ' + str(station + 1): None for station in range(number_of_stations)})

    number_of_servers = []

    for server in Number_of_servers:
        if server == 'Inf':
            number_of_servers.append(float(server))
        else:
            number_of_servers.append(server)       

    station_nets, patient_nets = [], [] 

    for station in range(number_of_stations):
        station_nets.append(StationClass(
            number_of_servers[station], 
            queue_capacities[station],
            class_change_matrices['Station ' + str(station + 1)]
        ))
    
    for clss in range(number_of_classes):
        patient_nets.append(PatientClass(
            arrival_dists[clss],
            service_dists[clss],
            transition_mats[clss],
            priority_clss[clss]
        ))

    Net = Network(station_nets, patient_nets)
    return Net

if __name__ == "__main__":

    check_mode = 'priority'

    ## basic version: M/M/1
    if check_mode == 'basic':
        N = create_network(
            Arrival_distributions=[['Exponential', 0.2]],
            Service_distributions=[['Exponential', 0.1]],
            Number_of_servers=[3])

    ## 3 stations + 2 classes
    if check_mode == 'advance':
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

    ## 2 classes with priority
    if check_mode == 'priority':
        N = create_network(
            Arrival_distributions={'Class 0': [['Exponential', 5]],
                                'Class 1': [['Exponential', 5]]},
            Service_distributions={'Class 0': [['Exponential', 10]],
                                'Class 1': [['Exponential', 10]]},
            Priority_classes={'Class 0': 0, 'Class 1': 1},
            Number_of_servers=[1]
            )

    # 1 station + 3 classes + change class
    if check_mode == 'change_class':
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
    pdb.set_trace()