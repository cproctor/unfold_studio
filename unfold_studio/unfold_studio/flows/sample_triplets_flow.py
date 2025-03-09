from ..models import StoryPlayInstance
from ..choices import StoryPlayRecordDataType

class TripletType:
    DIRECT_CONTINUE = "DIRECT_CONTINUE"
    BRIDGE_AND_CONTINUE = "BRIDGE_AND_CONTINUE"
    NEEDS_INPUT = "NEEDS_INPUT"
    INVALID_USER_INPUT = "INVALID_USER_INPUT"
    

class SampleTripletsFlow:

    def __init__(self):
        needs_input_range = 5
        needs_input_difference_threshold = 2
        pass

    def execute_flow(self, story_play_instance_uuids):
        triplets = []
        for story_play_instance_uuid in story_play_instance_uuids:
            try:
                instance = StoryPlayInstance.objects.get(uuid=story_play_instance_uuid)
            except Exception as e:
                print(str(e))
                continue
            records = list(instance.records.order_by('story_point'))

            direct_continue_triplets = self.get_direct_continue_triplets(records)
            print(direct_continue_triplets)

            print("=========================================================================================================================================================================================================")

            bridge_and_continue_triplets = self.get_bridge_and_continue_triplets(records)
            print(bridge_and_continue_triplets)

            print("=========================================================================================================================================================================================================")

            needs_input_triplets = self.get_needs_input_triplets(records)
            print(needs_input_triplets)


        return triplets
    
    def get_direct_continue_triplets(self, records):
        triplets = []
        i = 0
        while i <= len(records) - 5:
            if (records[i].data_type == StoryPlayRecordDataType.AUTHORS_TEXT and
                records[i+1].data_type == StoryPlayRecordDataType.AUTHORS_CHOICE_LIST and
                records[i+2].data_type == StoryPlayRecordDataType.READERS_CHOSEN_CHOICE and
                records[i+3].data_type == StoryPlayRecordDataType.AUTHORS_TEXT and 
                records[i+4].data_type == StoryPlayRecordDataType.AUTHORS_TEXT):
                
                triplet = {
                    'initial_text': records[i].data['text'],
                    'chosen_choice': records[i+2].data,
                    'next_text': records[i+4].data['text'],
                    'triplet_type': TripletType.DIRECT_CONTINUE,
                }
                triplets.append(triplet)
                i += 3
            else:
                i += 1

        return triplets
    
    def get_bridge_and_continue_triplets(self, records):
        triplets = []
        i = 0
        while i <= len(records) - 6:
            if (records[i].data_type == StoryPlayRecordDataType.AUTHORS_TEXT and
                records[i+1].data_type == StoryPlayRecordDataType.AUTHORS_CHOICE_LIST and
                records[i+2].data_type == StoryPlayRecordDataType.READERS_CHOSEN_CHOICE and
                records[i+3].data_type == StoryPlayRecordDataType.AUTHORS_TEXT and
                records[i+4].data_type == StoryPlayRecordDataType.AUTHORS_TEXT and 
                records[i+5].data_type == StoryPlayRecordDataType.AUTHORS_TEXT):
                
                triplet = {
                    'initial_text': records[i].data['text'],
                    'chosen_choice': records[i+2].data,
                    'next_text': records[i+5].data['text'],
                    'triplet_type': TripletType.BRIDGE_AND_CONTINUE,
                }
                triplets.append(triplet)
                i += 4
            else:
                i += 1

        return triplets
    

    def get_needs_input_triplets(self, records):
        triplets = []
        i = 0
        while i <= len(records) - 4:
            if (records[i].data_type == StoryPlayRecordDataType.AUTHORS_TEXT and
                records[i+1].data_type == StoryPlayRecordDataType.AUTHORS_CHOICE_LIST and
                records[i+2].data_type == StoryPlayRecordDataType.READERS_CHOSEN_CHOICE and 
                records[i+3].data_type == StoryPlayRecordDataType.AUTHORS_TEXT):
                
                authors_texts = []
                j = i + 4
                skipped_authors_text = 0
                while j < len(records) and len(authors_texts) < 5:
                    if records[j].data_type == StoryPlayRecordDataType.AUTHORS_TEXT:
                        if skipped_authors_text < 2:
                            skipped_authors_text += 1
                        else:
                            authors_texts.append(records[j])
                    j += 1

                for text_record in authors_texts:
                    triplets.append({
                        'initial_text': records[i].data['text'],
                        'chosen_choice': records[i+2].data,
                        'next_text': text_record.data['text'],
                        'triplet_type': TripletType.NEEDS_INPUT,
                    })
                
                i = j
            else:
                i += 1
        return triplets