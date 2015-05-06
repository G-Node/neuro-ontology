__author__ = '11235813'

import sys
import getopt
import uuid
import rdflib
import re
import random
import datetime
import os


# Namespaces
nso = rdflib.Namespace("http://www.semanticweb.org/ontology#")    # ontology namespace
nsd = rdflib.Namespace("http://www.semanticweb.org/ontology/data#")    # Namespace for data
rdf = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
# owl = rdflib.Namespace("http://www.w3.org/2002/07/owl#")


# property shortcuts
rdf_is_a = rdf["type"]
rdfs_label = rdfs["label"]

def make_project(graph, no_project, args, datatype_properties):
    """
    Function: make_project
    ---------------------------------
    Input:

    Output:
    """

    entity = "Project"
    label = 'Project-' + str(no_project)
    print(label)

    # create individual of type Project
    project = nsd[str(uuid.uuid4())]

    # add the individual to the graph based on its URI and set its
    # corresponding label
    add_individual(graph, entity, project, label)

    # get the datatype properties for the Project class
    dtps = datatype_properties[entity]

    # display datatype properties
    if no_project == 0:
        display_datatype_properties(dtps, entity)

    # create datatype properties for the project individual
    create_dtp(dtps, graph, project)

    no_experiments = get_no(args)

    for i in range(no_experiments):
        # TODO: add meaning
        make_experiment(graph, project, no_project, i, args[1:], datatype_properties)

    """ TODO: establish object properties both on-the-fly, following the
    hierarchical call but also after all the projects have been created such
    that one has interconnected elements that give graph and not simply a tree """


def make_experiment(graph, project, no_project, no_experiment, args, datatype_properties):
    """
    Function: make_experiment
    ---------------------------------
    Input:

    Output:
    """

    entity = "Experiment"
    label = 'Experiment-' + str(no_project) + '-' + str(no_experiment)
    print("    %s" % label)

    # create individual of type Experiment
    experiment = nsd[str(uuid.uuid4())]

    # add the individual to the graph based on its URI and set its
    # corresponding label
    add_individual(graph, entity, experiment, label)

    # get the datatype properties for the Experiment class
    dtps = datatype_properties[entity]

    # display datatype properties
    if no_experiment == 0:
        display_datatype_properties(dtps, entity)

    # create datatype properties for the experiment individual
    create_dtp(dtps, graph, experiment)

    no_research_activities = get_no(args)

    for i in range(no_research_activities):
        # TODO: add meaning
        make_research_activity(graph, experiment, no_experiment, i, args[1:], datatype_properties)


def make_research_activity(graph, experiment, no_experiment, no_research_activity, args, datatype_properties):
    """
    Function: make_research_activity
    ---------------------------------
    Create a research activity

    Input:

    Output:
    """

    """ TODO: discard Experiment in the case of Experiment hasResearchActivity
    the same for all intersection-like Domains or Ranges"""

    entity = "ResearchActivity"
    label = 'ResearchActivity-' + str(no_experiment) + '-' + str(no_research_activity)
    print("        %s" % label)

    # create individual of type ResearchActivity
    research_activity = nsd[str(uuid.uuid4())]

    # add the individual to the graph based on its URI and set its
    # corresponding label
    add_individual(graph, entity, research_activity, label)

    # get the datatype properties for the ResearchActivity class
    dtps = datatype_properties[entity]

    # display datatype properties
    if no_research_activity == 0:
        display_datatype_properties(dtps, entity)

    # create datatype properties for the research_activity individual
    create_dtp(dtps, graph, research_activity)

    no_research_activities = get_no(args)

    for i in range(no_research_activities):
        # TODO: meaning
        break


def add_individual(graph, entity, uri, label):
    """
    Function: add_individual
    ---------------------------------

    Input:

    Output:
    """

    # add the individual to the graph based on its URI
    triple = (uri, rdf_is_a, nso[entity])
    graph.add(triple)

    # set its corresponding label
    triple = (uri, rdfs_label, nso[label])
    graph.add(triple)


