# Especificação de Software e Contrato de Negócio (SDD) - TaskAnalyzer

## 1. VISÃO GERAL E CONTRATO DE NEGÓCIO (SDD)

### 1.1 Identificação


---

### 1.2 Propósito do Módulo TaskAnalyzer
O módulo **TaskAnalyzer** tem como objetivo central atuar como um motor de análise de dados operacionais, processando registros de tarefas executadas para gerar métricas de produtividade e eficiência. O sistema atua exclusivamente na avaliação do ciclo de vida das atividades, fornecendo métricas exatas para a tomada de decisão e melhoria contínua.

O escopo do sistema abrange o cálculo automatizado dos seguintes indicadores analíticos:
* **Tempo Médio de Conclusão:** Cálculo do tempo transcorrido entre a criação e a finalização das atividades, avaliando o desempenho no cenário global e também segmentado por prioridades.
* **Taxa de Atraso:** Apuração rigorosa da proporção de tarefas que foram concluídas após o prazo estipulado em relação ao total de tarefas finalizadas.
* **Indicadores por Prioridade:** Geração de dados quantitativos e de desempenho focados especificamente nos níveis de prioridade da tarefa (Baixa, Média e Alta).

---

### 1.3 CONTRATO EXECUTÁVEL DE INTERFACE

#### 1.3.1 Entradas (Inputs)
A função principal do módulo deverá receber uma lista de objetos da classe `Task`, contendo estritamente os seguintes campos:

| Campo | Tipo de Dado (Python) | Regras e Valores Permitidos |
| :--- | :--- | :--- |
| `id` | `str` | Identificador único da tarefa. Não pode ser nulo. |
| `titulo` | `str` | Nome/descrição da tarefa. |
| `prioridade` | `str` | Estritamente os valores: `"Baixa"`, `"Média"`, `"Alta"`. |
| `status` | `str` | Estritamente os valores: `"Pendente"`, `"Concluída"`. |
| `data_criacao` | `datetime` | Data e hora em que a tarefa foi registrada. Obrigatória para tarefas concluídas. |
| `data_limite` | `datetime` | Prazo máximo estipulado para entrega. Obrigatória para tarefas concluídas. |
| `data_conclusao` | `datetime` | Data e hora em que a tarefa foi finalizada. Deve ser `None` para tarefas pendentes e é obrigatória para tarefas concluídas. |

#### 1.3.2 Saídas (Outputs)
O analisador deverá retornar um dicionário estruturado (ou objeto de métricas) contendo exatamente as chaves abaixo:

| Campo de Saída | Tipo de Dado | Descrição do Retorno |
| :--- | :--- | :--- |
| `total_tarefas_concluidas` | `int` | Quantidade absoluta de tarefas avaliadas no escopo (`status="Concluída"`). |
| `tempo_medio_conclusao_geral` | `float` | Tempo médio geral (em horas) transcorrido entre `data_criacao` e `data_conclusao`. |
| `taxa_atraso_geral` | `float` | Percentual (de $0.0$ a $100.0$) de tarefas concluídas após a `data_limite`. |
| `indicadores_por_prioridade` | `dict` | Dicionário contendo as métricas de tarefas concluídas separadas pelas três chaves fixas `"Baixa"`, `"Média"` e `"Alta"`. |

#### 1.3.3 Regras de Negócio e Restrições
Para garantir a confiabilidade dos dados e prevenir falhas de execução, a implementação deverá obrigatoriamente respeitar as seguintes regras:

