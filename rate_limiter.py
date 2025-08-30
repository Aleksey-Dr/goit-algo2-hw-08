import random
from typing import Dict
import time
from collections import deque

class SlidingWindowRateLimiter:
    """
    Реалізація Rate Limiter з використанням алгоритму Sliding Window.
    """
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        """
        Ініціалізує Rate Limiter.

        :param window_size: Розмір часового вікна в секундах.
        :param max_requests: Максимальна кількість запитів у вікні.
        """
        self.window_size = window_size
        self.max_requests = max_requests
        # Зберігаємо історію повідомлень для кожного користувача
        # у вигляді словника, де ключ — user_id, а значення — deque міток часу.
        self.users_history: Dict[str, deque[float]] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Очищає застарілі запити з вікна користувача.

        :param user_id: Ідентифікатор користувача.
        :param current_time: Поточна мітка часу.
        """
        if user_id in self.users_history:
            window_start_time = current_time - self.window_size
            # Видаляємо всі мітки часу, які старші за початок вікна
            while self.users_history[user_id] and self.users_history[user_id][0] < window_start_time:
                self.users_history[user_id].popleft()
            # Якщо після очищення deque порожній, видаляємо користувача зі словника
            if not self.users_history[user_id]:
                del self.users_history[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """
        Перевіряє, чи може користувач відправити повідомлення.

        :param user_id: Ідентифікатор користувача.
        :return: True, якщо повідомлення можна відправити, інакше False.
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        # Якщо користувача немає в історії або кількість його запитів
        # менша за ліміт, він може відправити повідомлення.
        if user_id not in self.users_history or len(self.users_history[user_id]) < self.max_requests:
            return True
        return False

    def record_message(self, user_id: str) -> bool:
        """
        Записує нове повідомлення, якщо воно дозволене.

        :param user_id: Ідентифікатор користувача.
        :return: True, якщо повідомлення записано, інакше False.
        """
        if self.can_send_message(user_id):
            current_time = time.time()
            if user_id not in self.users_history:
                self.users_history[user_id] = deque()
            self.users_history[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Розраховує час очікування до можливості відправлення наступного повідомлення.

        :param user_id: Ідентифікатор користувача.
        :return: Час очікування в секундах.
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        # Якщо користувача немає або він може відправити повідомлення,
        # час очікування дорівнює 0.
        if user_id not in self.users_history or len(self.users_history[user_id]) < self.max_requests:
            return 0.0
        # Час очікування — це час, що залишився до кінця вікна
        # після найстарішого запиту.
        oldest_message_time = self.users_history[user_id][0]
        wait_time = self.window_size - (current_time - oldest_message_time)
        return max(0, wait_time)
    
# Демонстрація роботи

# ANSI escape-послідовності для кольору та скидання кольору
RED = '\033[91m'
GREEN = '\033[92m' # Код для яскраво-зеленого кольору
BLUE = '\033[94m'  # Код для яскраво-синього кольору
RESET = '\033[0m'

def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print(f"{BLUE}\n=== Симуляція потоку повідомлень ==={RESET}")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{f'{GREEN}✓{RESET}' if result else f'{RED}×{RESET} (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

    print(f"{GREEN}\nОчікуємо 4 секунди...{RESET}")
    time.sleep(4)

    print(f"{BLUE}\n=== Нова серія повідомлень після очікування ==={RESET}")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{f'{GREEN}✓{RESET}' if result else f'{RED}×{RESET} (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()