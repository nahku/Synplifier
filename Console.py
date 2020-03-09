import argparse
import InputOutput
from GraphBuilder import TPTPGraphBuilder,Node,RuleType

parser = argparse.ArgumentParser(description='Extract sublanguage using TPTP language grammar specification and control file.')
parser.add_argument('-g','--grammar', metavar='', type=str, required=True,
                    help='Path of the TPTP grammar file')
parser.add_argument('-c','--control', metavar='', type=str, required=True,
                    help='Path of the control file')
parser.add_argument('-o','--output', metavar='', type=str, required=False,
                    help='Optional output file name and path (default output.txt)')

args = parser.parse_args()

if __name__ == "__main__":
    graphBuilder = TPTPGraphBuilder(args.grammar,args.control)
    start_node = graphBuilder.nodes_dictionary.get(Node("<start_symbol>", RuleType.GRAMMAR))
    if start_node:
        if args.output is not None:
            output_path = args.output
        else:
            output_path = "output.txt"
        InputOutput.save_ordered_rules_from_graph(output_path, start_node)

pass