from django.conf import settings
from datetime import datetime
import json
from ..models import ContinueDecisionRecord
from ..backends import TextGenerationFactory
from ..constants import (
    EVALUATION_SYSTEM_PROMPT,
    EVALUATION_USER_PROMPT_TEMPLATE
)


class StoryTransitionEvaluator:

    def __init__(self):
        backend_config = settings.TEXT_GENERATION
        self.backend = TextGenerationFactory.create(backend_config)

    def get_records(self, story_play_instance_uuids):
        # return ContinueDecisionRecord.objects.filter(
        #     story_play_instance_uuid__in=story_play_instance_uuids
        # ).exclude(ai_evaluation__isnull=False)
        return ContinueDecisionRecord.objects.filter(
            story_play_instance_uuid__in=story_play_instance_uuids
        )

    def evaluate_and_update_records(self, story_play_instance_uuids):
        records = self.get_records(story_play_instance_uuids)
        results = {
            "total_processed": 0,
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }

        for record in records:
            try:
                evaluation = self._generate_evaluation(record)
                print(evaluation)
                # record.ai_evaluation = {
                #     "smoothness_score": evaluation['score'],
                #     "analysis": evaluation['reason'],
                # }
                # record.save(update_fields=['ai_evaluation'])
                results["success_count"] += 1
            except Exception as e:
                results["errors"].append({
                    "id": record.id,
                    "error": str(e)
                })
                results["error_count"] += 1
            finally:
                results["total_processed"] += 1

        return results

    def _build_system_and_user_prompt(self, prompt_params):
        system_prompt = EVALUATION_SYSTEM_PROMPT
        user_prompt = EVALUATION_USER_PROMPT_TEMPLATE % prompt_params

        return system_prompt, user_prompt

    def _generate_evaluation(self, record):
        prompt_params = self._get_prompt_parameters(record)
        system_prompt, user_prompt = self._build_system_and_user_prompt(prompt_params)
        print(system_prompt)
        print(user_prompt)
        
        response = self.backend.get_ai_response_by_system_and_user_prompt(
            system_prompt=EVALUATION_SYSTEM_PROMPT,
            user_prompt=user_prompt
        )

        return self._parse_response(response)

    def _get_prompt_parameters(self, record):
        return {
            'previous_timeline': json.dumps(
                record.previous_story_timeline, 
                indent=2
            ),
            'user_input': record.user_input,
            'target_knot': record.target_knot_data.get('knotName', 'Unknown'),
            'direction': record.ai_decision.get('direction', 'NO_DIRECTION'),
            'decision_content': json.dumps(
                record.ai_decision.get('content', {}), 
                indent=2
            )
        }

    def _parse_response(self, response):
        try:
            data = json.loads(response)
            if not all(key in data for key in ('score', 'reason')):
                raise ValueError("Missing required fields in response")
                
            return {
                "score": data['score'],
                "reason": data['reason'],
            }
        except json.JSONDecodeError:
            return {
                "score": 0,
                "reason": "Invalid JSON response from AI model",
            }