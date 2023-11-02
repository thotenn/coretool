import threading
from concurrent import futures # INVESTIGAR MAS DE ESTA LIBRERIA
from random import random
from time import sleep
import requests # pip3 install requests

nums = range(1, 11)

url_tpl = "http://jsonplaceholder.typicode.com/todos/{}"

def get_data(myid):
    url = url_tpl.format(myid)
    data = requests.get(url).json()
    sleep(random() * 5)
    return data

def main(): # Espera a que todas las llamadas se ejecuten en paralelo
    with futures.ThreadPoolExecutor(4) as executor:
        results = executor.map(get_data, nums)
        print()
        for result in results:
            print(result)

def main2(): # realiza ya cosas a medida que vaya volviendo cada una, RESULTADOS SEGUN ESTAN DISPONIBLES
    with futures.ThreadPoolExecutor(4) as executor:
        jobs = [executor.submit(get_data, num) for num in nums]
        for comp_job in futures.as_completed(jobs):
            print(comp_job.result())



if __name__ == '__main__':
    main()


# en vez de ThreadPoolExecutor puedo utilizar ProcessPoolExecutor para en vez de ejecutarse en hilos
# esto se ejecute en procesos, sera mas rapido solo que esto requiere de mas poder de procesamiento