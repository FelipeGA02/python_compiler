# Compilador BRL — Front-end

> Felipe Gurgel Araujo — D21120

Implementação do **front-end** de um compilador para a linguagem **BRL** (Portuguese-like), desenvolvida em Python puro, sem dependências externas. Cobre as três fases iniciais do pipeline de compilação:

```text
Código-fonte (.LC)
      │
      ▼
┌─────────────────┐
│  Análise Léxica │  AFD manual · produz tokens + tabela de símbolos
└────────┬────────┘
         │ tokens
         ▼
┌──────────────────────┐
│  Análise Sintática   │  Parser LL(1) descendente recursivo · produz AST
└────────┬─────────────┘
         │ AST
         ▼
┌──────────────────────┐
│  Análise Semântica   │  Verificação de tipos, escopos e compatibilidade
└──────────────────────┘
```

---

## Linguagem BRL

A BRL é uma linguagem imperativa de ensino com sintaxe em português.

### Tipos de dados

| Tipo | Exemplos de literais |
| --- | --- |
| `inteiro` | `0`, `42`, `-7` |
| `real` | `3.14`, `0.5`, `-1.0` |
| `logico` | `verdadeiro`, `falso` |
| `caractere` | `"Olá, mundo!"`, `"teste"` |

### Estrutura de um programa

```text
inicio <nome> ;
    <declarações>
    <instruções>
fim
```

### Exemplo completo

```text
inicio exemplo ;

    x , y : inteiro ;
    media : real ;
    msg   : caractere ;

    leia ( x , y ) ;
    media := ( x + y ) / 2 ;

    se media >= 7.0 entao
    inicio
        msg := "Aprovado"
    fim
    senao
    inicio
        msg := "Reprovado"
    fim ;

    escreva ( msg )

fim
```

### Operadores suportados

| Categoria | Operadores |
| --- | --- |
| Aritméticos | `+`  `-`  `*`  `/`  `div`  `mod` |
| Relacionais | `==`  `<>`  `<`  `>`  `<=`  `>=` |
| Lógicos | `&&`  `ou`  `not` |
| Atribuição | `:=` |

> **Promoção implícita:** `inteiro` → `real` em atribuições e expressões mistas.
> **Concatenação:** `caractere + caractere` produz `caractere`.

---

## Requisitos

- Python **3.10+** (sem bibliotecas externas)

---

## Como rodar o front-end

### Compilar um arquivo `.LC`

```bash
python main.py caminho/para/programa.LC
```

### Modo verbose — exibe tokens, AST e variáveis declaradas

```bash
python main.py caminho/para/programa.LC -v
```

### Sem arquivo — roda o programa de demonstração embutido

```bash
python main.py
```

### Exemplos de saída

**Programa aceito:**

```text
OK — programa aceito.
```

**Erro léxico:**

```text
[Erro léxico] linha 6, col 13: caractere inesperado '@'
```

**Erro sintático:**

```text
[Erro sintático] linha 8, col 11: esperado 'entao', encontrado 'inicio'
```

**Erro semântico:**

```text
[Erro semântico] linha 5, col 0: tipo incompatível na atribuição de 'x': variável é 'inteiro', expressão é 'real'
```

### Saída verbose (`-v`)

```text
=== TOKENS ===
  Token(TokenType.INICIO, 'inicio', linha=1)
  Token(TokenType.ID, 'exemplo', linha=1)
  ...

=== AST ===
Programa 'exemplo'
  Decl x, y : inteiro
  Decl media : real
  Atrib media :=
      BinOp '/'
        BinOp '+'
          Var 'x'
          Var 'y'
        Int 2

=== VARIÁVEIS DECLARADAS ===
  x: inteiro
  y: inteiro
  media: real
```

---

## Estrutura do projeto

