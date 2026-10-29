"""Regressões da autenticação do canary, sem acessar a AWS."""

from pathlib import Path

import yaml

WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "canary-classificador.yml"


def test_credenciais_validadas_antes_do_preparo_e_deploy():
    steps = yaml.safe_load(WORKFLOW.read_text())["jobs"]["canary"]["steps"]
    indice = next(i for i, step in enumerate(steps) if step.get("id") == "credenciais")
    credenciais = steps[indice]

    assert credenciais["uses"] == "aws-actions/configure-aws-credentials@v6"
    assert credenciais["with"] == {
        "aws-access-key-id": "${{ secrets.AWS_ACCESS_KEY_ID }}",
        "aws-secret-access-key": "${{ secrets.AWS_SECRET_ACCESS_KEY }}",
        "aws-session-token": "${{ secrets.AWS_SESSION_TOKEN }}",
        "aws-region": "us-east-1",
        "retry-max-attempts": 1,
    }
    assert not credenciais.get("continue-on-error", False)
    assert indice < next(i for i, step in enumerate(steps) if "actions/setup-python@" in step.get("uses", ""))
    assert indice < next(i for i, step in enumerate(steps) if step.get("id") == "candidata")


def test_falha_de_autenticacao_orienta_renovacao_sem_ignorar_erro():
    steps = yaml.safe_load(WORKFLOW.read_text())["jobs"]["canary"]["steps"]
    indice = next(i for i, step in enumerate(steps) if step.get("id") == "credenciais")
    orientacao = steps[indice + 1]

    assert orientacao["if"] == "failure() && steps.credenciais.outcome == 'failure'"
    for texto in (
        "::error::",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
        "producao",
        "roteiros/setup-aws-academy.md",
    ):
        assert texto in orientacao["run"]
