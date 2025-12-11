from access_data import token_Ydisk   # Для работы требуется ваш токен
from tqdm import tqdm
import requests
import logging
import time
import json



# Настройка параметров логирования
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    filename="Dog_API_log.log",
    level=logging.INFO,
    encoding='utf-8',
    filemode='w'

)

class DogKeeper:
    "Класс загружает картинки собак в ваш Яндекс Диск"
    def __init__(self, token: str):
        "Для работы требуется ваш токен"
        self.token = token

    def save_dog(self, breed: str = "mastiff"):
        "Сохраняет ссылку на картинку собаки той породы переданной в аргумент, а если есть подпороды, то сохраняет и их тоже"
        self.response = requests.get(f"https://dog.ceo/api/breed/{breed}/list", timeout=45).json()   # Повышенное время ожидания

        # Проверка корректности запроса
        if self.response['status'] == 'success':
            self.list_subbreed = self.response['message']
            logging.info("Успешный ответ от dog.ceo")

            # Проверка наличия подпород
            if len(self.list_subbreed) != 0:
                logging.info("Условие подпород выполнено")
                for s_breed in tqdm(self.list_subbreed):
                    # Получаем ссылку на картинку и имя для неё
                    self.link_f_picture = requests.get(f"https://dog.ceo/api/breed/{breed}/{s_breed}/images/random").json()
                    self.name_image = self.link_f_picture["message"].split('/')[-1]

                    # Данные для работы при условии подпород
                    self.path = f'{breed}/{breed}-{s_breed}_{self.name_image}'
                    self.for_save = f'{breed}-{s_breed}/{self.name_image}'

                    # Вызов рабочей метода с нужными данными
                    self.create_folder(self.path, breed, self.for_save) # тут прогресс бар!
                    time.sleep(1)
            else:
                logging.info("Условие подпород не выполнено")
                # Условие, если нет подпород
                self.link_f_picture = requests.get(f"https://dog.ceo/api/breed/{breed}/images/random").json()
                self.name_image = self.link_f_picture["message"].split('/')[-1]

                # Данные для работы при условии отсутствия подпород
                self.path = f'{breed}/{breed}_{self.name_image}'
                self.for_save = f'{breed}/{self.name_image}'

                # Вызов метода
                self.create_folder(self.path, breed, self.for_save)
        else:
            logging.error("Ошибка вводимого аргумента")
            raise ValueError("""Такой породы не найдено!
            Проверьте правильность ввода породы и повторите попытку""")

    def create_folder(self, path, breed, data):
        """
        Метод:
        создаёт папку, если её ещё нет,
        получает ссылку для загрузки,
        загружает картинку на диск,
        фиксирует работу в техническом файле.
         """
        # Создание папки
        try:
            requests.put(
                    'https://cloud-api.yandex.net/v1/disk/resources',
                    headers={'Authorization': self.token},
                    params={'path': f'{breed}'}
            )

            # Получение ссылки для загрузки
            self.down_link = requests.get(
                'https://cloud-api.yandex.net/v1/disk/resources/upload',
                    headers={'Authorization': self.token},
                    params={'path': f'{self.path}'}
            ).json()["href"]

            # Осуществление загрузки
            requests.post(
                self.down_link,
                files={'file': requests.get(self.link_f_picture["message"]).content},
                headers={'Authorization': self.token},
                params={
                    'path': f'{self.path}',
                    'url': self.down_link
                    },
                )
            logging.info(f"Файл {self.name_image} успешно загружен")

            # Фиксация работы в технический файл
            with open("tech_data_dogs.json", "r", encoding='utf-8') as fl:
                self.data = fl.read()
            with open("tech_data_dogs.json", "w+t", encoding='utf-8') as f:
                self.new = json.loads(self.data)
                self.new.append(
                    {
                        "File_name": f"{breed}_{self.name_image}",
                        "Completed": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        "Content_Length": str(requests.get(f"https://images.dog.ceo/breeds/{data}").headers).split("', '")[2].split("': '")[1]
                    }
                )
                json.dump(self.new, f, ensure_ascii=False, indent=2)
                logging.info("Технический файл обновлён")

        except KeyError:
            logging.error("Ошибка существования загружаемого файла")
            raise FileExistsError(f"""Файл {self.name_image} уже существует - программа не сможет его перезаписать
            Удалите с диска этот файл вручную или выберите другую породу""")
        except TimeoutError:
            logging.error("Ошибка сервер не отвечает")
            raise TimeoutError("Сервер молчит слишком долго")
        except:
            logging.critical("Непредвиденный крах программы")
            raise Exception("Незафиксированная ошибка")

    def clear_tech_data(self):
        "Позволяет очистить данные технического файла"
        with open("tech_data_dogs.json", "w") as fl:
            json.dump([], fl)
        logging.info("Технический файл очищен")


# Демонстрация выполнения
logging.info("Начало работы программы")
save_dog = DogKeeper(token_Ydisk)
save_dog.save_dog()   # Можно и задать породу по необходимости
logging.info("Конец выполнения программы")