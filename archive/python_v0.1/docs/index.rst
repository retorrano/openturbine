OpenTurbine Documentation
==========================

OpenTurbine is an open-source wind turbine simulation application.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   parameters
   user_guide/index
   theory/index
   api/index

Features
--------

* 3D Interactive turbine visualization
* Aerodynamic simulation using Blade Element Momentum theory
* Structural analysis capabilities
* Control systems simulation
* Real-time parameter adjustment
* Export results to CSV

Quick Start
-----------

1. Download and install OpenTurbine for your platform
2. Launch the application
3. Adjust turbine parameters in the left panel
4. Set wind speed using the slider
5. Click Run to start simulation

API Documentation
-----------------

For developers wanting to use OpenTurbine programmatically::

    from openturbine import SimulationRunner

    simulator = SimulationRunner()
    result = simulator.run_steady_state(wind_speed=8.0)
    print(f"Power: {result['power_mw']} MW")

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
