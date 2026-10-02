"""File des synthèses : progression par sondage et temps estimé.

La file est la table `summaries`, remplie par l'application et vidée par le
daemon. Ce paquet est la seule chose qui sache lire son état : l'encodage de
`Summary.http_status`, le décompte fait / en attente / en erreur, la règle de
« terminé » et l'estimation. Les appelants lui passent leur session.
"""

from oceens.summaries_queue._progress import (
    SummariesQueueUnavailable,
    SurveyProgress,
    progress,
)

__all__ = ["SummariesQueueUnavailable", "SurveyProgress", "progress"]