def create_dtp(datatype_props, graph, subject):
    """
    Function: create_dtp
    ---------------------------------
    Create datatype properties

    Input:

    Output:
    """

    """ TODO: For some properties, only one value per resource makes sense
    (i.e they are functional properties, or have max-cardinality of 1). The set()
    method is useful for this """

    # create datatype properties based on their required type
    # triple = (uuid->to be generated, key->dtp name, val->Literal)
    for dtp in datatype_props:

        # TODO: adapt cardinality based on actual ontology specifications
        cardinality = 1

        # remove all possible prefixes, such as: 'at' and 'has'
        label = re.sub(r'has', '', dtp[0].split('#')[1])  # remove label prefix
        label = re.sub(r'at', '', label)  # remove label prefix
        datatype = dtp[1].split('#')[1]

        # create a literal that should correspond to this datatype property
        literal = create_literal(label, dtp[1], cardinality)  # send the entire uri of the type
        print ("> literal for %s with datatype %s is: %s" % (label, datatype, literal))

        # add the triple to the graph
        triple = (subject, dtp[0], literal)
        graph.add(triple)


def display_datatype_properties(dtps, name):
    """
    Function: display_datatype_properties
    ---------------------------------
    Display datatype properties

    Input:

    Output:
    """

    print("> datatype properties for %s:" % name)
    for dtp in dtps:
        prop = dtp[0].split('#')[1]
        prop_type = dtp[1].split('#')[1]
        print("    %s : %s" % (prop, prop_type))


