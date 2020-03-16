import argparse
import Input,Output
from GraphBuilder import TPTPGraphBuilder, Node, RuleType

class Console:

    def run(self):
        args = self.argument_parser.parse_args()
        graphBuilder = TPTPGraphBuilder(file=Input.read_text_from_file(args.grammar), disable_rules_string=Input.read_text_from_file(args.control))
        start_node = graphBuilder.nodes_dictionary.get(Node("<start_symbol>", RuleType.GRAMMAR))
        if start_node:
            if args.output is not None:
                output_path = args.output
            else:
                output_path = "output.txt"
            Output.save_ordered_rules_from_graph(output_path, start_node)

    def __init__(self):
        self.argument_parser = argparse.ArgumentParser(
            description='Extract sublanguage using TPTP syntax file and a control file')
        self.argument_parser.add_argument('-g', '--grammar', metavar='', type=str, required=True,
                                     help='path of the TPTP language grammar file')
        self.argument_parser.add_argument('-c', '--control', metavar='', type=str, required=True,
                                     help='path of the control file')
        self.argument_parser.add_argument('-o', '--output', metavar='', type=str, required=False,
                                     help='optional output file name (default output.txt)')

if __name__ == "__main__":
    console = Console()
    console.run()
    # args = argument_parser.parse_args()
    #
    # graphBuilder = TPTPGraphBuilder(Input.read_text_from_file(args.grammar), Input.read_text_from_file(args.control))
    # start_node = graphBuilder.nodes_dictionary.get(Node("<start_symbol>", RuleType.GRAMMAR))
    # if start_node:
    #     if args.output is not None:
    #         output_path = args.output
    #     else:
    #         output_path = "output.txt"
    #     Output.save_ordered_rules_from_graph(output_path, start_node)
