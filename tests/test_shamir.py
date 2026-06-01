import pytest
from crypto.shamir import (
    split_secret, 
    recover_secret, 
    PRIME, 
    split_string_secret, 
    recover_string_secret
)


def test_successful_reconstruction():
    """Перевірка, що секрет успішно відновлюється з мінімально необхідної кількості часток."""
    secret = 987654321
    n = 5
    k = 3

    shares = split_secret(secret, n, k)
    assert len(shares) == n

    # Беремо рівно k часток (перші 3)
    recovered = recover_secret(shares[:k])
    assert recovered == secret


def test_reconstruction_with_all_shares():
    """Перевірка відновлення, якщо використано всі n часток."""
    secret = 55555
    n = 6
    k = 4

    shares = split_secret(secret, n, k)
    recovered = recover_secret(shares)
    assert recovered == secret


def test_reconstruction_with_random_subset():
    """Перевірка, що секрет відновлюється з будь-якої комбінації k часток."""
    secret = 123456789
    n = 7
    k = 3

    shares = split_secret(secret, n, k)
    
    # Беремо не послідовні частки, наприклад: 2-гу, 4-ту та 6-ту (індекси 1, 3, 5)
    subset = [shares[1], shares[3], shares[5]]
    recovered = recover_secret(subset)
    assert recovered == secret


def test_insufficient_shares_raises_error():
    """
    Важливий тест: якщо часток менше ніж k, алгоритм НЕ повинен відновлювати секрет.
    Оскільки ми працюємо в полі GF(p), будь-яка менша кількість часток дасть випадкове неправильне число.
    """
    secret = 11111
    n = 5
    k = 3

    shares = split_secret(secret, n, k)
    
    # Беремо лише 2 частки замість 3
    insufficient_shares = shares[:2]
    recovered = recover_secret(insufficient_shares)
    
    # Секрет ТОЧНО не повинен збігатися
    assert recovered != secret


def test_invalid_parameters():
    """Перевірка обробки некоректних вхідних даних (k > n, великий секрет тощо)."""
    # k > n
    with pytest.raises(ValueError, match="Поріг .* не може бути більшим за загальну кількість часток"):
        split_secret(123, 5, 6)

    # Секрет більший або рівний PRIME
    with pytest.raises(ValueError, match="Секрет занадто великий"):
        split_secret(PRIME + 1, 5, 3)

    # Від'ємний секрет
    with pytest.raises(ValueError, match="Секрет не може бути від'ємним числом"):
        split_secret(-10, 5, 3)


def test_empty_shares_raises_error():
    """Перевірка виклику помилки при передачі порожнього списку часток."""
    with pytest.raises(ValueError, match="Список часток порожній"):
        recover_secret([])


def test_duplicate_shares_raises_error():
    """Перевірка, що однакові частки (дублікати) викличуть помилку."""
    shares = [(1, 500), (1, 500), (3, 600)]
    with pytest.raises(ValueError, match="Координати 'x' усіх часток мають бути унікальними"):
        recover_secret(shares)

def test_string_secret_reconstruction_short():
    """Перевірка відновлення короткого рядка (менше 15 символів)."""
    secret = "Hello!"
    n, k = 5, 3
    
    # Отримуємо частки для блоків (буде 1 блок)
    blocks_shares = split_string_secret(secret, n, k)
    
    # Імітуємо, що користувач надіслав перші k часток для кожного блоку
    user_shares = [block[:k] for block in blocks_shares]
    
    recovered = recover_string_secret(user_shares)
    assert recovered == secret


def test_string_secret_reconstruction_long():
    """Перевірка відновлення довгого рядка, який точно розіб'ється на кілька блоків."""
    secret = "This is a very long secret that will definitely take more than fifteen bytes to store!"
    n, k = 5, 3
    
    blocks_shares = split_string_secret(secret, n, k)
    
    # Беремо випадкові k часток (наприклад, останні 3: з індексу 2 до 5)
    user_shares = [block[2:] for block in blocks_shares]
    
    recovered = recover_string_secret(user_shares)
    assert recovered == secret