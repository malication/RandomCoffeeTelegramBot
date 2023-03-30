import random
from datetime import datetime
from itertools import permutations
import logging

import pandas as pd

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def gen_groups(ids: tuple) -> list:
    """
    Generates a set of random groups of two from the given ids,
    if the size of ids is odd, groups the last three ids together.
    """

    if len(ids) < 4:
        return [ids]

    groups = []
    ids = list(ids)
    random.shuffle(ids)
    while ids:
        if len(ids) == 3:
            groups.append(tuple(ids))
            break
        groups.append((ids.pop(), ids.pop()))
    return groups


def gen_session(
        session_id: str,
        participant_ids: tuple,
        previous_sessions: pd.DataFrame = None,
        attempts: int = 5
):
    """
    | date | session_id | first | second |
    """
    date = datetime.today().date()

    groups = gen_groups(participant_ids)

    if previous_sessions is not None:
        logger.info(f"Validating the current session (ID: {session_id}) groups against previous sessions: "
                    f"{previous_sessions['session_id'].unique().tolist()}.")
        previous_pairs = previous_sessions[["first", "second"]].values
        while attempts > 0:
            try:
                logger.info(f"Attempts left: {attempts}")
                for group in groups:
                    for pair in permutations(group, 2):
                        for prev_pair in previous_pairs:
                            if set(prev_pair) == set(pair):
                                print(f"Pair ({pair}) already exists in previous sessions.")
                                raise ValueError
                break
            except ValueError:
                attempts -= 1
                if attempts == 0:
                    logger.warning("Could not generate a new unique groups. "
                                   "Let the groups contain pairs possibly from previous sessions.")
                # regenerate groups
                groups = gen_groups(participant_ids)

    return pd.DataFrame([
        {
            'date': date,
            'session_id': session_id,
            "first": first,
            "second": second
        } for group in groups for first, second in permutations(group, 2)
    ])


if __name__ == '__main__':
    # generate multiple sessions
    num_sessions = 4
    num_participants = 30
    test_participant_ids = list(range(1, num_participants + 1))
    session_ids = list(range(1, num_sessions + 1))
    participant_samples = [tuple(random.sample(test_participant_ids, k=4)) for _ in range(num_sessions)]

    sessions = pd.concat([
        gen_session(session_id=session_id, participant_ids=participant_ids)
        for session_id, participant_ids in zip(session_ids, participant_samples)
    ], ignore_index=True)

    # get the sessions with session_id
    history_size = 4
    last_sessions = sessions[sessions["session_id"].isin(session_ids[-history_size:])]
    print(last_sessions)
    # generate a new session with history
    session = gen_session(
        session_id=f"{num_sessions + 1}",
        participant_ids=tuple(random.sample(test_participant_ids, k=25)),
        previous_sessions=last_sessions
    )
    print(session)