def query_class_name(graph):
    """
    Function: query_class_name
    ---------------------------------
    Input:

    Output:
    """

    q = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT DISTINCT ?subject
        WHERE {
            ?subject a owl:Class.
            FILTER(!isBlank(?subject))
        }
        """

    result = graph.query(q)
    return result


def query_dtp(graph, classnames):
    """
    Function: query_dtp
    ---------------------------------
    Input:

    Output:
    """

    dtp_dict = {}

    for cn in classnames:
        if re.search("#", cn[0]):
            cn = cn[0].split('#')[1]

        q = """
        PREFIX onto:<http://www.semanticweb.org/ontology#>
        PREFIX owl:<http://www.w3.org/2002/07/owl#>
        SELECT DISTINCT ?prop ?range
            WHERE {
                { #for domains AND ranges with multiple classes (union of classes)
                {?prop a owl:DatatypeProperty} UNION {?prop a owl:AnnotationProperty} .
                ?prop rdfs:domain ?u .
                ?u owl:unionOf ?list .
                ?list rdf:rest* ?subList .
                ?subList rdf:first onto:""" + cn + """ .
                ?prop rdfs:range ?r .
                ?r owl:unionOf ?ur.
                ?ur rdf:rest* ?subList .
                ?subList rdf:first ?range .
                }
                UNION
                { #for domains with a single class AND ranges with multiple types(union of types)
                {?prop a owl:DatatypeProperty} UNION {?prop a owl:AnnotationProperty} .
                ?prop rdfs:domain onto:""" + cn + """ .
                ?prop rdfs:range ?r .
                ?r owl:unionOf ?ur.
                ?ur rdf:rest* ?subList .
                ?subList rdf:first ?range .
                }
                UNION
                { #for domains with multiple classes (union of classes) AND range with a single type
                {?prop a owl:DatatypeProperty} UNION {?prop a owl:AnnotationProperty} .
                ?prop rdfs:domain ?u .
                ?u owl:unionOf ?list .
                ?list rdf:rest* ?subList .
                ?subList rdf:first onto:""" + cn + """ .
                ?prop rdfs:range ?range .
                }
                UNION
                { #for domains with a single class AND range with a single type
                {?prop a owl:DatatypeProperty} UNION {?prop a owl:AnnotationProperty} .
                ?prop rdfs:domain onto:""" + cn + """ .
                ?prop rdfs:range ?range .
                }
            }
            VALUES (?range) {
            (xsd:float) (xsd:integer) (xsd:nonNegativeInteger) (xsd:positiveInteger) (xsd:string)
            }
            """

        result = graph.query(q)
        dtp_dict[cn] = result

    return dtp_dict


def create_literal(label, dt, cardinality):
    """
    Function: create_literal
    ---------------------------------
    Input:

    Output:
    """

    # TODO: adequately adjust the ranges for int, float, dateTime

    # get only the actual type
    type = dt.split('#')[1]
    if "string" in type:
        val = label + "_" + str(cardinality)
    elif "integer" in type:
        val = random.int(-13, 13)
    elif "nonNegativeInteger" in type:
        val = random.randint(0)
        # alternative: randint(a, b)
    elif "positiveInteger" in type:
        val = random.randint(1)
        # alternative: randint(a, b)
    elif "float" in type:
        val = random.uniform(-13, 13)
    elif "dateTime" in type:
        val = create_random_datetime('1990/01/01 00:00', datetime.datetime.utcnow(), '%Y/%m/%d %H:%M', random.random())

    literal = rdflib.Literal(val, datatype=rdflib.URIRef(dt))

    return literal


def create_random_datetime(start, end, f, rnd):
    """
    Function: create_literal
    ---------------------------------
    Input:

    Output:
    """

    """Get a time at a proportion of a range of two formatted times.
    start and end should be strings specifying times formatted in the
    given format f (strftime-style), giving an interval [start, end].
    rnd specifies how a proportion of the interval to be taken after
    start. The returned time will be in the specified format.
    """

    # TODO: So far, the randomly generated time always starts at 00:00:00.
    # TODO: Find a different method that makes use of the floating point
    # TODO: number rnd_time such that hours, minutes and seconds are also
    # TODO: randomly generated

    # TODO: Consistency for the datetime format: the presence of seconds

    start_time = datetime.datetime.strptime(start, f).toordinal()
    end_time = end.toordinal()

    rnd_time = start_time + rnd * (end_time - start_time)

    print("> randomly generated time: %s" % datetime.datetime.fromordinal(int(rnd_time)).__str__())

    return datetime.datetime.fromordinal(int(rnd_time))


def get_no(args):
    """
    Function: get_no
    ---------------------------------
    Input:

    Output:
    """
    # TODO: establish default values depending on the class type

    if args:
        return args[0]
    return 13


def usage():
    """
    Function: usage
    ---------------------------------
    Input:

    Output:
    """

    print("> individuals_generator.py [--ontology=|-o ontology_file] [project_no "
          "experiment_no]. \nExample: > individuals_generator.py --ontology=../ontology_rdf.owl 2 3")


def main(argv):
    """
    Function: main
    ---------------------------------
    Input:

    Output:
    """

    try:
        opts, args = getopt.getopt(argv, "ho:", ["help", "ontology="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # TODO: group for and if together such that args and opts work for all usecases
    ontology_file = "../ontology_rdf.owl"     # default ontology file

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-o", "--ontology"):
            ontology_file = arg

    # check if in case arguments are provided, they contain only numbers
    if args:
        if re.search('[0-9]', ''.join(args)):
            args = map(int, args)
        else:
            usage()
            sys.exit()

    no_projects = get_no(args)
    print("> no Projects: %s" % str(no_projects))

    # prepare the rdf graph
    graph = rdflib.ConjunctiveGraph()
    graph.parse(ontology_file)
    print("> graph has %s statements." % len(graph))

    # query the names of the classes that exist in the ontology
    classnames = query_class_name(graph)

    # query the datatype properties for each class of the ontology
    # dictionary data structure of the form (classname, {datatype properties})
    datatype_properties = query_dtp(graph, classnames)

    for key, val in datatype_properties.iteritems():
        print("> class %s has the datatype properties: " % key)
        for dtp in val:
            prop = dtp[0].split('#')[1]
            prop_type = dtp[1].split('#')[1]
            print("    %s : %s" % (prop, prop_type))

    # create the requested number of projects
    for i in range(no_projects):
        make_project(graph, i, args[1:], datatype_properties)

    # save the new graph
    out_file = "../metadata_rdf.owl"

    if os.access(out_file, os.W_OK):
        os.remove(out_file)
    with open(out_file, "w") as out:
        out.write(graph.serialize(format="xml"))

if __name__ == "__main__":
    main(sys.argv[1:])