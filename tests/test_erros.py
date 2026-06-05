import sys
import os
import subprocess

BASE = os.path.dirname(os.path.dirname(__file__))

# prefixo_esperado usa apenas ASCII para comparacao robusta no Windows
CASOS = [
    # (arquivo,                                     prefixo_esperado,  descricao)
    # -- Lexicos ------------------------------------------------------------------
    ("lexico_01_char_invalido",             "Erro l",   "caractere inesperado '@'"),
    ("lexico_02_e_comercial_isolado",       "Erro l",   "'&' isolado invalido"),
    ("lexico_03_igual_isolado",             "Erro l",   "'=' isolado invalido"),
    ("lexico_04_string_nao_fechada",        "Erro l",   "string nao fechada"),
    ("lexico_05_comentario_nao_fechado",    "Erro l",   "comentario nao fechado"),
    # -- Sintaticos ---------------------------------------------------------------
    ("sintatico_01_sem_inicio",             "Erro sint", "falta 'inicio'"),
    ("sintatico_02_sem_ponto_virgula",      "Erro sint", "falta ';' apos nome"),
    ("sintatico_03_sem_fim",                "Erro sint", "falta 'fim' no final"),
    ("sintatico_04_atribuicao_errada",      "Erro sint", "falta ':='"),
    ("sintatico_05_sem_entao",              "Erro sint", "falta 'entao'"),
    ("sintatico_06_sem_faca",               "Erro sint", "falta 'faca'"),
    ("sintatico_07_sem_tipo",               "Erro sint", "falta tipo na declaracao"),
    ("sintatico_08_sem_parentese_fechar",   "Erro sint", "falta ')'"),
    # -- Semanticos ---------------------------------------------------------------
    ("semantico_01_redeclaracao",                       "Erro sem", "variavel redeclarada"),
    ("semantico_02_var_nao_declarada_expr",             "Erro sem", "var nao declarada em expressao"),
    ("semantico_03_var_nao_declarada_atrib",            "Erro sem", "var nao declarada em atribuicao"),
    ("semantico_04_var_nao_declarada_leia",             "Erro sem", "var nao declarada em leia"),
    ("semantico_05_atrib_real_para_inteiro",            "Erro sem", "inteiro := real"),
    ("semantico_06_atrib_logico_para_inteiro",          "Erro sem", "inteiro := logico"),
    ("semantico_07_atrib_inteiro_para_logico",          "Erro sem", "logico := inteiro"),
    ("semantico_08_atrib_caractere_para_inteiro",       "Erro sem", "inteiro := caractere"),
    ("semantico_09_se_condicao_inteiro",                "Erro sem", "condicao 'se' nao e logico"),
    ("semantico_10_enquanto_condicao_caractere",        "Erro sem", "condicao 'enquanto' nao e logico"),
    ("semantico_11_not_em_inteiro",                     "Erro sem", "not em inteiro"),
    ("semantico_12_unario_em_logico",                   "Erro sem", "unario '-' em logico"),
    ("semantico_13_and_com_inteiro",                    "Erro sem", "'&&' com inteiro"),
    ("semantico_14_ou_com_inteiro",                     "Erro sem", "'ou' com real"),
    ("semantico_15_div_com_real",                       "Erro sem", "'div' com real"),
    ("semantico_16_mod_com_real",                       "Erro sem", "'mod' com real"),
    ("semantico_17_aritmetica_em_logico",               "Erro sem", "'+' entre logicos"),
    ("semantico_18_comparacao_tipos_incompativeis",     "Erro sem", "'==' inteiro vs logico"),
]

PASS = "PASS"
FAIL = "FAIL"

def run(nome):
    path = os.path.join(BASE, "tests", "erros", nome + ".LC")
    result = subprocess.run(
        [sys.executable, os.path.join(BASE, "main.py"), path],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return (result.stdout + result.stderr).strip()

def main():
    largura_nome = max(len(n) for n, _, _ in CASOS) + 2
    total = len(CASOS)
    passou = 0

    print(f"{'ARQUIVO':<{largura_nome}}  {'STATUS'}  SAIDA")
    print("-" * 100)

    for nome, prefixo, descricao in CASOS:
        saida = run(nome)
        ok = prefixo.lower() in saida.lower()
        status = PASS if ok else FAIL
        if ok:
            passou += 1
        icone = "OK" if ok else "XX"
        saida_ascii = saida.encode("ascii", errors="replace").decode("ascii")
        print(f"{nome:<{largura_nome}}  [{status}]  {icone}  {saida_ascii}")

    print("-" * 100)
    print(f"\nResultado: {passou}/{total} testes passaram")
    if passou < total:
        sys.exit(1)

if __name__ == "__main__":
    main()
