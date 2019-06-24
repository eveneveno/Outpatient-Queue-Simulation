evenNet Queuing Model
====

Introduction
------------

`evenNet` is a simplified queuing model simulator used for hospital outpatient operation management

It supports many kinds of settings that are pratical in real hospitals

- Multi-stations: clinics, examination stations, etc.
- User-defined transition probability between multi-staions (networks)
- Multi-class of patients: new patients / re-visit patients ...
- Possibility for patients classes change: after examination, prev new patients => re-visit patients
- Records for a variety of performance measures

See the `ciw <https://ciw.readthedocs.io/en/latest/index.html>`_ for more general queuing network.

Acknowledgement

@misc{ciwpython,
  author       = {{{The Ciw library developers}}},
  title        = {Ciw: <RELEASE TITLE>},
  year         = <YEAR>,
  doi          = {<DOI INFORMATION>},
  url          = {http://dx.doi.org/10.5281/zenodo.<DOI NUMBER>}
}

Documents
------------

Try and start with simple case, with [one station], [one class of patient], [three doctors in outpatint clinics] 

.. code::

    python simulation.py --case "basic_3"


for more advanced assumptions you could try and compare their performance measures


.. code::

    python simulation.py --case "basic_4" 
    python simulation.py --case "homo_class_with_transition"
    python simulation.py --case "hetero_class_with_transition"
    python simulation.py --case "priority"
    python simulation.py --case "class_change"

By default case, records will be output as all_records.csv, you could change it by setting args.write_csv = False or specify another output path by specifying args.path = "<file_path>"
