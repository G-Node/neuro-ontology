from rdflib import *
import sys
import getopt


def query_object_properties(class_domain, class_range):
    """
    Function: query_object_properties
    ---------------------------------
    Returns a query string that looks for object properties. Its set of results
    should have the following triplet form: (object property, range, inverse property)

    Input: class_domain - the name of a class that should be considered as a domain
                          of the object property
           class_range  - one or more class names that should be considered as range
                          of the object property

    Output: Returns a string of characters.
    """

    q_objprop_select = """
    PREFIX onto:<http://www.semanticweb.org/ontology#>
    PREFIX owl:<http://www.w3.org/2002/07/owl#>
    SELECT DISTINCT ?prop ?range ?inverse
      WHERE {
      VALUES ?domain {onto:""" + class_domain + """}
      { #for domains AND ranges with multiple classes (union of classes)
      ?prop a owl:ObjectProperty .
      ?prop rdfs:domain ?u . 
      ?u owl:unionOf ?list .
      ?list rdf:rest* ?subList .
      ?subList rdf:first ?domain .
      ?prop rdfs:range ?r .
      ?r owl:unionOf ?ur.
      ?ur rdf:rest* ?sl .
      ?sl rdf:first ?range .
      OPTIONAL {?prop owl:inverseOf ?inverse . ?inverse a owl:ObjectProperty .}
      OPTIONAL {?inverse owl:inverseOf ?prop . ?inverse a owl:ObjectProperty .}
      }
      UNION
	{ #for domains with a single class AND ranges with multiple classes(union of classes)
	?prop a owl:ObjectProperty .
	?prop rdfs:domain ?domain .
	?prop rdfs:range ?r .
	?r owl:unionOf ?ur.
	?ur rdf:rest* ?sl .
	?sl rdf:first ?range .
	OPTIONAL {?prop owl:inverseOf ?inverse . ?inverse a owl:ObjectProperty .}
	OPTIONAL {?inverse owl:inverseOf ?prop . ?inverse a owl:ObjectProperty .}
	}
      UNION
	{ #for domains with multiple classes(union of classes) AND ranges with a single class
	?prop a owl:ObjectProperty .
	?prop rdfs:domain ?u . 
	?u owl:unionOf ?list .
	?list rdf:rest* ?subList .
	?subList rdf:first ?domain .
	?prop rdfs:range ?range .
	OPTIONAL {?prop owl:inverseOf ?inverse . ?inverse a owl:ObjectProperty .}
	OPTIONAL {?inverse owl:inverseOf ?prop . ?inverse a owl:ObjectProperty .}
	}
      UNION
	{ #for domains AND ranges with a single class
	?prop a owl:ObjectProperty .
	?prop rdfs:domain ?domain .
	?prop rdfs:range ?range .
	OPTIONAL {?prop owl:inverseOf ?inverse . ?inverse a owl:ObjectProperty .}
	OPTIONAL {?inverse owl:inverseOf ?prop . ?inverse a owl:ObjectProperty .}
	}
    }
    VALUES (?range)  {  """

    # set the classes that should be considered as range
    for i in xrange(len(class_range)):
        q_objprop_select += "(onto:" + class_range[i] + ") "
    q_objprop_select += "}"

    return q_objprop_select


