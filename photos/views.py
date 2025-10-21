from django.views.generic import ListView, DetailView
from .models import Batch


class BatchListView(ListView):
    """
    Display list of all batches
    """
    model = Batch
    template_name = 'photos/batch_list.html'
    context_object_name = 'batches'
    
    # Optional: Add ordering, filtering, pagination
    ordering = ['-created_at']  # If you have a created_at field
    paginate_by = 12  # Optional: paginate results


class BatchDetailView(DetailView):
    """
    Display details of a single batch
    """
    model = Batch
    template_name = 'photos/batch_detail.html'
    context_object_name = 'batch'
    
    # Optional: Add related data to context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Example: Add any additional context you need
        # context['related_batches'] = Batch.objects.exclude(pk=self.object.pk)[:4]
        return context