1. **Filtro de Processamento:** O cálculo das métricas deve considerar apenas tarefas concluídas (`status == "Concluída"`). Tarefas pendentes (`status == "Pendente"`) devem ser completamente ignoradas na geração das médias e taxas de atraso. Para tarefas pendentes, a ausência de `data_conclusao` é considerada um comportamento normal e não deve gerar exceção.
2. **Consistência de Datas:** Para toda tarefa concluída, o sistema deve validar se `data_conclusao` é igual ou posterior a `data_criacao`. Caso `data_conclusao` seja anterior a `data_criacao`, o sistema deve levantar a exceção customizada `DataInconsistenteError`.
3. **Cálculo de Atraso:** Uma tarefa concluída é contabilizada como "atrasada" exclusivamente se `data_conclusao` for estritamente maior que `data_limite`. Caso `data_conclusao` seja igual a `data_limite`, a tarefa não será considerada atrasada.
4. **Prevenção de Exceções Matemáticas:** É terminantemente proibida a ocorrência de `ZeroDivisionError`. Caso não existam tarefas concluídas, o sistema deve retornar $0.0$ para `tempo_medio_conclusao_geral` e `taxa_atraso_geral`. Da mesma forma, quando não houver tarefas concluídas de determinada prioridade, `tempo_medio_conclusao` e `taxa_atraso` daquela prioridade devem ser $0.0$.

#### 1.3.4 Unidade de Medida de Tempo
Para garantir consistência matemática e evitar ambiguidades na geração automatizada de código, fica estabelecido que:
* Todas as métricas de tempo (`tempo_medio_conclusao_geral` e `tempo_medio_conclusao` dentro de `indicadores_por_prioridade`) serão expressas exclusivamente em horas, com representação do tipo `float`.
* O cálculo deve ser feito com base na diferença entre `data_conclusao` e `data_criacao`, convertida para horas por meio da seguinte fórmula canônica:

```python
delta = data_conclusao - data_criacao
tempo_em_horas = delta.total_seconds() / 3600.0
```

Não é permitido arredondar os valores internamente. O arredondamento, se necessário para exibição, é responsabilidade da camada consumidora.

#### 1.3.5 Exceção Customizada para Inconsistência de Dados
Para padronizar o tratamento de erros e permitir asserções precisas nos testes automatizados, o módulo deverá definir uma exceção customizada:

```python
class DataInconsistenteError(ValueError):
    """Exceção levantada quando uma tarefa apresenta inconsistência
    cronológica entre data_criacao e data_conclusao, ou quando
    o status é 'Concluída' mas a data_conclusao está ausente."""
```

**Regras de disparo:**

| Situação Detectada | Exceção Disparada |
| :--- | :--- |
| `data_conclusao` anterior a `data_criacao` | `DataInconsistenteError` |
| `status == "Concluída"` e `data_conclusao is None` | `DataInconsistenteError` |

**Formato obrigatório da mensagem de erro:**
> `"Tarefa ID {id} apresenta inconsistência: {descrição_do_problema}."`

*Exemplo de mensagem:*
> `"Tarefa ID 99 apresenta inconsistência: data_conclusao (2024-01-09T10:00:00) é anterior à data_criacao (2024-01-10T10:00:00)."`

#### 1.3.6 Estrutura Detalhada de indicadores_por_prioridade
Para eliminar qualquer ambiguidade na saída, a chave `indicadores_por_prioridade` deve seguir exatamente a estrutura abaixo, com as três chaves fixas `"Baixa"`, `"Média"` e `"Alta"` sempre presentes, mesmo quando não houver tarefas concluídas daquela prioridade:

```json
"indicadores_por_prioridade": {
    "Baixa": {
        "total_tarefas_concluidas": int,
        "tempo_medio_conclusao": float,
        "taxa_atraso": float
    },
    "Média": {
        "total_tarefas_concluidas": int,
        "tempo_medio_conclusao": float,
        "taxa_atraso": float
    },
    "Alta": {
        "total_tarefas_concluidas": int,
        "tempo_medio_conclusao": float,
        "taxa_atraso": float
    }
}
```

**Regras associadas:**
* As três chaves (`"Baixa"`, `"Média"` e `"Alta"`) devem sempre existir no dicionário de retorno, independentemente da presença de tarefas concluídas daquela prioridade.
* Quando não houver tarefas concluídas de uma determinada prioridade, `total_tarefas_concluidas` deve ser `0`, `tempo_medio_conclusao` deve ser `0.0` e `taxa_atraso` deve ser `0.0`.
* Nenhuma outra chave deve ser adicionada ao dicionário de `indicadores_por_prioridade`, mantendo a estrutura de saída fechada definida na Seção 1.3.2.

#### 1.3.7 Tratamento de Dados Faltantes
Para garantir a integridade dos cálculos, ficam estabelecidas as seguintes regras de validação:

