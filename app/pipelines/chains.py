# pipelines/chains.py
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI  # ou outro provedor de LLM

# Exemplo: Define um prompt que inclui a recuperação do RAG e o contexto da pergunta
prompt_template = PromptTemplate(
    input_variables=["question", "context", "retrieved_info"],
    template="""
    O aluno fez a seguinte pergunta: "{question}"
    Com base no contexto de aula: "{context}"
    Segue um resumo dos materiais relevantes que recuperamos: "{retrieved_info}"
    Gere uma resposta didática para o aluno.
    """
)

# Inicializa o LLM (você pode configurar parâmetros ou usar outro provedor)
llm = OpenAI(temperature=0.7)

# Define a LLMChain que será utilizada para gerar a resposta final
chain = LLMChain(llm=llm, prompt=prompt_template)

def run_chain(question: str, context: str, retrieved_info: str) -> str:
    # Executa a chain e retorna a resposta
    result = chain.run(question=question, context=context, retrieved_info=retrieved_info)
    return result
