#!/bin/bash
cd /home/mano/hacks/antigravity/simulations/openturbine
source venv/bin/activate
export PYTHONPATH=/home/mano/hacks/antigravity/simulations/openturbine/src:$PYTHONPATH
python -c "from openturbine.ui.main_window import main; main()"
