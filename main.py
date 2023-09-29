# from Elizarovskaya.bot import start_eli_bot
from Veteranov.bot import start_vet_bot
from Apollo.bot import start_apo_bot
from ChernayaRechka.bot import start_che_bot
from Paroizolaziya.bot import start_par_bot
from Yanino_bricks.bot import start_yan_bot
from evropeysakaya.bot import start_evr_bot

import threading

# start_bot = [start_eli_bot, start_vet_bot, start_apo_bot,
#              start_che_bot, start_par_bot, start_yan_bot, start_evr_bot]

if __name__ == "__main__":
    # thread1 = threading.Thread(target=start_eli_bot)
    thread2 = threading.Thread(target=start_vet_bot)
    thread3 = threading.Thread(target=start_apo_bot)
    # thread4 = threading.Thread(target=start_che_bot)
    # thread5 = threading.Thread(target=start_par_bot)
    thread6 = threading.Thread(target=start_yan_bot)
    thread7 = threading.Thread(target=start_evr_bot)

    # thread1.start()
    thread2.start()
    thread3.start()
    # thread4.start()
    # thread5.start()
    thread6.start()
    thread7.start()

    # thread1.join()
    thread2.join()
    thread3.join()
    # thread4.join()
    # thread5.join()
    thread6.join()
    thread7.join()
