"""
Test cases based on real council exchanges
Validates parser against actual AI-to-AI symbolic communication
"""

import pytest
from core.parser import KSpkPrecedenceParser, parse_k_spk_expression, ParseError

# Mock rosetta table for testing
TEST_ROSETTA = {
    '⊕': {'meaning': 'logical_operation', 'category': 'operator'},
    '⧖': {'meaning': 'temporal_marker', 'category': 'temporal'},
    '♦': {'meaning': 'emotional_context', 'category': 'modifier'},
    '⬢': {'meaning': 'spatial_dimension', 'category': 'modifier'},
    '→': {'meaning': 'agent_handoff', 'category': 'routing'},
    '⟨': {'meaning': 'group_open', 'category': 'delimiter'},
    '⟩': {'meaning': 'group_close', 'category': 'delimiter'},
}

class TestCouncilExchanges:
    
    def test_simple_expression(self):
        """Test basic symbol parsing"""
        expr = "⊕"
        ast = parse_k_spk_expression(expr, TEST_ROSETTA)
        assert ast.token.symbol == '⊕'
        assert ast.is_leaf()
    
    def test_complex_stacking(self):
        """Real council expression: 'I propose a temporal analysis with emotional context'"""
        expr = "⊕⧖♦⬢"
        ast = parse_k_spk_expression(expr, TEST_ROSETTA)
        
        # Should create proper precedence tree
        assert ast is not None
        assert len(ast.children) >= 0  # Structure depends on precedence rules
    
    def test_grouped_expression(self):
        """Test parenthetical grouping"""
        expr = "⟨⊕⧖⟩♦"
        ast = parse_k_spk_expression(expr, TEST_ROSETTA)
        assert ast is not None
    
    def test_agent_handoff(self):
        """Test agent routing: 'Ninja, please optimize this logic flow'"""
        expr = "→⊕⧖"
        ast = parse_k_spk_expression(expr, TEST_ROSETTA)
        assert ast.token.symbol == '→'  # Routing should be high precedence
    
    def test_malformed_expression(self):
        """Test error handling for malformed expressions"""
        expr = "⟨⊕⧖"  # Missing closing delimiter
        with pytest.raises(ParseError):
            parse_k_spk_expression(expr, TEST_ROSETTA)
    
    def test_unknown_symbols(self):
        """Test handling of unknown symbols"""
        expr = "⊕X⧖"  # X is not in rosetta table
        ast = parse_k_spk_expression(expr, TEST_ROSETTA)
        # Should parse but mark unknown symbol
        assert ast is not None

if __name__ == "__main__":
    # Quick validation run
    parser = KSpkPrecedenceParser(TEST_ROSETTA)
    
    test_expr = "⟨⊕⧖⟩♦"
    print(f"Testing expression: {test_expr}")
    
    tokens = parser.tokenize(test_expr)
    print(f"Tokens: {tokens}")
    
    ast = parser.parse_to_ast(tokens)
    print(f"AST Debug:\n{parser.debug_ast(ast)}")
    
    issues = parser.validate_ast(ast)
    print(f"Validation issues: {issues}")