| Campo | Condição | Ação do Sistema |
| :--- | :--- | :--- |
| `data_conclusao` | `None` e `status == "Concluída"` | Levantar `DataInconsistenteError` |
| `data_conclusao` | `None` e `status == "Pendente"` | Ignorar a tarefa |
| `data_criacao` | `None` e `status == "Concluída"` | Levantar `ValueError` |
| `data_limite` | `None` e `status == "Concluída"` | Levantar `ValueError` |
| `prioridade` | Valor fora de `{"Baixa", "Média", "Alta"}` | Levantar `ValueError` |
| `status` | Valor fora de `{"Pendente", "Concluída"}` | Levantar `ValueError` |

*As validações de `data_criacao`, `data_limite` e `data_conclusao` são aplicáveis às tarefas concluídas, pois somente essas tarefas participam dos cálculos das métricas.*
*Tarefas pendentes devem ser ignoradas para fins de cálculo e não devem gerar exceção pela ausência de `data_conclusao`.*

#### 1.3.8 Padrão de Logging
O módulo deverá utilizar exclusivamente o módulo padrão `logging` da biblioteca Python para registro de eventos relevantes, sem configurar o sistema global de logging.

O logger deverá ser obtido da seguinte forma:
```python
import logging

logger = logging.getLogger(__name__)
```

**Níveis e eventos obrigatórios:**

| Nível | Evento | Exemplo de Mensagem |
| :--- | :--- | :--- |
| `INFO` | Início do processamento | `"Iniciando análise de {n} tarefas."` |
| `INFO` | Conclusão do processamento | `"Análise concluída. Total de tarefas concluídas: {n}."` |
| `WARNING` | Tarefa ignorada por estar pendente | `"Tarefa ID {id} ignorada (status=Pendente)."` |
| `WARNING` | Prioridade sem tarefas concluídas | `"Nenhuma tarefa concluída com prioridade {prioridade}."` |
| `ERROR` | Inconsistência de datas | `"Tarefa ID {id} com data_conclusao anterior à data_criacao."` |
| `ERROR` | Campo obrigatório ausente | `"Tarefa ID {id} sem campo obrigatório: {campo}."` |

**Restrições:**
* É proibido o uso de `print()` para qualquer finalidade de diagnóstico.
* É proibido o uso de `basicConfig()` dentro do módulo. A configuração do logging deve ser responsabilidade da camada chamadora.
* O módulo não deve criar handlers destinados à persistência dos logs em arquivos.
* O uso de `logging` deve limitar-se ao registro de eventos relevantes ao processamento e tratamento de erros.

#### 1.3.9 Assinatura Pública Consolidada
Para garantir estabilidade do contrato e evitar alterações indevidas pela IA, fica fixada a assinatura pública da função principal do módulo:

```python
def analisar_tarefas(tarefas: list[Task]) -> dict:
    """Analisa uma lista de tarefas e retorna métricas de produtividade.

    Args:
        tarefas: Lista de objetos Task representando as tarefas,
            contendo os atributos: id, titulo, prioridade, status,
            data_criacao, data_limite e data_conclusao.

    Returns:
        Dicionário com as chaves:
            - total_tarefas_concluidas (int)
            - tempo_medio_conclusao_geral (float, em horas)
            - taxa_atraso_geral (float, de 0.0 a 100.0)
            - indicadores_por_prioridade (dict com chaves "Baixa", "Média", "Alta")

    Raises:
        DataInconsistenteError: Se houver inconsistência cronológica
            entre data_criacao e data_conclusao, ou se o status for
            "Concluída" sem data_conclusao preenchida.
        ValueError: Se houver campos obrigatórios ausentes ou valores
            inválidos em prioridade ou status.
    """
```

*A assinatura pública de `analisar_tarefas` não deve ser alterada sem autorização formal documentada.*

#### 1.3.10 Subfunções Internas Sugeridas (Arquitetura SRP)
Para respeitar o Princípio da Responsabilidade Única (SRP) e manter o código coeso e testável, a implementação deve ser modularizada nas seguintes funções auxiliares privadas:

