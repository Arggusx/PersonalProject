import json
import os
import sys
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QFormLayout, QComboBox, QMessageBox, QDialog,
    QTreeWidget, QTreeWidgetItem, QGridLayout
)

class Pessoa:
    def __init__(self, nome, idade, cpf, cor_faixa):
        self.nome = nome
        self.idade = idade
        self.cpf = cpf
        self.cor_faixa = cor_faixa

class CadastroAlunos:
    def __init__(self, arquivo="C:\\Users\\dougc\\OneDrive\\Documentos\\Projetos\\interfaces\\cadastro.txt"):
        self.arquivo = arquivo
        # Verificar se o diretório do arquivo existe, se não, criá-lo
        diretorio = os.path.dirname(arquivo)
        os.makedirs(diretorio, exist_ok=True)

    def ler_alunos(self):
        alunos = []
        try:
            with open(self.arquivo, "r") as arquivo:
                for linha in arquivo:
                    pessoa_dict = json.loads(linha)
                    aluno = Pessoa(**pessoa_dict)
                    alunos.append(aluno)
        except FileNotFoundError:
            # Se o arquivo não existir, criar um novo
            with open(self.arquivo, "w") as arquivo:
                pass
        return alunos

    def verificar_cpf_existente(self, cpf):
        with open(self.arquivo, "r") as arquivo:
            for linha in arquivo:
                pessoa_dict = json.loads(linha)
                if pessoa_dict["cpf"] == cpf:
                    return True
        return False

    def adicionar_pessoa(self, pessoa):
        with open(self.arquivo, "a") as arquivo:
            arquivo.write(json.dumps(pessoa.__dict__) + "\n")

    def sobrescrever_alunos(self, alunos):
        with open(self.arquivo, "w") as arquivo:
            for aluno in alunos:
                arquivo.write(json.dumps(aluno.__dict__) + "\n")

class EditarInformacoesDialog(QDialog):
    edit_accepted = pyqtSignal(object)

    def __init__(self, aluno, parent=None):
        super().__init__(parent)
        self.aluno = aluno
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Editar Informações - {self.aluno.nome}")
        layout = QFormLayout()

        self.nome_entry = QLineEdit(self.aluno.nome)
        self.idade_entry = QLineEdit(str(self.aluno.idade))
        self.cor_combobox = QComboBox()
        self.cor_combobox.addItems(["Branca", "Amarela", "Vermelha", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])
        self.cor_combobox.setCurrentText(self.aluno.cor_faixa)

        layout.addRow("Nome*:", QLabel(self.aluno.nome))

        layout.addRow("Idade:", self.idade_entry)
        layout.addRow("Cor da Faixa:", self.cor_combobox)

        buttons_layout = QVBoxLayout()
        edit_button = QPushButton("Editar")
        edit_button.clicked.connect(self.aplicar_edicao)
        buttons_layout.addWidget(edit_button)

        layout.addRow(buttons_layout)
        self.setLayout(layout)

    def aplicar_edicao(self):
        if not self.nome_entry.text():
            QMessageBox.critical(self, "Erro", "O campo 'Nome' não pode ficar vazio.")
            return
        self.aluno.nome = self.nome_entry.text()
        self.aluno.idade = int(self.idade_entry.text())
        self.aluno.cor_faixa = self.cor_combobox.currentText()

        # Emitir sinal para informar que a edição foi aceita
        self.edit_accepted.emit(self.aluno)

        # Fechar o diálogo
        self.accept()

