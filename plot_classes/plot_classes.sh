#!bin/bash

# Copyright (c) 2015, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.

#run the DOT constructor
python plot_classes.py $@

#convert the DOT file to SVG
#dot -Tps graph.dot -o graph.ps
dot -Tsvg graph.dot -o graph.svg

#visualize the PS file
#xdg-open graph.ps
xdg-open graph.svg
