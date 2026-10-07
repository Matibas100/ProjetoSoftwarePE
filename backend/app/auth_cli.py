import click

from app.domain.autenticacao import AutenticacaoError
from app.services.autenticacao_service import CriarUsuarioService, LimparAutenticacaoService


def registrar_comandos(app):
    @app.cli.command("criar-administrador")
    @click.option("--nome", prompt="Nome")
    @click.option("--email", prompt="E-mail")
    def criar_administrador(nome, email):
        senha = click.prompt("Senha", hide_input=True, confirmation_prompt="Confirmar senha")
        try:
            CriarUsuarioService.executar({"nome": nome, "email": email, "senha": senha,
                                          "senha_confirmacao": senha}, "administrador")
        except AutenticacaoError as erro:
            raise click.ClickException(str(erro)) from None
        except Exception:
            raise click.ClickException("Não foi possível criar o Administrador.") from None
        click.echo("Administrador criado. Entre pela tela de login.")

    @app.cli.command("limpar-autenticacao")
    def limpar_autenticacao():
        try:
            resultado = LimparAutenticacaoService.executar()
        except Exception:
            raise click.ClickException("Não foi possível limpar a autenticação.") from None
        click.echo(f"Removidos: {resultado['sessoes']} sessões e {resultado['limites']} limites antigos.")
