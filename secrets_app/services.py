from django.contrib.auth import get_user_model
from crypto.shamir import split_string_secret, recover_string_secret
from crypto.encryption import encrypt_data, decrypt_data
from logs.utils import log_event  # Імпортуємо наш логер
from .models import Secret, Share
import json

User = get_user_model()

def create_secret_with_shares(user, title: str, raw_secret: str, n: int, k: int) -> Secret:
    # 1. Шифруємо секрет
    encrypted_text = encrypt_data(raw_secret)
    
    # 2. Створюємо об'єкт секрету
    secret_obj = Secret.objects.create(
        title=title,
        encrypted_secret=encrypted_text,
        shares_count=n,
        threshold=k,
        owner=user
    )
    
    # 3. Генеруємо частки
    blocks_shares = split_string_secret(raw_secret, n, k)
    
    # 4. Зберігаємо частки в БД
    for participant_index in range(1, n + 1):
        y_coords_for_participant = []
        for block in blocks_shares:
            for x_val, y_val in block:
                if x_val == participant_index:
                    y_coords_for_participant.append(y_val)
                    break
        
        Share.objects.create(
            secret=secret_obj,
            participant=user,
            x=participant_index,
            y=json.dumps(y_coords_for_participant)
        )
        
    # [НОВЕ] 5. Записуємо подію в журнал аудіту
    log_event(
        user=user, 
        action="Створення секрету", 
        details=f"Створено секрет '{title}' (n={n}, k={k})"
    )
        
    return secret_obj

def reconstruct_secret_from_shares(secret_id: int, user_shares_data: list) -> str:
    """
    Приймає список часток (кожна частка — це словник або об'єкт із координатою x та y у вигляді JSON-строки),
    форматує їх під наш алгоритм Шаміра і відновлює оригінальний текст.
    """
    import json
    
    # Перетворюємо дані у формат, який очікує recover_string_secret
    # Нам потрібно отримати: [ [ (x1, y1_блок1), (x2, y2_блок1)... ], [ (x1, y1_блок2)... ] ]
    
    # Дізнаємося, скільки блоків у нас взагалі є, глянувши на першу частку
    first_y_list = json.loads(user_shares_data[0]['y'])
    num_blocks = len(first_y_list)
    
    shares_by_blocks = [[] for _ in range(num_blocks)]
    
    for share in user_shares_data:
        x_val = share['x']
        y_list = json.loads(share['y'])
        
        for block_idx in range(num_blocks):
            shares_by_blocks[block_idx].append((x_val, y_list[block_idx]))
            
    # Відновлюємо текст за допомогою нашого ядра
    raw_secret = recover_string_secret(shares_by_blocks)
    return raw_secret