```text
python_compiler/
├── main.py                        # Ponto de entrada — CLI
├── src/
│   ├── lexer/
│   │   ├── lexer.py               # AFD — tokenizador
│   │   └── token.py               # TokenType, Token, RESERVED_WORDS
│   ├── parser/
│   │   ├── parser.py              # Parser LL(1) descendente recursivo
│   │   └── ast_nodes.py           # Dataclasses dos nós da AST + print_ast()
│   ├── semantic/
│   │   └── semantic_analyzer.py   # Verificação de tipos e escopos
│   └── utils/
│       ├── error.py               # LexicalError, SyntaxError, SemanticError
│       └── symbol_table.py        # Tabela de símbolos
└── tests/
    ├── exemplo.LC                 # Programa de teste completo (todas as construções)
    ├── test_lexer.py              # Smoke test do léxico
    ├── test_parser.py             # Smoke test do parser (imprime AST)
    ├── test_erros.py              # Suite de 31 casos de erro — executa e valida
    └── erros/                     # Arquivos .LC — um por tipo de erro
        ├── lexico_01_char_invalido.LC
        ├── lexico_02_e_comercial_isolado.LC
        ├── lexico_03_igual_isolado.LC
        ├── lexico_04_string_nao_fechada.LC
        ├── lexico_05_comentario_nao_fechado.LC
        ├── sintatico_01_sem_inicio.LC
        ├── sintatico_02_sem_ponto_virgula.LC
        ├── sintatico_03_sem_fim.LC
        ├── sintatico_04_atribuicao_errada.LC
        ├── sintatico_05_sem_entao.LC
        ├── sintatico_06_sem_faca.LC
        ├── sintatico_07_sem_tipo.LC
        ├── sintatico_08_sem_parentese_fechar.LC
        ├── semantico_01_redeclaracao.LC
        ├── semantico_02_var_nao_declarada_expr.LC
        ├── semantico_03_var_nao_declarada_atrib.LC
        ├── semantico_04_var_nao_declarada_leia.LC
        ├── semantico_05_atrib_real_para_inteiro.LC
        ├── semantico_06_atrib_logico_para_inteiro.LC
        ├── semantico_07_atrib_inteiro_para_logico.LC
        ├── semantico_08_atrib_caractere_para_inteiro.LC
        ├── semantico_09_se_condicao_inteiro.LC
        ├── semantico_10_enquanto_condicao_caractere.LC
        ├── semantico_11_not_em_inteiro.LC
        ├── semantico_12_unario_em_logico.LC
        ├── semantico_13_and_com_inteiro.LC
        ├── semantico_14_ou_com_inteiro.LC
        ├── semantico_15_div_com_real.LC
        ├── semantico_16_mod_com_real.LC
        ├── semantico_17_aritmetica_em_logico.LC
        └── semantico_18_comparacao_tipos_incompativeis.LC
```

---

## Rodando os testes

### Smoke test do léxico (imprime tokens do `exemplo.LC`)

```bash
python tests/test_lexer.py
```

### Smoke test do parser (imprime AST do `exemplo.LC`)

```bash
python tests/test_parser.py
```

### Suite de erros — 31 casos, um por tipo de erro

```bash
python tests/test_erros.py
```

Saída esperada:

```text
ARQUIVO                                        STATUS  SAIDA
----------------------------------------------------------------------------------------------------
lexico_01_char_invalido                        [PASS]  OK  [Erro léxico] linha 6, col 13: ...
lexico_02_e_comercial_isolado                  [PASS]  OK  [Erro léxico] linha 8, col 14: ...
...
semantico_18_comparacao_tipos_incompativeis    [PASS]  OK  [Erro semântico]: operador '==' ...
----------------------------------------------------------------------------------------------------

Resultado: 31/31 testes passaram
```

---

## Detalhes de implementação

### Léxico — AFD com 24 estados

O tokenizador é um Autômato Finito Determinístico implementado manualmente.
Estados não-finais (`q0`–`q12`) lêem caracteres; estados finais (`q13`–`q24`)
emitem tokens e retornam a `q0`. Erros léxicos identificados:

| Erro                   | Exemplo                           |
| ---------------------- | --------------------------------- |
| Caractere inválido     | `@`, `#`, `$`                     |
| `&` isolado            | `x & y` (deve ser `&&`)           |
| `=` isolado            | `x = 5` (deve ser `:=` ou `==`)   |
| String não fechada     | `"sem fecha`                      |
| Comentário não fechado | `/* sem fechar`                   |

### Sintático — Parser LL(1) descendente recursivo

Uma função por não-terminal; a tabela LL(1) é representada implicitamente
pelos `if/elif` sobre o token de lookahead. Produz diretamente uma AST
composta por dataclasses (`Program`, `VarDecl`, `Assign`, `If`, `While`,
`Read`, `Write`, `BinOp`, `UnaryOp`, `Var`, `IntConst`, `RealConst`,
`StringConst`, `BoolConst`).

### Semântico — passagem única sobre a AST

Verifica em ordem:

1. Ausência de redeclaração dentro do mesmo escopo
2. Declaração antes do uso em expressões, atribuições e `leia`
3. Compatibilidade de tipos em atribuições (com promoção `inteiro → real`)
4. Condição de `se` e `enquanto` deve ser `logico`
5. Operadores recebem operandos do tipo correto (`not` → `logico`; `div`/`mod` → `inteiro`; etc.)
