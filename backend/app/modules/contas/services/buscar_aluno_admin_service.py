from app.modules.contas.models.usuario import Usuario
from app.modules.contas.domain.gestao_alunos import validar_id, exigir_aluno, apresentar_usuario


class BuscarAlunoAdminService:
    @staticmethod
    def executar(usuario_id):
        usuario = exigir_aluno(Usuario.buscar_por_id(validar_id(usuario_id)))
        return apresentar_usuario(usuario)