| Função | Responsabilidade |
| :--- | :--- |
| `_validar_tarefa(tarefa: Task) -> None` | Validar os campos, tipos, valores permitidos e consistência cronológica da tarefa. |
| `_filtrar_concluidas(tarefas: list[Task]) -> list[Task]` | Retornar apenas as tarefas com `status == "Concluída"`. |
| `_calcular_tempo_conclusao(tarefa: Task) -> float` | Retornar o tempo, em horas, entre `data_criacao` e `data_conclusao`. |
| `_calcular_atraso(tarefa: Task) -> bool` | Retornar `True` se `data_conclusao > data_limite`; caso contrário, retornar `False`. |
| `_calcular_indicadores(tarefas: list[Task]) -> dict` | Calcular as métricas para um subconjunto de tarefas concluídas. |
| `_inicializar_indicadores_vazios() -> dict` | Retornar o dicionário padrão contendo as três prioridades e seus respectivos valores zerados. |

As funções auxiliares são internas ao módulo e não constituem parte da interface pública. Seus nomes e assinaturas podem ser ajustados durante a implementação apenas quando necessário para atender ao contrato definido nesta especificação, sem alterar a assinatura pública de `analisar_tarefas`.

A modularização tem como objetivo facilitar a realização de testes unitários isolados, manter cada função com uma responsabilidade bem definida e reduzir o risco de geração de código monolítico pela IA.

---

#### 1.3.11 Exemplos Concretos de Entrada e Saída

##### Exemplo 1: Cenário de sucesso com cálculo detalhado (média geral = $50.5\text{ h}$, taxa de atraso = $50.0\%$).

**Entrada (Input):**
```python
tarefas = [
    {
        "id": 1,
        "titulo": "Implementar tela de login",
        "prioridade": "Alta",
        "status": "Concluida",
        "data_criacao": datetime(2024, 1, 1, 8, 0, 0),
        "data_limite": datetime(2024, 1, 2, 18, 0, 0),
        "data_conclusao": datetime(2024, 1, 2, 12, 0, 0)
    },
    {
        "id": 2,
        "titulo": "Corrigir bug do relatório financeiro",
        "prioridade": "Média",
        "status": "Concluida",
        "data_criacao": datetime(2024, 1, 1, 10, 0, 0),
        "data_limite": datetime(2024, 1, 3, 10, 0, 0),
        "data_conclusao": datetime(2024, 1, 4, 10, 0, 0)
    },
    {
        "id": 3,
        "titulo": "Atualizar documentação da API",
        "prioridade": "Baixa",
        "status": "Concluida",
        "data_criacao": datetime(2024, 1, 2, 14, 0, 0),
        "data_limite": datetime(2024, 1, 5, 14, 0, 0),
        "data_conclusao": datetime(2024, 1, 4, 14, 0, 0)
    },
    {
        "id": 4,
        "titulo": "Refatorar módulo de pagamentos",
        "prioridade": "Alta",
        "status": "Concluida",
        "data_criacao": datetime(2024, 1, 3, 9, 0, 0),
        "data_limite": datetime(2024, 1, 5, 9, 0, 0),
        "data_conclusao": datetime(2024, 1, 5, 15, 0, 0)
    },
    {
        "id": 5,
        "titulo": "Criar testes de integração",
        "prioridade": "Média",
        "status": "Pendente",
        "data_criacao": datetime(2024, 1, 4, 8, 0, 0),
        "data_limite": datetime(2024, 1, 10, 18, 0, 0),
        "data_conclusao": None
    },
    {
        "id": 6,
        "titulo": "Revisar Pull Requests abertos",
        "prioridade": "Baixa",
        "status": "Pendente",
        "data_criacao": datetime(2024, 1, 5, 11, 0, 0),
        "data_limite": datetime(2024, 1, 8, 11, 0, 0),
        "data_conclusao": None
    }
]
```

**Memória de Cálculo (para validação manual):**
Tarefas concluídas consideradas: IDs 1, 2, 3 e 4 (IDs 5 e 6 são ignoradas por serem `"Pendente"`).

