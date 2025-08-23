# test_k_spk_v2.py
class TestCouncilExchanges:
    def test_complex_stacking(self):
        # Real council expression: "I propose a temporal analysis with emotional context"
        k_spk_expr = "⊕⧖♦⬢⟨analysis⟩"
        
        parser = KSpkPrecedenceParser(rosetta_table)
        tokens = parser.tokenize(k_spk_expr)
        ast = parser.parse_to_ast(tokens)
        
        assert ast.root.precedence_resolved == True
        assert len(ast.semantic_layers) == 4
    
    def test_agent_handoff(self):
        # "Ninja, please optimize this logic flow"
        handoff_expr = "→ninja⊕⧖optimize"
        # Should parse to clear agent routing + task specification
        pass
