from Elizarovskaya.bot import start_eli_bot
from Veteranov.bot import start_vet_bot
from Apollo.bot import start_apo_bot
from ChernayaRechka.bot import start_che_bot
from Paroizolaziya.bot import start_par_bot
from Yanino_bricks.bot import start_yan_bot
from evropeysakaya.bot import start_evr_bot
from Kushelevka.bot import start_kush_bot

import threading
import sys




if __name__ == "__main__":
    print("enter")
    start_kush_bot()
    # bot_functions = [start_kush_bot]
    # # Создайте и запустите потоки
    # threads = [threading.Thread(target=func) for func in bot_functions]
    #
    # try:
    #     for thread in threads:
    #         thread.start()
    #
    #     for thread in threads:
    #         thread.join()
    #
    #     # Установите обработчик для события нажатия клавиши
    #     print("Нажмите Ctrl+C для завершения программы.")
    #     while True:
    #         pass
    #
    # except KeyboardInterrupt:
    #     # Завершите программу
    #     sys.exit()
    #
