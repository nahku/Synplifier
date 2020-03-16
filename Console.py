import argparse
import Input,Output
from GraphBuilder import TPTPGraphBuilder, Node, RuleType

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Extract sublanguage using TPTP language grammar specification and control file')
    parser.add_argument('-g', '--grammar', metavar='', type=str, required=True,
                        help='path of the TPTP language grammar file')
    parser.add_argument('-c', '--control', metavar='', type=str, required=True,
                        help='path of the control file')
    parser.add_argument('-o', '--output', metavar='', type=str, required=False,
                        help='optional output file name (default output.txt)')
    args = parser.parse_args()

    graphBuilder = TPTPGraphBuilder(Input.read_text_from_file(args.grammar), Input.read_text_from_file(args.control))
    start_node = graphBuilder.nodes_dictionary.get(Node("<start_symbol>", RuleType.GRAMMAR))
    if start_node:
        if args.output is not None:
            output_path = args.output
        else:
            output_path = "output.txt"
        Output.save_ordered_rules_from_graph(output_path, start_node)
