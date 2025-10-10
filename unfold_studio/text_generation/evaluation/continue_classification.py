from unfold_studio.models import Story, StoryPlayRecord
from django.db.models import Exists, OuterRef
from collections import defaultdict
from random import sample

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

    # Future optimization (may be needed in prod): 
    # Fetch records in batches.
    # query_page_size = 10

    def generate_examples(self, story_queryset=None, n=100, dist=None):
        """Generates [text, action, target, label] examples from the given queryset.

        Arguments:
        - story_queryset: a queryset built off of unfold_studio.models.Story.objects.
        - n: Number of samples.
        - dist: A dict with the four classifications as keys and 
        """
        queryset = story_queryset or self.get_default_queryset()
        if dist:
            self.validate_dist(dist)
        else:
            dist = self.get_default_dist()
        n_by_class = self.get_n_by_class(n, dist) 
        results = defaultdict(list)
        for play in self.iter_story_plays(queryset):
            turns = self.get_turn_sequence(play.records.all())
            for target_index in range(1, len(turns) - 1):
                target = turns[target_index]['text']
                current_text = ""
                for current_index in range(target_index):
                    current_text += turns[current_index]['text']
                    action = turns[current_index]['action']
                    label = self.get_classification(current_index, target_index)
                    results[label].append([current_text, action, target, label])
                    if self.enough_results(results, n_by_class):
                        clipped_results = {cls: sample(ex, n_by_class[cls]) for cls, ex in results.items()}
                        return sum(clipped_results.values(), [])
        
        n_results = len(results.values())
        raise ValueError(f"Not enough story plays to generate the {n} requested examples ({n_results} generated).")

    # TODO: improve default queryset according to #189
    def get_default_queryset(self):
        """Returns the default queryset:
          - No AI generated text
          - Shared
        """
        ai_story_play_records = StoryPlayRecord.objects.filter(
            story_play_instance__story__id=OuterRef("id"),
            data_type="AI_GENERATED_TEXT"
        )
        return Story.objects.annotate(
            uses_ai=Exists(ai_story_play_records)
        ).filter(
            uses_ai=False,
            shared=True,
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

    def iter_story_plays(self, story_queryset):
        """Yields a sequence of StoryPlayInstances from the story_queryset.
        """
        for story in story_queryset.order_by('?'):
            for play in story.story_play_instances.all():
                yield play

    def get_turn_sequence(self, story_play_records):
        """Maps a sequence of StoryPlayRecords into a sequence of turns, 
        where each turn has text and an action, representing how a story is 
        presented to a reader.
        """
        turns = []
        turn = {'text': '', 'action': None}
        for r in story_play_records:
            if r.data_type == 'AUTHORS_TEXT': 
                turn['text'] += r.data['text']
            elif r.data_type == 'READERS_CHOSEN_CHOICE':
                turn['action'] = r.data
                turns.append(turn)
                turn = {'text': '', 'action': None}
        if turn['text']:
            turns.append(turn)
        return turns

    def get_classification(self, current, target):
        """Classifies current and target by index. 
        """
        if current + 1 == target:
            return "DIRECT_CONTINUE"
        if current + 2 == target:
            return "BRIDGE_AND_CONTINUE"
        else:
            return "NEEDS_INPUT"

    def get_n_by_class(self, n, dist):
        """Returns a dict mapping each classification to the number of 
        examples to generate.
        """
        n_by_class = {cls: round(n * prob) for cls, prob in dist.items()}
        del n_by_class["INVALID_USER_INPUT"]
        return n_by_class

    def enough_results(self, results, n_by_class):
        "Checks whether there are enough results in each class"
        #return all(len(examples) >= n_by_class[cls] for cls, examples in results.items())
        return all(len(results.get(cls, [])) >= cls_min for cls, cls_min in n_by_class.items())




            

