"""Lecture de la progression de la file `summaries`."""

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import case, func, select

from oceens.models import Summary

# Valeurs de `Summary.http_status` qui marquent l'état de la file.
_PENDING = 0
_DONE = 200

# Durée d'un job, en secondes : B du Design Document v1 (EPF-MDE/OceENS#122),
# mesurée le 25 septembre 2026. Constante : ni mesure en direct, ni horloge.
_SECONDS_PER_JOB = 10


class SummariesQueueUnavailable(Exception):
    """La base n'a pas pu être lue : la progression est inconnue.

    On ne répond jamais « 0 en attente » à la place : cela se lirait « terminé ».
    L'exception d'origine est la cause (`__cause__`).
    """


@dataclass(frozen=True)
class SurveyProgress:
    done: int
    pending: int
    error: int
    # Estimation jusqu'à la fin de la file entière, jamais absente.
    estimated_seconds: int

    @property
    def total(self) -> int:
        return self.done + self.pending + self.error

    @property
    def finished(self) -> bool:
        return self.total > 0 and self.pending == 0


def progress(session, survey_ids: Iterable[int]) -> dict[int, SurveyProgress]:
    """Progression de chaque sondage de `survey_ids` qui a au moins une ligne.

    L'estimation compte tous les jobs en attente de la table, de tous les
    sondages : le daemon les prend sans ordre de sondage. Elle vaut 0 pour un
    sondage sans job en attente.
    """
    survey_ids = list(survey_ids)
    try:
        rows = session.exec(
            select(
                Summary.survey_id,
                func.sum(case((Summary.http_status == _DONE, 1), else_=0)),
                func.sum(case((Summary.http_status == _PENDING, 1), else_=0)),
                func.count(Summary.summary_id),
            )
            .where(Summary.survey_id.in_(survey_ids))
            .group_by(Summary.survey_id)
        ).all()
        queue_pending = session.exec(
            select(func.count(Summary.summary_id)).where(
                Summary.http_status == _PENDING
            )
        ).one()
    except SQLAlchemyError as error:
        raise SummariesQueueUnavailable(
            "Lecture de la file des synthèses impossible."
        ) from error

    estimate = queue_pending * _SECONDS_PER_JOB
    return {
        survey_id: SurveyProgress(
            done=done,
            pending=pending,
            error=total - done - pending,
            estimated_seconds=estimate if pending else 0,
        )
        for survey_id, done, pending, total in rows
    }
