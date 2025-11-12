import csv
import sys
from collections import defaultdict
from itertools import product
from random import sample, shuffle, choice, randrange
from django.db.models import Count, Exists, OuterRef
from tqdm import tqdm
from tabulate import tabulate
from unfold_studio.models import Story, StoryPlayRecord, StoryPlayInstance
from threading import Thread, Semaphore
import numpy as np

MIN_STORY_PLAY_SEQUENCE_LENGTHS = {
    "DIRECT_CONTINUE": 3,
    "BRIDGE_AND_CONTINUE": 4, 
    "NEEDS_INPUT": 5,
}
VALID_CLASSES = [
    "DIRECT_CONTINUE", 
    "BRIDGE_AND_CONTINUE", 
    "NEEDS_INPUT",
]

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

    def generate_examples(self, queryset=None, n=100, dist=None, verbose=False):
        """Generates [text, action, target, label] examples from the given queryset.

        Arguments:
        - queryset: a queryset built off of unfold_studio.models.StoryPlayInstance.
        - n: Number of samples.
        - dist: A dict with the four classifications as keys and floats summing to 
          1 as values.
        - verbose: Whether to print details.
        """
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(self.embedding_model)
        self.turn_sequences = []
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
        valid_examples = {}
        for c in VALID_CLASSES:
            n = n_by_class[c]
            valid_examples[c] = [self.generate_example(c, queryset) for _ in range(n)]
        invalid_examples = self.generate_invalid_examples(n_by_class["INVALID_USER_INPUT"], verbose=verbose)
        examples = sum(valid_examples.values(), invalid_examples)
        shuffle(examples)
        if verbose:
            print(tabulate(
                examples, 
                headers=["history", "action", "target", "label"],
                maxcolwidths=[40, 20, 20, 10],
            ))
        return examples

    def generate_example(self, _class, queryset):
        """Generates a single example for _class.
        """
        while True:
            spi = queryset.order_by("?").first()
            ts = self.get_turn_sequence(spi.records.all())
            if len(ts) >= MIN_STORY_PLAY_SEQUENCE_LENGTHS[_class]:
                break
        self.turn_sequences.append(ts)
        if _class == "DIRECT_CONTINUE":
            i = randrange(1, len(ts) - 1)
            history = ' '.join(ts[:i])
            action = ts[i]
            target = ts[i+1]
        elif _class == "BRIDGE_AND_CONTINUE":
            i = randrange(1, len(ts) - 2)
            history = ' '.join(ts[:i])
            action = ts[i]
            target = ts[i+2]
        elif _class == "NEEDS_INPUT": 
            i = randrange(1, len(ts) - 3)
            history = ' '.join(ts[:i])
            action = ts[i]
            target = choice(ts[i+2:])
        return [history, action, target, _class]

    def evaluate(self, examples, max_parallel_requests=8):
        """Evaluates examples. Each example should be [text, action, target, label]
        """
        results, threads, predictions, explanations = [], [], [], []
        semaphore = Semaphore(max_parallel_requests)

        def classify(i, history, action, target):
            semaphore.acquire()
            prediction, explanation = self.classify(history, action, target)
            results.append((i, prediction, explanation))
            semaphore.release()

        for i, (history, action, target, label) in enumerate(examples):
            threads.append(Thread(target=classify, args=(i, history, action, target)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        for i, prediction, explanation in sorted(results):
            predictions.append(prediction)
            explanations.append(explanation)

        self._examples = examples
        self._explanations = explanations
        self._labels = [label for history, action, target, label in examples]
        self._predictions = predictions
        self._classes = sorted(set(self._labels + self._predictions))
        self._confusion_matrix = np.ndarray([len(self._classes), len(self._classes)])
        for pred, label in zip(self._predictions, self._labels):
            ixp, ixl = self._classes.index(pred), self._classes.index(label)
            self._confusion_matrix[ixl, ixp] += 1

        self._precision = np.diag(self._confusion_matrix) / np.sum(self._confusion_matrix, axis=1)
        self._recall = np.diag(self._confusion_matrix) / np.sum(self._confusion_matrix, axis=0)
        self._f1 = 2 * self._precision * self._recall / (self._precision + self._recall)
        self._precision = np.nan_to_num(self._precision)
        self._recall = np.nan_to_num(self._recall)
        self._f1 = np.nan_to_num(self._f1)

    def classify(self, history, action, target):
        """Uses this instance of Unfold Studio to classify a continue example. 
        This is a mess currently; there should be a cleaner interface. 
        """
        from text_generation.views import GetNextDirectionView
        view = GetNextDirectionView()
        prediction, explanation = view.get_next_direction_details_for_story(
            target_knot_data={'knotContents': [target]},
            story_history=history,
            user_input=action,
            seed=self.seed
        )
        return prediction, explanation

    def generate_invalid_examples(self, n, verbose=False):
        """Generates examples of invalid input. 
        First, dissimilar turn sequences are generated. We generate an embedding vector
        for each turn sequence and compare pairs, keeping those below a certain similarity threshold.
        Then, for each required example, a random dissimilar pair (source, external) is chosen. 
        A random point, i, is selected from source; history is source[:i], the target is a 
        randomly chosen item from source[i+1:], 

        """
        embeddings = self.model.encode([' '.join(ts) for ts in self.turn_sequences])
        sims = self.model.similarity(embeddings, embeddings)
        dissimilar_turn_sequences = []
        for [ixa, a], [ixb, b] in product(enumerate(self.turn_sequences), repeat=2):
            if sims[ixa, ixb] <= self.invalid_story_similarity_threshold:
                dissimilar_turn_sequences.append([a, b])
        if not dissimilar_turn_sequences:
            raise ValueError("Can't generate invalid examples; No dissimilar turn sequences.")
        if verbose:
            print(
                "Generating invalid examples from " + 
                f"{len(dissimilar_turn_sequences)/2} pairs of dissimilar turn sequences."
            )
        invalid_examples = []
        for _ in range(n):
            source, external = choice(dissimilar_turn_sequences)
            i = randrange(1, len(source) - 1)
            history = ' '.join(source[:i])
            action = choice(external)
            target = choice(source[i+1:])
            label = "INVALID_USER_INPUT"
            invalid_examples.append([history, action, target, label])
        return invalid_examples

    def get_default_queryset(self):
        """Returns the default StoryPlayInstance queryset, selecting SPIs from 
        stories which are shared and have no AI generated text.
        """
        ai_story_play_records = StoryPlayRecord.objects.filter(
            story_play_instance__id=OuterRef("id"),
            data_type="AI_GENERATED_TEXT"
        )
        return StoryPlayInstance.objects.annotate(
            uses_ai=Exists(ai_story_play_records)
        ).filter(
            uses_ai=False,
            story__shared=True,
        )

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

    def report_evaluation_results(self):
        """Print evaluation results. Should already have
        """
        results = []
        for label_class, preds in zip(self._classes, self._confusion_matrix):
            results.append([label_class] + preds.tolist())
        print("Confusion matrix")
        print(tabulate(results, headers=["Label     Pred ->"] + self._classes))
        print()

        print("Stats")
        print(tabulate(
            self._get_evaluation_stats(), 
            headers=["Class", "Precision", "Recall", "F1"]
        ))

    def evaluation_stats_csv(self, version_name):
        """Prints evaluation stats in CSV format"""
        writer = csv.writer(sys.stdout)
        for row in self._get_evaluation_stats():
            writer.writerow([version_name] + row)

    def _get_evaluation_stats(self):
        """Returns a list of lists reporting precision, recall, and f1, like:
            BRIDGE_AND_CONTINUE         0.95  0.240506  0.383838
            DIRECT_CONTINUE             0.05  0.2       0.08
            INVALID_USER_INPUT          0.8   0.727273  0.761905
            NEEDS_INPUT                 0.04  0.4       0.0727273
            Weighted average            0.3   0.360829  0.205322
        """
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
        return stats

    def _get_error_analysis(self):
        """Returns a list of examples where the prediction was incorrect. 
        [label, pred, history, action, target, explanation]
        """
        errors = []
        for pred, example, expl in zip(self._predictions, self._examples, self._explanations):
            history, action, target, label = example
            if label != pred:
                errors.append([label, pred, history, action, target, expl['reason']])
        return errors

    def report_error_analysis(self):
        print(tabulate(
            self._get_error_analysis(), 
            ["label", "prediction", "history", "action", "target", "explanation"],
            maxcolwidths=[8, 8, 40, 20, 20, 20],
        ))

    def save_error_analysis(self, outfile):
        with open(outfile, "w") as fh:
            writer = csv.writer(fh)
            writer.writerow(["label", "prediction", "history", "action", "target", "explanation"])
            writer.writerows(self._get_error_analysis())
