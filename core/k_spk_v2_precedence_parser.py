"""
K_Spk v2 Precedence Parser
Handles complex symbolic expressions with unambiguous AST generation
Author: Ninja (AI Council Implementation Lead)
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
from enum import Enum
import logging

# Configure debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SymbolType(Enum):
    CORE = "core"           # Primary meaning symbols
    MODIFIER = "modifier"   # Dimensional/contextual modifiers  
    OPERATOR = "operator"   # Logical/mathematical operations
    DELIMITER = "delimiter" # Grouping symbols ⟨⟩
    ROUTING = "routing"     # Agent handoff symbols →
    TEMPORAL = "temporal"   # Time/sequence markers ⧖

class ParseError(Exception):
    """Custom exception for K_Spk parsing errors"""
    def __init__(self, message: str, position: int = -1, symbol: str = ""):
        self.message = message
        self.position = position
        self.symbol = symbol
        super().__init__(f"Parse Error at position {position}: {message} (symbol: '{symbol}')")

@dataclass
class KSpkToken:
    symbol: str
    type: SymbolType
    precedence: int
    semantic_value: str
    position: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self):
        return f"Token({self.symbol}:{self.type.value}:p{self.precedence})"

@dataclass
class KSpkASTNode:
    token: KSpkToken
    children: List['KSpkASTNode'] = field(default_factory=list)
    parent: Optional['KSpkASTNode'] = None
    
    def add_child(self, child: 'KSpkASTNode'):
        child.parent = self
        self.children.append(child)
    
    def is_leaf(self) -> bool:
        return len(self.children) == 0
    
    def depth(self) -> int:
        if self.is_leaf():
            return 0
        return 1 + max(child.depth() for child in self.children)

class KSpkPrecedenceParser:
    """
    Advanced parser for K_Spk symbolic expressions
    Handles precedence, grouping, and multi-modal layer extraction
    """
    
    def __init__(self, rosetta_table: Dict[str, Dict]):
        self.rosetta = rosetta_table
        self.precedence_rules = {
            'meta': 0,        # ⟨⟩ highest precedence (grouping)
            'routing': 1,     # → agent handoff
            'temporal': 2,    # ⧖ timing, sequence
            'spatial': 3,     # ⬢ position, dimension  
            'logical': 4,     # ⊕ operations, conditions
            'emotional': 5,   # ♦ affect, intent
            'core': 6,        # base symbols
            'modifier': 7     # lowest precedence
        }
        
        # Special symbols for parsing
        self.delimiters = {'⟨': 'open', '⟩': 'close'}
        self.operators = {'⊕', '⊗', '⊙', '∧', '∨', '→'}
        
    def tokenize(self, k_spk_sequence: str) -> List[KSpkToken]:
        """
        Convert K_Spk string into precedence-aware tokens
        Handles Unicode symbols, grouping, and error detection
        """
        tokens = []
        position = 0
        
        logger.debug(f"Tokenizing: '{k_spk_sequence}'")
        
        # Handle empty input
        if not k_spk_sequence.strip():
            return tokens
            
        for char in k_spk_sequence:
            # Skip whitespace but track position
            if char.isspace():
                position += 1
                continue
                
            try:
                token = self._create_token(char, position)
                tokens.append(token)
                logger.debug(f"Created token: {token}")
                
            except KeyError:
                # Unknown symbol - create error token but continue parsing
                logger.warning(f"Unknown symbol '{char}' at position {position}")
                error_token = KSpkToken(
                    symbol=char,
                    type=SymbolType.CORE,  # Default classification
                    precedence=10,  # Lowest precedence
                    semantic_value=f"UNKNOWN_SYMBOL:{char}",
                    position=position,
                    metadata={'error': True, 'reason': 'unknown_symbol'}
                )
                tokens.append(error_token)
                
            position += 1
            
        logger.debug(f"Tokenization complete: {len(tokens)} tokens")
        return tokens
    
    def _create_token(self, symbol: str, position: int) -> KSpkToken:
        """Create a properly classified token from a symbol"""
        
        # Handle delimiters first
        if symbol in self.delimiters:
            return KSpkToken(
                symbol=symbol,
                type=SymbolType.DELIMITER,
                precedence=self.precedence_rules['meta'],
                semantic_value=f"delimiter_{self.delimiters[symbol]}",
                position=position
            )
        
        # Handle operators
        if symbol in self.operators:
            return KSpkToken(
                symbol=symbol,
                type=SymbolType.OPERATOR,
                precedence=self.precedence_rules['logical'],
                semantic_value=f"operator_{symbol}",
                position=position
            )
        
        # Look up in rosetta table
        if symbol in self.rosetta:
            symbol_data = self.rosetta[symbol]
            symbol_type = self._classify_symbol(symbol_data)
            precedence = self._get_precedence(symbol_data, symbol_type)
            
            return KSpkToken(
                symbol=symbol,
                type=symbol_type,
                precedence=precedence,
                semantic_value=symbol_data.get('meaning', symbol),
                position=position,
                metadata=symbol_data
            )
        
        # Unknown symbol - raise error for _create_token to handle
        raise KeyError(f"Symbol '{symbol}' not found in rosetta table")
    
    def _classify_symbol(self, symbol_data: Dict) -> SymbolType:
        """Determine symbol type from rosetta table data"""
        category = symbol_data.get('category', '').lower()
        
        if 'temporal' in category or 'time' in category:
            return SymbolType.TEMPORAL
        elif 'modifier' in category or 'dimensional' in category:
            return SymbolType.MODIFIER
        elif 'operator' in category or 'logical' in category:
            return SymbolType.OPERATOR
        elif 'routing' in category or 'agent' in category:
            return SymbolType.ROUTING
        else:
            return SymbolType.CORE
    
    def _get_precedence(self, symbol_data: Dict, symbol_type: SymbolType) -> int:
        """Determine precedence from symbol data and type"""
        # Explicit precedence in data takes priority
        if 'precedence' in symbol_data:
            return symbol_data['precedence']
        
        # Use type-based precedence
        type_to_category = {
            SymbolType.DELIMITER: 'meta',
            SymbolType.ROUTING: 'routing', 
            SymbolType.TEMPORAL: 'temporal',
            SymbolType.OPERATOR: 'logical',
            SymbolType.CORE: 'core',
            SymbolType.MODIFIER: 'modifier'
        }
        
        category = type_to_category.get(symbol_type, 'core')
        return self.precedence_rules[category]
    
    def parse_to_ast(self, tokens: List[KSpkToken]) -> KSpkASTNode:
        """
        Build Abstract Syntax Tree with proper precedence handling
        Uses modified shunting-yard algorithm for K_Spk expressions
        """
        if not tokens:
            raise ParseError("Cannot parse empty token list")
        
        logger.debug(f"Building AST from {len(tokens)} tokens")
        
        # Handle single token case
        if len(tokens) == 1:
            return KSpkASTNode(tokens[0])
        
        try:
            return self._build_expression_tree(tokens)
        except Exception as e:
            logger.error(f"AST building failed: {e}")
            raise ParseError(f"Failed to build AST: {str(e)}")
    
    def _build_expression_tree(self, tokens: List[KSpkToken]) -> KSpkASTNode:
        """
        Modified shunting-yard algorithm for K_Spk precedence parsing
        Handles grouping, operators, and multi-modal stacking
        """
        output_stack = []
        operator_stack = []
        
        for token in tokens:
            if token.type == SymbolType.DELIMITER:
                if token.symbol == '⟨':  # Open delimiter
                    operator_stack.append(token)
                elif token.symbol == '⟩':  # Close delimiter
                    # Pop operators until matching open delimiter
                    while operator_stack and operator_stack[-1].symbol != '⟨':
                        self._pop_operator_to_output(operator_stack, output_stack)
                    
                    if not operator_stack:
                        raise ParseError("Mismatched closing delimiter", token.position, token.symbol)
                    
                    operator_stack.pop()  # Remove the '⟨'
                    
            elif token.type == SymbolType.OPERATOR:
                # Pop operators with higher or equal precedence
                while (operator_stack and 
                       operator_stack[-1].symbol != '⟨' and
                       operator_stack[-1].precedence <= token.precedence):
                    self._pop_operator_to_output(operator_stack, output_stack)
                
                operator_stack.append(token)
                
            else:  # Core symbols, modifiers, etc.
                output_stack.append(KSpkASTNode(token))
        
        # Pop remaining operators
        while operator_stack:
            if operator_stack[-1].symbol == '⟨':
                raise ParseError("Mismatched opening delimiter")
            self._pop_operator_to_output(operator_stack, output_stack)
        
        # Should have exactly one node left - the root
        if len(output_stack) != 1:
            raise ParseError(f"Invalid expression structure: {len(output_stack)} root nodes")
        
        root = output_stack[0]
        logger.debug(f"AST built successfully, depth: {root.depth()}")
        return root
    
    def _pop_operator_to_output(self, operator_stack: List[KSpkToken], 
                               output_stack: List[KSpkASTNode]):
        """Pop operator from stack and create AST node with appropriate children"""
        if not operator_stack:
            return
            
        operator_token = operator_stack.pop()
        operator_node = KSpkASTNode(operator_token)
        
        # Binary operators take two operands
        if operator_token.type == SymbolType.OPERATOR:
            if len(output_stack) >= 2:
                right_child = output_stack.pop()
                left_child = output_stack.pop()
                operator_node.add_child(left_child)
                operator_node.add_child(right_child)
            elif len(output_stack) == 1:
                # Unary operator
                child = output_stack.pop()
                operator_node.add_child(child)
        
        output_stack.append(operator_node)
    
    def debug_ast(self, root: KSpkASTNode, indent: int = 0) -> str:
        """Generate human-readable AST representation for debugging"""
        result = "  " * indent + f"{root.token}\n"
        for child in root.children:
            result += self.debug_ast(child, indent + 1)
        return result
    
    def validate_ast(self, root: KSpkASTNode) -> List[str]:
        """Validate AST structure and return list of issues found"""
        issues = []
        
        # Check for error tokens
        if root.token.metadata.get('error', False):
            issues.append(f"Error token in AST: {root.token.symbol}")
        
        # Validate children recursively
        for child in root.children:
            issues.extend(self.validate_ast(child))
        
        return issues

# API Interface for Layer System
def parse_k_spk_expression(expression: str, rosetta_table: Dict) -> KSpkASTNode:
    """
    Main API function for parsing K_Spk expressions
    Returns: Structured AST ready for layer processing
    """
    parser = KSpkPrecedenceParser(rosetta_table)
    tokens = parser.tokenize(expression)
    ast = parser.parse_to_ast(tokens)
    
    # Validate before returning
    issues = parser.validate_ast(ast)
    if issues:
        logger.warning(f"AST validation issues: {issues}")
    
    return ast