| ID | Prioridade | Tempo de Conclusão (h) | Dentro do Prazo? |
| :--- | :--- | :--- | :--- |
| 1 | Alta | $28\text{ h}$ | Sim |
| 2 | Média | $72\text{ h}$ | Não (atrasada) |
| 3 | Baixa | $48\text{ h}$ | Sim |
| 4 | Alta | $54\text{ h}$ | Não (atrasada) |

* **Tempo médio geral:** $$\frac{28 + 72 + 48 + 54}{4} = \frac{202}{4} = 50.5\text{ h}$$
* **Taxa de atraso geral:** $$\left(\frac{2\text{ tarefas atrasadas}}{4\text{ concluídas}}\right) \times 100 = 50.0\%$$

**Por prioridade:**

| Prioridade | Qtd | Tempo Médio | Taxa de Atraso |
| :--- | :--- | :--- | :--- |
| **Alta** | 2 | $$\frac{28 + 54}{2} = 41.0\text{ h}$$ | $$\left(\frac{1}{2}\right) \times 100 = 50.0\%$$ |
| **Média** | 1 | $72.0\text{ h}$ | $$\left(\frac{1}{1}\right) \times 100 = 100.0\%$$ |
| **Baixa** | 1 | $48.0\text{ h}$ | $$\left(\frac{0}{1}\right) \times 100 = 0.0\%$$ |

**Saída Esperada (Output):**
```json
{
    "total_tarefas_concluidas": 4,
    "tempo_medio_conclusao_geral": 50.5,
    "taxa_atraso_geral": 50.0,
    "indicadores_por_prioridade": {
        "Baixa": {
            "total_tarefas_concluidas": 1,
            "tempo_medio_conclusao": 48.0,
            "taxa_atraso": 0.0
        },
        "Média": {
            "total_tarefas_concluidas": 1,
            "tempo_medio_conclusao": 72.0,
            "taxa_atraso": 100.0
        },
        "Alta": {
            "total_tarefas_concluidas": 2,
            "tempo_medio_conclusao": 41.0,
            "taxa_atraso": 50.0
        }
    }
}
```
*Nota: O tempo é expresso em horas (float). Tarefas com `status="Pendente"` são completamente ignoradas em todos os cálculos.*

---

##### Exemplo 2: Cenário de exceção por inconsistência de datas (lança `DataInconsistenteError`).

**Entrada (Input):**
```python
tarefas_com_data_invalida = [
    {
        "id": 99,
        "titulo": "Tarefa com data de conclusão anterior à criação",
        "prioridade": "Alta",
        "status": "Concluida",
        "data_criacao": datetime(2024, 1, 10, 10, 0, 0),
        "data_limite": datetime(2024, 1, 12, 10, 0, 0),
        "data_conclusao": datetime(2024, 1, 9, 10, 0, 0)
    }
]
```

**Comportamento Esperado:**
O sistema deve interromper o processamento e levantar uma exceção específica:
`DataInconsistenteError`: `"Tarefa ID 99 apresenta inconsistência: data_conclusao (2024-01-09 10:00:00) é anterior à data_criacao (2024-01-10 10:00:00)."`

*Recomendação: Criar a exceção customizada `DataInconsistenteError(ValueError)` herdando de `ValueError`, permitindo que o teste use `pytest.raises(DataInconsistenteError)`.*

---

##### Exemplo 3: Cenário de zero tarefas concluídas (retorna $0.0$, sem `ZeroDivisionError`).

**Entrada (Input) - Opção A: Lista Vazia**
```python
tarefas = []
```

**Entrada (Input) - Opção B: Lista apenas com Pendentes**
```python
tarefas = [
    {
        "id": 10,
        "titulo": "Tarefa pendente A",
        "prioridade": "Alta",
        "status": "Pendente",
        "data_criacao": datetime(2024, 1, 1, 8, 0, 0),
        "data_limite": datetime(2024, 1, 5, 18, 0, 0),
        "data_conclusao": None
    },
    {
        "id": 11,
        "titulo": "Tarefa pendente B",
        "prioridade": "Baixa",
        "status": "Pendente",
        "data_criacao": datetime(2024, 1, 2, 8, 0, 0),
        "data_limite": datetime(2024, 1, 6, 18, 0, 0),
        "data_conclusao": None
    }
]
```

