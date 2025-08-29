# para validar se é realmente uma CNH e não é uma fake, considerar colocar algumas checagens como ter o Brasão da republica ou mesmo sempre usar ourtas imagens de referẽncia no prompt
valida_CNH = """
  Verifique se a imagem é de um documento chamado CNH. Ele deve conter no topo a inscrição "CARTEIRA NACIONAL DE HABILITAÇÃO". Ele também deve conter uma foto de rosto de uma pessoa real.
  Verifque se ele parece autêntico e não uma falsificação.
  Extrai os seguintes campos deste documento:
    1) nome: o nome da pessoa de quem é a CNH. Em geral, esse é o campo mais acima do documento de deve estar escrito "NOME e SOBRENOME";
    2) cpf: extraia o valor do campo "CPF" como texto, mesmo sendo um número com 11 digitos remova os pontos e traço, caso ele esteja escrito formatado como NNN.NNN.NNN-NN. Mantenha os zeros a esquerda, se existirem para totalizar os 11 digitos.
    3) nome_pai: encontre o campo "FILIAÇÂO" que deve ter dois nomes em linhas separadas. O primeiro é o nome do pai que deve ser extraido para esse campo "father_name". Veja se ele não continua na linha seguinte. Se ele ocntinuar, haverá um espaçoa a mais para o proximo nome que é da mãe.
    4) nome_mae: o segundo nome encontrado acima no campo "FILIAÇÂO"
    5) data_nascimento: a data de nascimento. Ele deve estar no campo que pode ter a data e mais informações sobre o nascimento. Extrai somente os numeros com o formato ddMMaaaa, incluindo o zero a esquerda para dias com um dígito.
    6) validade: a data de validade da carteira que deve estar no campo "Validade" Extrai somente os numeros com o formato ddMMaaaa, incluindo o zero a esquerda para dias com um dígito.
    7) valid: Se o documento parece verdadeiro, retorne "sim"; Se o documento não for uma CNH, retone o valor "nao"; Se o documento parecer que é uma falsificação, estiver muito rasurado ou pouco claro, difícil de ler, retone o valor "suspeito"

Se algum dos campos não for encontrado, deixe o valor vazio.
"""

valida_RG = """
Verifique se a imagem é de uma documento chamado Registro Geral. Ele deve conter no topo a inscrição "CARTEIRA DE IDENTIDADE" ou "CEDULA DE IDENTIDADE". 
Ele também deve conter a inscrição "REPUBLICA FEDERATIVA DO BRASIL". 

...... completar ....

"""

valida_CN = """
Verifique se a imagem é de uma documento chamado Certidão de Nascimento. Ele deve conter no topo o texto "CERTIDÂO DE NASCIMENTO". 
...... completar ....

"""

valida_CC = """
Verifique se a imagem é de uma documento chamado Certidão de Casamento. Ele deve conter no topo o texto "CERTIDÂO DE CASAMENTO". 
...... completar ....

"""