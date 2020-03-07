import Parser
import GraphBuilder

def test_find_top_of_page_line_id_no_top_of_page():
    comment_block = Parser.COMMENT_BLOCK(["%----White space may occur between any two tokens. White space is not specified",
                "%----in the grammar, but there are some restrictions to ensure that the grammar",
                "%----is compatible with standard Prolog: a <TPTP_file> should be readable with",
                "%----read/1."])
    gb = GraphBuilder.TPTPGraphBuilder()
    assert gb.find_top_of_page_line_ids(comment_block) == []

def test_find_top_of_page_line_id_one_top_of_page():
    comment_block = Parser.COMMENT_BLOCK(["%----White space may occur between any two tokens. White space is not specified",
                "%----Top of Page---------------------------------------------------------------",
                "%----is compatible with standard Prolog: a <TPTP_file> should be readable with",
                "%----read/1."])
    gb = GraphBuilder.TPTPGraphBuilder()
    assert gb.find_top_of_page_line_ids(comment_block) == [1]

def test_find_top_of_page_line_id_multiple_top_of_page():
    comment_block = Parser.COMMENT_BLOCK(["%----White space may occur between any two tokens. White space is not specified",
                "%----Top of Page---------------------------------------------------------------",
                "%----is compatible with standard Prolog: a <TPTP_file> should be readable with",
                "%----Top of Page---------------------------------------------------------------"])
    gb = GraphBuilder.TPTPGraphBuilder()
    assert gb.find_top_of_page_line_ids(comment_block) == [1,3]

def test_split_comment_block_by_top_of_page_no_top_of_page():
    comment_block = Parser.COMMENT_BLOCK(
        ["%----White space may occur between any two tokens. White space is not specified",
         "%----in the grammar, but there are some restrictions to ensure that the grammar",
         "%----is compatible with standard Prolog: a <TPTP_file> should be readable with",
         "%----read/1."])
    gb = GraphBuilder.TPTPGraphBuilder()
    assert gb.split_comment_block_by_top_of_page(comment_block) == [comment_block]

def test_split_comment_block_by_top_of_page_only_top_of_page():
    comment_block = Parser.COMMENT_BLOCK(["%----Top of Page---------------------------------------------------------------"])
    gb = GraphBuilder.TPTPGraphBuilder()
    expected = []
    result = gb.split_comment_block_by_top_of_page(comment_block)
    assert result == []

def test_split_comment_block_by_top_of_page_one_top_of_page():
    comment_block = Parser.COMMENT_BLOCK(
        ["%----White space may occur between any two tokens. White space is not specified",
         "%----Top of Page---------------------------------------------------------------",
         "%----is compatible with standard Prolog: a <TPTP_file> should be readable with"])
    gb = GraphBuilder.TPTPGraphBuilder()
    expected = [Parser.COMMENT_BLOCK(comment_block.list[0]), Parser.COMMENT_BLOCK(comment_block.list[2])]
    result = gb.split_comment_block_by_top_of_page(comment_block)
    assert len(result) == len(expected)
    for element, exp in zip(result,expected):
        assert element == exp

def test_split_comment_block_by_top_of_page_mulitple_top_of_page():
    comment_block = Parser.COMMENT_BLOCK(
        ["%----White space may occur between any two tokens. White space is not specified",
         "%----Top of Page---------------------------------------------------------------",
         "%----in the grammar, but there are some restrictions to ensure that the grammar",
         "%----Top of Page---------------------------------------------------------------"])
    gb = GraphBuilder.TPTPGraphBuilder()
    expected = [Parser.COMMENT_BLOCK(comment_block.list[0]), Parser.COMMENT_BLOCK(comment_block.list[2])]
    result = gb.split_comment_block_by_top_of_page(comment_block)
    assert len(result) == len(expected)
    for element, exp in zip(result,expected):
        assert element == exp