import yaml
from core.k_spk_v2_precedence_parser import parse_k_spk_expression
from core.k_spk_layers import LayerCompositor

# 1. Load the Rosetta Table
with open("core/K_Spk Rosetta Table V2.yaml", "r", encoding="utf-8") as f:
    rosetta = yaml.safe_load(f)

# 2. Choose a K_Spk test expression (edit this to play)
expression = "⊕⧖♦⬢⟨analysis⟩"
print("\nK_Spk Test Expression:", expression)

# 3. Parse it into an AST
ast = parse_k_spk_expression(expression, rosetta)
print("\n--- Abstract Syntax Tree ---")
print(ast)

# 4. Token list (for layers, if needed)
def flatten_ast_tokens(node):
    tokens = [node.token]
    for child in getattr(node, 'children', []):
        tokens.extend(flatten_ast_tokens(child))
    return tokens

tokens = flatten_ast_tokens(ast)
print("\n--- Token List ---")
for t in tokens:
    print(t)

# 5. Process through the multi-modal layer system
compositor = LayerCompositor()
# NOTE: LayerCompositor expects a list of tokens
multi_modal_message = compositor.compose_message(tokens)
print("\n--- Multi-Modal Message (All Layers) ---")
print(multi_modal_message)

# 6. Print sample layer outputs (if implemented)
if hasattr(multi_modal_message, 'semantic_content'):
    print("\nSemantic Content:", multi_modal_message.semantic_content)
if hasattr(multi_modal_message, 'temporal_structure'):
    print("Temporal Structure:", multi_modal_message.temporal_structure)

print("\n[Demo complete! If you see outputs above, your K_Spk v2 system is working!]")