**Saída Esperada (Output) Para ambos os casos:**
```json
{
    "total_tarefas_concluidas": 0,
    "tempo_medio_conclusao_geral": 0.0,
    "taxa_atraso_geral": 0.0,
    "indicadores_por_prioridade": {
        "Baixa": {
            "total_tarefas_concluidas": 0,
            "tempo_medio_conclusao": 0.0,
            "taxa_atraso": 0.0
        },
        "Média": {
            "total_tarefas_concluidas": 0,
            "tempo_medio_conclusao": 0.0,
            "taxa_atraso": 0.0
        },
        "Alta": {
            "total_tarefas_concluidas": 0,
            "tempo_medio_conclusao": 0.0,
            "taxa_atraso": 0.0
        }
    }
}
```
*Nota: O sistema não deve quebrar com `ZeroDivisionError`. Retorna $0.0$ para médias e taxas, conforme regra 1.3.3.*

---

##### Exemplo 4: Caso de Borda: Conclusão Exatamente no Prazo

**Entrada (Input):**
```python
tarefas = [
    {
        "id": 50,
        "titulo": "Tarefa concluída no limite exato",
        "prioridade": "Média",
        "status": "Concluida",
        "data_criacao": datetime(2024, 1, 1, 8, 0, 0),
        "data_limite": datetime(2024, 1, 2, 8, 0, 0),
        "data_conclusao": datetime(2024, 1, 2, 8, 0, 0) # Igual ao limite
    }
]
```

**Saída Esperada (Output):**
```json
{
    "total_tarefas_concluidas": 1,
    "tempo_medio_conclusao_geral": 24.0,
    "taxa_atraso_geral": 0.0,
    "indicadores_por_prioridade": {
        "Baixa": {
            "total_tarefas_concluidas": 0,
            "tempo_medio_conclusao": 0.0,
            "taxa_atraso": 0.0
        },
        "Média": {
            "total_tarefas_concluidas": 1,
            "tempo_medio_conclusao": 24.0,
            "taxa_atraso": 0.0
        },
        "Alta": {
            "total_tarefas_concluidas": 0,
            "tempo_medio_conclusao": 0.0,
            "taxa_atraso": 0.0
        }
    }
}
```
*Justificativa: A regra 1.3.3 define que uma tarefa é atrasada exclusivamente se $data\_conclusao > data\_limite$. Igualdade não configura atraso.*

---

## 2. ESPECIFICAÇÃO DE CENÁRIOS DE ACEITE E TEST HARNESS

### 2.1 Cenários de Aceite (Dado-Quando-Então)
Estes cenários definem o comportamento esperado do sistema e servirão como base para a homologação do código gerado.

* **Cenário 1 (Sucesso): Cálculo de métricas com dados válidos**
  * **Dado** um conjunto de tarefas válidas, contendo diferentes prioridades (`"Baixa"`, `"Média"`, `"Alta"`), status variados (`"Pendente"` e `"Concluída"`) e datas consistentes,
  * **Quando** o módulo `TaskAnalyzer` for executado,
  * **Então** o sistema deve ignorar as tarefas "Pendentes" e retornar as métricas corretas das tarefas "Concluídas", calculando com exatidão o tempo médio geral de conclusão, a taxa de atraso geral e as métricas segregadas por cada nível de prioridade.

* **Cenário 2 (Exceção/Erro): Tratamento de inconsistência de datas**
  * **Dado** uma lista de tarefas onde pelo menos um dos registros contém uma `data_conclusao` anterior à `data_criacao` (violação cronológica),
  * **Quando** o módulo `TaskAnalyzer` for executado,
  * **Então** o sistema deve interromper o cálculo e disparar a exceção `DataInconsistenteError`, exibindo uma mensagem de erro clara informando que há inconsistência nas datas da tarefa.

* **Cenário 3 (Exceção/Erro): Prevenção contra divisão por zero**
  * **Dado** uma lista de tarefas vazia ou uma lista onde nenhuma das tarefas possua o status `"Concluída"`,
  * **Quando** o módulo `TaskAnalyzer` for executado para calcular as médias,
  * **Então** o sistema deve tratar o risco de divisão por zero (`ZeroDivisionError`) e retornar valores $0.0$ para o tempo médio e para a taxa de atraso, não permitindo que a aplicação quebre de forma abrupta.

