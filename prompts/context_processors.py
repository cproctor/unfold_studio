from prompts.models import Prompt

def user_prompts(request):
    if request.user.is_authenticated:
        return {
            'prompts_owned': Prompt.objects.filter(owners=request.user).count(),
            'prompts_assigned': Prompt.objects.filter(assignee_groups__user=request.user).count(),
            'prompts_unsubmitted': Prompt.objects.filter(assignee_groups__user=request.user).exclude(
                    submissions__author=request.user).count()
        }
    else:
        return {
            'prompts_owned': 0,
            'prompts_assigned': 0,
            'prompts_unsubmitted': 0
        }
