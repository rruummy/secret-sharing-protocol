from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def secret_list_view(request):
    """Тимчасова заглушка для списку секретів"""
    return render(request, 'base.html')  # поки просто поверне базову сторінку

@login_required
def secret_create_view(request):
    """Тимчасова заглушка для створення секрету"""
    return render(request, 'base.html')

@login_required
def secret_detail_view(request, pk):
    """Тимчасова заглушка для перегляду секрету"""
    return render(request, 'base.html')

@login_required
def share_list_view(request, pk):
    """Тимчасова заглушка для перегляду часток"""
    return render(request, 'base.html')

@login_required
def secret_recover_view(request):
    """Тимчасова заглушка для відновлення секрету"""
    return render(request, 'base.html')