class CadastroPessoasApp(QWidget):
    def __init__(self):
        super().__init__()
        self.cadastro = CadastroAlunos()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cadastro de Pessoas")
        layout = QGridLayout(self)

        # Crie os widgets necessários
        self.nome_entry = QLineEdit()
        self.idade_entry = QLineEdit()
        self.cpf_busca_entry = QLineEdit()
        self.cpf_entry = QLineEdit()
        self.cor_combobox = QComboBox()
        self.cor_combobox.addItems(["Branca", "Amarela", "Vermelha", "Laranja", "Verde", "Roxa", "Marrom", "Preta"])

        cadastrar_button = QPushButton("Cadastrar")
        cadastrar_button.clicked.connect(self.cadastrar_pessoa)

        exibir_button = QPushButton("Exibir Alunos")
        exibir_button.clicked.connect(self.exibir_alunos)

        buscar_button = QPushButton("Buscar")
        buscar_button.clicked.connect(self.buscar_por_cpf)

        # Adicione os widgets ao layout
        layout.addWidget(QLabel("Nome:"), 0, 0)
        layout.addWidget(self.nome_entry, 0, 1)

        layout.addWidget(QLabel("Idade:"), 1, 0)
        layout.addWidget(self.idade_entry, 1, 1)

        layout.addWidget(QLabel("CPF:"), 2, 0)
        layout.addWidget(self.cpf_entry, 2, 1)

        layout.addWidget(QLabel("Cor da Faixa:"), 3, 0)
        layout.addWidget(self.cor_combobox, 3, 1)

        cadastrar_button = QPushButton("Cadastrar")
        cadastrar_button.clicked.connect(self.cadastrar_pessoa)
        layout.addWidget(cadastrar_button, 4, 0, 1, 1)  # Span the button across two columns

        exibir_button = QPushButton("Exibir Alunos")
        exibir_button.clicked.connect(self.exibir_alunos)
        layout.addWidget(exibir_button, 4, 1, 1, 1)  # Span the button across two columns

        buscar_button = QPushButton("Buscar")
        buscar_button.clicked.connect(self.buscar_por_cpf)
        layout.addWidget(buscar_button, 7, 0, 1, 1)

        
        layout.addWidget(QLabel("CPF para Busca:"), 6, 0)
        layout.addWidget(self.cpf_busca_entry, 6, 1, 1, 1)


        # Configure o layout principal da janela
        self.setLayout(layout)

    def editar_informacoes_aluno_selecionado(self, aluno, item_selecionado):
        tree = self.sender().parent().children()[0]
        item_selecionado = tree.currentItem()

        if not item_selecionado:
            self.mostrar_mensagem_erro("[Erro]", "Selecione um aluno para editar.")
            return

        nome_aluno = item_selecionado.text(0)
        aluno_selecionado = None

        for aluno in self.cadastro.ler_alunos():
            if aluno.nome == nome_aluno:
                aluno_selecionado = aluno
                break

        if not aluno_selecionado:
            self.mostrar_mensagem_erro("Erro", "Aluno não encontrado para edição.")
            return

        dialog = EditarInformacoesDialog(aluno_selecionado)
        dialog.edit_accepted.connect(lambda aluno, item=item_selecionado: self.handle_edit_informacoes_accepted(aluno, item))

        dialog.exec()

    def handle_edit_informacoes_accepted(self, aluno, item_selecionado):
    # Lidar com os dados editados aqui
    # Por exemplo, atualizar os dados na lista e atualizar a interface do usuário
    # Esta função será chamada quando o sinal edit_accepted for emitido
        print(f"Informações editadas aceitas para {aluno.nome}")

        # Atualizar a Treeview
        item_selecionado.setText(0, aluno.nome)
        item_selecionado.setText(1, str(aluno.idade))
        item_selecionado.setText(3, aluno.cor_faixa)

        # Atualizar o arquivo
        alunos = self.cadastro.ler_alunos()
        for i, a in enumerate(alunos):
            if a.nome == aluno.nome:
                alunos[i] = aluno
                break
        self.cadastro.sobrescrever_alunos(alunos)

        self.mostrar_mensagem_info("Sucesso", f"Dados de {aluno.nome} atualizados com sucesso.")

    def cadastrar_pessoa(self):
        nome = self.nome_entry.text()
        idade = self.idade_entry.text()
        cpf = self.cpf_entry.text()
        cor_faixa = self.cor_combobox.currentText()

        if not nome or not idade or not cpf or not cor_faixa:
            self.mostrar_mensagem_erro("Erro", "Preencha todos os campos!")
            return

        try:
            idade = int(idade)
        except ValueError:
            self.mostrar_mensagem_erro("Erro", "Idade deve ser um número inteiro!")
            return

        if not self.validar_cpf(cpf):
            self.mostrar_mensagem_erro("Erro", "CPF inválido!")
            return

        if self.cadastro.verificar_cpf_existente(cpf):
            self.mostrar_mensagem_erro("Erro", "CPF já cadastrado!")
            return

        pessoa = Pessoa(nome, idade, cpf, cor_faixa)
        self.cadastro.adicionar_pessoa(pessoa)

        self.mostrar_mensagem_info("Sucesso", "Cadastro realizado com sucesso!")

    def buscar_por_cpf(self):
        cpf = self.cpf_busca_entry.text()

        with open(self.cadastro.arquivo, "r") as arquivo:
            encontrou = False
            for linha in arquivo:
                pessoa_dict = json.loads(linha)
                if pessoa_dict["cpf"] == cpf:
                    resultado = (
                        f"Nome: {pessoa_dict['nome']}\n"
                        f"Idade: {pessoa_dict['idade']}\n"
                        f"CPF: {pessoa_dict['cpf']}\n"
                        f"Cor da faixa: {pessoa_dict['cor_faixa']}"
                    )
                    self.mostrar_mensagem_info("Informações encontradas", resultado)
                    encontrou = True
                    break

            if not encontrou:
                self.mostrar_mensagem_erro("Erro", "Nenhuma informação encontrada para o CPF informado.")

    def exibir_alunos(self):
        alunos = self.cadastro.ler_alunos()

        if not alunos:
            self.mostrar_mensagem_info("Aviso", "Não há alunos cadastrados.")
            return

        janela_alunos = QDialog(self)
        janela_alunos.setWindowTitle("Alunos Cadastrados")

        tree = QTreeWidget(janela_alunos)
        tree.setHeaderLabels(["Nome", "Idade", "CPF", "Cor Faixa"])

        for aluno in alunos:
            item = QTreeWidgetItem(tree)
            item.setText(0, aluno.nome)
            item.setText(1, str(aluno.idade))
            item.setText(2, aluno.cpf)
            item.setText(3, aluno.cor_faixa)

        tree.expandAll()

        excluir_button = QPushButton("Excluir Aluno Selecionado")
        excluir_button.clicked.connect(self.excluir_aluno_selecionado)

        editar_button = QPushButton("Editar Aluno Selecionado")
        editar_button.clicked.connect(self.editar_aluno_selecionado)

        layout = QVBoxLayout()
        layout.addWidget(tree)
        layout.addWidget(excluir_button)
        layout.addWidget(editar_button)

        janela_alunos.setLayout(layout)
        janela_alunos.exec()

    def excluir_aluno_selecionado(self):
        tree = self.sender().parent().children()[0]
        item_selecionado = tree.currentItem()

        if not item_selecionado:
            self.mostrar_mensagem_erro("Erro", "Selecione um aluno para excluir.")
            return

        nome_aluno = item_selecionado.text(0)
        alunos = self.cadastro.ler_alunos()
        alunos = [aluno for aluno in alunos if aluno.nome != nome_aluno]
        self.cadastro.sobrescrever_alunos(alunos)

        item_index = tree.indexOfTopLevelItem(item_selecionado)
        tree.takeTopLevelItem(item_index)

        self.mostrar_mensagem_info("Sucesso", f"Aluno {nome_aluno} excluído com sucesso.")

    def editar_aluno_selecionado(self):
        tree = self.sender().parent().children()[0]
        item_selecionado = tree.currentItem()

        if not item_selecionado:
            self.mostrar_mensagem_erro("Erro", "Selecione um aluno para editar.")
            return

        nome_aluno = item_selecionado.text(0)
        aluno_selecionado = None

        for aluno in self.cadastro.ler_alunos():
            if aluno.nome == nome_aluno:
                aluno_selecionado = aluno
                break

        if not aluno_selecionado:
            self.mostrar_mensagem_erro("[ERRO]", "Aluno não encontrado para edição.")
            return

        dialog = EditarInformacoesDialog(aluno_selecionado)
        dialog.edit_accepted.connect(lambda aluno, item=item_selecionado: self.handle_edit_informacoes_accepted(aluno, item))
        dialog.exec()

    def mostrar_mensagem_erro(self, titulo, mensagem):
        QMessageBox.critical(self, titulo, mensagem)

    def mostrar_mensagem_info(self, titulo, mensagem):
        QMessageBox.information(self, titulo, mensagem)

    def validar_cpf(self, cpf):
        cpf = ''.join(filter(str.isdigit, cpf))

        if len(cpf) != 11:
            return False

        total = 0
        for i in range(9):
            total += int(cpf[i]) * (10 - i)
        resto = total % 11
        digito1 = 11 - resto if resto != 0 and resto != 1 else 0

        total = 0
        for i in range(10):
            total += int(cpf[i]) * (11 - i)
        resto = total % 11
        digito2 = 11 - resto if resto != 0 and resto != 1 else 0

        return digito1 == int(cpf[9]) and digito2 == int(cpf[10])

if __name__ == "__main__":
    app = QApplication([])
    icone_path = "C:\\Users\\dougc\\OneDrive\\Documentos\\Projetos\\interfaces\\1062.jpg"

    if os.path.isfile(icone_path):
        app.setWindowIcon(QIcon(icone_path))
    else:
        print("Arquivo de ícone não encontrado. Usando o ícone padrão.")

    window = CadastroPessoasApp()
    window.show()
    sys.exit(app.exec())