# CONTEXT_RULES

## 3. GOVERNANÇA DE CONTEXTO E REGRAS PARA AGENTES DE IA (CONTEXT_RULES)
Esta seção atua como um conjunto restritivo de regras de contexto. Qualquer agente de Inteligência Artificial (LLM) encarregado de gerar, refatorar ou testar o código da Fase 2 deste projeto deverá obedecer incondicionalmente às diretrizes e proibições detalhadas abaixo.

### 3.1 Diretrizes de Desenvolvimento (Obrigações)
Para garantir a qualidade, manutenibilidade e padronização do código gerado, as seguintes regras arquiteturais devem ser aplicadas:

1. **Linguagem e Versão:** O código-fonte deve ser implementado estritamente na linguagem **Python 3.11** ou superior.
2. **Tipagem Estática Explicita:** É obrigatório o uso de **Type Hints** em todas as assinaturas de funções, métodos e variáveis de retorno (ex: `list`, `dict`, `float`), garantindo a validação de tipos na entrada e saída dos dados.
3. **Documentação de Código:** Todas as funções e eventuais classes geradas devem conter **Docstrings** claras e detalhadas (preferencialmente no padrão Google ou Sphinx), documentando o propósito da função, os parâmetros esperados, o tipo de retorno e as possíveis exceções que podem ser levantadas (`Raises`).
4. **Princípio da Responsabilidade Única (SRP):** A arquitetura do código deve ser modular e limpa. A lógica de cálculo deve ser desmembrada em métodos menores e isolados (ex: uma função exclusiva para validar datas, outra exclusiva para calcular atrasos), evitando a criação de scripts monolíticos.
5. **Funções Pequenas e Coesas:** As funções deverão ser pequenas, coesas e possuir um único propósito, evitando funções excessivamente complexas ou monolíticas.
6. **Tratamento de Exceções:** O código deverá utilizar exceções específicas e apresentar mensagens de erro claras e informativas para situações de inconsistência ou falha previstas no contrato.
7. **Logging:** O código deverá utilizar o módulo padrão `logging` para registrar eventos relevantes, erros e anomalias de forma estruturada.
8. **Legibilidade e Manutenibilidade (PEP 8):** O código deverá seguir as boas práticas de legibilidade e manutenibilidade, utilizando nomes descritivos para variáveis, funções, métodos e demais elementos, além de respeitar as convenções estabelecidas pela PEP 8.

---

### 3.2 Restrições e Proibições (Negative Prompts / Anti-Patterns)
Para evitar que a IA produza código fora do escopo ou que viole as regras de negócio do edital, aplicam-se as seguintes proibições absolutas na geração do código:

1. **PROIBIDO o uso de bibliotecas externas (Third-party libraries):** O uso de bibliotecas de análise de dados como `pandas`, `numpy` ou qualquer pacote que necessite de instalação via `pip` é estritamente bloqueado. O processamento deve ser feito utilizando exclusivamente algoritmos criados com as estruturas de dados nativas do Python e módulos da sua biblioteca padrão (como `datetime`). *Observação: A restrição ao uso de bibliotecas externas aplica-se ao módulo `task_analyzer.py` e ao código funcional gerado pela IA. O uso do framework `pytest` é permitido exclusivamente no `test_harness.py`, conforme definido no planejamento de testes.*
2. **PROIBIDA a persistência de dados:** A aplicação deve operar 100% em memória. É proibida a geração de rotinas para leitura, gravação ou exportação de arquivos físicos (CSV, JSON, Excel, TXT), bem como qualquer tentativa de conexão com bancos de dados relacionais ou NoSQL.
3. **PROIBIDA a criação de Interfaces de Usuário (UI/CLI):** O módulo `TaskAnalyzer` atua como um motor de backend. Não devem ser criados menus interativos no terminal (uso de comandos `input()` ou `print()` soltos), nem interfaces gráficas ou rotas web (como Flask ou FastAPI).
4. **PROIBIDA a "alucinação" de requisitos:** O assistente de IA não deve criar, sugerir ou implementar métricas adicionais (ex: "produtividade por responsável", "estimativa de tempo futuro") que não estejam explicitamente declaradas na Seção 1.3 (Saídas) deste documento. O escopo é fechado.
5. **PROIBIDO alterar, remover ou adaptar os cenários de teste fornecidos:** O assistente de IA não deve modificar, remover ou adaptar os cenários de teste definidos nesta especificação. Os testes fornecidos devem ser preservados integralmente.
6. **PROIBIDO modificar a estrutura de pastas definida nesta especificação:** O assistente de IA não deve alterar, remover ou criar pastas e arquivos fora da estrutura de repositório definida na Seção 4 deste documento.
7. **PROIBIDO alterar a assinatura das funções públicas sem autorização:** O assistente de IA não deve modificar o nome, os parâmetros ou a estrutura das funções públicas definidas no contrato de negócio sem autorização explícita.
8. **PROIBIDO gerar código duplicado sem necessidade:** O assistente de IA não deve inserir código ou lógica duplicada quando uma implementação existente puder ser reutilizada de forma adequada.
9. **PROIBIDO assumir comportamentos não especificados no contrato de negócio:** O assistente de IA não deve criar, inferir ou implementar comportamentos que não estejam explicitamente definidos nesta especificação.
10. **PROIBIDO gerar código sem testes correspondentes:** O assistente de IA não deve gerar novas funcionalidades ou alterações de comportamento sem que existam testes automatizados correspondentes para sua validação.

---
