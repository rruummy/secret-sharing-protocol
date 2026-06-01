import secrets
from typing import List, Tuple

# Велике просте число Мерсенна (p = 2^127 - 1) для обчислень у скінченному полі GF(p)
PRIME = 2**127 - 1


def _extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Розширений алгоритм Евкліда.
    Повертає (g, x, y), такі що a*x + b*y = g = gcd(a, b).
    """
    if a == 0:
        return b, 0, 1
    g, x1, y1 = _extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y


def _mod_inverse(k: int, p: int) -> int:
    """
    Обчислення модульного оберненого елемента (1 / k) mod p.
    """
    k = k % p
    if k < 0:
        k += p
    g, x, _ = _extended_gcd(k, p)
    if g != 1:
        raise ValueError("Модульне обернене число не існує (числа не взаємно прості).")
    return x % p


def split_secret(secret: int, n: int, k: int) -> List[Tuple[int, int]]:
    """
    Розділяє числовий секрет на n часток, де для відновлення потрібно мінімум k часток.
    Секрет повинен бути меншим за PRIME.
    """
    if k > n:
        raise ValueError("Поріг (k) не може бути більшим за загальну кількість часток (n).")
    if secret >= PRIME:
        raise ValueError(f"Секрет занадто великий. Має бути меншим за {PRIME}.")
    if secret < 0:
        raise ValueError("Секрет не може бути від'ємним числом.")

    # Генеруємо випадкові коефіцієнти для полінома ступеня k-1:
    # P(x) = a_0 + a_1*x + a_2*x^2 + ... + a_{k-1}*x^{k-1}
    # де a_0 — це наш секрет
    coefficients = [secret] + [secrets.randbelow(PRIME) for _ in range(k - 1)]

    shares = []
    for x in range(1, n + 1):
        # Обчислюємо значення полінома P(x) mod PRIME за схемою Горнера
        y = 0
        for coeff in reversed(coefficients):
            y = (y * x + coeff) % PRIME
        shares.append((x, y))

    return shares


def recover_secret(shares: List[Tuple[int, int]]) -> int:
    """
    Відновлює числовий секрет із часток за допомогою інтерполяції Лагранжа в полі GF(p).
    """
    if len(shares) == 0:
        raise ValueError("Список часток порожній.")

    x_coords, y_coords = zip(*shares)
    
    # Перевіряємо унікальність координат x
    if len(set(x_coords)) != len(x_coords):
        raise ValueError("Координати 'x' усіх часток мають бути унікальними.")

    secret = 0
    # Обчислюємо значення полінома в точці x = 0: P(0)
    for i in range(len(shares)):
        xi, yi = shares[i]
        num = 1
        den = 1
        for j in range(len(shares)):
            if i == j:
                continue
            xj, _ = shares[j]
            num = (num * (-xj)) % PRIME
            den = (den * (xi - xj)) % PRIME

        # l_i(0) = num / den (в сенсі модульної арифметики)
        l_i_0 = (num * _mod_inverse(den, PRIME)) % PRIME
        secret = (secret + yi * l_i_0) % PRIME

    return (secret + PRIME) % PRIME

def split_string_secret(secret_str: str, n: int, k: int) -> List[List[Tuple[int, int]]]:
    """
    Приймає текстовий секрет будь-якої довжини, кодує його в байти,
    розбиває на блоки по 15 байт і генерує частки для кожного блоку.
    Повертає список часток для кожного блоку.
    """
    secret_bytes = secret_str.encode('utf-8')
    block_size = 15  # 15 байт гарантовано менше ніж 2^127 - 1
    
    all_blocks_shares = []
    
    # Йдемо по тексту кроком у 15 байт
    for i in range(0, len(secret_bytes), block_size):
        block = secret_bytes[i:i+block_size]
        # Конвертуємо 15 байт у велике число int
        secret_int = int.from_bytes(block, byteorder='big')
        
        # Розділяємо це число за схемою Шаміра
        block_shares = split_secret(secret_int, n, k)
        all_blocks_shares.append(block_shares)
        
    return all_blocks_shares


def recover_string_secret(shares_by_blocks: List[List[Tuple[int, int]]]) -> str:
    """
    Приймає частки для кожного блоку, відновлює числові значення,
    конвертує їх назад у байти та збирає початковий рядок.
    """
    if not shares_by_blocks or len(shares_by_blocks) == 0:
        raise ValueError("Немає часток для відновлення.")
        
    reconstructed_bytes = bytearray()
    
    for block_shares in shares_by_blocks:
        # Відновлюємо число для конкретного блоку
        secret_int = recover_secret(block_shares)
        
        # Рахуємо, скільки байт займає це число (мінімум 1)
        byte_length = max((secret_int.bit_length() + 7) // 8, 1)
        
        # Конвертуємо int назад у байти
        block_bytes = secret_int.to_bytes(byte_length, byteorder='big')
        reconstructed_bytes.extend(block_bytes)
        
    return reconstructed_bytes.decode('utf-8')