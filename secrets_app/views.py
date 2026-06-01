from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json

from logs.utils import log_event
from .models import Secret, Share
from .services import create_secret_with_shares

@login_required
def secret_list_view(request):
    """Відображення всіх секретів поточного користувача."""
    secrets = request.user.secrets.all().order_by('-created_at')
    return render(request, 'secrets_app/secret_list.html', {'secrets': secrets})


@login_required
def secret_create_view(request):
    """Сторінка створення (розділення) нового секрету."""
    if request.method == 'POST':
        title = request.POST.get('title')
        raw_secret = request.POST.get('secret_text')
        try:
            n = int(request.POST.get('shares_count'))
            k = int(request.POST.get('threshold'))
        except (ValueError, TypeError):
            messages.error(request, "Параметри N та K повинні бути числами.")
            return render(request, 'secrets_app/secret_form.html')

        # Валідація параметрів Шаміра
        if k > n:
            messages.error(request, "Помилка: Поріг відновлення (K) не може бути більшим за загальну кількість часток (N).")
            return render(request, 'secrets_app/secret_form.html')
        if k < 2:
            messages.error(request, "Помилка: Поріг відновлення (K) має бути не менше 2.")
            return render(request, 'secrets_app/secret_form.html')

        # Викликаємо наш сервіс, який шифрує, б'є на частки та зберігає в БД
        create_secret_with_shares(
            user=request.user,
            title=title,
            raw_secret=raw_secret,
            n=n,
            k=k
        )
        
        messages.success(request, f"Секрет '{title}' успішно розділено на {n} часток!")
        return redirect('accounts:dashboard')

    return render(request, 'secrets_app/secret_form.html')


@login_required
def secret_detail_view(request, pk):
    """Детальна сторінка секрету (показує метадані, але не сам секрет, бо він зашифрований)."""
    secret = get_object_or_404(Secret, pk=pk, owner=request.user)
    shares = secret.shares.all()
    return render(request, 'secrets_app/secret_detail.html', {'secret': secret, 'shares': shares})


@login_required
def share_list_view(request, pk):
    """Перегляд згенерованих часток для конкретного секрету."""
    secret = get_object_or_404(Secret, pk=pk, owner=request.user)
    shares = secret.shares.all()
    
    # Для зручності розпарсимо JSON координати Y, щоб гарно вивести в HTML
    formatted_shares = []
    for share in shares:
        formatted_shares.append({
            'id': share.id,
            'participant': share.participant.username,
            'x': share.x,
            'y_preview': json.loads(share.y)[:2],  # покажемо перші 2 блоки для прев'ю
            'full_y': share.y
        })
        
    return render(request, 'secrets_app/share_list.html', {
        'secret': secret,
        'shares': formatted_shares
    })


@login_required
def secret_recover_view(request):
    """Сторінка відновлення секрету за наданими частками."""
    reconstructed_text = None
    
    if request.method == 'POST':
        # Отримуємо масив рядків із форми
        shares_text_list = request.POST.getlist('shares[]')
        
        parsed_shares = []
        for raw_share in shares_text_list:
            if not raw_share.strip():
                continue
            try:
                # Оскільки кнопка "Копіювати" у нас зберігає частку як JSON-рядок {"x":..., "y":...},
                # ми парсимо цей JSON-рядок
                share_data = json.loads(raw_share.strip())
                if 'x' in share_data and 'y' in share_data:
                    parsed_shares.append(share_data)
            except json.JSONDecodeError:
                messages.error(request, "Некоректний формат однієї з часток. Переконайтеся, що це валідний JSON.")
                return render(request, 'secrets_app/secret_recover.html')

        if not parsed_shares:
            messages.error(request, "Ви не надали жодної частки для відновлення.")
            return render(request, 'secrets_app/secret_recover.html')

        try:
            # Викликаємо функцію відновлення з нашого файлу services.py
            from .services import reconstruct_secret_from_shares
            reconstructed_text = reconstruct_secret_from_shares(None, parsed_shares)
            
            # Логуємо успішну спробу відновлення
            log_event(request.user, "Відновлення секрету", "Успішно відновлено секрет за допомогою наданих часток.")
            messages.success(request, "Секрет успішно відновлено!")
            
        except Exception as e:
            # Якщо часток замало або вони пошкоджені, Лагранж видасть помилку або неправильний текст
            log_event(request.user, "Помилка відновлення", f"Невдала спроба відновлення секрету: {str(e)}")
            messages.error(request, f"Помилка при відновленні секрету. Можливо, часток недостатньо або вони несумісні. Деталі: {e}")

    return render(request, 'secrets_app/secret_recover.html', {'reconstructed_text': reconstructed_text})