---

### 2.2 Planejamento do Test Harness
Para garantir que o código gerado pelo assistente de IA esteja estritamente alinhado com este contrato executável, os cenários descritos acima serão convertidos em testes automatizados na Fase 2, utilizando o framework `pytest`.

A estratégia de validação ocorrerá da seguinte forma:
1. **Fixtures de Dados (O "Dado"):** Serão criados conjuntos de dados simulados (*mocks*) dentro do arquivo `tests/test_harness.py` representando as entradas de sucesso, as entradas com datas inválidas e os cenários de listas vazias.
2. **Execução (O "Quando"):** O script de testes importará a função principal do `src/task_analyzer.py` gerado pela IA e passará esses dados simulados como parâmetro.
3. **Asserções (O "Então"):** Utilizaremos comandos `assert` para verificar se os cálculos matemáticos batem com o gabarito esperado e comandos `pytest.raises` para confirmar se as exceções de datas inválidas estão sendo disparadas corretamente.

---

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

## 4. ARQUITETURA DO REPOSITÓRIO E PREPARAÇÃO PARA GIT/GITHUB

### 4.1 Desenho da Árvore do Repositório

```
sdd-task-analyzer/
├── README.md               # Visão geral do projeto e instruções de execução
├── CONTEXT_RULES.md        # Arquivo de regras de contexto e restrições para a IA
├── .gitignore              # Arquivos e pastas ignorados pelo Git (ex: __pycache__, .pytest_cache)
├── specs/
│   └── task_analyzer_spec.md # Especificação técnica do contrato de negócio (SDD)
├── tests/
│   └── test_harness.py     # Testes automatizados de validação (pytest)
└── src/
    └── task_analyzer.py    # Módulo principal com o código homologado
```

---

### 4.2 Plano de Homologação Humana
Na Fase 2, todo código-fonte gerado por assistentes de Inteligência Artificial será submetido a um fluxo sistemático de homologação técnica conduzido pelo engenheiro responsável antes de qualquer integração ao repositório final. O plano de validação é composto por cinco etapas obrigatórias:

* **Validação Automatizada:** Execução integral da suíte de testes no arquivo `tests/test_harness.py` utilizando o framework `pytest`, exigindo 100% de aprovação em todos os cenários de sucesso, borda e exceção.
* **Revisão de Conformidade com o SDD:** Verificação rigorosa para garantir que a assinatura pública da função `analisar_tarefas`, os tipos de dados e a estrutura do dicionário de retorno estão estritamente alinhados com a Seção 1.3.
* **Auditoria de CONTEXT_RULES:** Checagem de cumprimento das proibições absolutas, confirmando a ausência de bibliotecas externas (ex: `pandas`, `numpy`), a inexistência de chamadas a `print()` ou `input()`, a não persistência em disco e o uso correto do módulo padrão de `logging`.
* **Inspeção de Qualidade de Código:** Avaliação da legibilidade, tipagem estática com Type Hints, documentação via Docstrings (padrão Google) e modularização orientada ao Princípio da Responsabilidade Única (SRP).
* **Aprovação e Commit:** Promoção do código homologado para o ambiente de controle de versão somente após o aceite final de todos os critérios descritos.

---

### 4.3 Estratégia de Versionamento e Controle de Código
* **Estrutura de Branches:** Adoção do modelo Git Flow simplificado. A branch `main` permanecerá protegida para versões estáveis e homologadas, a branch `develop` concentrará as integrações da Fase 2, e branches auxiliares (`feature/*`) serão criadas para tarefas específicas de implementação.
* **Padrão de Commits:** Utilização de mensagens de commit atômicas e estruturadas segundo o padrão Conventional Commits (ex: `feat: adiciona validacao de datas inconsistentes`, `test: inclui mocks para zero tarefas concluidas`).
* **Pull Requests (PRs):** Todo merge para as branches principais exigirá verificação automatizada prévia e revisão do plano de homologação.