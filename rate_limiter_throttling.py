import time
from typing import Dict
import random

class ThrottlingRateLimiter:
    """
    Реалізація Rate Limiter з використанням алгоритму Throttling.
    
    Цей клас контролює частоту повідомлень, забезпечуючи фіксований мінімальний
    інтервал між повідомленнями для кожного користувача.
    """
    def __init__(self, min_interval: float = 10.0):
        """
        Ініціалізує лімітер.

        :param min_interval: Мінімальний інтервал у секундах між повідомленнями.
        """
        self.min_interval = min_interval
        self.last_message_time: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        """
        Перевіряє, чи може користувач відправити повідомлення.

        :param user_id: Ідентифікатор користувача.
        :return: True, якщо повідомлення можна відправити, інакше False.
        """
        last_time = self.last_message_time.get(user_id)
        if last_time is None:
            return True
        
        return (time.time() - last_time) >= self.min_interval

    def record_message(self, user_id: str) -> bool:
        """
        Записує нове повідомлення від користувача, якщо це дозволено.

        :param user_id: Ідентифікатор користувача.
        :return: True, якщо повідомлення було записано, інакше False.
        """
        if self.can_send_message(user_id):
            self.last_message_time[user_id] = time.time()
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Розраховує час до наступного дозволеного повідомлення.

        :param user_id: Ідентифікатор користувача.
        :return: Час очікування в секундах.
        """
        last_time = self.last_message_time.get(user_id)
        if last_time is None:
            return 0.0
            
        time_to_wait = self.min_interval - (time.time() - last_time)
        return max(0, time_to_wait)

# ANSI escape-послідовності для кольору та скидання кольору
RED = '\033[91m'
GREEN = '\033[92m' # Код для яскраво-зеленого кольору
BLUE = '\033[94m'  # Код для яскраво-синього кольору
RESET = '\033[0m'

def test_throttling_limiter():
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print(f"{BLUE}\n=== Симуляція потоку повідомлень (Throttling) ==={RESET}")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{f'{GREEN}✓{RESET}' if result else f'{RED}×{RESET} (очікування {wait_time:.1f}с)'}")

        # Випадкова затримка між повідомленнями
        time.sleep(random.uniform(0.1, 1.0))

    print(f"{GREEN}\nОчікуємо 10 секунд...{RESET}")
    time.sleep(10)

    print(f"{BLUE}\n=== Нова серія повідомлень після очікування ==={RESET}")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{f'{GREEN}✓{RESET}' if result else f'{RED}×{RESET} (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_throttling_limiter()