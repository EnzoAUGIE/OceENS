"""Progression de la file des synthèses : l'estimation compte toute la file (#146).

La file est la table `summaries` ; le daemon prend les lignes sans ordre de
sondage, donc l'estimation de chaque sondage porte sur tous les jobs en attente,
pas seulement les siens.
"""

import pytest
from sqlmodel import Session, SQLModel, create_engine

from oceens.models import Summary, Survey
from oceens.summaries_queue import progress

PENDING = 0
DONE = 200

SURVEYS = 10
JOBS_PER_SURVEY = 45
# 10 sondages x 45 jobs = 450 jobs, a 20 s chacun (B, Design Document v1 #122).
EXPECTED_SECONDS = 450 * 20


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def add_survey(session, http_status, jobs=JOBS_PER_SURVEY):
    """Un sondage avec `jobs` lignes de file au même état ; retourne son id."""
    survey = Survey(status=2)
    session.add(survey)
    session.commit()
    session.add_all(
        Summary(survey_id=survey.survey_id, http_status=http_status)
        for _ in range(jobs)
    )
    session.commit()
    return survey.survey_id


def test_every_survey_gets_the_estimate_of_the_whole_queue(session):
    survey_ids = [add_survey(session, PENDING) for _ in range(SURVEYS)]

    result = progress(session, survey_ids)

    assert set(result) == set(survey_ids)
    for survey_id in survey_ids:
        assert result[survey_id].estimated_seconds == EXPECTED_SECONDS


def test_asking_about_one_survey_gives_the_same_estimate(session):
    survey_ids = [add_survey(session, PENDING) for _ in range(SURVEYS)]

    for survey_id in survey_ids:
        result = progress(session, [survey_id])

        assert result[survey_id].estimated_seconds == EXPECTED_SECONDS


def test_a_survey_with_no_pending_row_gets_zero(session):
    pending_ids = [add_survey(session, PENDING) for _ in range(SURVEYS)]
    finished_id = add_survey(session, DONE)

    result = progress(session, [*pending_ids, finished_id])

    assert result[finished_id].estimated_seconds == 0
    assert result[pending_ids[0]].estimated_seconds == EXPECTED_SECONDS