def dtp_box(graph, classname, out):
    """
    Function: dtp_box
    -----------------
    Forms a query for datatype properties of a given class that belongs to the
    given graph. Queries the graph. Creates the UML-like box for this class,
    adding its name and its datatype properties.

    Input: graph      - the ontology RDF graph
           classname  - the name of the class whose datatype properties are queried
           out        - DOT file

    Output: -
    """

    q = """
    PREFIX onto:<http://www.semanticweb.org/ontology#>
    PREFIX owl:<http://www.w3.org/2002/07/owl#>
    SELECT ?prop ?range
	WHERE {
	  { #for domains with multiple classes (union of classes)
	  ?prop a owl:DatatypeProperty .
	  ?prop rdfs:domain ?u . 
	  ?u owl:unionOf ?list .
	  ?list rdf:rest* ?subList .
	  ?subList rdf:first onto:""" + classname + """ .
	  ?prop rdfs:range ?range .
	  }
	UNION
	  { #for domains with a single class
	  ?prop a owl:DatatypeProperty .
	  ?prop rdfs:domain onto:""" + classname + """ .
	  ?prop rdfs:range ?range .
	  }
	}
    """
    dtp = graph.query(q)

    # start constructing the box node
    out.write('%s[fontsize = "11"; shape=none;\n label = <<table border="1" \
    cellborder="0" cellspacing="0">\n<tr><td port="port1" border="1" bgcolor=\
    "palegreen">%s</td></tr>' % (classname, classname))

    idx = 1
    for r in dtp:
        prop = r[0].split('#')[1]
        prop_type = r[1].split('#')[1]
        out.write('\n<tr><td port="port%i" align="left" bgcolor="white">%s: %s\
        </td></tr>' % (idx+1, prop, prop_type))
    out.write('</table>>];')


def query_results_to_dot(graph, filename, classname):
    """
    Function: query_results_to_dot
    ---------------------------------
    Begins the construction of the DOT file by defining the graph properties.
    Draws boxes for each requested class together with its datatype properties.
    Queries the graph for object properties and their inverses for each possible
    connection among the specified classes.

    Input: graph     - the ontology RDF graph
           filename  - DOT file
           classname - list of class names

    Output: -
    """

    out = file(filename,'w')

    out.write('digraph obj{\n')
    out.write('node[shape=record]; #use the label and the instructions provided below\n')
    out.write('#rankdir="RB" arrange hierarchically\n')

    # draw the boxes together with the datatype properties that correspond to each class
    no_classes = len(classname)
    for c in classname:
        dtp_box(graph, c, out)

    # query the object properties for all the classes
    for i in xrange(no_classes-1):
        class_domain = classname[i]
        class_range = classname[i+1:no_classes]
        q = query_object_properties(class_domain, class_range)
        results = graph.query(q)
        print classname[i] + "->" + ", ".join(classname[i+1:no_classes]) + " have " + str(len(results)) + " relationship(s) defined"

        idx = 1
        for r in results:
            prop = r[0].split('#')[1]
            prop_range = r[1].split('#')[1]

            # check if there is an inverse property
            if r[2]:
                prop_inverse = r[2].split('#')[1]
            else:
                prop_inverse = None

            # mark association between the Domain and the Range
            # TODO: adapt cardinality based on some/only
            # check if the inverse of this property exists. If so, add the reverse association that corresponds to it
            if prop_inverse:
                out.write('%s->%s [dir="forward", arrowhead="none", arrowtail=\
                "normal", headlabel="%s 1", taillabel="1.. %s", labelfontsize="9", \
                labeldistance="1"];\n' % (classname[i], prop_range, prop_inverse, prop))
            else:
                out.write('%s->%s [dir="forward", arrowhead="none", arrowtail=\
                "normal", headlabel="1", taillabel="1..", xlabel="%s", fontsize="9", \
                labelfontsize="9", labeldistance="1"];\n' % (classname[i], prop_range, prop))

            idx += 1

    out.write('}')


def main(argv):
    """
    Function: main
    ---------------------------------
    Construct a UML-like graph for the ontology classes provided as arguments from the command line.

    Input: argv - command line arguments: list with names of classes

    Output: -
    """

    try:
        opts, args = getopt.getopt(argv, ":")
    except getopt.GetoptError:
        print 'plot_classes.py <class_names>'
        sys.exit(2)

    class_names = args

    if class_names:

        # prepare the graph
        g = ConjunctiveGraph()

        g.parse("ontology_rdf.owl")
        print("graph has %s statements." % len(g))

        # perform query for each Class that was requested from the CL
        query_results_to_dot(g, 'graph.dot', class_names)

if __name__ == "__main__":
    main(sys.argv[1:])
