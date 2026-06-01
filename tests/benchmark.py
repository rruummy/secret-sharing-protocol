import time
import json
from crypto.shamir import split_string_secret, recover_string_secret


def benchmark_secret_size():
    """Замір залежності часу від розміру секрету (n=5, k=3)."""
    print("\n--- Бенчмарк: Розмір Секрету ---")
    n, k = 5, 3
    sizes = [10, 100, 1000, 5000, 10000]  # довжина рядка в символах
    results = []

    for size in sizes:
        secret = "A" * size
        
        # Замір розділення
        start_split = time.perf_counter()
        shares = split_string_secret(secret, n, k)
        end_split = time.perf_counter()
        
        # Замір відновлення (беремо перші k часток для кожного блоку)
        user_shares = [block[:k] for block in shares]
        start_recover = time.perf_counter()
        recover_string_secret(user_shares)
        end_recover = time.perf_counter()
        
        split_time = end_split - start_split
        recover_time = end_recover - start_recover
        
        print(f"Розмір: {size:5} симв. | Розділення: {split_time:.5f}с | Відновлення: {recover_time:.5f}с")
        results.append({"size": size, "split_time": split_time, "recover_time": recover_time})
        
    return results


def benchmark_parameters():
    """Замір залежності часу від параметрів N та K (фіксований секрет 100 символів)."""
    print("\n--- Бенчмарк: Вплив N та K ---")
    secret = "This is a standard benchmark secret string used to measure performance with different parameters."
    
    # Пари (N, K)
    scenarios = [
        (5, 3),
        (10, 5),
        (20, 10),
        (50, 25),
        (100, 50)
    ]
    results = []

    for n, k in scenarios:
        # Замір розділення
        start_split = time.perf_counter()
        shares = split_string_secret(secret, n, k)
        end_split = time.perf_counter()
        
        # Замір відновлення
        user_shares = [block[:k] for block in shares]
        start_recover = time.perf_counter()
        recover_string_secret(user_shares)
        end_recover = time.perf_counter()
        
        split_time = end_split - start_split
        recover_time = end_recover - start_recover
        
        print(f"N={n:<3} K={k:<3} | Розділення: {split_time:.5f}с | Відновлення: {recover_time:.5f}с")
        results.append({"n": n, "k": k, "split_time": split_time, "recover_time": recover_time})
        
    return results


if __name__ == "__main__":
    print("Запуск досліджень для курсової роботи...")
    size_data = benchmark_secret_size()
    param_data = benchmark_parameters()
    
    # Збережемо результати в файл для майбутнього використання
    report = {
        "size_benchmark": size_data,
        "parameter_benchmark": param_data
    }
    with open("docs/benchmark_results.json", "w") as f:
        json.dump(report, f, indent=4)
    print("\n[Успішно] Результати збережено у docs/benchmark_results.json")