#!bin/bash
#run the DOT constructor
python plot_classes.py $@

#convert the DOT file to SVG
#dot -Tps graph.dot -o graph.ps
dot -Tsvg graph.dot -o graph.svg

#visualize the PS file
#xdg-open graph.ps
xdg-open graph.svg
