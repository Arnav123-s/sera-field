"""World-side words offered to the mind at public events."""

from dataclasses import dataclass

import numpy as np


REGIME_WORDS = {
    'rubbing': 'rough',
    'water drag': 'wet',
    'dry friction': 'sticky',
    'thick oil': 'gooey',
    'spring': 'springy',
    'tight spring': 'tight',
    'stiff spring': 'stiff',
    'swing': 'swingy',
    'valley': 'bumpy',
    'slope': 'downhill',
    'none': 'free',
}
MASS_WORDS = ('heavy', 'light')
FILLERS = ('look', 'nice', 'oops', 'again')
VOCABULARY = tuple(sorted(set(REGIME_WORDS.values()) | set(MASS_WORDS) | set(FILLERS)))
_RANDOM_WORDS = tuple(sorted(set(REGIME_WORDS.values()) | set(MASS_WORDS)))
_ALIASES = {'swing small': 'swing', 'faint rubbing': 'rubbing'}


@dataclass(frozen=True)
class Utterance:
    world_no: int
    situation: int
    word: str
    reason: str


class Caretaker:
    def __init__(self, arm, seed, filler_rate=0.2, p_random=0.15):
        if arm not in ('timed', 'random', 'none', 'definition'):
            raise ValueError(f'unknown caretaker arm: {arm}')
        if not 0 <= filler_rate <= 1 or not 0 <= p_random <= 1:
            raise ValueError('word probabilities must be between 0 and 1')
        self.arm = arm
        self.seed = seed
        self.filler_rate = filler_rate
        self.p_random = p_random
        self.log = []
        self._regime_said = set()
        self._first_event = set()
        self._mass_said = set()

    @staticmethod
    def _regime_words(world):
        kind = getattr(world, 'force', None)
        if kind is None:
            kind = world.kind_name
        words = []
        for part in kind.split('+'):
            name = _ALIASES.get(part.strip(), part.strip())
            if name in REGIME_WORDS:
                word = REGIME_WORDS[name]
                if word not in words:
                    words.append(word)
        return words

    def _say(self, world_no, situation, words, reason):
        utterances = [Utterance(world_no, situation, word, reason) for word in words]
        self.log.extend(utterances)
        return utterances

    def start_world(self, world_no, world, word_only=False):
        if not word_only or self.arm == 'none':
            return []
        self._regime_said.add(world_no)
        return self._say(world_no, -1, self._regime_words(world), 'word-only')

    def on_event(self, world_no, world, situation, event):
        if event not in ('surprise', 'blocked', 'alarm'):
            raise ValueError(f'unknown caretaker event: {event}')
        if self.arm not in ('timed', 'definition'):
            return []
        utterances = []
        if world_no not in self._first_event:
            self._first_event.add(world_no)
            if world_no not in self._regime_said:
                self._regime_said.add(world_no)
                utterances.extend(self._say(world_no, situation, self._regime_words(world), event))
        if event == 'surprise' and (world_no, situation) not in self._mass_said:
            mass = world.masses[situation]
            word = 'heavy' if mass > 2.0 else 'light' if mass < 0.9 else None
            if word is not None:
                self._mass_said.add((world_no, situation))
                utterances.extend(self._say(world_no, situation, (word,), event))
        return utterances

    def on_situation(self, world_no, world, situation):
        if self.arm == 'none':
            return []
        rng = np.random.default_rng([self.seed, 41, world_no, situation])
        utterances = []
        if rng.random() < self.filler_rate:
            word = FILLERS[int(rng.integers(len(FILLERS)))]
            utterances.extend(self._say(world_no, situation, (word,), 'filler'))
        if self.arm == 'random' and rng.random() < self.p_random:
            word = _RANDOM_WORDS[int(rng.integers(len(_RANDOM_WORDS)))]
            utterances.extend(self._say(world_no, situation, (word,), 'random'))
        return utterances

    def heard(self, world_no):
        return frozenset(u.word for u in self.log if u.world_no == world_no)

    def definitions(self):
        return {word: kind for kind, word in REGIME_WORDS.items()}
