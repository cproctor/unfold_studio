from collections import defaultdict
from itertools import product
from random import sample, shuffle
from django.db.models import Exists, OuterRef
from tqdm import tqdm
from tabulate import tabulate
from unfold_studio.models import Story, StoryPlayRecord
import numpy as np

class ContinueClassificationModel:
    """Models the continue function's classification function.
    The continue function is given the current story state and a proposed action, 
    and must classify the action into one of the following:
     - DIRECT_CONTINUE 
     - BRIDGE_AND_CONTINUE 
     - NEEDS_INPUT 
     - INVALID_USER_INPUT 

    This model generates labeled examples by sampling existing story plays, 
    and evaluates examples. 
    """

    embedding_model = 'all-MiniLM-L6-v2'
    invalid_story_similarity_threshold = 0.3
    seed = 0

    def generate_examples(self, queryset=None, n=100, dist=None, min_story_turns=3,
            turn_sequences_per_story=None, verbose=False):
        """Generates [text, action, target, label] examples from the given queryset.

        Arguments:
        - story_queryset: a queryset built off of unfold_studio.models.Story.objects.
        - n: Number of samples.
        - dist: A dict with the four classifications as keys and floats summing to 1 as values.
        - min_story_turns: Minimum number of story turns (a turn consists of text being
          presented and then the reader making a choice.
        """
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(self.embedding_model)
        self.turn_sequences_per_story = turn_sequences_per_story
        if queryset is None:
            queryset = self.get_default_queryset()
        if dist:
            self.validate_dist(dist)
        else:
            dist = self.get_default_dist()
        n_by_class = self.get_n_by_class(n, dist) 
        if verbose: 
            print("Using distribution:")
            for cls, p in dist.items():
                print(f" - {cls}: {p}")
            print(f"Required examples:")
            for cls, n in n_by_class.items():
                print(f" - {cls}: {n}")
        turn_sequences = list(self.iter_story_turn_sequences(queryset))
        if verbose: 
            print(f"Generated {len(turn_sequences)} turn sequences")
        valid = self.generate_valid_examples(turn_sequences, n_by_class)
        invalid = self.generate_invalid_examples(turn_sequences, n_by_class)
        examples = valid + invalid
        shuffle(examples)
        return examples

    def evaluate(self, examples):
        """Evaluates examples. Each example should be [text, action, target, label]
        """
        from text_generation.views import GetNextDirectionView

        view = GetNextDirectionView()
        predictions = []
        for text, action, target, label in tqdm(examples):

            # TODO This is a mess. Should refactor the underlying system.
            prediction, explanation = view.get_next_direction_details_for_story(
                target_knot_data={'knotContents': [target]},
                story_history=text,
                user_input=action,
                seed=self.seed
            )
            predictions.append(prediction)

        self._examples = examples
        self._labels = [label for text, action, target, label in examples]
        self._predictions = predictions
        self._classes = sorted(set(self._labels + self._predictions))
        self._confusion_matrix = np.ndarray([len(self._classes), len(self._classes)])
        for pred, label in zip(self._predictions, self._labels):
            ixp, ixl = self._classes.index(pred), self._classes.index(label)
            self._confusion_matrix[ixl, ixp] += 1

        self._precision = np.diag(self._confusion_matrix) / np.sum(self._confusion_matrix, axis=1)
        self._recall = np.diag(self._confusion_matrix) / np.sum(self._confusion_matrix, axis=0)
        self._f1 = 2 * self._precision * self._recall / (self._precision + self._recall)

    def report_evaluation_results(self):
        """Print evaluation results. Should already have
        """
        results = []
        for label_class, preds in zip(self._classes, self._confusion_matrix):
            results.append([label_class] + preds.tolist())
        print("Confusion matrix")
        print(tabulate(results, headers=["Label     Pred ->"] + self._classes))
        print()

        stats = []
        for label_class, p, r, f1 in zip(self._classes, self._precision, self._recall, self._f1):
            stats.append([label_class, p, r, f1])

        counts = np.array([len([l for l in self._labels if l == c]) for c in self._classes])
        dist = counts / len(self._labels)
        stats.append([
            "Weighted average", 
            np.sum(self._precision * dist), 
            np.sum(self._recall * dist), 
            np.sum(self._f1 * dist), 
        ])
        print("Stats")
        print(tabulate(stats, headers=["Class", "Precision", "Recall", "F1"]))


    def generate_valid_examples(self, turn_sequences, n_by_class):
        valid_classes = ["DIRECT_CONTINUE", "BRIDGE_AND_CONTINUE", "NEEDS_INPUT"]
        examples = {cls: [] for cls in valid_classes}
        for turns in turn_sequences:
            for target_index in range(2, len(turns) - 1):
                target = turns[target_index]
                current_text = ""
                for current_index in range(target_index - 1):
                    current_text += turns[current_index]
                    action = turns[current_index + 1]
                    label = self.get_classification(current_index, target_index)
                    examples[label].append([current_text, action, target, label])
        if not all(len(examples[cls]) >= n_by_class[cls] for cls in valid_classes):
            stats = [[min(len(examples[c]), n_by_class[c]), n_by_class[c], c] for c in valid_classes]
            n = sum(n_by_class.values())
            raise ValueError(
                f"Not enough story plays to generate the {n} requested examples " + 
                f"in distribution provided: " + 
                ", ".join(f"{n}/{d} {c}" for n, d, c in stats)
            )
        return sum([sample(ex, n_by_class[cls]) for cls, ex in examples.items()], [])

    def generate_invalid_examples(self, turn_sequences, n_by_class):

        n_invalid = n_by_class["INVALID_USER_INPUT"]
        embeddings = self.model.encode([' '.join(ts) for ts in turn_sequences])
        sims = self.model.similarity(embeddings, embeddings)
        dissimilar_turn_sequences = []
        for [ixa, a], [ixb, b] in product(enumerate(turn_sequences), repeat=2):
            if sims[ixa, ixb] <= self.invalid_story_similarity_threshold:
                dissimilar_turn_sequences.append([a, b])
        invalid_params = []
        for ix, [a, b] in enumerate(dissimilar_turn_sequences):
            for ixa in range(len(a)):
                for ixbt in range(2, len(b)):
                    for ixbc in range(1, ixbt):
                        invalid_params.append([ix, ixa, ixbc, ixbt])
        if len(invalid_params) < n_invalid:
            raise ValueError(
                f"Not enough story plays to generate {n_invalid} examples of INVALID_USER_INPUT. " + 
                f"Only {len(dissimilar_turn_sequences)/2} pairs of story plays had similarity " +
                f"below threshold {self.invalid_story_similarity_threshold}, producing " + 
                f"{len(invalid_params)} examples."
            )
        invalid_examples = []
        for ix, ixa, ixbc, ixbt in sample(invalid_params, n_invalid):
            a, b = dissimilar_turn_sequences[ix]
            current_text = ' '.join(b[:ixbc])
            action = a[ixa]
            target = b[ixbt]
            label = "INVALID_USER_INPUT"
            invalid_examples.append([current_text, action, target, label])
        return invalid_examples

    def get_default_queryset(self):
        """Returns the default queryset, selecting stories which:
          - No AI generated text
          - Shared
        """
        any_story_play_records = StoryPlayRecord.objects.filter(
            story_play_instance__story__id=OuterRef("id"),
        )
        ai_story_play_records = StoryPlayRecord.objects.filter(
            story_play_instance__story__id=OuterRef("id"),
            data_type="AI_GENERATED_TEXT"
        )
        return Story.objects.annotate(
            has_plays=Exists(any_story_play_records),
            uses_ai=Exists(ai_story_play_records)
        ).filter(
            has_plays=True,
            uses_ai=False,
            shared=True,
        ).order_by("?")

    def get_default_dist(self):
        """dist is a dirichlet distribution representing our prior for 
        distribution of classifications. We generate examples according to 
        this distribution.
        """
        return {
            "DIRECT_CONTINUE": 0.2,
            "BRIDGE_AND_CONTINUE": 0.2,
            "NEEDS_INPUT": 0.5,
            "INVALID_USER_INPUT": 0.1
        }

    def validate_dist(self, dist):
        """Confirms that the probabilities in dist sum to 1.
        """
        if not sum(dist.values()) == 1:
            raise ValueError(f"invalid dist {dist}. Values must sum to 1.")

    def iter_story_turn_sequences(self, story_queryset):
        """Yields a sequence of StoryPlayInstances from the story_queryset.
        """
        for story in story_queryset:
            qs = story.story_play_instances.all()
            if self.turn_sequences_per_story:
                qs = qs[:self.turn_sequences_per_story]
            for spi in qs:
                yield self.get_turn_sequence(spi.records.all())

    def get_turn_sequence(self, story_play_records):
        """Maps a sequence of StoryPlayRecords into a sequence of turns, 
        where each turn has text and an action, representing how a story is 
        presented to a reader.
        """
        turns = []
        turn = ""
        for r in story_play_records:
            if r.data_type == 'AUTHORS_TEXT': 
                turn += r.data['text']
            elif r.data_type == 'READERS_CHOSEN_CHOICE':
                # This line includes the chosen choice in the story. More useful in some cases.
                #turn += ' ' + r.data
                turns.append(turn)
                turn = ""
        if turn:
            turns.append(turn)
        return turns

    def get_classification(self, current, target):
        """Classifies current and target by index. 
        """
        if current + 2 == target:
            return "DIRECT_CONTINUE"
        if current + 3 == target:
            return "BRIDGE_AND_CONTINUE"
        else:
            return "NEEDS_INPUT"

    def get_n_by_class(self, n, dist):
        """Returns a dict mapping each classification to the number of 
        examples to generate.
        """
        n_by_class = {cls: round(n * prob) for cls, prob in dist.items()}
        del n_by_class["INVALID_USER_INPUT"]
        n_by_class["INVALID_USER_INPUT"] = n - sum(n_by_class.values())
        return n_by_class
